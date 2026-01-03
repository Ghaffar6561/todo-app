"""Tests for interactive shell mode."""

import io
import pytest

from todo.interactive import InteractiveShell, ALIASES, format_task_detail
from todo.application.services import TodoService


class TestInteractiveShell:
    def create_shell(self, commands: list[str]) -> tuple[InteractiveShell, io.StringIO]:
        """Create a shell with predefined input and capture output."""
        input_stream = io.StringIO("\n".join(commands) + "\n")
        output_stream = io.StringIO()
        service = TodoService()
        shell = InteractiveShell(
            service=service,
            input_stream=input_stream,
            output_stream=output_stream,
        )
        return shell, output_stream

    def test_help_command(self):
        shell, output = self.create_shell(["help", "quit"])
        shell.run()
        result = output.getvalue()

        assert "Commands:" in result
        assert "add [title]" in result
        assert "list" in result
        assert "done <id>" in result
        assert "Aliases:" in result

    def test_quit_exits(self):
        shell, output = self.create_shell(["quit"])
        shell.run()
        result = output.getvalue()

        assert "Goodbye!" in result

    def test_exit_also_works(self):
        shell, output = self.create_shell(["exit"])
        shell.run()
        result = output.getvalue()

        assert "Goodbye!" in result

    def test_add_then_list_shows_task(self):
        shell, output = self.create_shell([
            'add "Buy groceries"',
            "list",
            "quit",
        ])
        shell.run()
        result = output.getvalue()

        assert "Added task 1: Buy groceries" in result
        assert "Buy groceries" in result
        assert "[ ]" in result  # open status

    def test_add_with_options(self):
        shell, output = self.create_shell([
            'add "Important task" --priority high --due 2025-12-31 --tag work,urgent',
            "list",
            "quit",
        ])
        shell.run()
        result = output.getvalue()

        assert "Added task 1: Important task" in result
        assert "HIGH" in result
        assert "2025-12-31" in result
        assert "work" in result

    def test_done_marks_task_complete(self):
        shell, output = self.create_shell([
            'add "Test task"',
            "done 1",
            "list",
            "quit",
        ])
        shell.run()
        result = output.getvalue()

        assert "Marked task 1 as done" in result
        assert "[x]" in result  # done status

    def test_reopen_marks_task_open(self):
        shell, output = self.create_shell([
            'add "Test task"',
            "done 1",
            "reopen 1",
            "list",
            "quit",
        ])
        shell.run()
        result = output.getvalue()

        assert "Reopened task 1" in result
        assert "[ ]" in result  # open status again

    def test_update_changes_task(self):
        shell, output = self.create_shell([
            'add "Original title"',
            'update 1 --title "New title"',
            "list",
            "quit",
        ])
        shell.run()
        result = output.getvalue()

        assert "Updated task 1: New title" in result
        assert "New title" in result

    def test_delete_removes_task(self):
        # Use --force to skip confirmation
        shell, output = self.create_shell([
            'add "To delete"',
            "delete 1 -f",
            "list",
            "quit",
        ])
        shell.run()
        result = output.getvalue()

        assert "Deleted task 1" in result
        assert "No tasks found" in result

    def test_delete_with_confirmation_yes(self):
        shell, output = self.create_shell([
            'add "To delete"',
            "delete 1",
            "y",  # Confirm deletion
            "list",
            "quit",
        ])
        shell.run()
        result = output.getvalue()

        assert "Deleted task 1" in result
        assert "No tasks found" in result

    def test_delete_with_confirmation_no(self):
        shell, output = self.create_shell([
            'add "To keep"',
            "delete 1",
            "n",  # Reject deletion
            "list",
            "quit",
        ])
        shell.run()
        result = output.getvalue()

        assert "Cancelled." in result
        assert "To keep" in result  # Task still exists

    def test_clear_removes_done_tasks(self):
        # Use --force to skip confirmation
        shell, output = self.create_shell([
            'add "Open task"',
            'add "Done task"',
            "done 2",
            "clear -f",
            "list",
            "quit",
        ])
        shell.run()
        result = output.getvalue()

        assert "Cleared 1 completed task(s)" in result
        assert "Open task" in result
        assert "Done task" not in result.split("Cleared")[1]

    def test_clear_with_confirmation_yes(self):
        shell, output = self.create_shell([
            'add "Done task"',
            "done 1",
            "clear",
            "y",  # Confirm
            "quit",
        ])
        shell.run()
        result = output.getvalue()

        assert "Cleared 1 completed task(s)" in result

    def test_clear_no_done_tasks(self):
        shell, output = self.create_shell([
            'add "Open task"',
            "clear",
            "quit",
        ])
        shell.run()
        result = output.getvalue()

        assert "No completed tasks to clear." in result


