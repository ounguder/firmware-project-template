# Firmware Project Template

A blank project template for embedded firmware development with Claude AI agents.
Copy this template when starting a new firmware project — Claude fills the documentation
in the first session based on an interview about your hardware and requirements.

## How to Use

**1. Copy the template**
```bash
git clone https://github.com/ounguder/firmware-project-template.git my-project
cd my-project
```

**2. Fill in your machine-specific config** (the only file you edit manually)
```
CLAUDE.local.md  ←  your COM port, programmer path, local tokens
```

**3. Start Claude and kick off the project**
```bash
claude
```
Say: *"Let's set up a new firmware project. Interview me and fill the docs."*
Claude will ask questions about your hardware, protocols, and requirements,
then fill every file in the template from your answers.

## What's Included

```
├── CLAUDE.md                   ← agent briefing (filled by Claude in Session 1)
├── CLAUDE.local.md             ← your machine config (never committed)
├── VAULT-BLUEPRINT.md          ← defines where docs sync to in Obsidian vault
├── WORKFLOW.md                 ← complete workflow guide for working with Claude
├── TEMPLATE-GUIDE.md           ← what every file is for and how to fill it
├── .claude/rules/
│   ├── coding-style.md         ← C/C++ naming, file structure, error handling
│   ├── hardware.md             ← peripheral ownership, power domains, timing
│   └── safety.md               ← NEVER/ALWAYS rules, watchdog policy
├── docs/
│   ├── FSD.md                  ← full system design and requirements
│   ├── HARDWARE.md             ← pin map, power architecture, errata
│   ├── PROTOCOL.md             ← communication frame specs
│   ├── BRING-UP.md             ← flash and bring-up procedure
│   ├── DEBUGGING.md            ← known issues, errata, debug procedures
│   └── HANDOFF.md              ← session status (updated every session)
├── Report/                     ← Claude-generated reports (synced to Obsidian)
├── lessonsLearned/             ← post-mortems and retrospectives (synced to Obsidian)
├── src/
├── include/
└── tests/
```

## Key Concepts

- **Claude fills the docs, you answer the questions.** Only `CLAUDE.local.md` is filled manually.
- **CLAUDE.md is the context bridge.** Claude reads it at every session start — no re-explaining needed.
- **HANDOFF.md is the session bridge.** Updated at the end of every session so the next one picks up exactly where you left off.
- **VAULT-BLUEPRINT.md** tells automation scripts where to copy `Report/` and `lessonsLearned/` into your Obsidian vault, preserving project hierarchy.

## Related Repositories

| Repo | Purpose |
|------|---------|
| [firmware-project-template-example](https://github.com/ounguder/firmware-project-template-example) | Fully filled reference based on an imaginary IoT project |
| [firmware-project-template-ci](https://github.com/ounguder/firmware-project-template-ci) | Living master template — continuously improved over time |
