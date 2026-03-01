# /sync-vault — On-demand vault sync

Run a one-shot reconciliation between the local project folder and the Obsidian vault.
Invoke any time you want to manually push or pull documentation changes.

---

## Steps

### Step 1 — Verify working directory

Confirm you are running from the project root (where `VAULT-BLUEPRINT.md` lives).
If not, stop and say:
> "Run /sync-vault from the project root folder (e.g., `cd C:\Desktop\Projects\{project-name}`)."

### Step 2 — Run one-shot sync

```
python vault-sync.py --once
```

### Step 3 — Report results

Read the output and summarize what happened:
- List each file that was synced (local → vault or vault → local)
- List any conflicts detected and the names of the backup files created
- Confirm total files processed

If no files changed: "Vault is already up to date — no files needed syncing."

If conflicts were detected, remind the user:
> "Conflict files are saved as `{filename}.obsidian-{timestamp}.md` alongside the original.
> Merge manually, then run /sync-vault again to clear the conflict."
