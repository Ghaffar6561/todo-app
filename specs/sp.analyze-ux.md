/sp.analyze Interactive UX Enhancements for Todo Shell

Context:
- Current implementation: command-driven shell (`python -m todo shell`)
- New requirements from sp.specify.md Amendment:
  - Guided prompts for missing required inputs
  - Convenient command aliases
  - `show <id>` command for task details
  - Confirmation prompts for destructive actions

---

## 1) Guided Prompts

### Which commands trigger guided prompts?

| Command | Trigger Condition | Prompted Fields |
|---------|-------------------|-----------------|
| `add` | Called with no arguments | Title (required) |
| `update` | Called with ID but no update flags | Title, due, priority, tags (all optional, show current values) |
| `delete` | N/A - uses confirmation instead | N/A |
| `clear` | N/A - uses confirmation instead | N/A |

### Decision: Minimal Prompting

Prompt only when:
1. `add` is called with no title argument
2. `update <id>` is called with no `--title/--due/--priority/--tag` flags

Rationale:
- Keep shell fast for power users who know the syntax
- Prompts are fallback UX, not the primary path
- Avoid prompting for optional fields on `add` (users can use flags)

### Guided Prompt Format

```
todo> add
Title: Buy groceries
Added task 1: Buy groceries

todo> update 1
Current: Buy groceries (open, no due date, no priority, no tags)
Title [Buy groceries]:
Due [none]: 2025-02-01
Priority [none]: high
Tags [none]: shopping,errands
Updated task 1: Buy groceries
```

Rules:
- Show current value in brackets as default
- Empty input = keep current value (for update) or skip (for add optional fields)
- For `add`, only prompt for title; other fields remain optional via flags
- Pressing Enter without input accepts default/skips

---

## 2) Command Aliases

### Proposed Alias Mapping

| Alias | Full Command | Rationale |
|-------|--------------|-----------|
| `ls` | `list` | Unix convention |
| `l` | `list` | Single-char shortcut |
| `a` | `add` | Single-char shortcut |
| `rm` | `delete` | Unix convention |
| `d` | `delete` | Single-char shortcut |
| `x` | `done` | "X marks complete" |
| `o` | `reopen` | "O for open" |
| `u` | `update` | Single-char shortcut |
| `s` | `show` | Single-char shortcut |
| `?` | `help` | Common convention |

### Conflict Rules

1. **No conflicts with existing commands**: Aliases must not shadow full command names
2. **Case-insensitive matching**: `LS`, `Ls`, `ls` all work
3. **Aliases are second-class**: If a future command needs `s`, alias can be removed
4. **Help displays both**: `help` output shows aliases alongside full commands

### Implementation

Alias resolution happens before command dispatch:
```python
ALIASES = {
    "ls": "list", "l": "list",
    "a": "add",
    "rm": "delete", "d": "delete",
    "x": "done",
    "o": "reopen",
    "u": "update",
    "s": "show",
    "?": "help",
}
```

---

## 3) Output Format

### `list` Output (Current - Keep)

```
 ID STS PRI  DUE        TITLE                          TAGS
----------------------------------------------------------------------
  1 [ ] HIGH 2025-02-01 Buy groceries                  [shopping,errands]
  2 [x] -    -          Call mom                       [-]
```

Decision: Keep current format. It's compact and readable.

### `show <id>` Output (New)

```
todo> show 1
Task #1
  Title:    Buy groceries
  Status:   open
  Priority: high
  Due:      2025-02-01
  Tags:     shopping, errands
  Created:  2025-01-15 10:30:22 UTC
```

Format rules:
- Vertical key-value layout for readability
- Priority displayed as lowercase (matches input format)
- Created timestamp in ISO-like format with UTC indicator
- Tags comma-separated (not brackets)
- If field is None/empty: display "none" or "-"

### Operation Confirmations (add/update/done/reopen)

Keep current one-line format:
```
Added task 1: Buy groceries
Marked task 1 as done: Buy groceries
Updated task 1: Buy groceries
Reopened task 1: Buy groceries
Deleted task 1
Cleared 3 completed task(s)
```

---

