/sp.implement Todo In-Memory Python Console App (Phase I)

Environment:
- Ubuntu on WSL2
- Python 3.11+
- Project root: /mnt/d/Todo-app
- Run: python -m todo
- Tests: pytest -q

Implementation rules:
- Keep layers separate: CLI → services → domain → repository
- No persistence (no files, no DB)
- No unhandled exceptions in normal usage
- Print user output to stdout; errors to stderr; return non-zero exit codes on failure
- Use UTC timezone-aware timestamps
- Prefer standard library (argparse, dataclasses, datetime, typing)

Build steps (deliver working code, not pseudocode):

1) Create package + structure
- Create directories and files:
  - todo/__init__.py
  - todo/__main__.py
  - todo/cli.py
  - todo/domain/models.py
  - todo/domain/errors.py
  - todo/application/services.py
  - todo/repository/memory_repo.py
  - tests/
  - README.md

2) Domain layer
- Implement Task model (dataclass):
  - id: int
  - title: str
  - status: Literal["open","done"]
  - created_at: datetime (UTC aware)
  - due_date: date | None
  - priority: Literal["low","med","high"] | None
  - tags: list[str]
- Implement validation helpers:
  - title must be non-empty after strip
  - due_date parse from YYYY-MM-DD
  - priority must be in {"low","med","high"} if provided
  - tags parse from comma-separated string into normalized list
- Implement domain errors:
  - ValidationError(message)
  - TaskNotFound(task_id)

3) Repository layer (in-memory)
- Implement MemoryTaskRepo with:
  - internal storage dict[int, Task]
  - next_id counter starting at 1 (monotonic, never reuse)
- Methods:
  - add(task_data) -> Task
  - get(task_id) -> Task
  - update(task_id, fields) -> Task
  - delete(task_id) -> None
  - clear_done() -> int (count removed)
  - list(status, tag, sort) -> list[Task]
- Sorting rules (deterministic):
  - created: created_at asc, tie-break id asc
  - due: tasks with due_date first sorted asc, then no-due, tie-break id asc
  - priority: high > med > low, None last, tie-break id asc

4) Application/service layer
- Implement services that call repo and enforce validation:
  - add_task(title, due, priority, tags) -> Task
  - list_tasks(status="all", tag=None, sort="created") -> list[Task]
  - mark_done(task_id) -> Task
  - reopen_task(task_id) -> Task
  - update_task(task_id, title=None, due=None, priority=None, tags=None) -> Task
  - delete_task(task_id) -> None
  - clear_done() -> int
- Services must raise domain errors (ValidationError, TaskNotFound)

5) CLI layer (argparse)
- Implement subcommands:
  - add "title" [--due YYYY-MM-DD] [--priority low|med|high] [--tag a,b]
  - list [--status all|open|done] [--tag X] [--sort due|priority|created]
  - done <id>
  - reopen <id>
  - update <id> [--title ...] [--due ...] [--priority ...] [--tag a,b]
  - delete <id>
  - clear-done
- Output format:
  - add/update/done/reopen: print one-line confirmation including id and title
  - list: print table-like rows: ID | STATUS | PRIORITY | DUE | TITLE | TAGS
  - clear-done: print count cleared
- Error handling:
  - ValidationError → stderr message, exit 2
  - TaskNotFound → stderr message, exit 3
  - argparse errors handled by argparse (exit 2)

6) Entry point
- todo/__main__.py calls todo.cli.main()
- Ensure `python -m todo --help` works

7) Tests (pytest)
- Domain tests:
  - title validation
  - date parsing valid/invalid
  - priority validation
  - tag parsing normalization
- Service + repo tests:
  - add/list flows
  - done/reopen
  - update partial fields
  - delete + not found
  - clear_done count
  - sorting behavior is deterministic (due/priority/created)
  - filtering by status and tag

8) README
- WSL venv setup:
  - python3 -m venv .venv && source .venv/bin/activate
  - pip install -r requirements.txt OR pip install -e .
- Usage examples (at least 8 commands)
- Short architecture note (layers, why it’s Phase II ready)

Completion criteria:
- `python -m todo add "Test"` works
- `python -m todo list` shows the task
- `python -m todo done 1` marks done
- `pytest -q` passes with meaningful coverage
- No persistence (data resets on restart)
