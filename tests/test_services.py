"""Tests for the application service layer."""

import pytest

from todo.application.services import TodoService
from todo.domain.errors import ValidationError, TaskNotFoundError


class TestAddTask:
    def test_add_simple_task(self):
        service = TodoService()
        task = service.add_task(title="Test task")

        assert task.id == 1
        assert task.title == "Test task"
        assert task.status == "open"

    def test_add_task_with_all_options(self):
        service = TodoService()
        task = service.add_task(
            title="Full task",
            due="2025-12-31",
            priority="high",
            tags="work,urgent",
        )

        assert task.due_date.isoformat() == "2025-12-31"
        assert task.priority == "high"
        assert task.tags == ["work", "urgent"]

    def test_add_empty_title_raises(self):
        service = TodoService()
        with pytest.raises(ValidationError):
            service.add_task(title="")

    def test_add_invalid_date_raises(self):
        service = TodoService()
        with pytest.raises(ValidationError):
            service.add_task(title="Test", due="invalid")

    def test_add_invalid_priority_raises(self):
        service = TodoService()
        with pytest.raises(ValidationError):
            service.add_task(title="Test", priority="urgent")


class TestListTasks:
    def test_list_empty(self):
        service = TodoService()
        tasks = service.list_tasks()
        assert tasks == []

    def test_list_returns_added_tasks(self):
        service = TodoService()
        service.add_task(title="Task 1")
        service.add_task(title="Task 2")

        tasks = service.list_tasks()
        assert len(tasks) == 2

    def test_list_filter_by_status(self):
        service = TodoService()
        service.add_task(title="Open task")
        task2 = service.add_task(title="Done task")
        service.mark_done(task2.id)

        open_tasks = service.list_tasks(status="open")
        assert len(open_tasks) == 1
        assert open_tasks[0].title == "Open task"

    def test_list_filter_by_tag(self):
        service = TodoService()
        service.add_task(title="Work task", tags="work")
        service.add_task(title="Home task", tags="home")

        work_tasks = service.list_tasks(tag="work")
        assert len(work_tasks) == 1
        assert work_tasks[0].title == "Work task"


class TestMarkDone:
    def test_mark_done(self):
        service = TodoService()
        task = service.add_task(title="Test")
        updated = service.mark_done(task.id)

        assert updated.status == "done"

    def test_mark_done_nonexistent_raises(self):
        service = TodoService()
        with pytest.raises(TaskNotFoundError):
            service.mark_done(999)


class TestReopenTask:
    def test_reopen(self):
        service = TodoService()
        task = service.add_task(title="Test")
        service.mark_done(task.id)
        reopened = service.reopen_task(task.id)

        assert reopened.status == "open"

    def test_reopen_nonexistent_raises(self):
        service = TodoService()
        with pytest.raises(TaskNotFoundError):
            service.reopen_task(999)


class TestUpdateTask:
    def test_update_title(self):
        service = TodoService()
        task = service.add_task(title="Original")
        updated = service.update_task(task.id, title="Updated")

        assert updated.title == "Updated"

    def test_update_multiple_fields(self):
        service = TodoService()
        task = service.add_task(title="Test")
        updated = service.update_task(
            task.id,
            title="Updated",
            due="2025-06-15",
            priority="med",
            tags="new,tags",
        )

        assert updated.title == "Updated"
        assert updated.due_date.isoformat() == "2025-06-15"
        assert updated.priority == "med"
        assert updated.tags == ["new", "tags"]

    def test_update_invalid_title_raises(self):
        service = TodoService()
        task = service.add_task(title="Test")
        with pytest.raises(ValidationError):
            service.update_task(task.id, title="   ")

    def test_update_nonexistent_raises(self):
        service = TodoService()
        with pytest.raises(TaskNotFoundError):
            service.update_task(999, title="New")


class TestDeleteTask:
    def test_delete(self):
        service = TodoService()
        task = service.add_task(title="To delete")
        service.delete_task(task.id)

        tasks = service.list_tasks()
        assert len(tasks) == 0

    def test_delete_nonexistent_raises(self):
        service = TodoService()
        with pytest.raises(TaskNotFoundError):
            service.delete_task(999)


class TestClearDone:
    def test_clear_done(self):
        service = TodoService()
        service.add_task(title="Open")
        done = service.add_task(title="Done")
        service.mark_done(done.id)

        count = service.clear_done()

        assert count == 1
        tasks = service.list_tasks()
        assert len(tasks) == 1
        assert tasks[0].title == "Open"

    def test_clear_done_returns_zero_when_none(self):
        service = TodoService()
        service.add_task(title="Open")

        count = service.clear_done()
        assert count == 0
