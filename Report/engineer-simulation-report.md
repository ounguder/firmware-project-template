---
type: simulation-report
date: 2026-03-01
author: Claude (claude-sonnet-4-6) — senior embedded engineer persona
project: firmware-project-template
---

# Engineer Simulation Report — First-Time User Experience

**Persona:** Senior embedded systems engineer (8 years, STM32/ESP32/SAMD, PlatformIO, KiCAD).
No prior knowledge of this template. Discovered it on GitHub.
**Simulated project:** LoRaWAN soil moisture node — Adafruit Feather M0 LoRa (SAMD21),
capacitive soil moisture sensor (ADC), DHT22 (GPIO), LIS3DH accelerometer (I2C).
No Obsidian vault on machine 1. Vault present on machine 2.

---

## Simulation Narrative

---

### Step 1 — GitHub discovery. Read README.

Engineer reads README.md on GitHub. Finds a clear promise: *"Claude fills the docs from an
interview."* Sounds useful. The "How to Use" section says:

```
1. git clone ... my-project
2. Fill CLAUDE.local.md
3. claude → "Let's set up a new firmware project. Interview me and fill the docs."
```

**Engineer follows these instructions exactly.**

---

### Step 2 — Clone and attempt to use

```powershell
git clone https://github.com/ounguder/firmware-project-template.git soil-monitor
cd soil-monitor
claude
```

Engineer types: *"Let's set up a new firmware project. Interview me and fill the docs."*

Claude reads CLAUDE.md (blank template), HANDOFF.md (blank). Claude is helpful but
generic — it has no structure for the interview. It fills some docs partially but:

- `/new-project`, `/session-start`, `/session-end` are visible as project-level skills
- Claude tries to use them but `VAULT-BLUEPRINT.md` has placeholder values
- vault-sync.py crashes immediately: `vault.root` = `"[auto-filled by firmware-init.py...]"`

**BLOCKER F1:** README describes a completely different, older workflow. Following it leads
the engineer into a broken state — stubs unfilled, vault sync broken, no project hierarchy.

---

### Step 3 — Engineer reads WORKFLOW.md

Notices the real workflow is in WORKFLOW.md, not README. Reads it. Now understands the
correct entry point: clone `claude-global-config`, run `setup.ps1`, then run `/new-project`
from the Projects directory.

