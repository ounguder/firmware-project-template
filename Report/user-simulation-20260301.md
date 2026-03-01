# User Simulation Report — Firmware Project Template

**Date:** 2026-03-01
**Persona:** Senior embedded firmware engineer, 8 years experience (STM32/ESP32, PlatformIO, KiCAD). Regular Claude Code user. Found this template on GitHub, cloning it fresh with no prior knowledge of its conventions.
**Entry point:** README.md → `git clone` × 2 → `setup.ps1` → `/new-project`

---

## Summary

| Severity | Count |
|---|---|
| Critical | 1 |
| Major | 1 |
| Minor | 3 |
| **Total** | **5** |

The template is in very good shape. The three-phase `/new-project` flow, the vault-sync
architecture, and the daily session skills are well-designed and well-documented. The README
is concise and correctly describes the setup path. One Critical issue must be fixed before
sharing: real report files left in `Report/` will be copied into every new project created
from this template. The remaining findings are documentation polish.

---

## Findings

### [F1] — Report/ contains real content that will be copied into every new project ← CRITICAL
**Severity:** Critical
**Location:** `Report/engineer-simulation-report.md` · `Report/phase2-phase3-review.md`
**What happened:** After `/new-project` Phase 1 ran `firmware-init.py` (which uses
`shutil.copytree`), my new project folder contained two real simulation/review reports
from the template repository's own history. These are not template files — they are
content that belongs in the CI project history, not in a blank starting template.
**Why it matters:** Every project initialized from this template inherits these files.
They appear under `Report/` as if they are part of the new project. They will also sync
to the vault via vault-sync.py on first sync, polluting the new project's vault folder
with irrelevant content. The only template file that should be in `Report/` is
`(TEMPLATE) Report.md`.

---

### [F2] — CLAUDE.md blank stub carries old workflow instruction
**Severity:** Major
**Location:** `CLAUDE.md` — top comment block (lines 3–5)
**What happened:** The blank `CLAUDE.md` contains the instruction:
*"Start Claude and say: 'Let's set up a new firmware project. Interview me and fill the docs.'"*
This is the old, pre-skill workflow. The current system uses `/new-project`. A user who
clones this template repo and opens Claude inside it (before running `/new-project`) gets
guidance that contradicts the README. It also means the old interview flow still works as
a fallback path — creating inconsistent results depending on which instruction the user follows.
**Why it matters:** First impression inside Claude is wrong for any user who doesn't read
the README top-to-bottom before typing anything. The two instructions (README's `/new-project`
vs CLAUDE.md's interview style) create a fork in the workflow with no warning.

---

### [F3] — README structure listing is missing sync-status.md
**Severity:** Minor
**Location:** `README.md` — "What's Included" `.claude/commands/` block
**What happened:** The README lists four command files: `session-start.md`,
`session-end.md`, `sync-vault.md`, `promote.md`. The actual `.claude/commands/` folder
contains five — `sync-status.md` is present but not listed. WORKFLOW.md correctly
documents `/sync-status` in its skills table and Quick Reference.
**Why it matters:** A user reading the README catalog gets an incomplete picture of
available skills and may not discover `/sync-status` until they check the file system
or read WORKFLOW.md in full.

---

### [F4] — VAULT-BLUEPRINT.md documentation example uses personal username
**Severity:** Minor
**Location:** `VAULT-BLUEPRINT.md` — "Vault Path Example" section (line ~109)
**What happened:** The example path shows `C:\Users\ungud\...\obsidian-git\...` — a
personal username hardcoded into what should be a generic template document.
**Why it matters:** Minor cosmetic issue. Any user reading this sees a specific person's
username rather than a `{your-username}` placeholder. Low confusion risk since it's
clearly in an "example" block, but inconsistent with the `{you}` placeholder style used
elsewhere in the docs.

---

### [F5] — __pycache__/ directory visible in template root
**Severity:** Minor
**Location:** Project root — `__pycache__/`
**What happened:** Running vault-sync.py or firmware-init.py locally generates a
`__pycache__/` directory. It is correctly gitignored and excluded from `copytree`, so it
won't be committed or copied to new projects. But it is visible when browsing the
template folder locally or on GitHub if someone has run the scripts before committing.
**Why it matters:** Cosmetic only — no functional impact. Makes the template look less
clean and could confuse someone inspecting the template folder structure before cloning.

---

## Action Plan

### Phase A — Blockers
- **[AP-1]** Delete `Report/engineer-simulation-report.md` and `Report/phase2-phase3-review.md`
  from `firmware-project-template`. Only `Report/(TEMPLATE) Report.md` should remain.
  Commit: *"chore: remove stale reports from blank template"* — fixes [F1]

### Phase B — Major gaps
- **[AP-2]** Update the comment block in `CLAUDE.md` (blank template) to replace the old
  interview instruction with: *"Run `/new-project` to initialize this project — it interviews
  you and fills all docs automatically."* Mirror this change in `firmware-project-template-ci`.
  — fixes [F2]

### Phase C — Polish
- **[AP-3]** Add `sync-status.md ← /sync-status skill` to the `.claude/commands/` block
  in `README.md`. — fixes [F3]
- **[AP-4]** Replace `C:\Users\ungud\...` in the VAULT-BLUEPRINT.md "Vault Path Example"
  with `C:\Users\{your-username}\...`. Mirror this in `firmware-project-template-ci`. — fixes [F4]
- **[AP-5]** Add `__pycache__/` cleanup note to `TEMPLATE-GUIDE.md` or add a `.gitkeep`
  policy note — or simply run `git clean -fdx __pycache__` and confirm gitignore catches
  future runs before any public sharing. — fixes [F5]
