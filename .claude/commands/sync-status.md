# /sync-status — Check whether vault-sync.py is running

Check the vault-sync.py lockfile and report whether the sync process is active.

---

## Steps

### Step 1 — Read the lockfile

Check for `.vault-sync.lock` in the project root.

**If `.vault-sync.lock` does not exist:**
> "vault-sync.py is not running. Start it with /session-start, or run `python vault-sync.py` manually."

**If `.vault-sync.lock` exists:**
- Read the PID from the file.
- Check whether the process is still alive:
  ```
  # Unix / Git Bash
  kill -0 {pid}

  # PowerShell fallback
  Get-Process -Id {pid} -ErrorAction SilentlyContinue
  ```

**If the process is running:**
> "vault-sync.py is running (PID {pid}). Continuous sync is active."

**If the process is not running** (stale lockfile):
> "vault-sync.py is NOT running — stale lockfile found (PID {pid} no longer exists).
> The lockfile will be cleaned up automatically on next startup.
> To start vault-sync.py now: run /session-start or `python vault-sync.py`."

### Step 2 — Show last sync state (optional)

If `.vault-sync-state.json` exists, read it and report:
> "Last sync state: {n} file(s) tracked.
> Most recently synced: {filename} at {timestamp}."

If the state file does not exist:
> "No sync state found — vault-sync.py has not run a reconciliation yet."
