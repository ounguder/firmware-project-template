# Firmware Project Template — Guide

This file explains every file in this template: what it is, what goes in it,
when to update it, and why it exists. Use this as a reference when setting up
a new project or onboarding a new Claude session.

---

## How This Template Works

When you start a Claude Code session inside a firmware project, Claude reads
`CLAUDE.md` automatically. That file is the agent's briefing — it tells Claude
what the hardware is, how to build and flash, what rules to follow, and where
to find detailed documentation. Every other file in `docs/` and `.claude/rules/`
is imported from `CLAUDE.md` using `@` references.

**The principle:** CLAUDE.md is the cockpit, not the manual.
It stays short (~100 lines). Detailed specs live in `docs/`. Rules live in `.claude/rules/`.

---

## File-by-File Reference

---

### CLAUDE.md
**What it is:** The primary briefing file. Read by Claude at the start of every session.

**What goes in it:**
- Target MCU, board, and hardware revision
- Build, flash, and test commands
- Brief code style rules (full rules imported from `.claude/rules/`)
- Memory constraints
- Key pin/peripheral assignments (full map imported from `docs/HARDWARE.md`)
- Protocol spec reference (imported from `docs/PROTOCOL.md`)
- IMPORTANT rules — hard constraints Claude must never violate
- References to `HANDOFF.md` for current status

**When to update:** When the hardware changes, build system changes, or new hard rules are established.

**Keep it under 150 lines.** If it grows beyond that, move content into a rules file and import it.

**Example snippet:**
```markdown
## Toolchain & Build
- Build system: PlatformIO
- Compile:  `pio run`
- Flash:    `pio run --target upload`
- Monitor:  `pio device monitor --baud 115200`

## IMPORTANT Rules
- NEVER disable the watchdog in production code
- See @.claude/rules/safety.md for the full list
```

---

### CLAUDE.local.md *(not committed to git)*
**What it is:** Machine-specific configuration that must never be committed.

**What goes in it:**
- COM port or device path for the programmer and serial monitor
- Local tool paths (e.g. OpenOCD location)
- Environment variables: tokens, device IDs, broker addresses
- Any quirks specific to this workstation

**When to update:** Once per machine when setting up the project.

**Important:** This file is in `.gitignore`. Every developer creates their own copy.
A blank template is provided below.

**Example:**
```markdown
# Local Machine Config — DO NOT COMMIT
## Debug Probe
- Programmer: ST-Link V2 on COM4
- OpenOCD config: C:/tools/openocd/scripts/interface/stlink.cfg

## Environment Variables
- INFLUX_TOKEN=abc123xyz
- DEVICE_ID=DEV_003
```

---

### .claude/rules/coding-style.md
**What it is:** Full C/C++ coding conventions for this project.

**What goes in it:**
- Naming conventions table (functions, variables, types, macros, files)
- File structure order (includes → macros → types → functions)
- Header file rules (include guards, self-contained headers)
- Error handling pattern (status codes, logging)
- ISR rules (no blocking, no malloc, volatile shared variables)
- Comment style

**When to update:** When the team agrees on a new convention.

**Example snippet:**
```markdown
## Naming Conventions
| Element   | Convention           | Example              |
|-----------|---------------------|----------------------|
| Functions | `module_verb_noun()` | `uart_send_frame()`  |
| Globals   | `g_` prefix          | `g_system_tick`      |
| ISR vars  | `volatile`           | `volatile bool g_rx_ready` |
```

---

### .claude/rules/hardware.md
**What it is:** Peripheral ownership rules, timing budgets, and power domain rules.

**What goes in it:**
- Peripheral ownership table (which module owns which peripheral)
- Power domain control table (which GPIO controls which rail)
- Timing constraints (deadlines for TX windows, sensor reads, etc.)
- ADC reference and conversion formula
- Cross-reference to errata in `docs/DEBUGGING.md`

