"""Tests for CSV serialization utilities."""

import csv
import io
from datetime import datetime, timezone

from coach_memory.csv_utils import (
    MEMORY_CSV_FIELDS,
    MEMORY_SEARCH_CSV_FIELDS,
    PLAN_CSV_FIELDS,
    models_to_csv,
)
from coach_memory.models import Memory, MemorySearchResult, Plan


def _parse_csv(csv_output: str) -> list[list[str]]:
    """Parse CSV string into list of rows."""
    return list(csv.reader(io.StringIO(csv_output)))


def _make_plan(**overrides) -> Plan:
    defaults = dict(
        id=1,
        created_at=datetime(2026, 2, 6, 19, 0, 0, tzinfo=timezone.utc),
        planned_at="2026-02-17",
        description="Rodaje 8km",
        status="pending",
        notes=None,
        activity_id=None,
    )
    defaults.update(overrides)
    return Plan(**defaults)


def _make_memory(**overrides) -> Memory:
    defaults = dict(
        id=1,
        created_at=datetime(2026, 2, 6, 19, 0, 0, tzinfo=timezone.utc),
        author="agent",
        content="Test memory",
    )
    defaults.update(overrides)
    return Memory(**defaults)


class TestEmptyList:
    def test_empty_list_returns_empty_string(self):
        assert models_to_csv([], PLAN_CSV_FIELDS) == ""


class TestNoneValues:
    def test_none_values_become_empty_fields(self):
        plan = _make_plan(notes=None, activity_id=None)
        rows = _parse_csv(models_to_csv([plan], PLAN_CSV_FIELDS))
        assert rows[0] == PLAN_CSV_FIELDS
        assert len(rows[1]) == 6
        # notes and activity_id should be empty
        assert rows[1][3] == ""  # notes
        assert rows[1][5] == ""  # activity_id


class TestSpecialCharacterEscaping:
    def test_commas_in_fields_are_properly_escaped(self):
        plan = _make_plan(description="10km easy, then 4x100m strides")
        rows = _parse_csv(models_to_csv([plan], PLAN_CSV_FIELDS))
        assert rows[1][2] == "10km easy, then 4x100m strides"

    def test_double_quotes_in_fields_are_properly_escaped(self):
        plan = _make_plan(description='Series "rápidas" de 400m')
        rows = _parse_csv(models_to_csv([plan], PLAN_CSV_FIELDS))
        assert rows[1][2] == 'Series "rápidas" de 400m'

    def test_newlines_in_fields_are_properly_escaped(self):
        memory = _make_memory(content="Línea 1\nLínea 2")
        rows = _parse_csv(models_to_csv([memory], MEMORY_CSV_FIELDS))
        assert rows[1][3] == "Línea 1\nLínea 2"

    def test_semicolons_in_fields_not_treated_as_delimiter(self):
        memory = _make_memory(content="Ritmo: 5:00; FC: 150")
        rows = _parse_csv(models_to_csv([memory], MEMORY_CSV_FIELDS))
        assert rows[1][3] == "Ritmo: 5:00; FC: 150"

    def test_mixed_special_characters(self):
        content = 'Comas, comillas "dobles", newline\ny punto;coma'
        memory = _make_memory(content=content)
        rows = _parse_csv(models_to_csv([memory], MEMORY_CSV_FIELDS))
        assert rows[1][3] == content


class TestRoundtripIntegrity:
    def test_roundtrip_integrity(self):
        models = [
            _make_plan(id=1, description="Easy, relaxed run", notes='Said "great"'),
            _make_plan(id=2, description="Intervals\n4x1000m", notes="Phase 2; build"),
            _make_plan(id=3, description='Mix: commas, "quotes"\nand lines', notes=None),
        ]
        csv_output = models_to_csv(models, PLAN_CSV_FIELDS)
        rows = _parse_csv(csv_output)

        assert len(rows) == 4  # header + 3 data rows
        assert rows[1][2] == "Easy, relaxed run"
        assert rows[1][3] == 'Said "great"'
        assert rows[2][2] == "Intervals\n4x1000m"
        assert rows[2][3] == "Phase 2; build"
        assert rows[3][2] == 'Mix: commas, "quotes"\nand lines'
        assert rows[3][3] == ""  # None


class TestFieldSelection:
    def test_created_at_excluded_from_plan_csv(self):
        assert "created_at" not in PLAN_CSV_FIELDS

    def test_header_matches_fields(self):
        plan = _make_plan()
        rows = _parse_csv(models_to_csv([plan], PLAN_CSV_FIELDS))
        assert rows[0] == PLAN_CSV_FIELDS

    def test_memory_search_fields_include_distance(self):
        result = MemorySearchResult(
            id=1,
            created_at=datetime(2026, 2, 6, 19, 0, 0, tzinfo=timezone.utc),
            author="agent",
            content="Test",
            distance=0.123,
        )
        rows = _parse_csv(models_to_csv([result], MEMORY_SEARCH_CSV_FIELDS))
        assert rows[0] == MEMORY_SEARCH_CSV_FIELDS
        assert rows[1][4] == "0.123"
