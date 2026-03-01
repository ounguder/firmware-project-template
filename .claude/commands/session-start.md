# /session-start — Begin a working session

Run this at the start of every working session, including immediately after /new-project completes.
It loads project context, starts vault sync, and orients you for the session.

Complete all steps in order. Do not skip any step.

---

## Step 1 — CLAUDE.local.md check

Check if `CLAUDE.local.md` exists in the project root.

**If it does not exist**, run the creation wizard:

> "This machine does not have a `CLAUDE.local.md`. Let me create it — this file holds
> machine-specific config and is never committed to git."

Ask the following questions one at a time:
1. "What COM port is your device connected to? (e.g., COM3, COM7 — or leave blank if not applicable)"
2. "What is the full path to your debug probe tool? (e.g., `C:\Program Files\OpenOCD\bin\openocd.exe` or `C:\Program Files\SEGGER\JLink\JLink.exe` — or leave blank)"
3. "Any other local environment variables or paths to record? (e.g., MQTT_BROKER_IP=192.168.1.10 — or leave blank)"

Write `CLAUDE.local.md` with the collected values using this format:
```markdown
# [PROJECT NAME] — Local Machine Config
# Fill this manually. DO NOT COMMIT — this file is gitignored.

## Debug Probe
[probe path or "Not configured"]

## Serial Monitor
[COM port or "Not configured"]

## Environment Variables
[variables or "None"]

## Notes

```

Then say: "CLAUDE.local.md created. This file stays on this machine only."

**If it already exists**, read it silently and continue.

---

## Step 2 — Load project context

Read all four files in sequence:

1. `CLAUDE.md` — hardware, build commands, code rules, memory limits
2. `docs/HANDOFF.md` — session status, what works, what's in progress, next steps
3. `docs/DESIGN-REVIEW.md` — project purpose, selected approach, constraints, open questions
4. `VAULT-BLUEPRINT.md` — vault path, sync config, predecessors

If any file is missing or still blank (template stub), note it and continue.

---

## Step 3 — Predecessor context (conditional)

Read the `predecessors:` field from `VAULT-BLUEPRINT.md`.

If predecessors are listed, ask:
> "This project builds on: {predecessor names, comma-separated}.
> Load their HANDOFF.md and lessonsLearned/ for context? [yes / no]"

If yes: for each predecessor in the list, read:
- `{vault_path}/docs/HANDOFF.md`
- All files in `{vault_path}/lessonsLearned/`

Summarize what was learned in each predecessor project in 2–3 lines each.

---

## Step 4 — Knowledge scan (08 - Knowledge)

From the content of `CLAUDE.md`, extract:
- MCU family and board name (e.g., ESP32-S3, STM32L476, RP2040)
- Peripherals in use (e.g., I2C, SPI, ADC, UART, LoRa, SDI-12)
- Protocols or stacks (e.g., MQTT, FreeRTOS, BLE, LoRaWAN)

Read `VAULT-BLUEPRINT.md` to get `vault.root`.

List filenames (not file contents) in `{vault.root}/08 - Knowledge/` recursively.

**If there are more than 200 files**, scan only the first 200 (sorted alphabetically) and print:
> "08-Knowledge is large — scanned top 200 files by name. Run /promote to search for specific topics manually."

Match filenames against the extracted keywords (case-insensitive). Do not read file contents during the scan.

If matching notes are found:
> "I found knowledge notes relevant to this project:
> - [{note filename}]({vault path})
> - ...
> Load them into context? [yes / no / skip]"

If yes: read those specific files and hold their content in context for the session.
If no or skip: continue without loading.

If no matches are found: skip this step silently.

---

## Step 5 — Start vault-sync.py

Check if `vault-sync.py` is already running by looking for `.vault-sync.lock` in the project root.

**If `.vault-sync.lock` exists:**
- Read the PID from the file
- Say: "vault-sync.py is already running (PID {pid}). Continuous sync is active."

**If `.vault-sync.lock` does not exist:**
- Start vault-sync.py in the background:
  ```
  python vault-sync.py
  ```
  Run this as a background process so it does not block the session.
- After it starts, read `.vault-sync.lock` to get the PID.
- Say: "vault-sync.py started (PID {pid}). Continuous sync is active. It will be stopped at /session-end."

---

## Step 6 — Session summary

Print a concise project summary (5–10 lines):

```
Project:    {project name} ({primary_board})
GitHub:     {github_repo from VAULT-BLUEPRINT.md}
Vault:      {vault.project_path}

Last session: {date and branch from HANDOFF.md}
What works:   {bullet summary from HANDOFF.md — What Works section}
In progress:  {bullet summary from HANDOFF.md — In Progress section}
Next steps:   {first 1–2 items from HANDOFF.md — Next Steps section}
```

Then ask:
> "What do you want to work on today?"
