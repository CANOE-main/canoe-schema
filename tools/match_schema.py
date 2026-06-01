#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SchemaSignature:
    version: str
    source_sql: Path
    tables: dict[str, tuple[str, ...]]


def _split_csv_top_level(text: str) -> list[str]:
    parts: list[str] = []
    buf: list[str] = []
    depth = 0
    in_str = False
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == "'":
            buf.append(ch)
            if in_str and i + 1 < len(text) and text[i + 1] == "'":
                buf.append(text[i + 1])
                i += 1
            else:
                in_str = not in_str
        elif not in_str and ch == '(':
            depth += 1
            buf.append(ch)
        elif not in_str and ch == ')':
            depth = max(0, depth - 1)
            buf.append(ch)
        elif not in_str and depth == 0 and ch == ',':
            part = ''.join(buf).strip()
            if part:
                parts.append(part)
            buf = []
        else:
            buf.append(ch)
        i += 1
    tail = ''.join(buf).strip()
    if tail:
        parts.append(tail)
    return parts


def _table_columns_from_create_body(body: str) -> tuple[str, ...]:
    columns: list[str] = []
    for item in _split_csv_top_level(body):
        stmt = item.strip()
        upper = stmt.upper()
        if not stmt:
            continue
        if upper.startswith('PRIMARY KEY'):
            continue
        if upper.startswith('FOREIGN KEY'):
            continue
        if upper.startswith('CHECK'):
            continue
        m = re.match(r'(\w+)\s+[A-Za-z]+', stmt)
        if m:
            columns.append(m.group(1))
    return tuple(columns)


def parse_sql_signature(sql_path: Path, version: str) -> SchemaSignature:
    sql_text = sql_path.read_text(encoding='utf-8')
    create_re = re.compile(r'CREATE TABLE IF NOT EXISTS\s+(\w+)\s*\((.*?)\);', re.S)

    tables: dict[str, tuple[str, ...]] = {}
    for m in create_re.finditer(sql_text):
        table = m.group(1)
        if table in tables:
            continue
        body = m.group(2)
        tables[table] = _table_columns_from_create_body(body)

    return SchemaSignature(version=version, source_sql=sql_path, tables=tables)


def read_sqlite_signature(db_path: Path) -> dict[str, tuple[str, ...]]:
    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()
        table_names = [
            row[0]
            for row in cur.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                  AND name NOT LIKE 'sqlite_%'
                ORDER BY name
                """
            )
        ]
        table_map: dict[str, tuple[str, ...]] = {}
        for table in table_names:
            cols = [
                row[1]
                for row in cur.execute(
                    f'PRAGMA table_info("{table.replace(chr(34), chr(34) * 2)}")'
                )
            ]
            table_map[table] = tuple(cols)
        return table_map
    finally:
        conn.close()


def read_metadata_version(db_path: Path) -> dict[str, int] | None:
    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()
        has_meta = cur.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='MetaData'"
        ).fetchone()
        if not has_meta:
            return None

        rows = dict(
            cur.execute(
                "SELECT element, value FROM MetaData WHERE element IN ('DB_MAJOR', 'DB_MINOR')"
            ).fetchall()
        )
        if 'DB_MAJOR' in rows and 'DB_MINOR' in rows:
            return {'major': int(rows['DB_MAJOR']), 'minor': int(rows['DB_MINOR'])}
        return None
    finally:
        conn.close()


def score_match(
    db_tables: dict[str, tuple[str, ...]],
    expected_tables: dict[str, tuple[str, ...]],
) -> tuple[float, int, int, int]:
    db_table_names = set(db_tables.keys())
    exp_table_names = set(expected_tables.keys())

    common = db_table_names & exp_table_names
    if not exp_table_names:
        return 0.0, 0, 0, 0

    table_overlap = len(common) / len(exp_table_names)

    col_total = 0
    col_overlap = 0
    for table in common:
        exp_cols = expected_tables[table]
        db_cols = db_tables[table]
        col_total += len(exp_cols)
        col_overlap += sum(1 for c in exp_cols if c in db_cols)

    col_score = (col_overlap / col_total) if col_total else 0.0
    score = 0.6 * table_overlap + 0.4 * col_score
    return score, len(common), len(exp_table_names), len(db_table_names)


def classify(db_path: Path, signatures: list[SchemaSignature]) -> dict:
    db_tables = read_sqlite_signature(db_path)
    metadata_version = read_metadata_version(db_path)

    exact_matches = [
        sig.version
        for sig in signatures
        if db_tables == sig.tables
    ]

    ranked = []
    for sig in signatures:
        score, common, expected_total, db_total = score_match(db_tables, sig.tables)
        ranked.append(
            {
                'version': sig.version,
                'score': round(score, 6),
                'common_tables': common,
                'expected_tables': expected_total,
                'db_tables': db_total,
                'exact': db_tables == sig.tables,
            }
        )

    ranked.sort(key=lambda x: x['score'], reverse=True)

    return {
        'database': str(db_path),
        'metadata_version': metadata_version,
        'exact_matches': exact_matches,
        'best_match': ranked[0] if ranked else None,
        'candidates': ranked,
        'recommendation': (
            "Add a string schema id in a dedicated table (for example SchemaIdentity with "
            "key='schema_version' and value='3.1' or '3.2') for unambiguous runtime detection."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Match a SQLite database against known CANOE schema versions.'
    )
    parser.add_argument('sqlite_db', type=Path, help='Path to SQLite database file')
    parser.add_argument(
        '--format',
        choices=['json', 'text'],
        default='text',
        help='Output format',
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    signatures = [
        parse_sql_signature(repo_root / 'schema' / 'v3_1' / 'schema_3_1.sql', '3.1'),
        parse_sql_signature(repo_root / 'schema' / 'v3_2' / 'schema_3_2.sql', '3.2'),
    ]

    result = classify(args.sqlite_db, signatures)

    if args.format == 'json':
        print(json.dumps(result, indent=2, sort_keys=True))
        return

    print(f"Database: {result['database']}")
    if result['metadata_version']:
        md = result['metadata_version']
        print(f"MetaData version keys: DB_MAJOR={md['major']} DB_MINOR={md['minor']}")
    else:
        print('MetaData version keys: unavailable')

    if result['exact_matches']:
        print('Exact schema match: ' + ', '.join(result['exact_matches']))
    else:
        print('Exact schema match: none')

    best = result['best_match']
    if best:
        print(
            f"Best candidate: {best['version']} (score={best['score']}, "
            f"tables {best['common_tables']}/{best['expected_tables']})"
        )

    print('Recommendation: ' + result['recommendation'])


if __name__ == '__main__':
    main()
