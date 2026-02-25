"""CSV serialization utilities for MCP tool responses."""

import csv
import io

from pydantic import BaseModel

PLAN_CSV_FIELDS = ["id", "planned_at", "description", "notes", "status", "activity_id"]
MEMORY_CSV_FIELDS = ["id", "created_at", "author", "content"]
MEMORY_SEARCH_CSV_FIELDS = ["id", "created_at", "author", "content", "distance"]


def models_to_csv(models: list[BaseModel], fields: list[str]) -> str:
    """Serialize a list of Pydantic models to CSV with RFC 4180 escaping.

    Returns empty string for empty lists. Otherwise returns header + data rows.
    """
    if not models:
        return ""

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(fields)

    for model in models:
        data = model.model_dump()
        row = []
        for field in fields:
            value = data.get(field)
            if value is None:
                row.append("")
            else:
                row.append(str(value))
        writer.writerow(row)

    return output.getvalue()
