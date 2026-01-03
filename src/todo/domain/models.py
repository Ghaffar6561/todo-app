"""Domain models and validation."""

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Literal

from .errors import ValidationError


Status = Literal["open", "done"]
Priority = Literal["low", "med", "high"]


@dataclass
class Task:
    """Represents a Todo task."""

    id: int
    title: str
    status: Status
    created_at: datetime
    due_date: date | None = None
    priority: Priority | None = None
    tags: list[str] = field(default_factory=list)


def validate_title(title: str) -> str:
    """Validate and normalize title. Raises ValidationError if invalid."""
    stripped = title.strip()
    if not stripped:
        raise ValidationError("Title cannot be empty")
    return stripped


def parse_due_date(due_str: str | None) -> date | None:
    """Parse due date from YYYY-MM-DD string. Raises ValidationError if invalid."""
    if due_str is None:
        return None
    try:
        return date.fromisoformat(due_str)
    except ValueError:
        raise ValidationError(f"Invalid date format: {due_str}. Expected YYYY-MM-DD")


def validate_priority(priority_str: str | None) -> Priority | None:
    """Validate priority value. Raises ValidationError if invalid."""
    if priority_str is None:
        return None
    valid = ("low", "med", "high")
    if priority_str not in valid:
        raise ValidationError(
            f"Invalid priority: {priority_str}. Must be one of: {', '.join(valid)}"
        )
    return priority_str  # type: ignore[return-value]


def parse_tags(tags_str: str | None) -> list[str]:
    """Parse comma-separated tags into a normalized list."""
    if tags_str is None:
        return []
    tags = [t.strip() for t in tags_str.split(",")]
    return [t for t in tags if t]


def utc_now() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)
