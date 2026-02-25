---
# VAULT BLUEPRINT — read by sync automation tools
# Edit the hierarchy section to match where this project sits in your Obsidian vault.
# The script will build the full destination path by joining base_folder + hierarchy.
# If any folder in the path does not exist in the vault, the script will create it.

vault:
  base_folder: "01 - Projects"
  hierarchy:
    - "[Main Project]"          # e.g. EcoTwin
    - "[Sub-Project]"           # e.g. Demo Setup       — remove if not needed
    - "[Sub-Sub-Project]"       # e.g. Testing          — remove if not needed
    - "[This Repository Name]"  # e.g. iot-backend      — should match the repo folder name

sync:
  - source_folder: "Report"
    vault_folder: "Report"
    include: "*.md"
    exclude_patterns:
      - "*.local.md"

  - source_folder: "lessonsLearned"
    vault_folder: "Lessons Learned"
    include: "*.md"
    exclude_patterns:
      - "*.local.md"
---

# Vault Blueprint — [PROJECT NAME]

This file tells automation scripts where to copy project documents into the Obsidian vault.
It is machine-readable (YAML frontmatter) and human-readable (this section).

---

## How It Works

A sync script reads the YAML frontmatter above and:

1. Builds the destination path in the vault:
   ```
   {vault_root} / {base_folder} / {hierarchy[0]} / {hierarchy[1]} / ... / {source_folder}
   ```

2. Creates any missing folders along the path.

3. Copies all `.md` files from each `source_folder` into the corresponding `vault_folder`,
   skipping files that match `exclude_patterns`.

**Example:** with the hierarchy `EcoTwin → Demo Setup → Testing → iot-backend`,
a file at `Report/test-results-2025-03.md` in this project would be copied to:
```
{vault_root}/01 - Projects/EcoTwin/Demo Setup/Testing/iot-backend/Report/test-results-2025-03.md
```

---

## How to Fill In the Hierarchy

- Set `hierarchy` to match the exact folder names in your Obsidian vault
- Remove levels that do not apply (e.g. if this is a top-level project with no parent, keep only one level)
- The last entry should be this repository's name
- Folder names must match exactly — the script does not fuzzy-match

**1-level (standalone project):**
```yaml
hierarchy:
  - "iot-backend"
```

**2-level (project → repo):**
```yaml
hierarchy:
  - "EcoTwin"
  - "iot-backend"
```

**4-level (main → sub → phase → repo):**
```yaml
hierarchy:
  - "EcoTwin"
  - "Demo Setup"
  - "Testing"
  - "iot-backend"
```

---

## Sync Folders

| Source (project folder) | Destination (vault subfolder) | What goes here |
|------------------------|------------------------------|----------------|
| `Report/`              | `Report/`                    | Technical reports, test results, architecture summaries |
| `lessonsLearned/`      | `Lessons Learned/`           | Post-mortems, retrospectives, bug analyses |

To add more folders to the sync, add entries under `sync:` in the frontmatter.

---

## Machine-Readable Fields Reference

| Field | Type | Description |
|-------|------|-------------|
| `vault.base_folder` | string | Top-level folder in the Obsidian vault where all projects live |
| `vault.hierarchy` | list of strings | Ordered folder names from root to this project |
| `sync[].source_folder` | string | Folder in this project repo to copy from |
| `sync[].vault_folder` | string | Subfolder name to create under the project path in the vault |
| `sync[].include` | glob string | File pattern to copy (typically `*.md`) |
| `sync[].exclude_patterns` | list of globs | Files to skip (machine-specific or secret files) |