**When to update:** When peripherals are reassigned or new timing constraints are discovered.

**Example snippet:**
```markdown
## Peripheral Ownership
| Peripheral | Pins        | Owner Module     | Notes          |
|-----------|-------------|-----------------|----------------|
| UART1     | PA9 / PA10  | `debug_console` | TX-only in prod|
| SPI1      | PA5/PA6/PA7 | `lora_driver`   | CS on PA4      |
```

---

### .claude/rules/safety.md
**What it is:** Hard rules Claude must follow at all times. Non-negotiable constraints.

**What goes in it:**
- NEVER list: things that must never happen in production code
- ALWAYS list: things that must always be done
- Watchdog policy (timeout, where to feed, where NOT to feed)
- Memory safety rules (bounds checking, NULL checks)
- Build flag requirements (NDEBUG, WDG_ENABLE)

**When to update:** When a new safety incident is discovered, or a new hard constraint is agreed.

**Example snippet:**
```markdown
## NEVER
- Disable or bypass the watchdog timer in production builds
- Call `malloc()` in interrupt handlers or hard real-time code paths
- Ignore the return value of any HAL or driver function

## ALWAYS
- Feed the watchdog at the top of the main loop — never inside retry loops
- Validate input buffer lengths before any copy operation
```

---

### docs/FSD.md — Full System Design
**What it is:** The authoritative requirements and architecture document.

**What goes in it:**
- Project purpose and scope (what is in/out of scope for this phase)
- Target stack (MCU, HAL, RTOS, build system, test framework)
- High-level architecture diagram (ASCII)
- Functional requirements (FR-01, FR-02, ...)
- Non-functional requirements (NFR-01, ...)
- Data model: every frame's byte-level layout with offsets, types, scaling, ranges
- Software module design (one section per module)
- Task/thread design if using an RTOS
- Testing strategy (unit tests, integration tests, acceptance criteria)
- Resolved design decisions table

**When to update:** When requirements change, new frames are added, or a design decision is made.

**Example snippet:**
```markdown
## Frame A: Sensor Reading (11 bytes)

| Offset | Field   | Type   | Scale | Range     | Description        |
|--------|---------|--------|-------|-----------|--------------------|
| 0x00   | VER     | uint8  | —     | 0x01      | Protocol version   |
| 0x07   | TEMP_C  | int16  | /10   | -400..850 | Temperature °C × 10|
| 0x0A   | ERR     | uint8  | mask  | —         | Sensor error flags |
```

---

### docs/HARDWARE.md
**What it is:** Schematic-level hardware reference. Single source of truth for pin assignments.

**What goes in it:**
- Board overview (MCU, board name, supply voltage, programming interface)
- Complete pin map table
- Power architecture diagram (ASCII)
- External components table (sensor names, interfaces, I2C addresses)
- Flash memory map
- Clock tree configuration
- Hardware errata and PCB rework notes

**When to update:** Before any pin is reassigned. When a new hardware revision is released.

**Example snippet:**
```markdown
## Pin Map
| Pin | Signal      | Direction | Peripheral | Notes            |
|-----|-------------|-----------|-----------|------------------|
| PA9 | UART1_TX    | OUT       | UART1     | Debug console    |
| PC8 | PWR_SENSOR  | OUT       | GPIO      | Sensor rail on/off |
```

---

### docs/PROTOCOL.md
**What it is:** Complete specification for all communication frames and transport settings.

**What goes in it:**
- Overview table of all frame types (direction, topic, size, purpose)
- For each frame: ASCII layout diagram, field definition table, ERR bitmask table, validation rules
- Encoding example in C (for the firmware)
- Decoding example in Python (for the backend)
- Transport layer: MQTT topics, QoS, broker settings
- Data budget estimate (bytes/month by mode)

**When to update:** When frame format changes or a new frame type is added. Never break this silently — update version field.

