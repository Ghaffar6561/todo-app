"""Interactive shell mode for the Todo application."""

import shlex
import sys
from typing import TextIO

from todo.application.services import TodoService
from todo.domain.errors import ValidationError, TaskNotFoundError
from todo.domain.models import Task
from todo.cli import format_task_table


# Command aliases mapping
ALIASES: dict[str, str] = {
    "ls": "list",
    "l": "list",
    "a": "add",
    "rm": "delete",
    "d": "delete",
    "x": "done",
    "o": "reopen",
    "u": "update",
    "s": "show",
    "?": "help",
    "q": "quit",
}


HELP_TEXT = """\
Commands:
  add [title] [--due D] [--priority P] [--tag T]   Add a new task
  list [--status S] [--tag T] [--sort S]           List tasks
  show <id>                                         Show task details
  done <id>                                         Mark task as done
  reopen <id>                                       Reopen a task
  update <id> [--title T] [--due D] [--priority P] [--tag T]
                                                   Update a task
  delete <id> [-f]                                  Delete a task
  clear [-f]                                        Clear completed tasks
  help                                              Show this help
  quit                                              Exit

Aliases: ls=list, l=list, a=add, rm=delete, d=delete,
         x=done, o=reopen, u=update, s=show, ?=help, q=quit
"""


def format_task_detail(task: Task) -> str:
    """Format a single task for detailed display."""
    priority = task.priority if task.priority else "none"
    due = str(task.due_date) if task.due_date else "none"
    tags = ", ".join(task.tags) if task.tags else "none"
    created = task.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")

    return f"""\
Task #{task.id}
  Title:    {task.title}
  Status:   {task.status}
  Priority: {priority}
  Due:      {due}
  Tags:     {tags}
  Created:  {created}"""


class PromptCancelled(Exception):
    """Raised when user cancels a prompt."""

    pass