**But also reads TEMPLATE-GUIDE.md** (listed prominently in README's "What's Included"):

```
## Workflow: Starting a New Project
1. Copy this template folder: cp -r firmware-project-template my-new-project
2. Replace all [PROJECT NAME], [MCU], and [placeholder] markers
3. Create CLAUDE.local.md ...
```

**BLOCKER F2:** TEMPLATE-GUIDE.md describes the same old workflow as README.md. Now the
engineer has three contradicting instruction sets. They cannot tell which one is authoritative.

---

### Step 4 — Follow WORKFLOW.md. Machine setup.

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
git clone https://github.com/ounguder/claude-global-config
cd claude-global-config
.\setup.ps1
```

`setup.ps1` output:
```
[OK] Python: Python 3.11.4
Installing Python dependencies from firmware-project-template...
[OK] Python dependencies installed (watchdog, PyYAML).
[OK] gh CLI found: C:\...\gh.exe
[OK] gh CLI authenticated.
[!!] obsidian CLI not found. Ensure Obsidian is installed and its directory is on your PATH.

Installed with warnings:
[!!] obsidian CLI not found. ...

Global Claude skills installed.
Available commands: /new-project
```

Warning about obsidian is clearly non-fatal here. Engineer proceeds.

---

### Step 5 — Run /new-project. Phase 1: firmware-init.py

```
cd C:\Users\ungud\Desktop\Projects
claude
/new-project
```

Claude runs pre-flight checks. Finds `firmware-project-template\firmware-init.py`. Good.
Checks `gh auth status` — authenticated. Proceeds to run `firmware-init.py`.

```
═══════════════════════════════════════════════
  firmware-init.py — New Project Initialization
═══════════════════════════════════════════════

ERROR: Prerequisites not met:

  • Obsidian CLI not found.
      Ensure Obsidian is installed and `obsidian` is on your PATH.
      On Windows, Obsidian CLI is available in the Obsidian install directory.
```

**BLOCKER F3 — Critical:** `check_prereqs()` calls `sys.exit(1)` when obsidian is not on PATH.
The entire `firmware-init.py` terminates. `/new-project` Phase 1 cannot complete.

The engineer has Obsidian installed but it is not in PATH — the Obsidian desktop app on Windows
does not ship as a CLI command. `obsidian` is never on PATH by default. This means
**firmware-init.py fails for the majority of users on first run.**

`detect_vault_path()` already has a fallback to manual input. The obsidian check should be a
warning — allow the engineer to proceed and enter the vault path manually.

Engineer attempts workaround: adds `C:\Users\ungud\AppData\Local\Obsidian` to PATH so that
`obsidian.exe` is findable. Re-runs firmware-init.py. check_prereqs() passes this time.

But then `detect_vault_path()` runs:
```python
result = subprocess.run(["obsidian", "vault", "info=path"], ...)
```

The Obsidian desktop app receives this command and does nothing useful — it might open the app
or silently ignore the unknown arguments. Output is empty. Auto-detection fails. Falls back to
manual input. Engineer types the vault path manually.

**F4 (Minor):** `obsidian vault info=path` is not a real Obsidian CLI command. The auto-detection
never works in practice. The fallback is reliable but the obsidian CLI check in `check_prereqs()`
is blocking users for a feature that doesn't actually work.

---

### Step 6 — firmware-init.py continues. Vault path entered.

Engineer enters the vault path. firmware-init.py proceeds:
- Collects metadata (Main Project: SoilMonitor, Component: SensorNode, etc.)
- Validates project name `soil-monitor` — passes
- No GitHub repo collision — proceeds
- Asks about predecessors — engineer says no
- Copies template to `C:\Desktop\Projects\soil-monitor\`

**F5 (Minor):** Engineer notices `firmware-init.py` is present in the new project folder.
No comment or README explains why it is there. The engineer might accidentally run it from
inside the new project, re-triggering initialization. The script's docstring says
"Do not run directly unless you know what you're doing" but that warning is only visible
if you open the file.

- Creates vault folder hierarchy in Obsidian vault
- Writes `VAULT-BLUEPRINT.md` — all fields filled
- Creates `00 - overview.md` at component level

---

### Step 7 — Phase 1: git setup

```
git init
git add .
git commit -m "feat: initial project setup from firmware-project-template"
gh repo create soil-monitor --private --source=. --remote=origin --push
```

Engineer notices `git add .` stages `firmware-init.py`, `vault-sync.py`, and `__pycache__/`.
Wait — `__pycache__/` was excluded from copytree (fixed in Phase 2 review). Confirmed: not staged.

But `firmware-init.py` IS committed to the new project. It serves no purpose there after
initialization. No warning is given.

---

### Step 8 — Phase 2: Design Review Interview

Goes smoothly. Claude asks structured questions across all five areas. Engineer provides:
- Purpose: read soil moisture + temp + tilt and transmit via LoRaWAN
- Hardware: Feather M0 LoRa, capacitive sensor, DHT22, LIS3DH, USB power initially
- Software: PlatformIO installed, Arduino framework + LMIC library
- Lab: only multimeter and USB serial adapter
- Constraints: must run on 3.7V LiPo, sleep mode required, 256KB flash limit

Claude proposes two approaches:
1. Interrupt-driven + deep sleep (complex but optimal power)
2. Polling loop + light sleep (simpler, adequate power)

Engineer selects approach 1. Claude writes `docs/DESIGN-REVIEW.md`.

**Review pause works correctly.** Claude stops and asks for confirmation. Engineer reads the
file, spots a mistake — Claude wrote "SPI interface" for DHT22 (DHT22 is 1-Wire). Engineer
corrects Claude. Claude updates the file. Engineer approves. Phase 3 begins.

---

### Step 9 — Phase 3: Technical Kickoff

Claude asks detailed technical questions. Engineer provides pin assignments for SAMD21
Feather M0. Claude fills:
- `CLAUDE.md` — complete
- `docs/FSD.md` — marked DRAFT, TODO markers on sections needing clarification
- `docs/HARDWARE.md` — marked `board_status: provisional` (no custom PCB yet)
- `docs/PROTOCOL.md` — placeholder (LoRaWAN payload format TBD)

**F6 (Minor):** Claude runs `vault-sync.py --once`. Several files sync to vault. Output is printed
but engineer has to read raw script output — no summary from Claude about what was synced and
whether anything was skipped or failed.

Phase 3 ends. Claude says: *"Run /session-start now to start continuous vault sync."*

**F7 (Gap):** This instruction appears in the terminal, which the engineer may not be watching
carefully after a long interview. If they miss it and start coding without /session-start, no
documentation changes will reach the vault until the next session.

---

### Step 10 — /session-start

```
/session-start
```

**Step 1 — CLAUDE.local.md wizard:**
`CLAUDE.local.md` doesn't exist (excluded from copytree by design). Wizard runs. Engineer
enters: COM3, `C:\Program Files\Segger\JLink\JLink.exe`. File created. Good.

**Step 2 — Context load:**
Reads CLAUDE.md, HANDOFF.md, DESIGN-REVIEW.md, VAULT-BLUEPRINT.md. Gives a clear summary. Good.

**Step 3 — Predecessors:** None. Skipped.

**Step 4 — 08-Knowledge scan:**
Engineer doesn't have an organized 08-Knowledge structure yet. Claude scans, finds nothing,
skips silently. Good.

**Step 5 — vault-sync.py start:**
Claude starts `python vault-sync.py` in background.

**F8 (Issue):** The background process is started by Claude via a Bash tool call. The engineer
has no visibility into its PID and no documented way to stop it gracefully. If the engineer
closes the terminal or the session, the background process may persist. There is no `/session-end`
step that stops vault-sync.py. The lockfile prevents duplicate instances on next session-start,
but the old process may still be running.

---

### Step 11 — Active development session

Engineer writes `src/sensor_adc.c`. Claude helps.

**F9 (Issue — session-end ambiguity):** At the end of the session, engineer runs `/session-end`.

Step 3 says: *"run `git add` for specific files only (list files explicitly)"*

But what does "specific files" mean? The skill doesn't list which file categories to include.
Claude interprets this conservatively and stages only documentation files (docs/, CLAUDE.md, etc.)
matching the vault-sync whitelist. `src/sensor_adc.c` is NOT staged.

Result: the code written this session is **not committed.** The engineer doesn't notice because
the commit message and hash look normal. On Machine 2 the next day, `git pull` gives nothing new
in `src/`.

**This is a significant workflow gap.** `/session-end` must commit ALL modified git-tracked files,
not just the documentation subset.

---

### Step 12 — Edge Case: File rename in VS Code

Engineer refactors `docs/FSD.md` → `docs/SYSTEM-DESIGN.md` using VS Code rename.

vault-sync.py behavior:
- Old file `docs/FSD.md` deleted locally → **deletion not propagated** (by design)
- New file `docs/SYSTEM-DESIGN.md` created locally → synced to vault

Result: vault now has BOTH `docs/FSD.md` (stale) AND `docs/SYSTEM-DESIGN.md` (current).

**F10 (Issue):** File renames appear as a create in vault and leave the old file orphaned.
Over months of development, the vault accumulates stale documentation files. CLAUDE.md and
skills that reference the old filename will work locally but point to a missing file in the vault.

There is no documented warning about this behavior and no manual cleanup procedure.

---

### Step 13 — Edge Case: Machine 2 continuation

Next day, engineer sits at a second machine (office desktop). Follows WORKFLOW.md:

```powershell
# setup.ps1 already run on this machine during previous project
git clone https://github.com/ounguder/soil-monitor
cd soil-monitor
claude
/session-start
```

/session-start detects missing CLAUDE.local.md. Wizard runs — engineer enters COM7 (different
port on this machine). Good — wizard works as designed.

Vault has latest docs (Obsidian Sync delivered them automatically). vault-sync.py startup
reconciliation detects no differences (vault matches local git checkout). Correct.

**F11 (Minor):** The engineer notices that vault-sync.py is running but isn't sure if the
background process was started by Claude Code or is a separate terminal process. There is
no status command like `/sync-status` to check vault-sync.py state or confirm it's running.

---

### Step 14 — Edge Case: /promote with domain ambiguity

Engineer discovers that the SAMD21 ADC on the Feather M0 loses accuracy when WiFi or BLE
is active (though SAMD21 doesn't have WiFi — but the LIS3DH SPI clock causes ADC noise
on shared ground). Wants to promote this as a knowledge note.

`/promote` runs. Domain priority rule applied:

1. MCU-specific (SAMD21 ADC) → `11 - Microcontrollers/SAMD21/`
2. Also general hardware phenomenon (SPI noise on ADC ground) → `09 - Hardware/`

Claude correctly proposes notes at both levels with cross-links. **Works as designed.**

But engineer has no `11 - Microcontrollers/SAMD21/` folder in their vault yet.
Claude writes the file anyway (creates the folder). **Correct behavior.**

---

### Step 15 — Edge Case: Long vault path warning

The engineer's full vault path for a nested note:
```
C:\Users\engineer_name\Documents\ObsidianVault\01 - Projects\SoilMonitor\SensorNode\
Sensor Reading\soil-monitor\lessonsLearned\samd21-adc-spi-noise.md
```
= ~170 characters. Safe for now, but with a longer username or deeper sub-project hierarchy
it would approach 260. No warning is given when path length is close to the limit.

---

## Findings Summary

| # | Severity | Component | Finding |
|---|---|---|---|
| F1 | **Critical** | `README.md` | Describes old workflow (clone → fill manually → claude). Contradicts WORKFLOW.md entirely. First thing engineers see on GitHub. |
| F2 | **Critical** | `TEMPLATE-GUIDE.md` | "Workflow" section at bottom describes the old workflow. Second contradiction. |
| F3 | **Critical** | `firmware-init.py` | `check_prereqs()` exits hard if `obsidian` not on PATH. Blocks all users. Obsidian desktop is not a CLI tool — `obsidian` is almost never on PATH. |
| F4 | Major | `firmware-init.py` | `obsidian vault info=path` is not a real command. Auto-detection never works. The obsidian CLI check in `check_prereqs()` blocks users for a feature that doesn't function. |
| F5 | Major | `/session-end` | Does not commit `src/`, `include/`, `tests/`. Only documentation files are staged. Code written during a session is silently left uncommitted. |
| F6 | Major | `vault-sync.py` | File renames/deletes locally leave orphaned stale files in vault. No cleanup mechanism, no documented warning. |
| F7 | Major | `TEMPLATE-GUIDE.md` | Full document describes old workflow; no mention of vault-sync, /new-project, /session-start. Should be updated or replaced. |
| F8 | Minor | `/new-project` | Post-Phase-3 instruction to run `/session-start` may be missed in terminal output after a long 3-phase interview. |
| F9 | Minor | `firmware-init.py` | Copies `firmware-init.py` itself into every new project with no explanation. Engineers may accidentally re-run it or be confused by its presence. |
| F10 | Minor | `/session-start` | vault-sync.py started in background with no PID reported. No documented stop procedure. No `/sync-status` command to check if it is running. |
| F11 | Minor | `WORKFLOW.md` | Windows long path warning is present but no guidance on what to do if a project path is already too long. |
| F12 | Minor | `/session-start` | 08-Knowledge scan unbounded on large vaults. Could be slow with 1000+ notes. No timeout or limit specified. |

---

## What Works Well

- **Three-phase /new-project flow** — the separation of Design Review from Technical Kickoff
  is excellent. Prevents misunderstood requirements from propagating into all documents.
- **Review pause** — Claude stopping after DESIGN-REVIEW.md and waiting for explicit approval
  before Phase 3 caught a real error (DHT22 interface mis-identified) in the simulation.
- **CLAUDE.local.md wizard** — runs automatically on machine 2, no manual steps needed. Correct.
- **Three-way sync logic** — conflict detection and backup files are solid. State-based approach
  is correct. No silent data loss.
- **Predecessor context loading** — well-specified. Engineers building `task-3` on top of `task-1`
  and `task-2` have a clear mechanism to load that context.
- **Knowledge promotion with domain priority rule** — works correctly for ambiguous learnings.
  Proposing notes at multiple levels with cross-links is the right approach.
- **Board status: provisional** — marking HARDWARE.md as provisional when PCB hasn't arrived
  is a small but important feature that prevents false confidence in pin assignments.

---

## Action Plan

### Priority 1 — Blockers (fix before any user can succeed)

**AP-1: Rewrite README.md**
Replace the old 3-step workflow with the current one. Minimum content:
- What this template does (one paragraph)
- Prerequisites (Python, gh CLI, Obsidian, Claude Code)
- One-time machine setup: clone both repos + setup.ps1
- Starting a project: `claude` → `/new-project`
- Point to WORKFLOW.md for the full guide
- Remove the old "git clone as project" instructions entirely

**AP-2: Fix firmware-init.py obsidian check — warning, not exit**
Change `check_prereqs()` to treat missing obsidian CLI as a warning, not a fatal error.
Print: *"obsidian CLI not found — vault path will be entered manually."*
Do not add to the `errors` list. Allow the script to continue to `detect_vault_path()`
which already handles this with a manual fallback.

**AP-3: Remove obsidian CLI from check_prereqs() entirely**
Since `obsidian vault info=path` is not a real command and detection always falls back to
manual input, checking for the obsidian binary in check_prereqs() provides no value and
blocks legitimate users. Remove the obsidian check from check_prereqs(). Vault path is
always entered manually — design around that reality.

### Priority 2 — Major gaps (fix before daily use is reliable)

**AP-4: Fix /session-end git add to include all modified files**
Replace "git add for specific files only" with: run `git status --short`, show all
modified/untracked files, and let the engineer confirm what to stage. Alternatively:
stage ALL git-tracked file changes (`git add -u`) plus any new files in the tracked folders.
Source code must be committed — not just documentation.

**AP-5: Add file rename/delete guidance to WORKFLOW.md and vault-sync behavior**
Add a section: **"Renaming or deleting documentation files"** that explains:
- Renames: the old filename persists in vault. After renaming, manually delete the old
  file from the vault folder, then run `/sync-vault` to push the renamed version.
- Deletes: same procedure — delete from vault manually.
- Add a new skill `/clean-vault` or add a `vault-sync.py --clean` flag that compares
  tracked files in local and vault and lists files present in vault but not locally.

**AP-6: Update TEMPLATE-GUIDE.md**
Either:
(a) Remove the old "Workflow" sections at the bottom and replace with a pointer to WORKFLOW.md, or
(b) Rewrite the workflow sections to match the current /new-project + /session-start flow.
Option (b) is better — TEMPLATE-GUIDE.md is a good reference document, just outdated.

### Priority 3 — Minor friction (polish)

**AP-7: Add comment to firmware-init.py explaining its presence in project copies**
In the file docstring, add: *"This script is copied into every new project as part of the
template. It does not need to be run from inside a project — only from the firmware-project-
template directory to initialize a new project."*

**AP-8: /session-start: report vault-sync.py PID after starting**
After starting vault-sync.py in background, print:
`"vault-sync.py started (PID {pid}). To stop: kill {pid} or close this terminal session."`
Also add a `/session-end` step that stops vault-sync.py gracefully before the session closes.

**AP-9: /session-start: bound the 08-Knowledge scan**
Add a practical limit: scan only filenames (not file contents) in 08-Knowledge, and cap at
500 files before informing the engineer that a full scan was not performed.

**AP-10: Clarify the vault-sync --once message format**
After Phase 3, Claude runs vault-sync.py --once and prints raw Python output. Add to the
/new-project skill step 3.4: after running the command, parse the output and summarize:
*"Synced {n} files to vault. {list of filenames}. No conflicts."*

**AP-11: Add /sync-status skill**
A simple skill that checks whether `.vault-sync.lock` exists, reads the PID, and verifies
the process is still running. Prints: *"vault-sync.py is running (PID 1234) / not running."*

---

## Implementation Order

```
Phase A — Blockers (AP-1, AP-2/AP-3)
  AP-1: Rewrite README.md
  AP-2/AP-3: Fix firmware-init.py obsidian check

Phase B — Major gaps (AP-4, AP-5, AP-6)
  AP-4: Fix /session-end git add
  AP-5: Vault rename/delete guidance + vault-sync --clean flag
  AP-6: Update TEMPLATE-GUIDE.md

Phase C — Polish (AP-7 through AP-11)
  AP-7: firmware-init.py docstring
  AP-8: vault-sync PID reporting + stop on session-end
  AP-9: 08-Knowledge scan limit
  AP-10: vault-sync output summary in /new-project
  AP-11: /sync-status skill
```

Total issues: 3 critical, 4 major, 5 minor.
Phases A and B are required before the template is reliable for independent use.
Phase C is polish that significantly improves daily experience.
