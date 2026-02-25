"""Tests for plan tools."""

import csv
import io
from datetime import date

from memory_mcp.csv_utils import PLAN_CSV_FIELDS
from memory_mcp.models import PlanUpdate
from memory_mcp.tools.plan import (
    add_plan,
    delete_plan,
    get_plan,
    get_today_plan,
    get_upcoming_plans,
    list_plans,
    update_plan,
)


def _parse_csv(csv_output: str) -> list[list[str]]:
    return list(csv.reader(io.StringIO(csv_output)))


def test_add_plan(db_connection):
    """Test adding a plan."""
    plan = add_plan(db_connection, "2025-01-30", "Rodaje 45' Z2")

    assert plan.id == 1
    assert plan.planned_at == "2025-01-30"
    assert plan.description == "Rodaje 45' Z2"
    assert plan.status == "pending"


def test_get_plan(db_connection):
    """Test getting a plan by ID."""
    created = add_plan(db_connection, "2025-01-30", "Rodaje 45' Z2")
    plan = get_plan(db_connection, created.id)

    assert plan is not None
    assert plan.id == created.id
    assert plan.description == "Rodaje 45' Z2"


def test_get_plan_not_found(db_connection):
    """Test getting a non-existent plan."""
    plan = get_plan(db_connection, 999)
    assert plan is None


def test_list_plans(db_connection):
    """Test listing plans returns CSV."""
    add_plan(db_connection, "2025-01-30", "Plan 1")
    add_plan(db_connection, "2025-01-31", "Plan 2")
    add_plan(db_connection, "2025-02-01", "Plan 3")

    csv_output = list_plans(db_connection)
    assert isinstance(csv_output, str)
    rows = _parse_csv(csv_output)
    assert rows[0] == PLAN_CSV_FIELDS
    assert len(rows) == 4  # header + 3 data rows

    # Test date filter
    csv_output = list_plans(db_connection, start_date="2025-01-31")
    rows = _parse_csv(csv_output)
    assert len(rows) == 3  # header + 2 data rows


def test_update_plan(db_connection):
    """Test updating a plan."""
    created = add_plan(db_connection, "2025-01-30", "Rodaje 45' Z2")

    updated = update_plan(
        db_connection,
        created.id,
        PlanUpdate(status="completed", activity_id="12345"),
    )

    assert updated is not None
    assert updated.status == "completed"
    assert updated.activity_id == "12345"


def test_delete_plan(db_connection):
    """Test deleting a plan."""
    created = add_plan(db_connection, "2025-01-30", "Rodaje 45' Z2")

    result = delete_plan(db_connection, created.id)
    assert result is True

    plan = get_plan(db_connection, created.id)
    assert plan is None


def test_get_today_plan(db_connection):
    """Test getting today's plans returns CSV."""
    today = date.today().isoformat()
    add_plan(db_connection, today, "Today's workout")
    add_plan(db_connection, "2030-01-01", "Future workout")

    csv_output = get_today_plan(db_connection)
    assert isinstance(csv_output, str)
    rows = _parse_csv(csv_output)
    assert rows[0] == PLAN_CSV_FIELDS
    assert len(rows) == 2  # header + 1 data row
    assert rows[1][2] == "Today's workout"


def test_get_upcoming_plans(db_connection):
    """Test getting upcoming plans returns CSV."""
    today = date.today().isoformat()
    add_plan(db_connection, today, "Today's workout")
    add_plan(db_connection, "2020-01-01", "Past workout")

    csv_output = get_upcoming_plans(db_connection, days=7)
    assert isinstance(csv_output, str)
    rows = _parse_csv(csv_output)
    assert rows[0] == PLAN_CSV_FIELDS
    assert len(rows) == 2  # header + 1 data row
    assert rows[1][2] == "Today's workout"
