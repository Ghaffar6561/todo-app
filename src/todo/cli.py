"""Command-line interface for the Todo application."""

import argparse
import sys
from typing import NoReturn

from todo.application.services import TodoService
from todo.domain.errors import ValidationError, TaskNotFoundError
from todo.domain.models import Task


EXIT_SUCCESS = 0
EXIT_VALIDATION_ERROR = 2
EXIT_NOT_FOUND = 3


# Global service instance (in-memory, resets on process restart)
_service: TodoService | None = None


def get_service() -> TodoService:
    """Get or create the global service instance."""
    global _service
    if _service is None:
        _service = TodoService()
    return _service


def format_task_line(task: Task) -> str:
    """Format a task as a single line for display."""
    status = "[x]" if task.status == "done" else "[ ]"
    priority = task.priority.upper() if task.priority else "-"
    due = str(task.due_date) if task.due_date else "-"
    tags = ",".join(task.tags) if task.tags else "-"
    return f"{task.id:>3} {status} {priority:<4} {due:<10} {task.title} [{tags}]"


def format_task_table(tasks: list[Task]) -> str:
    """Format a list of tasks as a table."""
    if not tasks:
        return "No tasks found."

    header = f"{'ID':>3} {'STS':<3} {'PRI':<4} {'DUE':<10} {'TITLE':<30} TAGS"
    separator = "-" * 70
    lines = [header, separator]
    for task in tasks:
        lines.append(format_task_line(task))
    return "\n".join(lines)


def cmd_add(args: argparse.Namespace) -> int:
    """Handle the 'add' command."""
    service = get_service()
    task = service.add_task(
        title=args.title,
        due=args.due,
        priority=args.priority,
        tags=args.tag,
    )
    print(f"Added task {task.id}: {task.title}")
    return EXIT_SUCCESS


def cmd_list(args: argparse.Namespace) -> int:
    """Handle the 'list' command."""
    service = get_service()
    tasks = service.list_tasks(
        status=args.status,
        tag=args.tag,
        sort=args.sort,
    )
    print(format_task_table(tasks))
    return EXIT_SUCCESS


def cmd_done(args: argparse.Namespace) -> int:
    """Handle the 'done' command."""
    service = get_service()
    task = service.mark_done(args.id)
    print(f"Marked task {task.id} as done: {task.title}")
    return EXIT_SUCCESS


def cmd_reopen(args: argparse.Namespace) -> int:
    """Handle the 'reopen' command."""
    service = get_service()
    task = service.reopen_task(args.id)
    print(f"Reopened task {task.id}: {task.title}")
    return EXIT_SUCCESS


def cmd_update(args: argparse.Namespace) -> int:
    """Handle the 'update' command."""
    service = get_service()
    task = service.update_task(
        task_id=args.id,
        title=args.title,
        due=args.due if hasattr(args, "due") and args.due is not None else ...,
        priority=args.priority if hasattr(args, "priority") and args.priority is not None else ...,
        tags=args.tag if hasattr(args, "tag") and args.tag is not None else ...,
    )
    print(f"Updated task {task.id}: {task.title}")
    return EXIT_SUCCESS


def cmd_delete(args: argparse.Namespace) -> int:
    """Handle the 'delete' command."""
    service = get_service()
    service.delete_task(args.id)
    print(f"Deleted task {args.id}")
    return EXIT_SUCCESS


def cmd_clear_done(args: argparse.Namespace) -> int:
    """Handle the 'clear-done' command."""
    service = get_service()
    count = service.clear_done()
    print(f"Cleared {count} completed task(s)")
    return EXIT_SUCCESS


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="todo",
        description="In-memory Todo CLI application",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # add command
    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("title", help="Task title")
    add_parser.add_argument("--due", metavar="YYYY-MM-DD", help="Due date")
    add_parser.add_argument(
        "--priority",
        choices=["low", "med", "high"],
        help="Priority level",
    )
    add_parser.add_argument("--tag", metavar="TAGS", help="Comma-separated tags")
    add_parser.set_defaults(func=cmd_add)

    # list command
    list_parser = subparsers.add_parser("list", help="List tasks")
    list_parser.add_argument(
        "--status",
        choices=["all", "open", "done"],
        default="all",
        help="Filter by status (default: all)",
    )
    list_parser.add_argument("--tag", help="Filter by tag")
    list_parser.add_argument(
        "--sort",
        choices=["created", "due", "priority"],
        default="created",
        help="Sort order (default: created)",
    )
    list_parser.set_defaults(func=cmd_list)

    # done command
    done_parser = subparsers.add_parser("done", help="Mark a task as done")
    done_parser.add_argument("id", type=int, help="Task ID")
    done_parser.set_defaults(func=cmd_done)

    # reopen command
    reopen_parser = subparsers.add_parser("reopen", help="Reopen a completed task")
    reopen_parser.add_argument("id", type=int, help="Task ID")
    reopen_parser.set_defaults(func=cmd_reopen)

    # update command
    update_parser = subparsers.add_parser("update", help="Update a task")
    update_parser.add_argument("id", type=int, help="Task ID")
    update_parser.add_argument("--title", help="New title")
    update_parser.add_argument("--due", metavar="YYYY-MM-DD", help="New due date")
    update_parser.add_argument(
        "--priority",
        choices=["low", "med", "high"],
        help="New priority",
    )
    update_parser.add_argument("--tag", metavar="TAGS", help="New tags (comma-separated)")
    update_parser.set_defaults(func=cmd_update)

    # delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a task")
    delete_parser.add_argument("id", type=int, help="Task ID")
    delete_parser.set_defaults(func=cmd_delete)

    # clear-done command
    clear_done_parser = subparsers.add_parser("clear-done", help="Clear all completed tasks")
    clear_done_parser.set_defaults(func=cmd_clear_done)

    # shell command (interactive mode)
    shell_parser = subparsers.add_parser("shell", help="Start interactive shell mode")
    shell_parser.set_defaults(func=cmd_shell)

    # menu command (alias for shell)
    menu_parser = subparsers.add_parser("menu", help="Start interactive menu mode")
    menu_parser.set_defaults(func=cmd_shell)

    return parser


def cmd_shell(args: argparse.Namespace) -> int:
    """Handle the 'shell' command - start interactive mode."""
    from todo.interactive import run_shell
    return run_shell()


def main(argv: list[str] | None = None) -> int:
    """Main entry point for the CLI."""
    parser = create_parser()

    try:
        args = parser.parse_args(argv)
        return args.func(args)
    except ValidationError as e:
        print(f"Error: {e.message}", file=sys.stderr)
        return EXIT_VALIDATION_ERROR
    except TaskNotFoundError as e:
        print(f"Error: {e.message}", file=sys.stderr)
        return EXIT_NOT_FOUND


if __name__ == "__main__":
    sys.exit(main())