class TestInteractiveErrorHandling:
    def create_shell(self, commands: list[str]) -> tuple[InteractiveShell, io.StringIO]:
        input_stream = io.StringIO("\n".join(commands) + "\n")
        output_stream = io.StringIO()
        service = TodoService()
        shell = InteractiveShell(
            service=service,
            input_stream=input_stream,
            output_stream=output_stream,
        )
        return shell, output_stream

    def test_empty_title_error(self):
        shell, output = self.create_shell([
            'add ""',
            "quit",
        ])
        shell.run()
        result = output.getvalue()

        assert "Error: Title cannot be empty" in result
        assert "Goodbye!" in result  # Session continues

    def test_add_guided_prompt_empty_title(self):
        # When add is called without args, it prompts for title
        # If user enters empty string, it should error
        shell, output = self.create_shell([
            "add",
            "",  # Empty title in prompt
            "quit",
        ])
        shell.run()
        result = output.getvalue()

        assert "Title:" in result
        assert "Error: Title cannot be empty" in result

    def test_add_guided_prompt_with_title(self):
        # When add is called without args, it prompts for title
        shell, output = self.create_shell([
            "add",
            "Prompted task",  # Title in prompt
            "list",
            "quit",
        ])
        shell.run()
        result = output.getvalue()

        assert "Title:" in result
        assert "Added task 1: Prompted task" in result

    def test_task_not_found_error(self):
        shell, output = self.create_shell([
            "done 999",
            "quit",
        ])
        shell.run()
        result = output.getvalue()

        assert "Error: Task with id 999 not found" in result
        assert "Goodbye!" in result  # Session continues

    def test_invalid_id_error(self):
        shell, output = self.create_shell([
            "done abc",
            "quit",
        ])
        shell.run()
        result = output.getvalue()

        assert "Error:" in result
        assert "not a valid task ID" in result

    def test_missing_id_error(self):
        shell, output = self.create_shell([
            "done",
            "quit",
        ])
        shell.run()
        result = output.getvalue()

        assert "Error: Task ID is required" in result

    def test_unknown_command(self):
        shell, output = self.create_shell([
            "foobar",
            "quit",
        ])
        shell.run()
        result = output.getvalue()

        assert "Unknown command: foobar" in result
        assert "help" in result.lower()

    def test_invalid_date_error(self):
        shell, output = self.create_shell([
            'add "Task" --due invalid-date',
            "quit",
        ])
        shell.run()
        result = output.getvalue()

        assert "Error:" in result
        assert "Invalid date format" in result

    def test_invalid_priority_in_list(self):
        shell, output = self.create_shell([
            "list --status invalid",
            "quit",
        ])
        shell.run()
        result = output.getvalue()

        assert "Error: Invalid status" in result

    def test_session_continues_after_error(self):
        shell, output = self.create_shell([
            "done 999",  # Error
            'add "Still works"',  # Should work
            "list",
            "quit",
        ])
        shell.run()
        result = output.getvalue()

        assert "Error: Task with id 999 not found" in result
        assert "Added task 1: Still works" in result
        assert "Still works" in result


class TestSessionPersistence:
    def create_shell(self, commands: list[str]) -> tuple[InteractiveShell, io.StringIO]:
        input_stream = io.StringIO("\n".join(commands) + "\n")
        output_stream = io.StringIO()
        service = TodoService()
        shell = InteractiveShell(
            service=service,
            input_stream=input_stream,
            output_stream=output_stream,
        )
        return shell, output_stream

    def test_multiple_tasks_persist_in_session(self):
        shell, output = self.create_shell([
            'add "Task 1"',
            'add "Task 2"',
            'add "Task 3"',
            "list",
            "quit",
        ])
        shell.run()
        result = output.getvalue()

        assert "Task 1" in result
        assert "Task 2" in result
        assert "Task 3" in result

    def test_operations_chain_correctly(self):
        shell, output = self.create_shell([
            'add "Original"',
            'update 1 --title "Modified"',
            "done 1",
            "list",
            "quit",
        ])
        shell.run()
        result = output.getvalue()

        lines = result.split("\n")
        # Find the line with Modified in the list output
        list_output = [l for l in lines if "Modified" in l and "[x]" in l]
        assert len(list_output) == 1  # Task is both modified and done

    def test_empty_lines_ignored(self):
        shell, output = self.create_shell([
            "",
            'add "Task"',
            "",
            "list",
            "",
            "quit",
        ])
        shell.run()
        result = output.getvalue()

        assert "Added task 1: Task" in result
        assert "Task" in result


