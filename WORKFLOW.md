# Firmware Development Workflow with Claude

How to work with Claude on a firmware project — from first-time machine setup through daily
development, knowledge capture, and continuing on a different computer.

---

## How This System Works

Three systems. Each owns distinct responsibilities. Connected by two mechanisms.

```
LOCAL PROJECT FOLDER                      OBSIDIAN VAULT
C:\Desktop\Projects\{project-name}\      obsidian-git\01 - Projects\{hierarchy}\
├── src/          ← code (VS Code)        ├── docs/
├── docs/         ← docs (synced) ──────► ├── Report/
├── Report/       ← reports (synced)      ├── lessonsLearned/
├── lessonsLearned/ ← learnings (synced)  └── CLAUDE.md
├── CLAUDE.md     ← agent briefing (synced)
└── CLAUDE.local.md ← machine config (NEVER synced)

vault-sync.py watches both sides in real time.
Edits in VS Code and Obsidian are both preserved.

          git push (code + docs)          Obsidian Sync (real-time, all 3 machines)
                   │                                    │
                   ▼                                    ▼
             GITHUB REPO                        OBSIDIAN VAULT
         Canonical for source code         Canonical for documentation
         and all project files             and knowledge notes (08 - Knowledge)
```

**Skills** are slash commands (`.claude/commands/*.md`) that encode the recurring workflows
so Claude executes them consistently without re-explanation every session.

| Skill | When to use |
|---|---|
| `/new-project` | Once — to create a new firmware project |
| `/session-start` | Every session — loads context, starts vault sync |
| `/session-end` | Every session — updates HANDOFF.md, promotes knowledge, commits |
| `/sync-vault` | On demand — force a one-shot sync to/from vault |
| `/promote` | On demand — promote a learning to 08 - Knowledge at any time |

---

## First-Time Machine Setup

Run this once on each machine before starting any project.

### Prerequisites

| Tool | Install |
|---|---|
| Python 3.10+ | https://python.org — tick "Add to PATH" during install |
| gh CLI | https://cli.github.com |
| Obsidian | https://obsidian.md |
| Claude Code CLI | `npm install -g @anthropic-ai/claude-code` |

### Setup steps

```powershell
# 1. Allow PowerShell scripts to run (required once per machine)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 2. Clone the template and global config repos
cd C:\Users\{you}\Desktop\Projects
git clone https://github.com/ounguder/firmware-project-template
git clone https://github.com/ounguder/claude-global-config

# 3. Run setup — installs Python deps, copies /new-project skill, checks prereqs
cd claude-global-config
.\setup.ps1

# 4. Authenticate gh CLI (if not already done)
gh auth login

# 5. Open Obsidian and let Obsidian Sync finish before starting any project
#    (vault docs arrive automatically — no manual steps)
```

`setup.ps1` checks Python, installs `watchdog` and `PyYAML`, verifies `gh` auth, and installs
the `/new-project` global skill into `~\.claude\commands\`.

### Windows path length (important)

The full vault path for a nested project can approach the Windows 260-character limit.
Enable long path support once per machine to avoid hard-to-diagnose errors:

```powershell
# Run as Administrator
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" `
    -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

Alternatively: Settings → System → For developers → Enable Win32 long paths.

---

## Starting a New Project

Open PowerShell in `C:\Desktop\Projects` and run:

```
claude
/new-project
```

The skill runs three phases automatically:

### Phase 1 — Initialization

