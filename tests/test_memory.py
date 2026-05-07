"""Tests for memory tools."""

import csv
import io

from coach_memory.csv_utils import MEMORY_CSV_FIELDS, MEMORY_SEARCH_CSV_FIELDS
from coach_memory.tools.memory import (
    add_memory,
    delete_memory,
    get_memory,
    list_memories,
    search_memories,
)


def _parse_csv(csv_output: str) -> list[list[str]]:
    return list(csv.reader(io.StringIO(csv_output)))


def test_add_memory(db_connection, mock_settings, mock_embedding):
    """Test adding a memory."""
    memory = add_memory(
        db_connection,
        mock_settings,
        author="user",
        content="El atleta prefiere entrenar por las mañanas",
    )

    assert memory.id == 1
    assert memory.author == "user"
    assert "mañanas" in memory.content


def test_get_memory(db_connection, mock_settings, mock_embedding):
    """Test getting a memory by ID."""
    created = add_memory(
        db_connection,
        mock_settings,
        author="agent",
        content="Test memory",
    )
    memory = get_memory(db_connection, created.id)

    assert memory is not None
    assert memory.content == "Test memory"


def test_list_memories_by_author(db_connection, mock_settings, mock_embedding):
    """Test listing memories filtered by author returns CSV."""
    add_memory(db_connection, mock_settings, author="user", content="User memory")
    add_memory(db_connection, mock_settings, author="agent", content="Agent memory")
    add_memory(db_connection, mock_settings, author="system", content="System memory")

    csv_output = list_memories(db_connection, author="user")
    assert isinstance(csv_output, str)
    rows = _parse_csv(csv_output)
    assert rows[0] == MEMORY_CSV_FIELDS
    assert len(rows) == 2  # header + 1 data row
    assert rows[1][2] == "user"


def test_search_memories(db_connection, mock_settings, mock_embedding):
    """Test semantic search of memories returns CSV."""
    add_memory(
        db_connection,
        mock_settings,
        author="user",
        content="Le gusta correr temprano por la mañana",
    )
    add_memory(
        db_connection,
        mock_settings,
        author="agent",
        content="Prefiere series de velocidad los martes",
    )

    csv_output = search_memories(db_connection, mock_settings, query="horario de entrenamiento", limit=5)
    assert isinstance(csv_output, str)
    rows = _parse_csv(csv_output)
    assert rows[0] == MEMORY_SEARCH_CSV_FIELDS
    assert len(rows) >= 2  # header + at least 1 result


def test_delete_memory(db_connection, mock_settings, mock_embedding):
    """Test deleting a memory."""
    created = add_memory(
        db_connection,
        mock_settings,
        author="user",
        content="To be deleted",
    )

    result = delete_memory(db_connection, created.id)
    assert result is True

    memory = get_memory(db_connection, created.id)
    assert memory is None
