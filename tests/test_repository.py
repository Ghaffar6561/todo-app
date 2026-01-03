"""Tests for the in-memory repository."""

import pytest
from datetime import date, datetime, timezone

from todo.repository.memory_repo import MemoryTaskRepository
from todo.domain.errors import TaskNotFoundError


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class TestMemoryTaskRepository:
    def test_add_returns_task_with_id(self):
        repo = MemoryTaskRepository()
        task = repo.add(title="Test task", created_at=utc_now())

        assert task.id == 1
        assert task.title == "Test task"
        assert task.status == "open"

    def test_add_increments_id(self):
        repo = MemoryTaskRepository()
        task1 = repo.add(title="Task 1", created_at=utc_now())
        task2 = repo.add(title="Task 2", created_at=utc_now())

        assert task1.id == 1
        assert task2.id == 2

    def test_add_with_all_fields(self):
        repo = MemoryTaskRepository()
        created = utc_now()
        due = date(2025, 12, 31)

        task = repo.add(
            title="Full task",
            created_at=created,
            due_date=due,
            priority="high",
            tags=["work", "urgent"],
        )

        assert task.title == "Full task"
        assert task.due_date == due
        assert task.priority == "high"
        assert task.tags == ["work", "urgent"]

    def test_get_existing_task(self):
        repo = MemoryTaskRepository()
        added = repo.add(title="Test", created_at=utc_now())
        fetched = repo.get(added.id)

        assert fetched.id == added.id
        assert fetched.title == added.title

    def test_get_nonexistent_raises(self):
        repo = MemoryTaskRepository()
        with pytest.raises(TaskNotFoundError) as exc_info:
            repo.get(999)
        assert exc_info.value.task_id == 999

    def test_update_title(self):
        repo = MemoryTaskRepository()
        task = repo.add(title="Original", created_at=utc_now())
        updated = repo.update(task.id, title="Updated")

        assert updated.title == "Updated"
        assert repo.get(task.id).title == "Updated"

    def test_update_status(self):
        repo = MemoryTaskRepository()
        task = repo.add(title="Test", created_at=utc_now())
        updated = repo.update(task.id, status="done")

        assert updated.status == "done"

    def test_update_nonexistent_raises(self):
        repo = MemoryTaskRepository()
        with pytest.raises(TaskNotFoundError):
            repo.update(999, title="New")

    def test_delete_removes_task(self):
        repo = MemoryTaskRepository()
        task = repo.add(title="To delete", created_at=utc_now())
        repo.delete(task.id)

        with pytest.raises(TaskNotFoundError):
            repo.get(task.id)

    def test_delete_nonexistent_raises(self):
        repo = MemoryTaskRepository()
        with pytest.raises(TaskNotFoundError):
            repo.delete(999)

    def test_delete_does_not_reuse_id(self):
        repo = MemoryTaskRepository()
        task1 = repo.add(title="Task 1", created_at=utc_now())
        repo.delete(task1.id)
        task2 = repo.add(title="Task 2", created_at=utc_now())

        assert task2.id == 2  # Not 1

    def test_clear_done_removes_completed_tasks(self):
        repo = MemoryTaskRepository()
        task1 = repo.add(title="Open task", created_at=utc_now())
        task2 = repo.add(title="Done task", created_at=utc_now())
        repo.update(task2.id, status="done")

        count = repo.clear_done()

        assert count == 1
        assert repo.get(task1.id).status == "open"
        with pytest.raises(TaskNotFoundError):
            repo.get(task2.id)

    def test_clear_done_returns_zero_when_none(self):
        repo = MemoryTaskRepository()
        repo.add(title="Open task", created_at=utc_now())

        count = repo.clear_done()
        assert count == 0


class TestListFiltering:
    def test_list_all_returns_all(self):
        repo = MemoryTaskRepository()
        repo.add(title="Task 1", created_at=utc_now())
        repo.add(title="Task 2", created_at=utc_now())

        tasks = repo.list_all()
        assert len(tasks) == 2

    def test_filter_by_status_open(self):
        repo = MemoryTaskRepository()
        repo.add(title="Open", created_at=utc_now())
        done = repo.add(title="Done", created_at=utc_now())
        repo.update(done.id, status="done")

        tasks = repo.list_all(status="open")
        assert len(tasks) == 1
        assert tasks[0].title == "Open"

    def test_filter_by_status_done(self):
        repo = MemoryTaskRepository()
        repo.add(title="Open", created_at=utc_now())
        done = repo.add(title="Done", created_at=utc_now())
        repo.update(done.id, status="done")

        tasks = repo.list_all(status="done")
        assert len(tasks) == 1
        assert tasks[0].title == "Done"

    def test_filter_by_tag(self):
        repo = MemoryTaskRepository()
        repo.add(title="Work task", created_at=utc_now(), tags=["work"])
        repo.add(title="Home task", created_at=utc_now(), tags=["home"])
        repo.add(title="Both", created_at=utc_now(), tags=["work", "home"])

        tasks = repo.list_all(tag="work")
        assert len(tasks) == 2
        titles = {t.title for t in tasks}
        assert titles == {"Work task", "Both"}

    def test_filter_by_tag_case_insensitive(self):
        repo = MemoryTaskRepository()
        repo.add(title="Work task", created_at=utc_now(), tags=["Work"])

        tasks = repo.list_all(tag="work")
        assert len(tasks) == 1


class TestListSorting:
    def test_sort_by_created(self):
        repo = MemoryTaskRepository()
        t1 = datetime(2025, 1, 1, tzinfo=timezone.utc)
        t2 = datetime(2025, 1, 2, tzinfo=timezone.utc)
        t3 = datetime(2025, 1, 3, tzinfo=timezone.utc)

        repo.add(title="Third", created_at=t3)
        repo.add(title="First", created_at=t1)
        repo.add(title="Second", created_at=t2)

        tasks = repo.list_all(sort="created")
        titles = [t.title for t in tasks]
        assert titles == ["First", "Second", "Third"]

    def test_sort_by_due(self):
        repo = MemoryTaskRepository()
        now = utc_now()

        repo.add(title="No due", created_at=now)
        repo.add(title="Later", created_at=now, due_date=date(2025, 12, 31))
        repo.add(title="Soon", created_at=now, due_date=date(2025, 1, 15))

        tasks = repo.list_all(sort="due")
        titles = [t.title for t in tasks]
        assert titles == ["Soon", "Later", "No due"]

    def test_sort_by_priority(self):
        repo = MemoryTaskRepository()
        now = utc_now()

        repo.add(title="Low", created_at=now, priority="low")
        repo.add(title="None", created_at=now)
        repo.add(title="High", created_at=now, priority="high")
        repo.add(title="Med", created_at=now, priority="med")

        tasks = repo.list_all(sort="priority")
        titles = [t.title for t in tasks]
        assert titles == ["High", "Med", "Low", "None"]

    def test_sort_deterministic_tiebreak(self):
        repo = MemoryTaskRepository()
        now = utc_now()

        repo.add(title="First", created_at=now, priority="high")
        repo.add(title="Second", created_at=now, priority="high")
        repo.add(title="Third", created_at=now, priority="high")

        tasks = repo.list_all(sort="priority")
        titles = [t.title for t in tasks]
        assert titles == ["First", "Second", "Third"]