## 4) Confirmation Prompts

### Which commands require confirmation?

| Command | Confirmation Required | Condition |
|---------|----------------------|-----------|
| `delete <id>` | Yes | Always |
| `clear` | Yes | When count > 0 |
| `add` | No | Non-destructive |
| `update` | No | Non-destructive (recoverable) |
| `done` | No | Non-destructive (reversible via reopen) |
| `reopen` | No | Non-destructive |

### Confirmation Format

```
todo> delete 1
Delete task 1 "Buy groceries"? [y/N]: y
Deleted task 1

todo> delete 1
Delete task 1 "Buy groceries"? [y/N]: n
Cancelled.

todo> clear
Clear 3 completed task(s)? [y/N]: y
Cleared 3 completed task(s)

todo> clear
No completed tasks to clear.
```

Rules:
- Default is No (safety)
- Accept: `y`, `Y`, `yes`, `YES`
- Reject: anything else (including empty)
- Show task title in delete confirmation for safety
- Show count in clear confirmation
- Skip confirmation if clear finds 0 tasks

### Bypass Flag (Optional Enhancement)

Consider adding `--force` or `-f` flag for scripting:
```
todo> delete 1 --force
Deleted task 1
```

Decision: Implement `--force` / `-f` for `delete` and `clear` to skip confirmation. Useful for scripted input or advanced users.

---

## 5) Error Handling

### Error Categories

| Error Type | Message Format | Shell Behavior |
|------------|---------------|----------------|
| Unknown command | `Unknown command: xyz. Type 'help' for options.` | Continue |
| Invalid ID format | `Error: 'abc' is not a valid task ID` | Continue |
| Task not found | `Error: Task with id 999 not found` | Continue |
| Validation error | `Error: Title cannot be empty` | Continue |
| Invalid option value | `Error: Invalid status 'xyz'. Use: all, open, done` | Continue |
| Parse error (quotes) | `Error: Invalid input - <shlex error>` | Continue |

All errors:
- Print to output (not stderr in interactive mode)
- Do NOT exit shell
- Return to prompt immediately

### Prompt Cancellation

During guided prompts, allow cancellation:
- Ctrl+C during prompt → print "Cancelled." and return to `todo>` prompt
- Ctrl+D (EOF) during prompt → print "Cancelled." and return to `todo>` prompt

---

## 6) Exit Behavior

### Exit Commands

| Input | Behavior |
|-------|----------|
| `quit` | Print "Goodbye!" and exit with code 0 |
| `exit` | Same as quit |
| `q` | Alias for quit |
| Ctrl+D | Print "\nGoodbye!" and exit with code 0 |
| Ctrl+C | Print "\nGoodbye!" and exit with code 0 |

### Exit Codes

| Scenario | Exit Code |
|----------|-----------|
| Normal exit (quit/exit/Ctrl+D/Ctrl+C) | 0 |
| Unexpected exception | 1 |

Note: In interactive mode, errors do NOT cause non-zero exit. Only the final exit matters.

---

## 7) Updated Help Text

```
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
```

---

## Summary of Decisions

1. **Guided prompts**: Only for `add` (no args) and `update <id>` (no flags)
2. **Aliases**: ls, l, a, rm, d, x, o, u, s, ?, q
3. **Conflicts**: Aliases are lowercase only, no conflicts with full commands
4. **List format**: Keep current table format
5. **Show format**: Vertical key-value layout
6. **Confirmations**: Required for `delete` and `clear` (with --force bypass)
7. **Errors**: All errors continue shell, no exit
8. **Exit**: quit/exit/q/Ctrl+C/Ctrl+D all exit cleanly with code 0

---

## Test Cases to Add

1. Alias resolution (ls → list, x → done, etc.)
2. Guided prompt for `add` with no args
3. Guided prompt for `update <id>` with no flags
4. Confirmation prompt for `delete` (y/n behavior)
5. Confirmation prompt for `clear` (y/n behavior)
6. `--force` flag bypasses confirmation
7. `show <id>` displays full task details
8. Cancellation during prompts (simulate Ctrl+C)
9. Empty input during guided prompts (accepts default)
