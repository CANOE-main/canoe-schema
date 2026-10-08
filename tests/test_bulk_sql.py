from __future__ import annotations

import inspect
from enum import Enum, IntEnum
from typing import Any, ClassVar, Sequence

import pytest
from pydantic import Field

from canoe_schema import v3_1, v3_2, v4_0
from canoe_schema.base import CanoeBaseModel

FLAG_COMBOS = [
    {"include_nulls": n, "include_defaults": d}
    for n in (True, False)
    for d in (True, False)
]


# ---------------------------------------------------------------------------
# Reference copies of the pre-refactor implementations
# ---------------------------------------------------------------------------


def old_to_bulk_insert_sql(
    cls: type[CanoeBaseModel],
    rows: Sequence[CanoeBaseModel],
    *,
    include_nulls: bool = False,
    include_defaults: bool = True,
    parameterized: bool = True,
) -> Any:
    first = rows[0]
    first_payload = first._dump_for_sql(
        include_nulls=include_nulls, include_defaults=include_defaults
    )
    columns = list(first_payload.keys())
    payloads = [first_payload]
    for row in rows[1:]:
        payload = row._dump_for_sql(
            include_nulls=include_nulls, include_defaults=include_defaults
        )
        assert list(payload.keys()) == columns
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


def _old_bulk_verb(
    verb: str,
    rows: Sequence[CanoeBaseModel],
    *,
    include_nulls: bool = False,
    include_defaults: bool = True,
) -> tuple[str, list[tuple[Any, ...]]]:
    first = rows[0]
    payload = first._dump_for_sql(
        include_nulls=include_nulls, include_defaults=include_defaults
    )
    columns = list(payload.keys())
    table_sql = first._quote_identifier(first.table_name())
    col_sql = ", ".join(first._quote_identifier(col) for col in columns)
    placeholders = ", ".join("?" for _ in columns)
    sql = f"{verb} INTO {table_sql} ({col_sql}) VALUES ({placeholders});"
    params = []
    for row in rows:
        row_payload = row._dump_for_sql(
            include_nulls=include_nulls, include_defaults=include_defaults
        )
        params.append(tuple(row._coerce_sql_value(row_payload[col]) for col in columns))
    return sql, params


def old_bulk_insert_or_ignore_sql(rows: Sequence[CanoeBaseModel], **kw: Any) -> Any:
    return _old_bulk_verb("INSERT OR IGNORE", rows, **kw)


def old_bulk_replace_into_sql(rows: Sequence[CanoeBaseModel], **kw: Any) -> Any:
    return _old_bulk_verb("REPLACE", rows, **kw)


# ---------------------------------------------------------------------------
# Test models
# ---------------------------------------------------------------------------


class Color(str, Enum):
    RED = "r"
    BLUE = "b"


class Level(IntEnum):
    LOW = 1
    HIGH = 2


class Widget(CanoeBaseModel):
    __table_name__: ClassVar[str] = "widget"
    name: str
    color: Color = Color.RED
    level: Level | None = None
    size: float | None = Field(None, alias="Size")
    notes: str | None = None


class SpecialWidget(Widget):
    pass


def aligned_widgets() -> list[Widget]:
    # Same set of None / default fields in every row, so all flag combos align.
    return [
        Widget(name="a", color=Color.RED, level=Level.HIGH, Size=1.5),
        Widget(name="b'q", color=Color.RED, level=Level.LOW, Size=2.0),
        Widget(name="c", color=Color.RED, level=Level.HIGH, Size=-3),
    ]


def misaligned_widgets() -> list[list[Widget]]:
    return [
        # Later row has a value in a column the first row drops.
        [Widget(name="a"), Widget(name="b", notes="n")],
        # Later row drops a column the first row has.
        [Widget(name="a", notes="n"), Widget(name="b")],
        # Later row drops a default the first row overrides.
        [Widget(name="a", color=Color.BLUE), Widget(name="b")],
    ]


SCHEMA_MODULES = [v3_1, v3_2, v4_0]


def schema_models() -> list[type[CanoeBaseModel]]:
    models = []
    for module in SCHEMA_MODULES:
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, CanoeBaseModel) and obj is not CanoeBaseModel:
                models.append(obj)
    return models


# ---------------------------------------------------------------------------
# Equivalence with the old implementation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("flags", FLAG_COMBOS)
def test_bulk_insert_or_ignore_matches_old(flags: dict[str, bool]) -> None:
    rows = aligned_widgets()
    new = Widget.bulk_insert_or_ignore_sql(rows, **flags)
    assert new == old_bulk_insert_or_ignore_sql(rows, **flags)


@pytest.mark.parametrize("flags", FLAG_COMBOS)
def test_bulk_replace_into_matches_old(flags: dict[str, bool]) -> None:
    rows = aligned_widgets()
    new = Widget.bulk_replace_into_sql(rows, **flags)
    assert new == old_bulk_replace_into_sql(rows, **flags)


@pytest.mark.parametrize("parameterized", [True, False])
@pytest.mark.parametrize("flags", FLAG_COMBOS)
def test_to_bulk_insert_matches_old(
    flags: dict[str, bool], parameterized: bool
) -> None:
    rows = aligned_widgets()
    new = Widget.to_bulk_insert_sql(rows, parameterized=parameterized, **flags)
    old = old_to_bulk_insert_sql(Widget, rows, parameterized=parameterized, **flags)
    assert new == old


