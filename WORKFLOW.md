# Firmware Development Workflow with Claude

This file describes exactly how to work with Claude on a firmware project —
from the first session through daily development, debugging, hardware changes,
and archiving. Read this once before starting a new project.

---

## Core Principles

1. **Claude fills the docs, you answer the questions.**
   Your job is to provide knowledge (hardware specs, requirements, decisions).
   Claude's job is to structure it, write it, implement it, and keep it up to date.

2. **CLAUDE.md is the context bridge.**
   Every session starts by Claude reading `CLAUDE.md` and `HANDOFF.md`.
   This means Claude knows the full project state from the first message —
   no need to re-explain anything.

3. **Spec before code.**
   When something new is added, Claude updates `FSD.md` and `PROTOCOL.md`
   *before* writing any implementation. This keeps docs and code in sync.

4. **Docs are updated as you go, not at the end.**
   When a bug is found → `DEBUGGING.md` is updated immediately.
   When a bring-up step changes → `BRING-UP.md` is updated immediately.
   End-of-session → `HANDOFF.md` is updated before closing.

5. **The only file you ever type manually is `CLAUDE.local.md`.**
   Everything else is written by Claude based on your answers and your work together.

---

## Session 0 — Project Setup (5 minutes, you do this once)

This is the only session where you do manual work before starting Claude.

```
1. Copy the template folder:
   cp -r firmware-project-template my-project-name

2. Rename the folder to match your project.

3. Create CLAUDE.local.md for your machine:
   - Open CLAUDE.local.md
   - Fill in your COM port, programmer path, and any local tokens
   - This file is gitignored — never commit it

4. Initialise a git repository:
   git init
   git remote add origin [your-repo-url]

5. That's it. Do not touch any other file. Claude will fill them.
```

---

## Session 1 — Project Kickoff (Claude fills all docs)

This session produces a fully documented project from a blank template.

### What you do:
Open a terminal in the project folder and start Claude:
```bash
claude
```

Then say something like:
> *"Let's start a new firmware project. I'll answer your questions so you can
> fill in the project documentation."*

### What Claude does:
Claude will interview you with questions like these. Answer them as accurately
as you can — incomplete answers are fine, they can be refined later.

**Hardware questions:**
- What is the target MCU? (e.g. STM32L476, ESP32-S3)
- What is the board? (custom PCB, devkit, Nucleo?)
- What hardware revision is this?
- What is the system clock?
- What peripherals are connected? (sensors, communication modules, displays)
- What interfaces do the peripherals use? (UART, SPI, I2C, ADC)
- Are there switchable power rails?

**Requirements questions:**
- What does this firmware do? (one paragraph)
- What is in scope for this phase? What is out of scope?
- What are the key functional requirements?
- Are there memory constraints? (flash size, RAM limit)
- Are there timing constraints? (TX windows, deadlines)
- Are there safety requirements? (watchdog, error handling)

**Protocol questions (if applicable):**
- What communication protocol is used? (LoRa, MQTT, CAN, UART custom)
- How many frame types are there?
- Walk me through each field in each frame.
- What is the encoding? (little-endian? scaling? signed/unsigned?)

**Build questions:**
- What build system? (PlatformIO, CMake, Arduino CLI)
- What test framework? (Unity, Cmocka, none yet)

### What gets produced:
By the end of Session 1, Claude has written:
- `CLAUDE.md` — complete agent briefing
- `.claude/rules/coding-style.md` — naming conventions, file structure
- `.claude/rules/hardware.md` — peripheral ownership, timing, power domains
- `.claude/rules/safety.md` — NEVER/ALWAYS rules for this project
- `docs/FSD.md` — full system design with requirements and data model
- `docs/HARDWARE.md` — pin map, power architecture, component table
- `docs/PROTOCOL.md` — frame specs with C and Python examples
- `docs/HANDOFF.md` — initial status (nothing implemented yet)

Claude then commits all docs:
```
git add .
git commit -m "docs: initial project documentation from session 1"
```

---

## Daily Development Session

This is the standard session for every working day.

### Starting a session
```bash
# Navigate to the project
cd my-project-name

# Start Claude
claude
```

Claude reads `CLAUDE.md` and `docs/HANDOFF.md` automatically.
It knows exactly where you left off — hardware, rules, current status, next steps.

You do not need to say anything special. Claude is ready.

### During the session

**Implementing a feature:**
> *"Implement the sensor_manager module according to FSD.md section 7."*

Claude reads the relevant doc sections, writes the code, writes the unit tests,
runs the tests, and reports results. If anything is unclear in the spec,
Claude asks before implementing.

**Debugging an issue:**
> *"The I2C bus is locking up after the first sensor read. Here's the serial output: ..."*

Claude investigates, identifies the cause, fixes the code, and updates
`docs/DEBUGGING.md` with the issue and solution so it is not forgotten.

**Asking about the project:**
> *"What frame format does the gateway sensor frame use?"*

Claude reads `docs/PROTOCOL.md` and answers precisely. You do not need to
remember the spec — it is always there.

### Ending a session
Before closing, always say:
> *"Update HANDOFF.md with what we did today and what comes next."*

Claude updates `docs/HANDOFF.md` with:
- What was completed
- What is in progress and its current state
- Known issues discovered
- Next steps in priority order
- Any non-obvious context for the next session

Then Claude commits:
```
git add .
git commit -m "session: [brief summary of what was done]"
git push
```

---

## Workflow: Adding a New Feature or Frame

When a new requirement is introduced — a new frame type, a new sensor,
a new communication channel — follow this order strictly.