class TestCommandAliases:
    def create_shell(self, commands: list[str]) -> tuple[InteractiveShell, io.StringIO]:
        input_stream = io.StringIO("\n".join(commands) + "\n")
        output_stream = io.StringIO()
        service = TodoService()
        shell = InteractiveShell(
            service=service,
            input_stream=input_stream,
            output_stream=output_stream,
        )
        return shell, output_stream

    def test_ls_alias_for_list(self):
        shell, output = self.create_shell([
            'add "Test"',
            "ls",
            "quit",
        ])
        shell.run()
        result = output.getvalue()

        assert "Test" in result
        assert "ID" in result  # Table header

    def test_l_alias_for_list(self):
        shell, output = self.create_shell([
            'add "Test"',
            "l",
            "quit",
        ])
        shell.run()
        result = output.getvalue()

        assert "Test" in result

    def test_a_alias_for_add(self):
        shell, output = self.create_shell([
            'a "Aliased add"',
            "list",
            "quit",
        ])
        shell.run()
        result = output.getvalue()

        assert "Added task 1: Aliased add" in result

    def test_rm_alias_for_delete(self):
        shell, output = self.create_shell([
            'add "To remove"',
            "rm 1 -f",
            "list",
            "quit",
        ])
        shell.run()
        result = output.getvalue()

        assert "Deleted task 1" in result
        assert "No tasks found" in result

    def test_d_alias_for_delete(self):
        shell, output = self.create_shell([
            'add "To delete"',
            "d 1 -f",
            "list",
            "quit",
        ])
        shell.run()
        result = output.getvalue()

        assert "Deleted task 1" in result

    def test_x_alias_for_done(self):
        shell, output = self.create_shell([
            'add "To complete"',
            "x 1",
            "list",
            "quit",
        ])
        shell.run()
        result = output.getvalue()

        assert "Marked task 1 as done" in result
        assert "[x]" in result

    def test_o_alias_for_reopen(self):
        shell, output = self.create_shell([
            'add "To reopen"',
            "done 1",
            "o 1",
            "list",
            "quit",
        ])
        shell.run()
        result = output.getvalue()

        assert "Reopened task 1" in result
        assert "[ ]" in result

    def test_u_alias_for_update(self):
        shell, output = self.create_shell([
            'add "Original"',
            'u 1 --title "Updated"',
            "list",
            "quit",
        ])
        shell.run()
        result = output.getvalue()

        assert "Updated task 1: Updated" in result

    def test_s_alias_for_show(self):
        shell, output = self.create_shell([
            'add "Show me"',
            "s 1",
            "quit",
        ])
        shell.run()
        result = output.getvalue()

        assert "Task #1" in result
        assert "Title:    Show me" in result

    def test_question_mark_alias_for_help(self):
        shell, output = self.create_shell([
            "?",
            "quit",
        ])
        shell.run()
        result = output.getvalue()

        assert "Commands:" in result
        assert "Aliases:" in result

    def test_q_alias_for_quit(self):
        shell, output = self.create_shell([
            "q",
        ])
        shell.run()
        result = output.getvalue()

        assert "Goodbye!" in result


class TestShowCommand:
    def create_shell(self, commands: list[str]) -> tuple[InteractiveShell, io.StringIO]:
        input_stream = io.StringIO("\n".join(commands) + "\n")
        output_stream = io.StringIO()
        service = TodoService()
        shell = InteractiveShell(
            service=service,
            input_stream=input_stream,
            output_stream=output_stream,
        )
        return shell, output_stream

    def test_show_displays_task_details(self):
        shell, output = self.create_shell([
            'add "Detailed task" --priority high --due 2025-06-15 --tag work,urgent',
            "show 1",
            "quit",
        ])
        shell.run()
        result = output.getvalue()

        assert "Task #1" in result
        assert "Title:    Detailed task" in result
        assert "Status:   open" in result
        assert "Priority: high" in result
        assert "Due:      2025-06-15" in result
        assert "Tags:     work, urgent" in result
        assert "Created:" in result

    def test_show_task_not_found(self):
        shell, output = self.create_shell([
            "show 999",
            "quit",
        ])
        shell.run()
        result = output.getvalue()

        assert "Error: Task with id 999 not found" in result

    def test_show_with_none_fields(self):
        shell, output = self.create_shell([
            'add "Simple task"',
            "show 1",
            "quit",
        ])
        shell.run()
        result = output.getvalue()

        assert "Priority: none" in result
        assert "Due:      none" in result
        assert "Tags:     none" in result


