from __future__ import annotations

from enum import Enum
from typing import Any, ClassVar, Sequence

from pydantic import BaseModel, ConfigDict


class CanoeBaseModel(BaseModel):
    """Common base model for all CANOE schema rows."""

    model_config = ConfigDict(extra="forbid")

    # Keep both names to support common SQLAlchemy-style naming and generated naming.
    __tablename__: ClassVar[str]
    __table_name__: ClassVar[str]

    @classmethod
    def table_name(cls) -> str:
        """Resolve SQL table name from model metadata."""
        table_name = getattr(cls, "__tablename__", None) or getattr(
            cls, "__table_name__", None
        )
        if not table_name:
            raise ValueError(f"{cls.__name__} is missing __tablename__ or __table_name__")
        return table_name

    @staticmethod
    def _quote_identifier(identifier: str) -> str:
        escaped = identifier.replace('"', '""')
        return f'"{escaped}"'

    @staticmethod
    def _coerce_sql_value(value: Any) -> Any:
        if isinstance(value, Enum):
            return value.value
        return value

    @classmethod
    def _sql_literal(cls, value: Any) -> str:
        if value is None:
            return "NULL"
        if isinstance(value, Enum):
            value = value.value
        if isinstance(value, bool):
            return "1" if value else "0"
        if isinstance(value, (int, float)):
            return str(value)
        escaped = str(value).replace("'", "''")
        return f"'{escaped}'"

    def _dump_for_sql(self, *, include_nulls: bool, include_defaults: bool) -> dict[str, Any]:
        payload = self.model_dump(
            mode="python",
            by_alias=True,
            exclude_none=not include_nulls,
            exclude_defaults=not include_defaults,
        )
        if not payload:
            raise ValueError("No fields available to build SQL statement")
        return payload

    def to_insert_sql(
        self,
        *,
        include_nulls: bool = False,
        include_defaults: bool = True,
        parameterized: bool = True,
    ) -> str | tuple[str, tuple[Any, ...]]:
        """Build an INSERT statement for this row.

        If parameterized=True, returns (sql, params).
        If parameterized=False, returns SQL with inlined literals.
        """
        payload = self._dump_for_sql(
            include_nulls=include_nulls,
            include_defaults=include_defaults,
        )
        columns = list(payload.keys())
        col_sql = ", ".join(self._quote_identifier(col) for col in columns)
        table_sql = self._quote_identifier(self.table_name())

        if parameterized:
            placeholders = ", ".join("?" for _ in columns)
            sql = f"INSERT INTO {table_sql} ({col_sql}) VALUES ({placeholders});"
            params = tuple(self._coerce_sql_value(payload[col]) for col in columns)
            return sql, params

        value_sql = ", ".join(self._sql_literal(payload[col]) for col in columns)
        return f"INSERT INTO {table_sql} ({col_sql}) VALUES ({value_sql});"

    @classmethod
    def to_bulk_insert_sql(
        cls,
        rows: Sequence[CanoeBaseModel],
        *,
        include_nulls: bool = False,
        include_defaults: bool = True,
        parameterized: bool = True,
    ) -> tuple[str, list[tuple[Any, ...]]] | list[str]:
        """Build INSERT SQL for many rows of the same table/model.

        Parameterized mode returns: (single_sql_template, list_of_params).
        Literal mode returns: list_of_sql_statements.
        """
        if not rows:
            raise ValueError("rows cannot be empty")

        first = rows[0]
        if any(not isinstance(r, cls) for r in rows):
            raise TypeError(f"All rows must be instances of {cls.__name__}")

        first_payload = first._dump_for_sql(
            include_nulls=include_nulls,
            include_defaults=include_defaults,
        )
        columns = list(first_payload.keys())

        payloads: list[dict[str, Any]] = [first_payload]
        for row in rows[1:]:
            payload = row._dump_for_sql(
                include_nulls=include_nulls,
                include_defaults=include_defaults,
            )
            if list(payload.keys()) != columns:
                raise ValueError(
                    "Rows produced different SQL columns. "
                    "Use include_nulls/include_defaults consistently so all rows align."
                )
            payloads.append(payload)

        col_sql = ", ".join(cls._quote_identifier(col) for col in columns)
        table_sql = cls._quote_identifier(cls.table_name())

        if parameterized:
            placeholders = ", ".join("?" for _ in columns)
            sql = f"INSERT INTO {table_sql} ({col_sql}) VALUES ({placeholders});"
            params = [
                tuple(cls._coerce_sql_value(payload[col]) for col in columns)
                for payload in payloads
            ]
            return sql, params

        statements = []
        for payload in payloads:
            value_sql = ", ".join(cls._sql_literal(payload[col]) for col in columns)
            statements.append(f"INSERT INTO {table_sql} ({col_sql}) VALUES ({value_sql});")
        return statements

    def to_upsert_sql(
        self,
        *,
        conflict_columns: Sequence[str],
        update_columns: Sequence[str] | None = None,
        include_nulls: bool = False,
        include_defaults: bool = True,
        parameterized: bool = True,
    ) -> str | tuple[str, tuple[Any, ...]]:
        """Build SQLite INSERT ... ON CONFLICT SQL for this row."""
        payload = self._dump_for_sql(
            include_nulls=include_nulls,
            include_defaults=include_defaults,
        )
        columns = list(payload.keys())

        unknown_conflicts = [c for c in conflict_columns if c not in payload]
        if unknown_conflicts:
            raise ValueError(f"conflict_columns not present in payload: {unknown_conflicts}")

        if update_columns is None:
            update_columns = [c for c in columns if c not in conflict_columns]

        unknown_updates = [c for c in update_columns if c not in payload]
        if unknown_updates:
            raise ValueError(f"update_columns not present in payload: {unknown_updates}")

        table_sql = self._quote_identifier(self.table_name())
        col_sql = ", ".join(self._quote_identifier(col) for col in columns)
        conflict_sql = ", ".join(self._quote_identifier(col) for col in conflict_columns)

        if update_columns:
            update_sql = ", ".join(
                f"{self._quote_identifier(col)} = excluded.{self._quote_identifier(col)}"
                for col in update_columns
            )
            conflict_action = f"DO UPDATE SET {update_sql}"
        else:
            conflict_action = "DO NOTHING"

        if parameterized:
            placeholders = ", ".join("?" for _ in columns)
            sql = (
                f"INSERT INTO {table_sql} ({col_sql}) VALUES ({placeholders}) "
                f"ON CONFLICT ({conflict_sql}) {conflict_action};"
            )
            params = tuple(self._coerce_sql_value(payload[col]) for col in columns)
            return sql, params

        value_sql = ", ".join(self._sql_literal(payload[col]) for col in columns)
        return (
            f"INSERT INTO {table_sql} ({col_sql}) VALUES ({value_sql}) "
            f"ON CONFLICT ({conflict_sql}) {conflict_action};"
        )

    @staticmethod
    def bulk_replace_into_sql(
        rows: Sequence[CanoeBaseModel],
        *,
        include_nulls: bool = False,
        include_defaults: bool = True,
    ) -> tuple[str, list[tuple[Any, ...]]]:
        """Build a REPLACE INTO ... SQL and parameter tuples for a batch of rows."""
        if not rows:
            raise ValueError("rows must not be empty")

        row_type = type(rows[0])
        if not all(type(row) is row_type for row in rows):
            raise TypeError(
                f"All rows must be the same type, got: "
                f"{', '.join(sorted({type(r).__name__ for r in rows}))}"
            )

        # Use the first row to build the SQL template
        first = rows[0]
        payload = first._dump_for_sql(
            include_nulls=include_nulls,
            include_defaults=include_defaults,
        )
        columns = list(payload.keys())
        table_sql = first._quote_identifier(first.table_name())
        col_sql = ", ".join(first._quote_identifier(col) for col in columns)
        placeholders = ", ".join("?" for _ in columns)

        sql = f"REPLACE INTO {table_sql} ({col_sql}) VALUES ({placeholders});"

        params = []
        for row in rows:
            row_payload = row._dump_for_sql(
                include_nulls=include_nulls,
                include_defaults=include_defaults,
            )
            params.append(tuple(row._coerce_sql_value(row_payload[col]) for col in columns))

        return sql, params
    
    def to_insert_or_ignore_sql(
        self,
        *,
        include_nulls: bool = False,
        include_defaults: bool = True,
        parameterized: bool = True,
    ) -> str | tuple[str, tuple[Any, ...]]:
        """Build a INSERT OR IGNORE ... SQL for this row."""
        payload = self._dump_for_sql(
            include_nulls=include_nulls,
            include_defaults=include_defaults,
        )
        columns = list(payload.keys())
        table_sql = self._quote_identifier(self.table_name())
        col_sql = ", ".join(self._quote_identifier(col) for col in columns)

        if parameterized:
            placeholders = ", ".join("?" for _ in columns)
            sql = f"INSERT OR IGNORE INTO {table_sql} ({col_sql}) VALUES ({placeholders});"
            params = tuple(self._coerce_sql_value(payload[col]) for col in columns)
            return sql, params

        value_sql = ", ".join(self._sql_literal(payload[col]) for col in columns)
        return f"INSERT OR IGNORE INTO {table_sql} ({col_sql}) VALUES ({value_sql});"


    @staticmethod
    def bulk_insert_or_ignore_sql(
        rows: Sequence[CanoeBaseModel],
        *,
        include_nulls: bool = False,
        include_defaults: bool = True,
    ) -> tuple[str, list[tuple[Any, ...]]]:
        """Build an INSERT OR IGNORE ... SQL and parameter tuples for a batch of rows."""
        if not rows:
            raise ValueError("rows must not be empty")

        row_type = type(rows[0])
        if not all(type(row) is row_type for row in rows):
            raise TypeError(
                f"All rows must be the same type, got: "
                f"{', '.join(sorted({type(r).__name__ for r in rows}))}"
            )

        first = rows[0]
        payload = first._dump_for_sql(
            include_nulls=include_nulls,
            include_defaults=include_defaults,
        )
        columns = list(payload.keys())
        table_sql = first._quote_identifier(first.table_name())
        col_sql = ", ".join(first._quote_identifier(col) for col in columns)
        placeholders = ", ".join("?" for _ in columns)

        sql = f"INSERT OR IGNORE INTO {table_sql} ({col_sql}) VALUES ({placeholders});"

        params = [
            tuple(row._coerce_sql_value(row._dump_for_sql(
                include_nulls=include_nulls,
                include_defaults=include_defaults,
            )[col]) for col in columns)
            for row in rows
        ]

        return sql, params
    
    def to_replace_sql(
        self,
        *,
        include_nulls: bool = False,
        include_defaults: bool = True,
        parameterized: bool = True,
    ) -> str | tuple[str, tuple[Any, ...]]:
        """Build a REPLACE INTO ... SQL for this row."""
        payload = self._dump_for_sql(
            include_nulls=include_nulls,
            include_defaults=include_defaults,
        )
        columns = list(payload.keys())
        table_sql = self._quote_identifier(self.table_name())
        col_sql = ", ".join(self._quote_identifier(col) for col in columns)

        if parameterized:
            placeholders = ", ".join("?" for _ in columns)
            sql = f"REPLACE INTO {table_sql} ({col_sql}) VALUES ({placeholders});"
            params = tuple(self._coerce_sql_value(payload[col]) for col in columns)
            return sql, params

        value_sql = ", ".join(self._sql_literal(payload[col]) for col in columns)
        return f"REPLACE INTO {table_sql} ({col_sql}) VALUES ({value_sql});"


    def to_delete_sql(
        self,
        *,
        parameterized: bool = True,
    ) -> str | tuple[str, tuple[Any, ...]]:
        """Build a DELETE ... SQL for this row, targeting by primary key."""
        pk_columns = self.__primary_key__
        payload = self._dump_for_sql(include_nulls=True, include_defaults=True)
        missing_pk = [c for c in pk_columns if c not in payload]
        if missing_pk:
            raise ValueError(f"Primary key columns not present in payload: {missing_pk}")

        table_sql = self._quote_identifier(self.table_name())
        where_sql = " AND ".join(
            f"{self._quote_identifier(col)} = ?" if parameterized
            else f"{self._quote_identifier(col)} = {self._sql_literal(payload[col])}"
            for col in pk_columns
        )

        if parameterized:
            params = tuple(self._coerce_sql_value(payload[col]) for col in pk_columns)
            return f"DELETE FROM {table_sql} WHERE {where_sql};", params

        return f"DELETE FROM {table_sql} WHERE {where_sql};"


    def to_update_sql(
        self,
        *,
        update_columns: Sequence[str] | None = None,
        include_nulls: bool = False,
        include_defaults: bool = True,
        parameterized: bool = True,
    ) -> str | tuple[str, tuple[Any, ...]]:
        """Build an UPDATE ... SQL for this row, targeting by primary key."""
        pk_columns = self.__primary_key__
        payload = self._dump_for_sql(
            include_nulls=include_nulls,
            include_defaults=include_defaults,
        )

        if update_columns is None:
            update_columns = [c for c in payload.keys() if c not in pk_columns]

        unknown_updates = [c for c in update_columns if c not in payload]
        if unknown_updates:
            raise ValueError(f"update_columns not present in payload: {unknown_updates}")

        missing_pk = [c for c in pk_columns if c not in payload]
        if missing_pk:
            raise ValueError(f"Primary key columns not present in payload: {missing_pk}")

        if not update_columns:
            raise ValueError("No columns to update after excluding primary key columns")

        table_sql = self._quote_identifier(self.table_name())
        where_sql = " AND ".join(
            f"{self._quote_identifier(col)} = ?"if parameterized
            else f"{self._quote_identifier(col)} = {self._sql_literal(payload[col])}"
            for col in pk_columns
        )

        if parameterized:
            set_sql = ", ".join(
                f"{self._quote_identifier(col)} = ?" for col in update_columns
            )
            sql = f"UPDATE {table_sql} SET {set_sql} WHERE {where_sql};"
            # SET params first, then WHERE params
            params = tuple(
                self._coerce_sql_value(payload[col]) for col in update_columns
            ) + tuple(
                self._coerce_sql_value(payload[col]) for col in pk_columns
            )
            return sql, params

        set_sql = ", ".join(
            f"{self._quote_identifier(col)} = {self._sql_literal(payload[col])}"
            for col in update_columns
        )
        return f"UPDATE {table_sql} SET {set_sql} WHERE {where_sql};"