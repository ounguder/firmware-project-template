---
# VAULT-BLUEPRINT.md
# Contract between the local project folder and the Obsidian vault.
# Written once at project initialization by firmware-init.py.
# Read by vault-sync.py on every startup.
# Read by Claude at every session start.
# Do not edit vault.root or vault.project_path manually — they are auto-detected.

project:
  name: "[project-name]"                    # kebab-case, matches folder and GitHub repo name
  main_project: "[Main Project]"            # e.g. Eco-Twin
  sub_project: "[Sub-Project]"              # e.g. DemoSetup — remove line if not applicable
  component: "[System Component]"           # e.g. Edge-Node
  task: "[Task Name]"                       # e.g. Sensor Reading
  primary_board: "[Primary MCU / Board]"    # e.g. Heltec LoRa32 V3 (ESP32-S3)
  github_repo: "https://github.com/[user]/[project-name]"

vault:
  root: "[auto-filled by firmware-init.py via: obsidian vault info=path]"
  project_path: "01 - Projects/[Main Project]/[Sub-Project]/[Component]/[Task]/[project-name]"

sync:
  include:
    - docs/
    - Report/
    - lessonsLearned/
    - CLAUDE.md
    - VAULT-BLUEPRINT.md
    - .claude/rules/
  exclude:
    - src/
    - include/
    - tests/
    - CLAUDE.local.md
    - .vault-sync-state.json
    - "*.obsidian-*.md"

# predecessors — optional, only present when this project builds on previous tasks.
# Filled by firmware-init.py if you answer "yes" to the predecessor question.
# Used by /session-start to offer loading predecessor HANDOFF.md and lessonsLearned/.
#
# predecessors:
#   - name: sensor-reading
#     vault_path: "01 - Projects/Eco-Twin/DemoSetup/Edge-Node/Sensor Reading/sensor-reading"
#     github_repo: https://github.com/[user]/sensor-reading
---

# Vault Blueprint — [PROJECT NAME]

This file is the contract between the local project folder and the Obsidian vault.
It is machine-readable (YAML frontmatter above) and human-readable (this section).

---

## How vault-sync.py Uses This File

On startup, `vault-sync.py` reads `vault.root` and `vault.project_path` to locate both sides of the sync. It then:

1. Runs a startup reconciliation pass — compares every tracked file against `.vault-sync-state.json`
2. Begins watching both directories using the whitelist in `sync.include`
3. On any file change: applies three-way logic to determine sync direction

**Sync directions:**
- Local file changed, vault unchanged → copies local → vault
- Vault file changed, local unchanged → copies vault → local
- Both changed since last sync → saves vault version as `{file}.obsidian-{timestamp}.md`, alerts you

You can safely edit documentation in both VS Code and Obsidian. Conflicts are never silently discarded.

---

## What Syncs and What Does Not

| Path | Synced? | Reason |
|---|---|---|
| `docs/` | Yes | Project documentation |
| `Report/` | Yes | Claude-generated technical reports |
| `lessonsLearned/` | Yes | Bug post-mortems and session learnings |
| `CLAUDE.md` | Yes | Agent briefing — Claude reads this every session |
| `VAULT-BLUEPRINT.md` | Yes | This file — visible in vault for reference |
| `.claude/rules/` | Yes | Coding style, hardware rules, safety rules |
| `src/` | No | Source code — GitHub only, not vault |
| `include/` | No | Header files — GitHub only |
| `tests/` | No | Test code — GitHub only |
| `CLAUDE.local.md` | No | Machine-specific config — never leaves this machine |
| `.vault-sync-state.json` | No | Runtime state — gitignored and never synced |
| `*.obsidian-*.md` | No | Conflict backup files — resolve manually |

---

## Predecessor Projects

If this project builds on previous tasks (e.g. `sensor-data-tx` builds on `sensor-reading`),
the `predecessors:` field lists them. `/session-start` reads this field and offers to load
predecessor context (HANDOFF.md, lessonsLearned/) at the start of each session.

To add predecessors, uncomment and fill the `predecessors:` block in the frontmatter above.

---

## Vault Path Example

With the values above, a file at `docs/FSD.md` in this project maps to:
```
{vault.root}/{vault.project_path}/docs/FSD.md
```
For example:
```
C:\Users\ungud\...\obsidian-git\01 - Projects\Eco-Twin\DemoSetup\Edge-Node\Sensor Reading\sensor-reading\docs\FSD.md
```
