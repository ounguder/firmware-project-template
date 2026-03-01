# /promote — Promote a learning to 08 - Knowledge

Standalone knowledge promotion. Run any time during a session when you have a specific
learning to capture — does not require /session-end.

Also embedded inside /session-end for end-of-session review.

---

## When to use

Run /promote when you have just:
- Fixed a non-obvious bug and understand the root cause
- Discovered a peripheral quirk, timing constraint, or hardware errata
- Written a driver or protocol pattern worth reusing
- Learned something about a tool, build system, or debug technique

---

## Step 1 — Identify candidates

If the user invokes /promote without specifying a topic, review:
- Files in `lessonsLearned/` created or modified this session
- Files in `Report/` created this session
- Any fix or discovery described in the current conversation

Ask if needed:
> "What learning do you want to promote? Describe it briefly, or point me to the file."

---

## Step 2 — Determine target location

Apply the domain priority rule (highest match wins):

1. Specific to one MCU family (only applies to ESP32-S3, STM32L476, RP2040, etc.)
   → `11 - Microcontrollers/{family}/`
2. General firmware pattern (applies to any MCU or platform)
   → `10 - Firmware/`
3. Protocol-specific (MQTT, LoRaWAN, SDI-12, Modbus, etc.)
   → `04 - Protocols/`
4. Hardware phenomenon (electrical, physical — ESD, decoupling, trace impedance, etc.)
   → `09 - Hardware/`
5. Domain science (agriculture sensing, RF propagation, signal processing, power systems, etc.)
   → `14 - Agriculture/`, `12 - RF Engineering/`, `15 - Signal Processing/`, etc.

If the learning genuinely applies at two levels (e.g., an MCU-specific I2C errata that also
illustrates a general clock-stretch pattern), propose notes at both levels with cross-links.

---

## Step 3 — Duplicate check

Read `VAULT-BLUEPRINT.md` to get `vault.root`.
Look in `{vault.root}/{target_subfolder}/` for existing notes with similar titles or topics.

**If a similar note exists:**
> "A note on **{topic}** already exists: `{path}`
> (a) Add this project to its `used_in` field — no new file created
> (b) Create a separate note at the same location
> (c) Skip"

If (a): read the existing note, append this project's wikilink to its `used_in` field, save.
If (b): proceed to Step 4.
If (c): done.

**If no similar note exists:** proceed to Step 4.

---

## Step 4 — Propose the note

Before writing anything, show the user what will be created:

> "I'll create a knowledge note:
>
> **Title:** {note title}
> **Location:** `08 - Knowledge/{target_subfolder}/{filename}.md`
> **Summary:** {one sentence describing the finding}
>
> Create it? [yes / no]"

If no: done.

---

## Step 5 — Write the note

Write the file directly to the vault:
`{vault.root}/{target_subfolder}/{note-title-in-kebab-case}.md`

Use this template:
```markdown
---
type: knowledge
domain: {Firmware / MCU / Protocol / Hardware / Agriculture / RF Engineering / ...}
tags: [{mcu-family}, {peripheral}, {topic}]
created: {today's date}
used_in:
  - "[[{vault.project_path}/CLAUDE]]"
---

# {Note Title}

## Context
{What project / situation / symptom led to this discovery}

## Finding
{The actual knowledge — what is true, what works, what to avoid}

## Why It Matters
{Why this is non-obvious or worth remembering}

## Example
{Code snippet, register value, waveform description, or concrete example}

## References
{Datasheet section, forum link, commit hash, issue ID — if applicable}
```

The `used_in` wikilink must use the exact `vault.project_path` from `VAULT-BLUEPRINT.md`:
```yaml
used_in:
  - "[[01 - Projects/Eco-Twin/DemoSetup/Edge-Node/Sensor Reading/sensor-reading/CLAUDE]]"
```

---

## Step 6 — Confirm

After writing:
> "Knowledge note created: `{full vault path}`
> It will appear in Obsidian after Obsidian Sync distributes it (usually within seconds).
> The `used_in` field links back to this project so you can trace where this knowledge came from."

If you also created a `lessonsLearned/` entry for this session, mention that the promotion
is linked to it.