class InteractiveShell:
    """Interactive shell for todo operations."""

    def __init__(
        self,
        service: TodoService | None = None,
        input_stream: TextIO | None = None,
        output_stream: TextIO | None = None,
    ) -> None:
        self.service = service or TodoService()
        self.input_stream = input_stream or sys.stdin
        self.output_stream = output_stream or sys.stdout

    def print(self, message: str = "") -> None:
        """Print to output stream."""
        print(message, file=self.output_stream)

    def prompt(self, message: str) -> str:
        """Prompt for input. Raises PromptCancelled on EOF/interrupt."""
        try:
            if self.input_stream == sys.stdin:
                return input(message)
            else:
                self.print(message)
                line = self.input_stream.readline()
                if not line:
                    raise PromptCancelled()
                return line.rstrip("\n")
        except (EOFError, KeyboardInterrupt):
            raise PromptCancelled()

    def confirm(self, message: str) -> bool:
        """Ask for confirmation. Returns True only if user enters y/Y/yes/YES."""
        try:
            response = self.prompt(f"{message} [y/N]: ")
            return response.strip().lower() in ("y", "yes")
        except PromptCancelled:
            return False

    def run(self) -> None:
        """Run the interactive shell loop."""
        self.print("Todo Interactive Mode (type 'help' or 'quit')")
        self.print("-" * 45)

        while True:
            try:
                if self.input_stream == sys.stdin:
                    line = input("todo> ")
                else:
                    line = self.input_stream.readline()
                    if not line:  # EOF
                        break
                    line = line.rstrip("\n")

                line = line.strip()
                if not line:
                    continue

                should_exit = self.execute(line)
                if should_exit:
                    break

            except EOFError:
                self.print("\nGoodbye!")
                break
            except KeyboardInterrupt:
                self.print("\nGoodbye!")
                break

    def execute(self, line: str) -> bool:
        """Execute a single command. Returns True if shell should exit."""
        try:
            tokens = shlex.split(line)
        except ValueError as e:
            self.print(f"Error: Invalid input - {e}")
            return False

        if not tokens:
            return False

        cmd = tokens[0].lower()
        args = tokens[1:]

        # Resolve aliases
        cmd = ALIASES.get(cmd, cmd)

        if cmd in ("quit", "exit"):
            self.print("Goodbye!")
            return True

        if cmd == "help":
            self.print(HELP_TEXT)
            return False

        handler = getattr(self, f"cmd_{cmd}", None)
        if handler is None:
            self.print(f"Unknown command: {cmd}. Type 'help' for options.")
            return False

        try:
            handler(args)
        except ValidationError as e:
            self.print(f"Error: {e.message}")
        except TaskNotFoundError as e:
            self.print(f"Error: {e.message}")
        except PromptCancelled:
            self.print("Cancelled.")

        return False

    def cmd_add(self, args: list[str]) -> None:
        """Handle add command."""
        opts = self._parse_options(args)

        # Check for -f/--force (not used for add, but parse it)
        # Extract title from non-option args
        non_option_args = self._get_non_option_args(args)

        if not non_option_args:
            # Guided prompt mode
            title = self.prompt("Title: ").strip()
            if not title:
                raise ValidationError("Title cannot be empty")
        else:
            title = non_option_args[0]

        task = self.service.add_task(
            title=title,
            due=opts.get("due"),
            priority=opts.get("priority"),
            tags=opts.get("tag"),
        )
        self.print(f"Added task {task.id}: {task.title}")

    def cmd_list(self, args: list[str]) -> None:
        """Handle list command."""
        opts = self._parse_options(args)

        status = opts.get("status", "all")
        if status not in ("all", "open", "done"):
            self.print(f"Error: Invalid status '{status}'. Use: all, open, done")
            return

        sort = opts.get("sort", "created")
        if sort not in ("created", "due", "priority"):
            self.print(f"Error: Invalid sort '{sort}'. Use: created, due, priority")
            return

        tasks = self.service.list_tasks(
            status=status,  # type: ignore[arg-type]
            tag=opts.get("tag"),
            sort=sort,  # type: ignore[arg-type]
        )
        self.print(format_task_table(tasks))

    def cmd_show(self, args: list[str]) -> None:
        """Handle show command - display detailed task info."""
        task_id = self._parse_id(args)
        if task_id is None:
            return

        task = self.service.get_task(task_id)
        self.print(format_task_detail(task))

    def cmd_done(self, args: list[str]) -> None:
        """Handle done command."""
        task_id = self._parse_id(args)
        if task_id is None:
            return

        task = self.service.mark_done(task_id)
        self.print(f"Marked task {task.id} as done: {task.title}")

    def cmd_reopen(self, args: list[str]) -> None:
        """Handle reopen command."""
        task_id = self._parse_id(args)
        if task_id is None:
            return

        task = self.service.reopen_task(task_id)
        self.print(f"Reopened task {task.id}: {task.title}")

    def cmd_update(self, args: list[str]) -> None:
        """Handle update command."""
        task_id = self._parse_id(args)
        if task_id is None:
            return

        opts = self._parse_options(args[1:])

        # Check if any update flags were provided
        has_update_flags = any(
            key in opts for key in ("title", "due", "priority", "tag")
        )

        if not has_update_flags:
            # Guided prompt mode - get current task first
            task = self.service.get_task(task_id)
            current_due = str(task.due_date) if task.due_date else "none"
            current_priority = task.priority if task.priority else "none"
            current_tags = ",".join(task.tags) if task.tags else "none"

            self.print(
                f"Current: {task.title} ({task.status}, due: {current_due}, "
                f"priority: {current_priority}, tags: {current_tags})"
            )

            # Prompt for each field
            new_title = self.prompt(f"Title [{task.title}]: ").strip()
            new_due = self.prompt(f"Due [{current_due}]: ").strip()
            new_priority = self.prompt(f"Priority [{current_priority}]: ").strip()
            new_tags = self.prompt(f"Tags [{current_tags}]: ").strip()

            # Use new values if provided, otherwise keep current
            opts["title"] = new_title if new_title else None
            if new_due and new_due != "none":
                opts["due"] = new_due
            elif new_due == "none" and task.due_date:
                # User explicitly wants to clear due date
                opts["due"] = None
            if new_priority and new_priority != "none":
                opts["priority"] = new_priority
            elif new_priority == "none" and task.priority:
                opts["priority"] = None
            if new_tags and new_tags != "none":
                opts["tag"] = new_tags
            elif new_tags == "none" and task.tags:
                opts["tag"] = ""

        updated_task = self.service.update_task(
            task_id=task_id,
            title=opts.get("title"),
            due=opts.get("due") if "due" in opts else ...,  # type: ignore[arg-type]
            priority=opts.get("priority") if "priority" in opts else ...,  # type: ignore[arg-type]
            tags=opts.get("tag") if "tag" in opts else ...,  # type: ignore[arg-type]
        )
        self.print(f"Updated task {updated_task.id}: {updated_task.title}")

    def cmd_delete(self, args: list[str]) -> None:
        """Handle delete command."""
        task_id = self._parse_id(args)
        if task_id is None:
            return

        opts = self._parse_options(args[1:])
        force = "f" in opts or "force" in opts

        # Get task first to show title in confirmation
        task = self.service.get_task(task_id)

        if not force:
            if not self.confirm(f'Delete task {task_id} "{task.title}"?'):
                self.print("Cancelled.")
                return

        self.service.delete_task(task_id)
        self.print(f"Deleted task {task_id}")

    def cmd_clear(self, args: list[str]) -> None:
        """Handle clear command (clear-done)."""
        opts = self._parse_options(args)
        force = "f" in opts or "force" in opts

        # Get count of done tasks first
        done_tasks = self.service.list_tasks(status="done")
        count = len(done_tasks)

        if count == 0:
            self.print("No completed tasks to clear.")
            return

        if not force:
            if not self.confirm(f"Clear {count} completed task(s)?"):
                self.print("Cancelled.")
                return

        cleared = self.service.clear_done()
        self.print(f"Cleared {cleared} completed task(s)")

    def _parse_id(self, args: list[str]) -> int | None:
        """Parse task ID from args. Returns None and prints error if invalid."""
        if not args:
            self.print("Error: Task ID is required")
            return None

        try:
            return int(args[0])
        except ValueError:
            self.print(f"Error: '{args[0]}' is not a valid task ID")
            return None

    def _parse_options(self, args: list[str]) -> dict[str, str]:
        """Parse --key value and -k pairs from args."""
        opts: dict[str, str] = {}
        i = 0
        while i < len(args):
            if args[i].startswith("--"):
                key = args[i][2:]
                if i + 1 < len(args) and not args[i + 1].startswith("-"):
                    opts[key] = args[i + 1]
                    i += 2
                else:
                    opts[key] = ""
                    i += 1
            elif args[i].startswith("-") and len(args[i]) == 2:
                # Short flag like -f
                key = args[i][1:]
                opts[key] = ""
                i += 1
            else:
                i += 1
        return opts

    def _get_non_option_args(self, args: list[str]) -> list[str]:
        """Get positional (non-option) arguments."""
        result = []
        i = 0
        while i < len(args):
            if args[i].startswith("--"):
                # Skip --key value pair
                if i + 1 < len(args) and not args[i + 1].startswith("-"):
                    i += 2
                else:
                    i += 1
            elif args[i].startswith("-") and len(args[i]) == 2:
                # Skip short flag
                i += 1
            else:
                result.append(args[i])
                i += 1
        return result


def run_shell() -> int:
    """Run the interactive shell. Returns exit code."""
    shell = InteractiveShell()
    shell.run()
    return 0