Claude runs `firmware-init.py` which:
- Auto-detects your Obsidian vault path
- Collects: Main Project, Sub-Project, Component, Task, Project Name (kebab-case), Primary MCU / Board
- Asks whether this project builds on previous tasks (fills `predecessors:` in VAULT-BLUEPRINT.md)
- Copies the template to `C:\Desktop\Projects\{project-name}\`
- Creates the vault folder: `01 - Projects\{Main}\{Sub}\{Component}\{Task}\{project-name}\`
- Writes `VAULT-BLUEPRINT.md` with all fields filled
- Creates or updates `00 - overview.md` at the component level in the vault

Claude then sets up git and GitHub:
```
git init
gh repo create {project-name} --private --source=. --remote=origin --push
```

### Phase 2 — Design Review Interview

Claude interviews you across five areas before any technical document is written:
1. **Purpose and target** — what must this project achieve, what does "done" look like
2. **Available hardware** — boards, sensors, PCBs, power supply
3. **Software infrastructure** — existing MQTT broker, cloud backend, predecessor firmware
4. **Laboratory instruments** — oscilloscope, logic analyzer, debug probes
5. **Development ideas and constraints** — approaches considered, time/cost constraints, hard requirements

Claude also asks about open questions and unknowns.

After the interview, Claude proposes solution approaches with trade-offs and waits for you to
select a direction. Then it writes `docs/DESIGN-REVIEW.md`.

**Review pause:** Claude stops and asks you to read and confirm `docs/DESIGN-REVIEW.md`.
Phase 3 does not start until you reply "looks good".

### Phase 3 — Technical Kickoff

Claude reads `VAULT-BLUEPRINT.md` and `docs/DESIGN-REVIEW.md`, then interviews you on:
board and MCU details, pin assignments, peripheral config, sensors, protocol structure,
power architecture, build system, and testing approach.

Claude fills:
- `CLAUDE.md` — complete agent briefing
- `docs/FSD.md` — full system design (marked DRAFT with TODO markers)
- `docs/HARDWARE.md` — pin map, power architecture, external components (marked provisional if PCB not arrived)
- `docs/PROTOCOL.md` — wire format, frame structure, example payloads

Then runs `vault-sync.py --once` to push all filled docs to the vault, and opens VS Code.

**After /new-project completes:** run `/session-start` immediately to start continuous vault sync
for Session 1.

---

## Daily Session Workflow

### Starting a session

```
cd C:\Desktop\Projects\{project-name}
claude
/session-start
```

`/session-start` does the following automatically:

1. **CLAUDE.local.md check** — if missing on this machine, runs a short wizard (COM port, debug probe path, local env vars) and creates it. This file is gitignored and stays local.
2. **Loads context** — reads `CLAUDE.md`, `docs/HANDOFF.md`, `docs/DESIGN-REVIEW.md`, `VAULT-BLUEPRINT.md`
3. **Predecessor context** — if `predecessors:` is set in `VAULT-BLUEPRINT.md`, offers to load their HANDOFF.md and lessonsLearned/ for context
4. **Knowledge scan** — scans `08 - Knowledge` for notes matching the project's MCU, peripherals, and protocols; offers to load relevant ones into context
5. **Starts vault-sync.py** — checks the lockfile; if not already running, starts `vault-sync.py` in the background
6. **Session summary** — prints 5–10 lines: project name, board, GitHub, last session date, what works, what's in progress, next steps
7. Asks: *"What do you want to work on today?"*

### During the session

Work normally. Claude writes to the local project folder. `vault-sync.py` watches for changes
and mirrors documentation files to the vault automatically — no manual steps needed.

On demand:
- `/sync-vault` — force an immediate one-shot sync and see what was transferred
- `/promote` — capture a specific learning to 08 - Knowledge right now, without waiting for session end

### Ending a session

```
/session-end
```

`/session-end` does the following:

1. **Updates `docs/HANDOFF.md`** — fully rewrites it: what works, what's in progress, known issues, next steps, key files changed, context for the next session
2. **Knowledge promotion review** — reviews what was done and identifies reusable learnings; for each candidate:
   - Checks `08 - Knowledge` for a duplicate note first
   - If duplicate: offers to update its `used_in` field or create a separate note
   - If no duplicate: proposes the note with the correct subfolder and waits for approval
   - Writes approved notes directly to the vault with `used_in` wikilink
3. **Git commit** — runs `git status`; if there are changes, proposes a commit message and asks "Shall I commit and push? [yes/no]"; if yes, runs `git add`, `git commit`, `git push`; if nothing changed, skips silently

---

## Two-Way Vault Sync

`vault-sync.py` runs continuously in the background during each session. It watches both the
local project folder and the vault project subfolder and keeps them in sync.

**You can edit documentation in both VS Code and Obsidian. Both are valid editing surfaces.**

### How sync direction is decided

vault-sync.py maintains `.vault-sync-state.json` (gitignored) which records the SHA-256
checksum of each tracked file at the time of last sync. On every file change:

| Local | Vault | Since last sync | Action |
|---|---|---|---|
| Changed | Unchanged | — | Local → vault (copy, update state) |
| Unchanged | Changed | — | Vault → local (copy, update state) |
| Changed | Changed | — | **Conflict** — vault version saved as backup, alert printed |
| Unchanged | Unchanged | — | No action |

### What syncs and what does not

| Path | Synced | Reason |
|---|:---:|---|
| `docs/` | Yes | Project documentation |
| `Report/` | Yes | Claude-generated reports |
| `lessonsLearned/` | Yes | Bug post-mortems and session learnings |
| `CLAUDE.md` | Yes | Agent briefing |
| `VAULT-BLUEPRINT.md` | Yes | Sync contract — visible in vault for reference |
| `.claude/rules/` | Yes | Coding style, hardware rules, safety rules |
| `src/` | No | Source code — GitHub only |
| `include/` | No | Header files — GitHub only |
| `tests/` | No | Test code — GitHub only |
| `CLAUDE.local.md` | No | Machine-specific config — never leaves this machine |

### Conflict files

If both sides were edited since last sync, vault-sync.py does not pick a winner.
It saves the vault version alongside the local file:

```
docs/FSD.obsidian-20260301-1430.md   ← vault version at time of conflict
docs/FSD.md                          ← local version, untouched
```

A conflict alert is printed:
```
[CONFLICT] docs/FSD.md
           Both local and vault were edited since last sync.
           Vault version saved as: docs/FSD.obsidian-20260301-1430.md
           Merge manually, then run /sync-vault to resync.
