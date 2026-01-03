/sp.constitution

Project: Todo In-Memory Python Console App (Phase I)

Target Environment:
- OS: Ubuntu (WSL2 on Windows)
- Shell: bash / zsh
- Python runtime: system Python or pyenv on Ubuntu
- Execution: terminal-only (no Windows-specific assumptions)

Goal:
Build a fast, reliable, in-memory Todo application that runs entirely in the Ubuntu terminal under WSL. Data exists only for the lifetime of the process and is lost on exit.

Core principles:
- Deterministic behavior across WSL sessions
- Correctness and stability (no crashes on malformed input)
- Clean, maintainable Python architecture
- Linux-first CLI ergonomics (pipes, exit codes, help flags)
- Easy evolution into Phase II (FastAPI + SQLModel backend)

Key standards:
- Python version: 3.11+ (PEP 484 / PEP 544 typing enforced)
- Platform assumptions:
  - POSIX-compliant paths
  - UTF-8 terminal encoding
  - No Windows-only libraries or path handling
- Architecture:
  - CLI layer (argparse or equivalent)
  - Application/service layer
  - Domain model
  - In-memory repository
- CLI behavior:
  - --help available for all commands
  - Non-zero exit codes on failure
  - Clear stderr vs stdout separation
- Error handling:
  - No unhandled exceptions in normal flows
  - User-facing errors are concise and actionable

Scope (Phase I only):
- In-memory task storage (Python dict/list)
- Commands:
  - add "title" [--due YYYY-MM-DD] [--priority low|med|high] [--tag tag1,tag2]
  - list [--status all|open|done] [--tag X] [--sort due|priority|created]
  - done <id>
  - reopen <id>
  - update <id> [--title ...] [--due ...] [--priority ...] [--tag ...]
  - delete <id>
  - clear-done
- Task attributes:
  - id (monotonic or UUID; deterministic in tests)
  - title (required)
  - status (open/done)
  - created_at (UTC, timezone-aware)
  - due_date (optional, ISO-8601)
  - priority (optional)
  - tags (optional list)
- Output:
  - Human-readable tabular or block format
  - Must render cleanly in Ubuntu terminal
  - No mandatory ANSI colors (optional via flag)

Non-goals (explicit exclusions):
- No persistence (files, SQLite, Redis)
- No REST or Web UI
- No authentication or multi-user support
- No AI features (reserved for Phase III)

Constraints:
- Must run as:
  - python -m todo
  - OR python main.py
- Must work inside WSL without elevated privileges
- Must not rely on Windows filesystem paths (/mnt/c assumptions prohibited)
- Minimal dependencies; standard library preferred
- All timestamps generated in UTC

Deliverables:
- todo/ (Python package)
- __main__.py entrypoint
- tests/ using pytest (Linux-compatible)
- README.md including:
  - WSL setup instructions
  - Python venv instructions
  - Command examples
  - Exit code behavior

Success criteria:
- All commands behave consistently in Ubuntu WSL
- Unit tests pass in WSL without platform-specific skips
- CLI supports piping and scripting (future automation)
- Architecture is ready for Phase II migration (FastAPI, SQLModel, Neon DB)
- Codebase is understandable by a Linux developer within 30 minutes
