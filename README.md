# Firmware Project Template

A blank project template for embedded firmware development with Claude AI agents.
Start a new firmware project using `/new-project` — Claude interviews you, initializes
the project folder, sets up the GitHub repo, and fills all documentation in one automated flow.

## Prerequisites

| Tool | Install |
|---|---|
| Python 3.10+ | https://python.org — tick "Add to PATH" |
| gh CLI | https://cli.github.com |
| Obsidian | https://obsidian.md |
| Claude Code CLI | `npm install -g @anthropic-ai/claude-code` |

## How to Use

### First-time machine setup (run once)

```powershell
cd C:\Users\{you}\Desktop\Projects
git clone https://github.com/ounguder/firmware-project-template
git clone https://github.com/ounguder/claude-global-config
cd claude-global-config
.\setup.ps1        # installs Python deps, copies /new-project skill, checks prereqs
gh auth login      # if not already done
```

### Starting a new project

```
cd C:\Users\{you}\Desktop\Projects
claude
/new-project
```

`/new-project` runs three phases automatically:
1. **Phase 1** — runs `firmware-init.py`: detects vault path, collects metadata (project name, MCU, hierarchy), copies template, creates vault folder, writes `VAULT-BLUEPRINT.md`, then `git init` + `gh repo create`
2. **Phase 2** — Design Review Interview: purpose, hardware, software infrastructure, instruments, constraints → writes `docs/DESIGN-REVIEW.md` → **review pause** (you confirm before Phase 3)
3. **Phase 3** — Technical Kickoff: fills `CLAUDE.md`, `docs/FSD.md`, `docs/HARDWARE.md`, `docs/PROTOCOL.md` → runs `vault-sync.py --once` → opens VS Code

### Daily session workflow

```
cd C:\Users\{you}\Desktop\Projects\{project-name}
claude
/session-start    ← loads context, starts vault sync, summarises status
... work ...
/session-end      ← updates HANDOFF.md, promotes learnings to vault, commits + pushes
```

## What's Included

```
├── CLAUDE.md                   ← agent briefing (filled by Claude in /new-project)
├── CLAUDE.local.md             ← your machine config (never committed, wizard via /session-start)
├── VAULT-BLUEPRINT.md          ← sync contract: local project ↔ Obsidian vault
├── WORKFLOW.md                 ← complete workflow guide
├── TEMPLATE-GUIDE.md           ← file-by-file reference
├── vault-sync.py               ← two-way file sync (local ↔ vault, continuous or --once)
├── firmware-init.py            ← project initialization script (run via /new-project)
├── requirements.txt            ← Python deps: watchdog, PyYAML
├── .claude/
│   ├── rules/
│   │   ├── coding-style.md     ← C/C++ naming, file structure, error handling
│   │   ├── hardware.md         ← peripheral ownership, power domains, timing
│   │   └── safety.md           ← NEVER/ALWAYS rules, watchdog policy
│   └── commands/
│       ├── session-start.md    ← /session-start skill
│       ├── session-end.md      ← /session-end skill
│       ├── sync-vault.md       ← /sync-vault skill
│       ├── promote.md          ← /promote skill
│       └── sync-status.md      ← /sync-status skill
├── docs/
│   ├── DESIGN-REVIEW.md        ← purpose, approach, acceptance criteria (Phase 2)
│   ├── FSD.md                  ← full system design and requirements
│   ├── HARDWARE.md             ← pin map, power architecture, errata
│   ├── PROTOCOL.md             ← communication frame specs
│   ├── BRING-UP.md             ← flash and bring-up procedure
│   ├── DEBUGGING.md            ← known issues, errata, debug procedures
│   └── HANDOFF.md              ← session status (updated every /session-end)
├── Report/                     ← Claude-generated reports (synced to Obsidian)
├── lessonsLearned/             ← post-mortems and retrospectives (synced to Obsidian)
├── src/
├── include/
└── tests/
```

## How It Works

```
LOCAL PROJECT FOLDER                      OBSIDIAN VAULT
C:\Desktop\Projects\{project-name}\      obsidian-git\01 - Projects\{hierarchy}\
├── src/          ← code (VS Code)        ├── docs/
├── docs/         ← docs (synced) ──────► ├── Report/
├── Report/       ← reports (synced)      ├── lessonsLearned/
├── lessonsLearned/ ← learnings (synced)  └── CLAUDE.md
└── CLAUDE.md     ← agent briefing (synced)

vault-sync.py watches both sides in real time.
Edits in VS Code and Obsidian are both preserved (two-way sync with conflict detection).

          git push (code + docs)          Obsidian Sync (real-time, all machines)
                   │                                    │
                   ▼                                    ▼
             GITHUB REPO                        OBSIDIAN VAULT
         Canonical for source code         Canonical for documentation
```

## Related Repositories

| Repo | Purpose |
|------|---------|
| [firmware-project-template-ci](https://github.com/ounguder/firmware-project-template-ci) | Living master template — continuously improved over time |
| [firmware-project-template-example](https://github.com/ounguder/firmware-project-template-example) | Fully filled reference based on an imaginary IoT project |
| [claude-global-config](https://github.com/ounguder/claude-global-config) | Global Claude skills including /new-project and setup.ps1 |