def test_default_flags_match_old() -> None:
    rows = aligned_widgets()
    assert Widget.bulk_insert_or_ignore_sql(rows) == old_bulk_insert_or_ignore_sql(rows)
    assert Widget.bulk_replace_into_sql(rows) == old_bulk_replace_into_sql(rows)
    assert Widget.to_bulk_insert_sql(rows) == old_to_bulk_insert_sql(Widget, rows)


def test_to_bulk_insert_accepts_subclass_rows_with_cls_table() -> None:
    rows = [SpecialWidget(name="a"), Widget(name="b")]
    flags = {"include_nulls": True, "include_defaults": True}
    assert Widget.to_bulk_insert_sql(rows, **flags) == old_to_bulk_insert_sql(
        Widget, rows, **flags
    )


# model_construct rows hold wrongly-typed placeholders; pydantic warns on dump.
@pytest.mark.filterwarnings("ignore:Pydantic serializer warnings")
@pytest.mark.parametrize(
    "model", schema_models(), ids=lambda m: f"{m.__module__}.{m.__name__}"
)
def test_schema_models_match_old(model: type[CanoeBaseModel]) -> None:
    # Construct without validation: only field values matter for SQL generation.
    rows = [
        model.model_construct(**{name: f"{name}_{i}" for name in model.model_fields})
        for i in range(3)
    ]
    flags = {"include_nulls": True, "include_defaults": True}
    assert model.bulk_insert_or_ignore_sql(
        rows, **flags
    ) == old_bulk_insert_or_ignore_sql(rows, **flags)
    assert model.bulk_replace_into_sql(rows, **flags) == old_bulk_replace_into_sql(
        rows, **flags
    )
    assert model.to_bulk_insert_sql(rows, **flags) == old_to_bulk_insert_sql(
        model, rows, **flags
    )


# ---------------------------------------------------------------------------
# Specific behaviours
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("flags", FLAG_COMBOS)
def test_enum_values_are_coerced(flags: dict[str, bool]) -> None:
    rows = [Widget(name="a", color=Color.BLUE, level=Level.HIGH, Size=1.0)]
    for _, params in (
        Widget.bulk_insert_or_ignore_sql(rows, **flags),
        Widget.bulk_replace_into_sql(rows, **flags),
        Widget.to_bulk_insert_sql(rows, **flags),
    ):
        assert "b" in params[0]
        assert 2 in params[0]
        assert not any(isinstance(v, Enum) for v in params[0])


def test_aliased_field_uses_alias_as_column() -> None:
    rows = [Widget(name="a", Size=1.0)]
    for sql, params in (
        Widget.bulk_insert_or_ignore_sql(rows, include_nulls=True),
        Widget.bulk_replace_into_sql(rows, include_nulls=True),
        Widget.to_bulk_insert_sql(rows, include_nulls=True),
    ):
        assert '"Size"' in sql
        assert '"size"' not in sql
        assert sql.endswith(
            '"widget" ("name", "color", "level", "Size", "notes") '
            "VALUES (?, ?, ?, ?, ?);"
        )
        assert params == [("a", "r", None, 1.0, None)]


@pytest.mark.parametrize("rows", misaligned_widgets())
def test_misaligned_rows_raise_value_error(rows: list[Widget]) -> None:
    flags = {"include_nulls": False, "include_defaults": False}
    for build in (
        lambda: Widget.bulk_insert_or_ignore_sql(rows, **flags),
        lambda: Widget.bulk_replace_into_sql(rows, **flags),
        lambda: Widget.to_bulk_insert_sql(rows, **flags),
        lambda: Widget.to_bulk_insert_sql(rows, parameterized=False, **flags),
    ):
        with pytest.raises(ValueError, match="Rows produced different SQL columns"):
            build()


def test_empty_rows_raise_value_error() -> None:
    with pytest.raises(ValueError, match="rows must not be empty"):
        Widget.bulk_insert_or_ignore_sql([])
    with pytest.raises(ValueError, match="rows must not be empty"):
        Widget.bulk_replace_into_sql([])
    with pytest.raises(ValueError, match="rows cannot be empty"):
        Widget.to_bulk_insert_sql([])


def test_mixed_types_raise_type_error() -> None:
    rows = [Widget(name="a"), SpecialWidget(name="b")]
    with pytest.raises(TypeError, match="All rows must be the same type"):
        Widget.bulk_insert_or_ignore_sql(rows)
    with pytest.raises(TypeError, match="All rows must be the same type"):
        Widget.bulk_replace_into_sql(rows)
    with pytest.raises(TypeError, match="All rows must be instances of SpecialWidget"):
        SpecialWidget.to_bulk_insert_sql(rows)


# model_construct rows hold wrongly-typed placeholders; pydantic warns on dump.
@pytest.mark.filterwarnings("ignore:Pydantic serializer warnings")
@pytest.mark.parametrize(
    "model", schema_models(), ids=lambda m: f"{m.__module__}.{m.__name__}"
)
def test_fast_path_columns_match_dump_keys(model: type[CanoeBaseModel]) -> None:
    fields = model._sql_fields()
    assert fields is not None, f"{model.__name__} unexpectedly needs the dump path"
    row = model.model_construct(**{name: None for name in model.model_fields})
    dump_keys = list(row._dump_for_sql(include_nulls=True, include_defaults=True))
    assert [column for _, column in fields] == dump_keys


def test_schema_modules_have_models() -> None:
    for module in SCHEMA_MODULES:
        assert any(m.__module__.startswith(module.__name__) for m in schema_models())
