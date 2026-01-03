# Todo In-Memory Python CLI Application

A fast, reliable, in-memory Todo application that runs entirely in the Ubuntu terminal under WSL. Data exists only for the lifetime of the process and is lost on exit.

## Requirements

- Python 3.11+
- Ubuntu (WSL2)

## Setup

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install in development mode with test dependencies
pip install -e ".[dev]"
```

## Usage

Run the application using:

```bash
python -m todo <command> [options]
```

### Commands

**Add a task:**
```bash
python -m todo add "Buy groceries"
python -m todo add "Submit report" --due 2025-01-15 --priority high --tag work,urgent
```

**List tasks:**
```bash
python -m todo list
python -m todo list --status open
python -m todo list --status done
python -m todo list --tag work
python -m todo list --sort due
python -m todo list --sort priority
```

**Mark task as done:**
```bash
python -m todo done 1
```

**Reopen a task:**
```bash
python -m todo reopen 1
```

**Update a task:**
```bash
python -m todo update 1 --title "New title"
python -m todo update 1 --due 2025-02-01 --priority med --tag updated,tags
```

**Delete a task:**
```bash
python -m todo delete 1
```

**Clear all completed tasks:**
```bash
python -m todo clear-done
```

**Get help:**
```bash
python -m todo --help
python -m todo add --help
```

### Interactive Mode

Start an interactive shell session where data persists across commands:

```bash
python -m todo shell
# or
python -m todo menu
```

Example session:
```
$ python -m todo shell
Todo Interactive Mode (type 'help' or 'quit')
---------------------------------------------
todo> add "Buy groceries" --priority high
Added task 1: Buy groceries

todo> add "Call mom"
Added task 2: Call mom

todo> ls
 ID STS PRI  DUE        TITLE                          TAGS
----------------------------------------------------------------------
  1 [ ] HIGH -          Buy groceries                  [-]
  2 [ ] -    -          Call mom                       [-]

todo> x 1
Marked task 1 as done: Buy groceries

todo> show 1
Task #1
  Title:    Buy groceries
  Status:   done
  Priority: high
  Due:      none
  Tags:     none
  Created:  2025-01-03 10:30:22 UTC

todo> list --status open
 ID STS PRI  DUE        TITLE                          TAGS
----------------------------------------------------------------------
  2 [ ] -    -          Call mom                       [-]

todo> q
Goodbye!
```

#### Interactive Commands

| Command | Description |
|---------|-------------|
| `add [title] [options]` | Add a new task (prompts for title if not provided) |
| `list [options]` | List tasks with optional filters |
| `show <id>` | Show detailed task information |
| `done <id>` | Mark task as done |
| `reopen <id>` | Reopen a completed task |
| `update <id> [options]` | Update task (guided prompts if no options given) |
| `delete <id> [-f]` | Delete a task (with confirmation) |
| `clear [-f]` | Clear completed tasks (with confirmation) |
| `help` | Show available commands |
| `quit` | Exit interactive mode |

#### Command Aliases

For faster typing, these aliases are available:

| Alias | Command |
|-------|---------|
| `ls`, `l` | `list` |
| `a` | `add` |
| `s` | `show` |
| `x` | `done` |
| `o` | `reopen` |
| `u` | `update` |
| `rm`, `d` | `delete` |
| `?` | `help` |
| `q` | `quit` |

#### Guided Prompts

When you run `add` without a title or `update` without any options, the shell enters guided prompt mode:

```
todo> add
Title: Buy milk
Added task 1: Buy milk

todo> update 1
Current: Buy milk (open, due: none, priority: none, tags: none)
Title [Buy milk]: Buy whole milk
Due [none]: 2025-01-15
Priority [none]: high
Tags [none]: groceries
Updated task 1: Buy whole milk
```

#### Confirmation Prompts

Destructive actions (`delete` and `clear`) require confirmation:

```
todo> delete 1
Delete task 1 "Buy milk"? [y/N]: y
Deleted task 1

todo> clear
Clear 2 completed task(s)? [y/N]: n
Cancelled.
```

Use `-f` or `--force` to skip confirmation:

```
todo> delete 1 -f
Deleted task 1

todo> clear --force
Cleared 2 completed task(s)
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 2 | Validation error (invalid input) |
| 3 | Task not found |

## Running Tests

```bash
python -m pytest -q
```

## Architecture

The application follows a clean architecture with clear separation of concerns:

```
src/todo/
├── __main__.py          # Entry point
├── cli.py               # CLI layer (argparse)
├── interactive.py       # Interactive shell mode
├── application/
│   └── services.py      # Use cases and business logic
├── domain/
│   ├── models.py        # Task model and validation
│   └── errors.py        # Domain errors
└── repository/
    └── memory_repo.py   # In-memory data storage
```

**Layers:**

1. **CLI Layer** - Handles command-line parsing, output formatting, and error display
2. **Application Layer** - Implements use cases, orchestrates domain and repository
3. **Domain Layer** - Core business logic, models, and validation rules
4. **Repository Layer** - Data storage abstraction (in-memory for Phase I)

This architecture is designed to support seamless migration to Phase II (FastAPI + SQLModel) by:
- Keeping domain logic independent of I/O
- Using repository pattern for data access
- Separating validation from persistence

## Phase I Scope

- In-memory storage only (no persistence)
- Console/CLI interface only
- No authentication or multi-user support
- No web API or UI

## License

MIT
# todo-app
