"""In-memory task repository."""

from datetime import date, datetime
from typing import Literal

from todo.domain.models import Task, Priority, Status
from todo.domain.errors import TaskNotFoundError


SortField = Literal["created", "due", "priority"]


class MemoryTaskRepository:
    """In-memory storage for tasks. Data is lost when the process exits."""

    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1

    def add(
        self,
        title: str,
        created_at: datetime,
        due_date: date | None = None,
        priority: Priority | None = None,
        tags: list[str] | None = None,
    ) -> Task:
        """Add a new task and return it."""
        task = Task(
            id=self._next_id,
            title=title,
            status="open",
            created_at=created_at,
            due_date=due_date,
            priority=priority,
            tags=tags or [],
        )
        self._tasks[self._next_id] = task
        self._next_id += 1
        return task

    def get(self, task_id: int) -> Task:
        """Get a task by ID. Raises TaskNotFoundError if not found."""
        if task_id not in self._tasks:
            raise TaskNotFoundError(task_id)
        return self._tasks[task_id]

    def update(
        self,
        task_id: int,
        title: str | None = None,
        status: Status | None = None,
        due_date: date | None = ...,  # type: ignore[assignment]
        priority: Priority | None = ...,  # type: ignore[assignment]
        tags: list[str] | None = ...,  # type: ignore[assignment]
    ) -> Task:
        """Update a task. Raises TaskNotFoundError if not found.

        Uses sentinel values (...) to distinguish between None and 'not provided'.
        """
        task = self.get(task_id)

        if title is not None:
            task.title = title
        if status is not None:
            task.status = status
        if due_date is not ...:
            task.due_date = due_date
        if priority is not ...:
            task.priority = priority
        if tags is not ...:
            task.tags = tags or []

        return task

    def delete(self, task_id: int) -> None:
        """Delete a task. Raises TaskNotFoundError if not found."""
        if task_id not in self._tasks:
            raise TaskNotFoundError(task_id)
        del self._tasks[task_id]

    def clear_done(self) -> int:
        """Remove all tasks with status 'done'. Returns count of removed tasks."""
        done_ids = [tid for tid, task in self._tasks.items() if task.status == "done"]
        for tid in done_ids:
            del self._tasks[tid]
        return len(done_ids)

    def list_all(
        self,
        status: Literal["all", "open", "done"] = "all",
        tag: str | None = None,
        sort: SortField = "created",
    ) -> list[Task]:
        """List tasks with optional filtering and sorting."""
        tasks = list(self._tasks.values())

        # Filter by status
        if status != "all":
            tasks = [t for t in tasks if t.status == status]

        # Filter by tag
        if tag is not None:
            tag_lower = tag.lower()
            tasks = [t for t in tasks if any(tg.lower() == tag_lower for tg in t.tags)]

        # Sort
        tasks = self._sort_tasks(tasks, sort)

        return tasks

    def _sort_tasks(self, tasks: list[Task], sort: SortField) -> list[Task]:
        """Sort tasks according to the specified field with deterministic tie-breaking."""
        if sort == "created":
            return sorted(tasks, key=lambda t: (t.created_at, t.id))

        if sort == "due":
            # Tasks with due_date first (sorted asc), then no-due tasks, tie-break by id
            def due_key(t: Task) -> tuple:
                if t.due_date is not None:
                    return (0, t.due_date, t.id)
                return (1, date.max, t.id)
            return sorted(tasks, key=due_key)

        if sort == "priority":
            # high > med > low, None last, tie-break by id
            priority_order = {"high": 0, "med": 1, "low": 2, None: 3}
            return sorted(tasks, key=lambda t: (priority_order[t.priority], t.id))

        return tasks