**Example snippet:**
```markdown
### Encoding Example (C)
```c
void frame_a_encode(frame_a_t *f, const sensor_reading_t *r) {
    f->ver        = 0x01;
    f->temp_c_x10 = (int16_t)(r->temp_c * 10.0f);
    f->err        = r->err_mask;
}
```

### Decoding Example (Python)
```python
def decode_frame_a(data: bytes) -> dict:
    ver, node_id, seq, time_s, temp_raw, hum, err = struct.unpack('<BBBIhBB', data)
    return {"temp_c": temp_raw / 10.0, "hum_pct": hum, "err": err}
```
```

---

### docs/BRING-UP.md
**What it is:** Step-by-step procedure for setting up and verifying the system from scratch.

**What goes in it:**
- Prerequisites checklist (hardware, tools, repo cloned)
- Numbered steps: power-on check → first flash → serial monitor → sensor verify → comms verify
- Expected serial output at each step
- Quick reference commands block
- Troubleshooting table

**When to update:** When the bring-up procedure changes (new tool, new step, new known issue).

**Example snippet:**
```markdown
## Step 2 — First Flash
```bash
pio run --target upload
# Expected: "Verified OK"
```
If flash fails:
- Check programmer port in `CLAUDE.local.md`
- Verify SWD wiring: SWDIO → PA13, SWDCLK → PA14
```

---

### docs/DEBUGGING.md
**What it is:** Living reference for hardware errata, known bugs, and debugging procedures.

**What goes in it:**
- Hardware errata table (chip errata with workarounds)
- Known issues table (ID, status, description, affected version, fix)
- Step-by-step debugging procedures for common failure modes
- Logging macro reference (what level to use for what)
- Test vector reference and decode verification procedure

**When to update:** Every time a new bug is found or a new errata is discovered. Keep this current.

**Example snippet:**
```markdown
### Watchdog Reset Loop
**Symptom:** Board resets every 8 s, serial shows `[BOOT]` repeatedly.
**Cause:** A task blocks longer than the WDG timeout.
**Debug steps:**
1. Add timestamps at start/end of each long operation
2. Temporarily increase WDG timeout to 30 s to identify the slow task
```

---

### docs/HANDOFF.md
**What it is:** Current project status. Updated at the end of every working session.

**What goes in it:**
- Date and branch
- What works checklist
- In-progress items with current state
- Known issues
- Next steps in priority order
- Key files changed this session
- Free-text context for the next agent (non-obvious things)

**When to update:** At the end of every Claude session and every working day.

**Example snippet:**
```markdown
## Context for the Next Agent
The gateway frame decoder in `src/decoder.c` has a temporary hardcoded
NODE_ID of 0x01 at line 47. This needs to be replaced with the config
lookup before testing with real hardware. The config module is not yet
implemented (see FR-05 in FSD.md).
```

---

## Workflow: Starting a New Project

1. Copy this template folder: `cp -r firmware-project-template my-new-project`
2. Replace all `[PROJECT NAME]`, `[MCU]`, and `[placeholder]` markers
3. Create `CLAUDE.local.md` for your machine (never commit it)
4. Fill in `docs/FSD.md` with your actual requirements
5. Fill in `docs/HARDWARE.md` with your pin map
6. Open a Claude Code session: `claude` in the project directory
7. Claude reads `CLAUDE.md` automatically — you are ready

## Workflow: Daily Session

1. Open terminal in project directory
2. Start Claude: `claude`
3. Claude reads `CLAUDE.md` and `HANDOFF.md` — context is restored
4. Work
5. Before closing: ask Claude to update `HANDOFF.md` with the session summary

## Workflow: New Frame or Protocol Change

1. Update `docs/PROTOCOL.md` first — spec before code
2. Update `docs/FSD.md` data model section
3. Add test vectors to `tests/test_vectors.json`
4. Implement the change
5. Run `pio test -e native` to verify test vectors pass
6. Update `HANDOFF.md`
