"""Application services / use cases."""

from typing import Literal

from todo.domain.models import (
    Task,
    validate_title,
    parse_due_date,
    validate_priority,
    parse_tags,
    utc_now,
)
from todo.repository.memory_repo import MemoryTaskRepository, SortField


class TodoService:
    """Application service for todo operations."""

    def __init__(self, repo: MemoryTaskRepository | None = None) -> None:
        self._repo = repo or MemoryTaskRepository()

    def add_task(
        self,
        title: str,
        due: str | None = None,
        priority: str | None = None,
        tags: str | None = None,
    ) -> Task:
        """Add a new task. Validates inputs and raises ValidationError if invalid."""
        validated_title = validate_title(title)
        due_date = parse_due_date(due)
        validated_priority = validate_priority(priority)
        parsed_tags = parse_tags(tags)

        return self._repo.add(
            title=validated_title,
            created_at=utc_now(),
            due_date=due_date,
            priority=validated_priority,
            tags=parsed_tags,
        )

    def get_task(self, task_id: int) -> Task:
        """Get a single task by ID. Raises TaskNotFoundError if not found."""
        return self._repo.get(task_id)

    def list_tasks(
        self,
        status: Literal["all", "open", "done"] = "all",
        tag: str | None = None,
        sort: SortField = "created",
    ) -> list[Task]:
        """List tasks with optional filtering and sorting."""
        return self._repo.list_all(status=status, tag=tag, sort=sort)

    def mark_done(self, task_id: int) -> Task:
        """Mark a task as done. Raises TaskNotFoundError if not found."""
        return self._repo.update(task_id, status="done")

    def reopen_task(self, task_id: int) -> Task:
        """Reopen a task (mark as open). Raises TaskNotFoundError if not found."""
        return self._repo.update(task_id, status="open")

    def update_task(
        self,
        task_id: int,
        title: str | None = None,
        due: str | None = ...,  # type: ignore[assignment]
        priority: str | None = ...,  # type: ignore[assignment]
        tags: str | None = ...,  # type: ignore[assignment]
    ) -> Task:
        """Update a task. Validates inputs. Raises ValidationError or TaskNotFoundError."""
        validated_title = validate_title(title) if title is not None else None
        due_date = parse_due_date(due) if due is not ... else ...
        validated_priority = validate_priority(priority) if priority is not ... else ...
        parsed_tags = parse_tags(tags) if tags is not ... else ...

        return self._repo.update(
            task_id,
            title=validated_title,
            due_date=due_date,  # type: ignore[arg-type]
            priority=validated_priority,  # type: ignore[arg-type]
            tags=parsed_tags,  # type: ignore[arg-type]
        )

    def delete_task(self, task_id: int) -> None:
        """Delete a task. Raises TaskNotFoundError if not found."""
        self._repo.delete(task_id)

    def clear_done(self) -> int:
        """Clear all completed tasks. Returns count of removed tasks."""
        return self._repo.clear_done()
