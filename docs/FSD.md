---
type: full-system-design
project: "[project-name]"
status: draft
---

# Full System Design — [PROJECT NAME]

<!-- Filled by Claude in Session 1 (Technical Kickoff) based on the requirements interview. -->
<!-- This document is a FIRST DRAFT. Sections marked TODO require further work.            -->
<!-- Update status to 'in-progress' as sections are completed, 'complete' when finalized. -->

## Status

> **DRAFT** — Generated during kickoff interview (Session 1).
> Sections marked `<!-- TODO -->` are incomplete and must be filled before implementation begins.
> Cross-reference with `DESIGN-REVIEW.md` for purpose, selected approach, and constraints.

---

## 1. Purpose & Scope

### Goal
<!-- TODO: Paste purpose from DESIGN-REVIEW.md → Purpose section -->

### In Scope (this phase)
<!-- TODO: List what this project delivers -->

### Out of Scope (this phase)
<!-- TODO: List explicitly excluded items to prevent scope creep -->

---

## 2. Target Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| MCU / Board | | |
| Framework / HAL | | |
| RTOS | | |
| Build System | | |
| Test Framework | | |

<!-- TODO: Fill from kickoff interview answers -->

---

## 3. High-Level Architecture

<!-- TODO: ASCII block diagram of system components and data flow -->
<!-- Cross-reference: DESIGN-REVIEW.md → Selected Approach -->

---

## 4. Functional Requirements

| ID | Requirement |
|----|-------------|
| FR-01 | |

<!-- TODO: Derived from DESIGN-REVIEW.md → Acceptance Criteria -->

## 5. Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR-01 | |

<!-- TODO: Power budget, timing constraints, reliability targets -->

---

## 6. Data Model

<!-- TODO: Byte-level data structures, sensor reading formats, frame layout -->
<!-- Cross-reference: PROTOCOL.md for wire format -->

---

## 7. Software Module Design

<!-- TODO: One subsection per module: purpose, API surface, dependencies, state -->

---

## 8. Task / Thread Design

<!-- TODO: Only if using RTOS. List tasks, priorities, stack sizes, blocking calls -->

---

## 9. Testing

### Unit Tests
<!-- TODO: List what is tested at unit level and how -->

### Integration Tests
<!-- TODO: List integration test scenarios -->

### Acceptance Criteria
<!-- TODO: Paste from DESIGN-REVIEW.md → Acceptance Criteria -->

---

## 10. Resolved Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| | | |

<!-- TODO: Record each architectural decision and its rationale as it is made -->