```

**How to resolve a conflict:**
1. Open both `docs/FSD.md` (local) and `docs/FSD.obsidian-{timestamp}.md` (vault version)
2. Merge the content you want to keep into `docs/FSD.md`
3. Delete the `.obsidian-*.md` conflict file
4. Run `/sync-vault` — vault-sync.py copies the merged local version to the vault and updates state

The conflict re-appears on every reconciliation until resolved, so it is never silently forgotten.

### Running vault-sync.py manually

```powershell
# Continuous mode (started automatically by /session-start)
python vault-sync.py

# One-shot reconciliation (used by /sync-vault)
python vault-sync.py --once

# vault-sync.py must be run from the project root folder
cd C:\Desktop\Projects\{project-name}
python vault-sync.py
```

Only one instance per project is allowed. If you try to start a second instance, vault-sync.py
detects the existing lockfile and exits with a clear message.

---

## Continuing on a Different Machine

The vault already has the latest documentation via Obsidian Sync — nothing to do on that side.

```powershell
# 1. Clone the project from GitHub (code + docs)
cd C:\Desktop\Projects
git clone https://github.com/ounguder/{project-name}

# 2. Start a session (CLAUDE.local.md wizard runs automatically on first use)
cd {project-name}
claude
/session-start
```

`/session-start` detects that `CLAUDE.local.md` is missing, runs the wizard (COM port, debug probe
path, env vars), and creates it. Then loads full context from git-tracked files and starts vault-sync.

---

## Knowledge Promotion

Every session, Claude reviews what was discovered and identifies learnings worth keeping permanently
in `08 - Knowledge`. This happens automatically in `/session-end`, or you can run `/promote` at
any time during a session.

### Domain priority rule

When deciding where a note belongs, apply in order — highest match wins:

1. Specific to one MCU family → `11 - Microcontrollers/{family}/`
2. General firmware pattern (any MCU) → `10 - Firmware/`
3. Protocol-specific → `04 - Protocols/`
4. Hardware phenomenon (electrical, physical) → `09 - Hardware/`
5. Domain science → `14 - Agriculture/`, `12 - RF Engineering/`, `15 - Signal Processing/`, etc.

If the learning applies at two levels, notes are created at both with cross-links.

### Duplicate detection

Before creating any note, Claude checks the target folder for existing notes on the same topic:
- **Duplicate found:** offers to add the current project to the existing note's `used_in` field (no new file), create a separate note, or skip
- **No duplicate:** proposes creation and waits for approval

### Traceability (`used_in`)

Every promoted note contains a `used_in` field linking back to the project where the knowledge
was earned:

```yaml
used_in:
  - "[[01 - Projects/Eco-Twin/DemoSetup/Edge-Node/Sensor Reading/sensor-reading/CLAUDE]]"
```

This is a clickable Obsidian wikilink. In graph view: knowledge node → project node → session → commit.

---

## Quick Reference

| Situation | Command |
|---|---|
| First-time machine setup | Clone repos, run `setup.ps1`, `gh auth login` |
| New project | `claude` → `/new-project` |
| Start every session | `claude` → `/session-start` |
| End every session | `/session-end` |
| Force sync docs to vault | `/sync-vault` |
| Promote a learning now | `/promote` |
| Check what's in progress | "Read HANDOFF.md and summarise next steps" |
| Resolve a conflict | Merge manually → delete `.obsidian-*.md` file → `/sync-vault` |
| Continue on another machine | `git clone` + `claude` + `/session-start` |

---

## File Ownership Summary

| File | Written by | Updated when |
|---|---|---|
| `CLAUDE.md` | Claude — Phase 3 of /new-project | Hardware or toolchain changes |
| `CLAUDE.local.md` | **You** (wizard via /session-start) | Once per machine |
| `VAULT-BLUEPRINT.md` | Claude — Phase 1 of /new-project | Never (read-only after init) |
| `.claude/rules/coding-style.md` | Claude — Phase 3 | Conventions change |
| `.claude/rules/hardware.md` | Claude — Phase 3 | Peripheral assignments change |
| `.claude/rules/safety.md` | Claude — Phase 3 | Safety requirements change |
| `docs/DESIGN-REVIEW.md` | Claude — Phase 2 of /new-project | If requirements change |
| `docs/FSD.md` | Claude — Phase 3 | New requirements added |
| `docs/HARDWARE.md` | Claude — Phase 3 | Hardware revision changes |
| `docs/PROTOCOL.md` | Claude — Phase 3 | Frame format changes |
| `docs/BRING-UP.md` | Claude — as built | Bring-up procedure changes |
| `docs/DEBUGGING.md` | Claude — ongoing | Every bug or errata discovered |
| `docs/HANDOFF.md` | Claude — /session-end | Every session |
| `Report/` | Claude — on demand | Reports, measurements, analyses |
| `lessonsLearned/` | Claude — on demand | Bug post-mortems, session learnings |
| `.vault-sync-state.json` | vault-sync.py | Automatically (gitignored) |
| `.vault-sync.lock` | vault-sync.py | Automatically (gitignored) |
