---
type: review
scope: Phase 2 (vault-sync.py, firmware-init.py) and Phase 3 (new-project.md, setup.ps1)
date: 2026-03-01
status: fixes-applied
reviewer: Claude (claude-sonnet-4-6)
---

# Phase 2 & Phase 3 Review Findings

Reviewed against the design spec in:
`obsidian-git/01 - Projects/firmware-project-template/03 - system-design.md`
`obsidian-git/01 - Projects/firmware-project-template/05 - corrective-actions-plan.md`

---

## Summary Table

| # | File | Severity | Issue | Fixed |
|---|---|---|---|---|
| 1 | `vault-sync.py` | Critical bug | Conflict state update causes vault to silently overwrite local on next startup | Yes |
| 2 | `vault-sync.py` | Minor | `save_state` called unconditionally including no-op skip cases | Yes |
| 3 | `firmware-init.py` | Issue | `__pycache__` and `*.pyc` copied into every new project via `copytree` | Yes |
| 4 | `firmware-init.py` | Uncertainty | `obsidian vault info=path` may not be a real CLI command — fallback to manual works | Not a code fix |
| 5 | `new-project.md` | Bug | `obsidian open path=` doubles "01 - Projects" prefix (already in `vault_project_path`) | Yes |
| 6 | `new-project.md` | Gap | No Obsidian running check before CLI calls (CA-25 / E6) | Yes |
| 7 | `new-project.md` | Minor | Post-completion instruction vague about starting vault-sync.py for Session 1 | Yes |

---

## Detailed Findings

---

### Finding 1 — vault-sync.py: Conflict state update causes data loss (CRITICAL)

**Location:** `vault-sync.py`, `sync_pair()`, conflict branch (~line 225)

**What happens:**
When a conflict is detected (both local and vault changed since last sync), the code saves the vault
version as a `.obsidian-{timestamp}.md` backup — correct. But it then updates the state record:

```python
state[rel_str] = {"checksum": local_cs, "last_sync": time.time()}
```

This records the local checksum as the new baseline. On the next startup reconciliation:
- `local_cs == state` → local appears **unchanged**
- `vault_cs != state` → vault appears **changed**
- Result: vault wins and **overwrites local silently**, destroying the user's local work.

**Fix:** Do not update `state[rel_str]` on conflict. Leave the state at the pre-conflict baseline
so the conflict is re-detected on every reconciliation until the user explicitly resolves it and
triggers a sync.

---

### Finding 2 — vault-sync.py: Unnecessary state writes on no-op (Minor)

**Location:** `vault-sync.py`, `sync_pair()`, final line

**What happens:**
`save_state(state, state_lock)` is called unconditionally at the end of every `sync_pair` call,
including the "no change / skip" branch where state was not modified. During a 20-file
reconciliation, the state JSON is written to disk 20 times even if nothing changed.

**Fix:** Remove the unconditional `save_state` from the bottom. Call it only inside the branches
that actually modify `state` (local wins and vault wins). The conflict branch does not call it
(per fix #1 above).

---

### Finding 3 — firmware-init.py: `__pycache__` copied into new projects (Issue)

**Location:** `firmware-init.py`, `main()`, Step 8 (`shutil.copytree`)

**What happens:**
Running `vault-sync.py` or `firmware-init.py` from the template directory generates a
`__pycache__/` folder. The `copytree` call only ignores `.git` and `CLAUDE.local.md`:

```python
shutil.copytree(
    template_dir, project_dir,
    ignore=shutil.ignore_patterns(".git", "CLAUDE.local.md"),
)
```

Python's `__pycache__/` and any `.pyc` files are copied into every new project.
The `.gitignore` correctly excludes them from git, but they end up in the project folder.

**Fix:** Add `"__pycache__"` and `"*.pyc"` to `ignore_patterns`.

---

### Finding 4 — firmware-init.py: `obsidian vault info=path` may not exist (Uncertainty)

**Location:** `firmware-init.py`, `detect_vault_path()`

**What happens:**
The design requires `obsidian vault info=path` for automatic vault detection. Obsidian does not
appear to ship a traditional CLI binary — it uses a URI handler (`obsidian://`) for external
integrations, not shell commands.

On machines where `obsidian` is not on PATH as a CLI tool, the `check_prereqs()` call will warn
about the missing obsidian CLI, and `detect_vault_path()` will fall back to manual path input.
The fallback is graceful and the script completes correctly.

**Status:** Not a code bug — the fallback works. Noted for documentation and future investigation.
If an Obsidian CLI ever becomes available, the code is ready. For now, manual vault input is the
real workflow.

---

### Finding 5 — new-project.md: `obsidian open` path doubles "01 - Projects" (Bug)

**Location:** `new-project.md`, Phase 3, Step 3.5

**What happens:**
The skill instructs:
```
obsidian open path="01 - Projects/{vault_project_path}/CLAUDE.md"
```

But `vault.project_path` in `VAULT-BLUEPRINT.md` is already the full path from the vault root:
```
01 - Projects/Eco-Twin/DemoSetup/Edge-Node/Sensor Reading/sensor-reading
```

This produces the broken path:
```
01 - Projects/01 - Projects/Eco-Twin/.../CLAUDE.md
```

**Fix:** Remove the hardcoded `"01 - Projects/"` prefix. Use:
```
obsidian open path="{vault_project_path}/CLAUDE.md"
```

---

### Finding 6 — new-project.md: No Obsidian running check before CLI calls (Gap)

**Location:** `new-project.md`, Phase 3, Step 3.5

**Spec reference:** CA-25 (E6) — "Before any `obsidian` CLI call, verify Obsidian is running."

**What happens:**
`obsidian open ...` is called without verifying Obsidian is running. If Obsidian is closed,
the command may fail silently or behave unexpectedly with no user-visible error.

**Fix:** Add an explicit check instruction before Step 3.5: verify Obsidian is running
(or instruct the user to open it), before calling `obsidian open`.

---

### Finding 7 — new-project.md: Vault-sync.py startup instruction too vague (Minor)

**Location:** `new-project.md`, Phase 3, Step 3.6

**What happens:**
The completion message says "Run /session-start at the beginning of each working session."
This does not make it clear that the user should run `/session-start` immediately now to
start continuous vault sync for the current Session 1.

Per CA-2 (C1): after `/new-project` completes, the watcher is not yet running. Session 1
proceeds with no sync unless the user knows to start it.

**Fix:** Change the instruction to say: "Run `/session-start` now to start continuous vault
sync for this session. Run it again at the start of every future session."

---

## What Is Correct

- `vault-sync.py` two-way sync architecture, three-way logic, debouncing, lockfile, startup
  reconciliation, and dual-observer structure are all correct and match the spec.
- `firmware-init.py` project name validation, collision detection, predecessor handling,
  vault folder creation, overview note logic, and VAULT-BLUEPRINT.md generation are all correct.
- `new-project.md` three-phase structure, design review interview content, review pause,
  and Phase 3 technical interview are all correct and match the spec.
- `setup.ps1` prerequisite checking, warning-not-abort behavior, and skill installation are correct.
- `.gitignore` correctly excludes all runtime files (`.vault-sync-state.json`, `.vault-sync.lock`,
  `*.obsidian-*.md`, `__pycache__/`, `CLAUDE.local.md`).
- `requirements.txt` is present with correct dependencies (`watchdog>=3.0.0`, `PyYAML>=6.0`).