class TestGuidedPrompts:
    def create_shell(self, commands: list[str]) -> tuple[InteractiveShell, io.StringIO]:
        input_stream = io.StringIO("\n".join(commands) + "\n")
        output_stream = io.StringIO()
        service = TodoService()
        shell = InteractiveShell(
            service=service,
            input_stream=input_stream,
            output_stream=output_stream,
        )
        return shell, output_stream

    def test_update_guided_mode(self):
        # When update is called with ID but no flags, it enters guided mode
        shell, output = self.create_shell([
            'add "Original title" --priority low',
            "update 1",
            "New title",  # New title
            "",  # Keep due
            "high",  # New priority
            "",  # Keep tags
            "list",
            "quit",
        ])
        shell.run()
        result = output.getvalue()

        assert "Current: Original title" in result
        assert "Title [Original title]:" in result
        assert "Updated task 1: New title" in result

    def test_update_guided_mode_keep_defaults(self):
        shell, output = self.create_shell([
            'add "Keep this"',
            "update 1",
            "",  # Keep title
            "",  # Keep due
            "",  # Keep priority
            "",  # Keep tags
            "show 1",
            "quit",
        ])
        shell.run()
        result = output.getvalue()

        assert "Updated task 1: Keep this" in result
        assert "Title:    Keep this" in result


class TestForceFlag:
    def create_shell(self, commands: list[str]) -> tuple[InteractiveShell, io.StringIO]:
        input_stream = io.StringIO("\n".join(commands) + "\n")
        output_stream = io.StringIO()
        service = TodoService()
        shell = InteractiveShell(
            service=service,
            input_stream=input_stream,
            output_stream=output_stream,
        )
        return shell, output_stream

    def test_delete_force_flag_short(self):
        shell, output = self.create_shell([
            'add "Force delete"',
            "delete 1 -f",
            "quit",
        ])
        shell.run()
        result = output.getvalue()

        assert "Deleted task 1" in result
        assert "?" not in result  # No confirmation prompt

    def test_delete_force_flag_long(self):
        shell, output = self.create_shell([
            'add "Force delete"',
            "delete 1 --force",
            "quit",
        ])
        shell.run()
        result = output.getvalue()

        assert "Deleted task 1" in result

    def test_clear_force_flag_short(self):
        shell, output = self.create_shell([
            'add "Done"',
            "done 1",
            "clear -f",
            "quit",
        ])
        shell.run()
        result = output.getvalue()

        assert "Cleared 1 completed task(s)" in result
        assert "?" not in result  # No confirmation prompt

    def test_clear_force_flag_long(self):
        shell, output = self.create_shell([
            'add "Done"',
            "done 1",
            "clear --force",
            "quit",
        ])
        shell.run()
        result = output.getvalue()

        assert "Cleared 1 completed task(s)" in result


class TestAliasMapping:
    def test_aliases_dict_contains_expected_mappings(self):
        assert ALIASES["ls"] == "list"
        assert ALIASES["l"] == "list"
        assert ALIASES["a"] == "add"
        assert ALIASES["rm"] == "delete"
        assert ALIASES["d"] == "delete"
        assert ALIASES["x"] == "done"
        assert ALIASES["o"] == "reopen"
        assert ALIASES["u"] == "update"
        assert ALIASES["s"] == "show"
        assert ALIASES["?"] == "help"
        assert ALIASES["q"] == "quit"


class TestFormatTaskDetail:
    def test_format_with_all_fields(self):
        from datetime import date, datetime, timezone

        from todo.domain.models import Task

        task = Task(
            id=1,
            title="Test task",
            status="open",
            created_at=datetime(2025, 1, 15, 10, 30, 22, tzinfo=timezone.utc),
            due_date=date(2025, 2, 1),
            priority="high",
            tags=["work", "urgent"],
        )
        result = format_task_detail(task)

        assert "Task #1" in result
        assert "Title:    Test task" in result
        assert "Status:   open" in result
        assert "Priority: high" in result
        assert "Due:      2025-02-01" in result
        assert "Tags:     work, urgent" in result
        assert "Created:  2025-01-15 10:30:22 UTC" in result

    def test_format_with_none_fields(self):
        from datetime import datetime, timezone

        from todo.domain.models import Task

        task = Task(
            id=2,
            title="Simple",
            status="done",
            created_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        )
        result = format_task_detail(task)

        assert "Priority: none" in result
        assert "Due:      none" in result
        assert "Tags:     none" in result
