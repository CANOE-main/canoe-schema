#!/usr/bin/env python3
"""
diff_db.py — row-level diff between two SQLite databases.

Usage:
    python diff_db.py a.db b.db                 # summary of all tables
    python diff_db.py a.db b.db --table demand   # detail for one table
    python diff_db.py a.db b.db --verbose        # detail for all tables
    python diff_db.py a.db b.db --limit 50       # cap rows shown per table
    python diff_db.py a.db b.db --all            # include identical tables
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path


LARGE_THRESHOLD = 100_000  # skip row diff for tables larger than this
AUTO_DETAIL_MAX = 20       # expand to full detail automatically when total diffs ≤ this
DEFAULT_LIMIT = 30         # max differing rows shown per table in detail mode


# ── schema types ──────────────────────────────────────────────────────────────


@dataclass
class ColInfo:
    name: str
    type_: str
    notnull: bool
    default: str | None
    pk_order: int  # 0 = not PK; >0 = PK column position


@dataclass
class TableSchema:
    name: str
    cols: list[ColInfo]

    @property
    def pk_names(self) -> list[str]:
        ordered = sorted((c for c in self.cols if c.pk_order > 0), key=lambda c: c.pk_order)
        return [c.name for c in ordered]

    @property
    def col_by_lower(self) -> dict[str, ColInfo]:
        return {c.name.lower(): c for c in self.cols}


# ── diff result types ─────────────────────────────────────────────────────────


@dataclass
class SchemaDiff:
    only_in_a: list[str]                        # col names (A's case) missing in B
    only_in_b: list[str]                        # col names (B's case) missing in A
    type_changes: list[tuple[str, str, str]]    # (col_name_a, type_a, type_b)

    @property
    def has_diff(self) -> bool:
        return bool(self.only_in_a or self.only_in_b or self.type_changes)


@dataclass
class TableDiff:
    name_a: str
    name_b: str
    match_kind: str | None   # None=exact, 'case'=renamed, 'fuzzy'=fuzzy match
    pk_cols: list[str]       # A-side PK column names, or ['rowid']
    count_a: int
    count_b: int
    schema: SchemaDiff
    only_in_a: list[tuple]                              # PK tuples of rows only in A
    only_in_b: list[tuple]                              # PK tuples of rows only in B
    differing: list[tuple[tuple, dict[str, tuple]]]     # (pk, {col: (val_a, val_b)})
    too_large: bool = False

    @property
    def total_delta(self) -> int:
        return len(self.only_in_a) + len(self.only_in_b) + len(self.differing)

    @property
    def has_diff(self) -> bool:
        return self.too_large or self.total_delta > 0 or self.schema.has_diff


# ── reading ───────────────────────────────────────────────────────────────────


def _q(s: str) -> str:
    """Escape a SQL identifier by doubling any embedded double-quotes."""
    return s.replace('"', '""')


def read_schema(conn: sqlite3.Connection) -> dict[str, TableSchema]:
    schemas: dict[str, TableSchema] = {}
    for (tname,) in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    ):
        cols = [
            ColInfo(
                name=row[1],
                type_=row[2] or '',
                notnull=bool(row[3]),
                default=row[4],
                pk_order=row[5],
            )
            for row in conn.execute(f'PRAGMA table_info("{_q(tname)}")')
        ]
        schemas[tname] = TableSchema(tname, cols)
    return schemas


# ── table matching ────────────────────────────────────────────────────────────


FUZZY_THRESH = 0.70

_CAMEL_RE = re.compile(r'[A-Z]+(?=[A-Z][a-z]|\d|$)|[A-Z]?[a-z0-9]+|[A-Z]+')


def _normalize(name: str) -> str:
    """
    Canonical token string for a table name, collapsing snake_case and CamelCase
    to the same form.  'demand_period' and 'DemandPeriod' both yield 'demandperiod'.
    """
    tokens: list[str] = []
    for part in name.split('_'):
        if part:
            tokens.extend(t.lower() for t in _CAMEL_RE.findall(part))
    return ''.join(tokens)


def _sim(a: str, b: str) -> float:
    """Similarity score [0, 1] between two lowercase table names."""
    if a == b:
        return 1.0
    # Substring containment: score proportional to how much shorter is of longer
    if a in b or b in a:
        return len(min(a, b, key=len)) / len(max(a, b, key=len))
    # Longest common prefix ratio
    matched = 0
    for ca, cb in zip(a, b):
        if ca == cb:
            matched += 1
        else:
            break
    return matched / max(len(a), len(b))


def match_tables(
    sa: dict[str, TableSchema],
    sb: dict[str, TableSchema],
) -> tuple[list[tuple[str, str, str | None]], list[str], list[str]]:
    """
    Returns (pairs, only_in_a, only_in_b).
    Each pair is (name_a, name_b, match_kind) where match_kind is:
        None     — exact name match
        'case'   — same name after case-folding  (e.g. demand → Demand)
        'norm'   — same tokens after normalizing snake_case/CamelCase  (e.g. demand_period → DemandPeriod)
        'fuzzy'  — similar name above threshold
    """
    pairs: list[tuple[str, str, str | None]] = []
    matched_a: set[str] = set()
    matched_b: set[str] = set()

    # Pass 1: exact
    for name_a in sorted(sa):
        if name_a in sb:
            pairs.append((name_a, name_a, None))
            matched_a.add(name_a)
            matched_b.add(name_a)

    # Pass 2: case-insensitive
    lower_b: dict[str, str] = {n.lower(): n for n in sb if n not in matched_b}
    for name_a in sorted(sa):
        if name_a in matched_a:
            continue
        key = name_a.lower()
        if key in lower_b:
            name_b = lower_b.pop(key)
            pairs.append((name_a, name_b, 'case'))
            matched_a.add(name_a)
            matched_b.add(name_b)

    # Pass 3: normalized name match (snake_case ↔ CamelCase equivalence)
    norm_b: dict[str, str] = {_normalize(n): n for n in sb if n not in matched_b}
    for name_a in sorted(sa):
        if name_a in matched_a:
            continue
        key = _normalize(name_a)
        if key in norm_b:
            name_b = norm_b.pop(key)
            pairs.append((name_a, name_b, 'norm'))
            matched_a.add(name_a)
            matched_b.add(name_b)

    # Pass 4: fuzzy (substring containment or long common prefix)
    rem_b = [n for n in sb if n not in matched_b]
    for name_a in sorted(sa):
        if name_a in matched_a:
            continue
        la = name_a.lower()
        best_score = 0.0
        best_b: str | None = None
        for name_b in rem_b:
            s = _sim(la, name_b.lower())
            if s > best_score:
                best_score = s
                best_b = name_b
        if best_b is not None and best_score >= FUZZY_THRESH:
            pairs.append((name_a, best_b, 'fuzzy'))
            matched_a.add(name_a)
            matched_b.add(best_b)
            rem_b.remove(best_b)

    only_a = sorted(n for n in sa if n not in matched_a)
    only_b = sorted(n for n in sb if n not in matched_b)
    return pairs, only_a, only_b


# ── content diff ──────────────────────────────────────────────────────────────


def _fetch_rows(
    conn: sqlite3.Connection,
    table: str,
    col_map: dict[str, ColInfo],
    pk_keys: list[str],   # lowercase keys; empty when using rowid
    data_keys: list[str], # lowercase keys for columns to compare
    use_rowid: bool,
) -> dict[tuple, dict[str, object]]:
    """
    Fetch all rows from `table`, returning a dict keyed by PK tuple.
    Values are dicts of {lowercase_col_key: value} for data_keys columns.
    """
    if use_rowid:
        if data_keys:
            cols_sql = 'rowid, ' + ', '.join(f'"{_q(col_map[k].name)}"' for k in data_keys)
        else:
            cols_sql = 'rowid'
        label_keys = ['__rowid__'] + data_keys
    else:
        all_keys = list(dict.fromkeys(pk_keys + data_keys))
        cols_sql = ', '.join(f'"{_q(col_map[k].name)}"' for k in all_keys)
        label_keys = all_keys

    rows_raw = conn.execute(f'SELECT {cols_sql} FROM "{_q(table)}"').fetchall()

    result: dict[tuple, dict[str, object]] = {}
    for raw in rows_raw:
        rd = dict(zip(label_keys, raw))
        pk_tuple = (rd['__rowid__'],) if use_rowid else tuple(rd[k] for k in pk_keys)
        result[pk_tuple] = {k: rd[k] for k in data_keys}
    return result


def diff_table(
    conn_a: sqlite3.Connection,
    conn_b: sqlite3.Connection,
    name_a: str,
    name_b: str,
    schema_a: TableSchema,
    schema_b: TableSchema,
    match_kind: str | None,
) -> TableDiff:
    map_a = schema_a.col_by_lower
    map_b = schema_b.col_by_lower
    keys_a = set(map_a)
    keys_b = set(map_b)

    # Schema comparison
    only_col_a = [map_a[k].name for k in sorted(keys_a - keys_b)]
    only_col_b = [map_b[k].name for k in sorted(keys_b - keys_a)]
    type_changes = [
        (map_a[k].name, map_a[k].type_.upper(), map_b[k].type_.upper())
        for k in sorted(keys_a & keys_b)
        if map_a[k].type_.upper() != map_b[k].type_.upper()
    ]
    schema_diff = SchemaDiff(only_col_a, only_col_b, type_changes)

    # PK resolution: use A's PK columns if all exist in B; else fall back to rowid
    pk_lower = [n.lower() for n in schema_a.pk_names]
    use_rowid = not pk_lower or not all(k in map_b for k in pk_lower)
    pk_keys = [] if use_rowid else pk_lower

    # Row counts
    count_a: int = conn_a.execute(f'SELECT COUNT(*) FROM "{_q(name_a)}"').fetchone()[0]
    count_b: int = conn_b.execute(f'SELECT COUNT(*) FROM "{_q(name_b)}"').fetchone()[0]

    display_pk_cols = ['rowid'] if use_rowid else [map_a[k].name for k in pk_keys]

    if max(count_a, count_b) > LARGE_THRESHOLD:
        return TableDiff(
            name_a=name_a, name_b=name_b, match_kind=match_kind,
            pk_cols=display_pk_cols, count_a=count_a, count_b=count_b,
            schema=schema_diff, only_in_a=[], only_in_b=[], differing=[],
            too_large=True,
        )

    # Common data columns: intersection excluding PK columns (already used as key)
    pk_key_set = set(pk_keys)
    common_keys = sorted((keys_a & keys_b) - pk_key_set)

    rows_a = _fetch_rows(conn_a, name_a, map_a, pk_keys, common_keys, use_rowid)
    rows_b = _fetch_rows(conn_b, name_b, map_b, pk_keys, common_keys, use_rowid)

    set_a = set(rows_a)
    set_b = set(rows_b)
    only_in_a = sorted(set_a - set_b)
    only_in_b = sorted(set_b - set_a)

    differing: list[tuple[tuple, dict[str, tuple]]] = []
    for pk in sorted(set_a & set_b):
        ra = rows_a[pk]
        rb = rows_b[pk]
        col_diffs = {
            map_a[k].name: (ra[k], rb[k])
            for k in common_keys
            if ra[k] != rb[k]
        }
        if col_diffs:
            differing.append((pk, col_diffs))

    return TableDiff(
        name_a=name_a, name_b=name_b, match_kind=match_kind,
        pk_cols=display_pk_cols, count_a=count_a, count_b=count_b,
        schema=schema_diff, only_in_a=only_in_a, only_in_b=only_in_b,
        differing=differing,
    )


# ── formatting ────────────────────────────────────────────────────────────────


def _pk_label(pk: tuple, pk_cols: list[str]) -> str:
    if len(pk_cols) == 1:
        return str(pk[0])
    return '(' + ', '.join(f'{c}={v}' for c, v in zip(pk_cols, pk)) + ')'


def _table_header(diff: TableDiff) -> str:
    if diff.match_kind == 'case':
        return f'[{diff.name_a} / {diff.name_b}]  (renamed: case only)'
    if diff.match_kind == 'norm':
        return f'[{diff.name_a} / {diff.name_b}]  (renamed: snake↔camel)'
    if diff.match_kind == 'fuzzy':
        return f'[{diff.name_a} / {diff.name_b}]  (fuzzy match — verify pairing manually)'
    return f'[{diff.name_a}]'


def _print_schema_diff(schema: SchemaDiff, indent: str = '  ') -> None:
    for col in schema.only_in_a:
        print(f'{indent}schema  -{col}  (column only in A)')
    for col in schema.only_in_b:
        print(f'{indent}schema  +{col}  (column only in B)')
    for col, ta, tb in schema.type_changes:
        print(f'{indent}schema  {col}: type {ta} → {tb}')


def _print_detail(diff: TableDiff, limit: int) -> None:
    pk_cols = diff.pk_cols

    if diff.only_in_a:
        shown = diff.only_in_a[:limit]
        print(f'  rows only in A  ({len(diff.only_in_a)}):')
        for pk in shown:
            print(f'    {_pk_label(pk, pk_cols)}')
        if len(diff.only_in_a) > limit:
            print(f'    … {len(diff.only_in_a) - limit} more  (increase with --limit)')

    if diff.only_in_b:
        shown = diff.only_in_b[:limit]
        print(f'  rows only in B  ({len(diff.only_in_b)}):')
        for pk in shown:
            print(f'    {_pk_label(pk, pk_cols)}')
        if len(diff.only_in_b) > limit:
            print(f'    … {len(diff.only_in_b) - limit} more')

    if diff.differing:
        shown = diff.differing[:limit]
        print(f'  changed rows  ({len(diff.differing)}):')
        for pk, col_diffs in shown:
            print(f'    {_pk_label(pk, pk_cols)}:')
            for col, (va, vb) in col_diffs.items():
                print(f'      {col}: {va!r} → {vb!r}')
        if len(diff.differing) > limit:
            print(f'    … {len(diff.differing) - limit} more')


def print_table_diff(diff: TableDiff, show_detail: bool, limit: int) -> None:
    header = _table_header(diff)

    if diff.too_large:
        print(header)
        print(f'  rows: {diff.count_a:,} (A) / {diff.count_b:,} (B)  —  skipped row diff (>{LARGE_THRESHOLD:,})')
        _print_schema_diff(diff.schema)
        return

    if not diff.has_diff:
        print(f'{header}  ✓  ({diff.count_a:,} rows)')
        return

    delta_parts: list[str] = []
    if diff.only_in_a:
        delta_parts.append(f'-{len(diff.only_in_a)} A-only')
    if diff.only_in_b:
        delta_parts.append(f'+{len(diff.only_in_b)} B-only')
    if diff.differing:
        delta_parts.append(f'~{len(diff.differing)} changed')

    count_note = ''
    if diff.count_a != diff.count_b:
        count_note = f'  ({diff.count_a:,} → {diff.count_b:,} rows)'
    elif diff.count_a:
        count_note = f'  ({diff.count_a:,} rows)'

    print(f'{header}{count_note}')
    if delta_parts:
        print(f'  content:  {", ".join(delta_parts)}')
    _print_schema_diff(diff.schema)

    if show_detail:
        _print_detail(diff, limit)


# ── JSON serialisation ────────────────────────────────────────────────────────


def _pk_dict(pk: tuple, pk_cols: list[str]) -> dict:
    return dict(zip(pk_cols, pk))


def table_diff_to_dict(diff: TableDiff) -> dict:
    d: dict = {
        'name_a': diff.name_a,
        'name_b': diff.name_b,
        'match_kind': diff.match_kind or 'exact',
        'pk_cols': diff.pk_cols,
        'count_a': diff.count_a,
        'count_b': diff.count_b,
        'schema_diff': {
            'cols_only_in_a': diff.schema.only_in_a,
            'cols_only_in_b': diff.schema.only_in_b,
            'type_changes': [
                {'col': col, 'type_a': ta, 'type_b': tb}
                for col, ta, tb in diff.schema.type_changes
            ],
        },
    }
    if diff.too_large:
        d['content_diff'] = {'too_large': True}
    else:
        d['content_diff'] = {
            'too_large': False,
            'only_in_a': [_pk_dict(pk, diff.pk_cols) for pk in diff.only_in_a],
            'only_in_b': [_pk_dict(pk, diff.pk_cols) for pk in diff.only_in_b],
            'differing': [
                {
                    'pk': _pk_dict(pk, diff.pk_cols),
                    'changes': {col: {'a': va, 'b': vb} for col, (va, vb) in col_diffs.items()},
                }
                for pk, col_diffs in diff.differing
            ],
        }
    return d


# ── entry point ───────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Row-level diff between two SQLite databases.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            'examples:\n'
            '  %(prog)s a.db b.db                        summary of all tables\n'
            '  %(prog)s a.db b.db --table demand          full detail for one table\n'
            '  %(prog)s a.db b.db --verbose               full detail for every table\n'
            '  %(prog)s a.db b.db --limit 100             cap rows shown per table\n'
            '  %(prog)s a.db b.db --all                   include identical tables\n'
            '  %(prog)s a.db b.db --format json           machine-readable output\n'
            '  %(prog)s a.db b.db --format json --all     JSON including identical tables\n'
        ),
    )
    parser.add_argument('db_a', type=Path, metavar='A.db', help='First database (A)')
    parser.add_argument('db_b', type=Path, metavar='B.db', help='Second database (B)')
    parser.add_argument('--table', '-t', metavar='NAME',
                        help='Restrict output to this table (case-insensitive)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show full row detail for every table (text format only)')
    parser.add_argument('--limit', '-l', type=int, default=DEFAULT_LIMIT,
                        help=f'Max rows shown per section in detail mode (text only, default {DEFAULT_LIMIT})')
    parser.add_argument('--all', '-a', dest='show_all', action='store_true',
                        help='Include identical tables in output')
    parser.add_argument('--format', '-f', choices=['text', 'json'], default='text',
                        help='Output format (default: text)')
    args = parser.parse_args()

    conn_a = sqlite3.connect(str(args.db_a))
    conn_b = sqlite3.connect(str(args.db_b))

    try:
        schema_a = read_schema(conn_a)
        schema_b = read_schema(conn_b)

        pairs, only_a, only_b = match_tables(schema_a, schema_b)

        # Restrict to a single table when --table is given
        if args.table:
            target = args.table.lower()
            pairs = [
                p for p in pairs
                if p[0].lower() == target or p[1].lower() == target
            ]
            if not pairs:
                # Also check only_a / only_b
                all_candidates = only_a + only_b
                matches = [n for n in all_candidates if n.lower() == target]
                if matches:
                    side = 'A' if matches[0] in only_a else 'B'
                    print(f'Table {matches[0]!r} exists only in {side} — no counterpart to diff against.')
                else:
                    print(f'Table {args.table!r} not found in either database.')
                return

        # Compute diffs for all matched pairs
        diffs: list[TableDiff] = []
        for name_a, name_b, kind in pairs:
            diff = diff_table(
                conn_a, conn_b,
                name_a, name_b,
                schema_a[name_a], schema_b[name_b],
                kind,
            )
            diffs.append(diff)

        visible_only_a = only_a if not args.table else []
        visible_only_b = only_b if not args.table else []

        if args.format == 'json':
            tables_out = [
                table_diff_to_dict(d)
                for d in diffs
                if d.has_diff or args.show_all
            ]
            print(json.dumps({
                'db_a': str(args.db_a),
                'db_b': str(args.db_b),
                'tables_only_in_a': visible_only_a,
                'tables_only_in_b': visible_only_b,
                'tables': tables_out,
            }, indent=2))
            return

        # ── text output ──────────────────────────────────────────────────────
        print(f'A: {args.db_a}  ({len(schema_a)} tables)')
        print(f'B: {args.db_b}  ({len(schema_b)} tables)')
        print()

        if visible_only_a:
            print(f'Tables only in A ({len(visible_only_a)}): {", ".join(visible_only_a)}')
        if visible_only_b:
            print(f'Tables only in B ({len(visible_only_b)}): {", ".join(visible_only_b)}')
        if visible_only_a or visible_only_b:
            print()

        any_diff = bool(visible_only_a) or bool(visible_only_b)

        for diff in diffs:
            if not diff.has_diff and not args.show_all and not args.table:
                continue
            any_diff = True
            show_detail = (
                args.verbose
                or bool(args.table)
                or diff.total_delta <= AUTO_DETAIL_MAX
            )
            print_table_diff(diff, show_detail=show_detail, limit=args.limit)
            print()

        if not any_diff:
            print('No differences found.')

    finally:
        conn_a.close()
        conn_b.close()


if __name__ == '__main__':
    main()
