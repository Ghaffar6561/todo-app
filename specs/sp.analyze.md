/sp.analyze Todo In-Memory Python Console App (Phase I)

Context:
- Environment: Ubuntu on WSL2
- Phase I scope: in-memory only, terminal/CLI only, Python 3.11+
- Future phases: Phase II web app (FastAPI + SQLModel), later AI + cloud-native

Analysis goals:
- Confirm the minimum functional scope for a usable Todo CLI
- Identify risks/edge cases early (inputs, IDs, sorting, output, testability)
- Propose a clean architecture that scales into Phase II without rework
- Define clear acceptance tests and quality gates for Phase I

Key questions to analyze:
1) CLI UX and command design
- Are the commands sufficient and intuitive (add/list/done/reopen/update/delete/clear-done)?
- Which flags are required vs optional?
- What should output look like for list and single-task operations?
- What should error messages and exit codes be for common failures?

2) Data model and invariants
- What fields are required/optional and why?
- What are the validation rules (title, due date format, priority enum, tags parsing)?
- How will created_at be generated (UTC timezone-aware) and displayed?

3) ID strategy (important for in-memory + tests)
- Choose between monotonic integers vs UUID
- Ensure deterministic behavior for tests and stable sorting
- Define how IDs behave after delete (reuse or never reuse)

4) Filtering and sorting behavior
- list filters: status, tag
- list sort: due, priority, created
- Define stable tie-break rules (id or created_at)
- Decide how to handle missing due dates/priorities in sorting

5) Architecture and boundaries
- Recommended layers:
  - CLI (argparse parsing + output formatting only)
  - Service layer (use-cases + validation + error mapping)
  - Domain (Task model + domain errors)
  - Repository (in-memory storage)
- Ensure CLI never directly mutates data; services do
- Ensure services do not depend on argparse/printing (testable)

6) Testing strategy
- What to test in domain vs service vs repository?
- Define core test cases:
  - add/list basic flow
  - update partial fields
  - mark done/reopen
  - delete/not found
  - invalid date/priority/title
  - sorting determinism and tag filtering
- Optional: CLI parsing smoke tests (limited)

7) WSL-specific considerations
- POSIX paths, UTF-8 terminal output
- No Windows path assumptions (/mnt/* is fine but not required)
- Ensure consistent behavior across bash/zsh
- Keep dependencies minimal and installable via venv in Ubuntu

Outputs expected from this analysis:
- Finalized command list and flag definitions
- Final data model specification + validation rules
- ID + sorting rules (deterministic)
- Proposed folder/module structure
- Test plan summary + acceptance tests
- Phase II readiness notes (what carries forward to FastAPI/SQLModel)

Acceptance criteria for the analysis:
- No ambiguity in how commands behave
- Edge cases identified with explicit decisions
- Architecture supports clean migration to Phase II
- Test plan covers the most failure-prone areas
