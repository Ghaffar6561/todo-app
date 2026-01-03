/sp.task Todo In-Memory Python Console App (Phase I)

Environment:
- Ubuntu on WSL2
- Python 3.11+
- Run: python -m todo

Objective:
Build a terminal-based, in-memory Todo app with clean architecture, robust CLI behavior, and unit-tested core logic. No persistence.

Tasks:

1) Project setup
- Create Python package:
  todo/ (__main__.py, cli.py)
  domain/ (models.py, errors.py)
  application/ (services.py)
  repository/ (memory_repo.py)
  tests/
- Add pytest (and minimal tooling only if needed)

2) Domain model
- Task fields: id, title, status, created_at (UTC), due_date?, priority?, tags?
- Validate title, due_date format, priority values
- Define domain errors (not found, validation)

3) In-memory repository
- CRUD + clear_done
- Stable, deterministic sorting & filtering

4) Service layer
- add, list, done, reopen, update, delete, clear_done
- Handle validation and errors
- No CLI dependencies

5) CLI
- argparse subcommands:
  add, list, done, reopen, update, delete, clear-done
- Clean stdout/stderr separation
- Non-zero exit codes on errors

6) Tests
- Unit tests for domain, services, repository
- No terminal I/O in tests

7) Documentation
- README: WSL setup, run commands, usage examples, design notes

Acceptance criteria:
- Commands work end-to-end in Ubuntu WSL
- pytest passes
- No unhandled exceptions
- Code is Phase II–ready (FastAPI + SQLModel)

Deliverables:
- Source code
- tests/
- README.md
