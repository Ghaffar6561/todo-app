/sp.specify Todo In-Memory Python Console App (Phase I)

Target audience:
- Developers and technical reviewers evaluating the foundation of a multi-phase Todo system
- Contributors who will extend the app into web, AI, and cloud-native phases

Focus:
- Functional correctness of a terminal-based Todo application
- Clean architecture and extensibility
- Linux-first (Ubuntu on WSL) developer experience

Success criteria:
- All core Todo workflows (add, list, update, complete, reopen, delete) function correctly
- Application runs reliably in Ubuntu (WSL) without platform-specific issues
- Core business logic is testable and covered by unit tests
- Codebase is structured to support seamless migration to Phase II (FastAPI + SQLModel)
- A new developer can understand the design and make changes within 30 minutes

Constraints:
- Runtime: Python 3.11+
- Execution environment: Ubuntu terminal (WSL2)
- Data storage: In-memory only (no files, no database)
- Interface: Console / CLI only
- Format:
  - Source code organized as a Python package
  - Markdown documentation for usage and design notes
- Testing:
  - pytest for domain and service layers
  - No dependency on terminal I/O for core logic tests
- Timeline: Phase I implementation should be achievable within a short development cycle (≤ 1 week)

Not building (explicitly out of scope for Phase I):
- Any form of persistence (files, SQLite, PostgreSQL, Redis, etc.)
- Web APIs or UI (REST, FastAPI, Next.js)
- Authentication or multi-user support
- AI, LLMs, or chatbot functionality
- Background jobs, schedulers, or notifications
- Windows-specific behavior or tooling

--- 
Amendment: Interactive Session Mode (Phase I)

Additional focus:
- Provide an interactive mode that keeps a single process running so users can add/view/update tasks in the same session (menu-driven or command-driven shell).

Updated success criteria (add these):
- User can start interactive mode with a single command (e.g., `python -m todo menu` or `python -m todo shell`).
- Within the same session: add → list shows the newly added task immediately.
- Within the same session: update/delete/done/reopen reflect correctly in subsequent list output.
- Graceful handling of invalid inputs (invalid menu choice, invalid/nonexistent id, empty title).

Clarification (important):
- “In-memory only” means data persists only for the lifetime of the running interactive session.
- No persistence across program restarts (still out of scope for Phase I).

Scope update (add this under Scope/Interface expectations):
- CLI supports both:
  - Existing one-shot subcommands (add/list/update/etc.)
  - An interactive session mode for multi-step workflows

Not building (confirm unchanged):
- No file/DB persistence between separate runs
- No web/API/UI
- No AI features

Amendment: Interactive UX Enhancements (Phase I)

Success criteria additions:
- Interactive mode supports guided prompts when required inputs are missing (e.g., `add` and `update`).
- Interactive mode supports convenient aliases (ls/rm/a/u/x/o).
- Interactive mode includes `show <id>` for task details and confirmation prompts for destructive actions.

Constraints:
- No persistence; all interactivity is within a single running session.
- No new heavy dependencies; standard library preferred.
