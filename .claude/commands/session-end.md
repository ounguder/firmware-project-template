# /session-end — Close a working session

Run this at the end of every working session.
Updates HANDOFF.md, proposes knowledge promotions, stops vault sync, and commits if there are changes.

Complete all steps in order.

---

## Step 1 — Update HANDOFF.md

Read the current `docs/HANDOFF.md`. Rewrite it with today's session state.

Fill every section:

```markdown
## Status
- Date: {today's date}
- Branch: {current git branch — run: git branch --show-current}
- Firmware version: {from CLAUDE.md or carry forward}
- Hardware revision: {from CLAUDE.md or carry forward from previous HANDOFF.md}
- Last verified on hardware: {carry forward or update if verified today}

## What Works
{updated checklist — add any new items confirmed working this session}

## In Progress
{updated table — move completed items to What Works, add new in-progress items}

## Known Issues
{updated table — add any new issues discovered, mark resolved ones}

## Next Steps (priority order)
{reordered list based on session progress — most important first}

## Key Files Changed This Session
{list of files created or modified this session}

## Context for the Next Agent
{2–4 sentences: what was attempted, what worked, what was left unresolved,
 any quirks the next agent should know immediately}
```

Write the updated file to `docs/HANDOFF.md`.

---

## Step 2 — Knowledge promotion review

Review what was done this session. Identify any learnings that are reusable beyond this project:
- Bug fixes with a non-obvious root cause
- Driver patterns or peripheral initialization sequences
- Protocol implementation details
- Hardware behavior discoveries (errata, timing quirks, signal issues)
- Tool or build system tricks

For each candidate learning:

### Duplicate detection

Before proposing anything, read `VAULT-BLUEPRINT.md` to get `vault.root`.
Check the target folder in `{vault.root}/08 - Knowledge/` for notes with similar titles.

**If a similar note already exists:**
> "A note on **{topic}** already exists at `{path}` (from {project}).
> What should I do?
> (a) Add this project to its `used_in` field
> (b) Create a separate note
> (c) Skip"

If (a): open the existing note, append this project's wikilink to its `used_in` frontmatter field,
and save. Do not create a new file.
If (b): proceed with new note creation below.
If (c): skip this candidate.

**If no similar note exists**, propose:
> "I'd like to promote a learning to 08 - Knowledge:
> **{topic}** → `{target_subfolder}/`
> This covers: {one-sentence description}
> Create this note? [yes / no / not now]"

### Domain priority rule (determines target subfolder)

Apply in order — highest match wins:
1. Specific to one MCU family → `11 - Microcontrollers/{family}/`
2. General firmware pattern (any MCU) → `10 - Firmware/`
3. Protocol-specific → `04 - Protocols/`
4. Hardware phenomenon (electrical, physical) → `09 - Hardware/`
5. Domain science (agriculture, RF, signal processing) → `14 - Agriculture/`, `12 - RF Engineering/`, etc.

If the learning genuinely applies at two levels (e.g., MCU-specific errata AND general debug pattern),
create a note at each level with cross-links between them.

### Writing approved notes

For each approved promotion, write the note directly to the vault:
`{vault.root}/{target_subfolder}/{note-title}.md`

Use this template:
```markdown
---
type: knowledge
domain: {e.g., Firmware / MCU / Protocol / Hardware}
tags: [{relevant tags}]
created: {today's date}
used_in:
  - "[[{vault.project_path}/CLAUDE]]"
---

# {Note Title}

## Context
{What project / situation led to this discovery}

## Finding
{The actual knowledge — what is true, what works, what to avoid}

## Why It Matters
{Why this is non-obvious or worth remembering}

## Example
{Code snippet, waveform description, or concrete example}

## References
{Datasheet section, forum post, commit, etc. — if applicable}
```

The `used_in` wikilink must use the exact `vault.project_path` from `VAULT-BLUEPRINT.md`:
```yaml
used_in:
  - "[[01 - Projects/Eco-Twin/DemoSetup/Edge-Node/Sensor Reading/sensor-reading/CLAUDE]]"
```

After writing each note, say: "Knowledge note created: `{path}`"

---

## Step 3 — Stop vault-sync.py

Check for `.vault-sync.lock` in the project root.

**If `.vault-sync.lock` exists:**
- Read the PID from the file
- Stop the process:
  ```
  kill {pid}        # Unix / Git Bash
  taskkill /PID {pid} /F   # PowerShell fallback
  ```
- Say: "vault-sync.py (PID {pid}) stopped."

**If `.vault-sync.lock` does not exist:**
- Say: "vault-sync.py is not running — nothing to stop."

---

## Step 4 — Git commit

Run:
```
git status --short
```

**If output is empty** (nothing changed): say "No file changes this session — nothing to commit."
Skip to Step 5.

**If there are changes**, show the full list of modified and untracked files, then stage all changes:

```
git add -u
```
This stages all modifications and deletions of already-tracked files (src/, include/, tests/,
docs/, Report/, lessonsLearned/, CLAUDE.md, VAULT-BLUEPRINT.md, .claude/rules/, etc.).

Then stage any new untracked files in tracked directories:
```
git add src/ include/ tests/ docs/ Report/ lessonsLearned/ .claude/rules/ CLAUDE.md VAULT-BLUEPRINT.md
```
(This is safe — git ignores directories it does not track and new files not in those paths.)

Run `git status --short` again to confirm the full staged set, then propose a commit message:
> "Here is the proposed commit message:
> ```
> {type}: {concise summary of what was done this session}
>
> {optional body — key changes if the summary is not enough}
> ```
> Shall I commit and push? [yes / no]"

`{type}` follows conventional commits: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`.

If yes:
1. Run `git commit -m "{message}"`
2. Run `git push`
3. Report: "Committed and pushed. {commit hash} — {message}"

If no: say "Skipping commit. Changes are saved locally."

---

## Step 5 — Done

Say:
> "Session closed. HANDOFF.md is updated.
> Run /session-start at the beginning of your next session."
