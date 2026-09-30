"""Reusable field types shared by the Teamcenter schemas and tools."""

from typing import Annotated, Any

from pydantic import Field, StringConstraints

# Non-empty string with surrounding whitespace removed.
NonBlankStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]

# Teamcenter date/time format, e.g. "23-Aug-2026 13:10".
TC_DATETIME_PATTERN = r"^\d{2}-[A-Za-z]{3}-\d{4}\s\d{2}:\d{2}$"
TC_DATETIME_HINT = "Format: DD-MMM-YYYY HH:mm (e.g. 23-Aug-2026 13:10)."


def tc_datetime_field(tc_name: str, description: str) -> Any:
    """Optional Teamcenter date/time filter mapped to the saved-query field ``tc_name``.

    The format hint is always appended to the description so the MCP client
    knows the expected input format.
    """
    return Field(
        default=None,
        pattern=TC_DATETIME_PATTERN,
        serialization_alias=tc_name,
        description=f"{description} {TC_DATETIME_HINT}",
    )