```
1. Discuss the requirement with Claude in plain language.
   Claude asks clarifying questions until the requirement is unambiguous.

2. Claude updates docs/FSD.md first:
   - Adds the requirement to the functional requirements table
   - Adds the data model (frame layout, field table) if applicable

3. Claude updates docs/PROTOCOL.md if a new or changed frame is involved:
   - Full byte-level spec
   - Updated C encoding example
   - Updated Python decoding example

4. Claude adds test vectors to tests/test_vectors.json.

5. Claude implements the feature in code.

6. Claude runs unit tests: `pio test -e native`
   Tests must pass before the session ends.

7. Claude updates docs/HANDOFF.md.

8. Claude commits everything together:
   git commit -m "feat: [feature name] — spec, implementation, and tests"
```

**Why spec before code?**
If the frame spec changes mid-implementation, both the spec and the code need
to be updated together. Writing the spec first gives Claude a fixed target
and prevents drift between documentation and implementation.

---

## Workflow: Hardware Change or New PCB Revision

When you receive a new board revision or change a pin assignment:

```
1. Tell Claude what changed:
   > "New PCB rev 2. UART2 moved from PA2/PA3 to PD5/PD6.
   >  Added an SPI2 bus for a second LoRa module on PB13/PB14/PB15, CS on PB12."

2. Claude updates docs/HARDWARE.md:
   - Pin map table updated
   - HW_REV incremented
   - Old assignments noted in the errata section

3. Claude updates CLAUDE.md:
   - Hardware revision field updated
   - Interface section updated

4. Claude updates .claude/rules/hardware.md:
   - Peripheral ownership table updated

5. Claude searches the codebase for any hardcoded pin references or
   old peripheral assignments and updates them.

6. Claude updates docs/HANDOFF.md noting the hardware change.

7. Claude commits:
   git commit -m "hw: update for PCB rev 2 — UART2 and SPI2 pin changes"
```

Never reassign a pin without going through this process.
`HARDWARE.md` must always match the physical hardware.

---

## Workflow: Bug Found

When something does not work as expected:

```
1. Describe the symptom to Claude:
   > "The board resets every 8 seconds. Serial shows [BOOT] repeating."

2. Claude investigates:
   - Reads relevant source files
   - Checks docs/DEBUGGING.md for known issues
   - Asks clarifying questions if needed

3. Claude identifies the root cause and proposes a fix.
   You approve or ask for an alternative approach.

4. Claude implements the fix.

5. Claude updates docs/DEBUGGING.md:
   - Adds the issue to the known issues table (or marks it fixed if pre-existing)
   - Adds a debugging procedure entry if the failure mode is likely to recur

6. Claude runs tests to confirm the fix does not break anything.

7. Claude commits:
   git commit -m "fix: [brief description of what was fixed]"
```

---

## Workflow: Switching Computers

Because docs and code are all in the same git repository, switching computers
requires no re-explanation to Claude. Context is fully preserved in the files.

```
1. On the new computer, clone the repository (if not already done):
   git clone [repo-url]

2. Create CLAUDE.local.md for this machine:
   - Fill in the correct COM port, programmer path, tokens for this workstation
   - This file is gitignored — it stays local

3. Open a terminal in the project folder and start Claude:
   claude

4. Claude reads CLAUDE.md and HANDOFF.md.
   Full context is restored. Continue working.
```

---

## Workflow: End of Project / Archiving

When the project phase is complete and you want to preserve it cleanly:

```
1. Ask Claude to write a final project summary:
   > "Write a final summary of what was built, what works,
   >  what was left out of scope, and any important notes for future reference."

2. Claude updates docs/HANDOFF.md with this summary.

3. Claude verifies all docs are consistent with the final code state:
   - HARDWARE.md matches the final hardware revision
   - PROTOCOL.md matches the implemented frame formats
   - DEBUGGING.md has all known issues documented
   - FSD.md acceptance criteria are checked off

4. Claude commits the final state:
   git commit -m "docs: final project state — [project name] phase complete"
   git push

5. Copy the docs folder into your Obsidian vault under the correct project path.
   (See your Obsidian vault workflow for where each project's docs belong.)
```

---

## Quick Reference: What to Say to Claude

| Situation | What to say |
|-----------|-------------|
| Starting session 1 | *"Let's start a new firmware project. Interview me and fill the docs."* |
| Starting any other session | Just `claude` — context is automatic |
| End of session | *"Update HANDOFF.md and commit."* |
| New requirement | *"We need to add [feature]. Update FSD.md first, then implement."* |
| New frame type | *"New frame type: [description]. Update PROTOCOL.md first."* |
| Hardware changed | *"New PCB rev. Here are the changes: ..."* |
| Bug found | *"[Symptom]. Investigate, fix, and update DEBUGGING.md."* |
| Unsure what to work on | *"Read HANDOFF.md and tell me the next priority."* |
| Want a status summary | *"Summarise the current project state."* |

---

## File Ownership Summary

| File | Written by | Updated when |
|------|-----------|-------------|
| `CLAUDE.md` | Claude (Session 1) | Hardware or toolchain changes |
| `CLAUDE.local.md` | **You** | Once per machine |
| `.claude/rules/*.md` | Claude (Session 1) | Conventions change |
| `docs/FSD.md` | Claude (Session 1) | New requirements added |
| `docs/HARDWARE.md` | Claude (Session 1) | Hardware revision changes |
| `docs/PROTOCOL.md` | Claude (Session 1) | Frame format changes |
| `docs/BRING-UP.md` | Claude (as built) | Bring-up procedure changes |
| `docs/DEBUGGING.md` | Claude (ongoing) | Every bug found or errata discovered |
| `docs/HANDOFF.md` | Claude (end of session) | Every session |
