# Planning: features, roadmap, tasks

Read this in phase 7. `scripts/check_kickoff.py` parses the formats below exactly, so keep the headings and field labels as shown.

## Feature inventory

The inventory lives in `docs/development/feature-inventory.md`, built from `templates/feature-inventory.md`.

**Coverage.** List every meaningful feature or system the design requires, including non-functional ones (security, performance, accessibility, operations) and infrastructure.

**IDs.** Use `PREFIX-NNN`, where the prefix is 2–6 capital letters per wiki section, such as `CORE`, `NET`, `UI`, `DATA`, `OPS` or `SEC`. IDs are stable forever. Never renumber; a retired feature becomes `N/A`.

**Block format:**

```markdown
### CORE-001 · Player movement
- **Status:** Not started
- **Priority:** P1
- **Source:** [DESIGN §3.2](../DESIGN.md#32-player-movement), D-014
- **Depends on:** —
- **Tasks:** T-006, T-007
- **Wiki:** [Player](../wiki/player/README.md)
- **Description:** What it does and how it should behave.
- **Acceptance:** Objective criteria for the whole feature.
- **Risks:** —
```

**Feature statuses:** Not started · In progress · Partially implemented · Implemented (unverified) · Verified · Blocked · Deferred · N/A

## Phases & roadmap

Derive the phases from real dependencies, not from this list. A typical shape:

0. **Spikes and decisions** that block the foundations
1. **Foundations.** Repo, toolchain, CI, environments, project skeleton.
2. **Walking skeleton.** The thinnest end-to-end path through every layer. For example: a page that writes to the database and reads back; two clients connecting to a server and seeing each other move.
3. **Core value.** The core loop or core job working end to end.
4. **Supporting features**
5. **Production readiness.** Persistence, accounts, deployment, operations.
6. **Experience and content**
7. **Hardening.** Performance, security, reliability, accessibility.
8. **Release**

Every phase needs a goal and an **exit criterion** that is a demo or a verifiable state.

`docs/development/roadmap.md` contains:
- a phase table with goal, exit criterion, task range and phase dependencies
- a Mermaid flowchart of how the phases depend on each other

Add dates only if the user gave them.

## Tasks

### Sizing

A task is a coherent unit that can be implemented, verified and documented in one fresh session.

- Fold setup, configuration and doc updates into the task that needs them.
- Split only where a reviewer could reasonably reject one part while approving the other.
- Avoid microtasks, and avoid vague tasks like "make multiplayer".

### Vertical slices

Prefer **tracer bullets**: narrow but complete paths through every layer, each demoable on its own. Foundations and wide mechanical changes are the exceptions.

### Types

| Type | Purpose | Output |
|---|---|---|
| `build` | Delivers features | Working, verified behaviour |
| `spike` | Timeboxed experiment that answers one question | A decision plus notes; the code is throwaway |
| `decision` | Resolves a deferred decision | Updated DESIGN.md and an ADR |
| `chore` | Tooling, setup, admin | Whatever the chore requires |

Every Deferred or Open decision becomes a spike or decision task. It blocks the first task that needs its answer.

### Priority

| Priority | Meaning |
|---|---|
| P0 | Blocks everything; critical path |
| P1 | Essential to the MVP |
| P2 | Required for v1, not for the MVP |
| P3 | Polish or optional |

Work you recommend that DESIGN.md doesn't require is titled `Optional: …`. It never outranks unfinished required work.

### Task statuses

Not started · In progress · Blocked · Done · Deferred · Cancelled

`Done` means the acceptance criteria were verified.

### Block format

Tasks are grouped into `tasks/phase-NN-<slug>.md` files (template: `templates/phase.md`):

```markdown
### T-006 · Walk and sprint on flat ground
- **Status:** Not started
- **Priority:** P1
- **Type:** build
- **Phase:** 2 · Walking skeleton
- **Features:** CORE-001
- **Blocked by:** T-003, T-004
- **Outcome:** What exists when this is done, from the user's or player's point of view.
- **Touches:** Player section, input config (systems or wiki sections; file paths only for code that already exists)
- **Acceptance criteria:**
  - [ ] Objective, checkable criterion
  - [ ] Another
- **Verify:** The minimal proof: a command, a test name, or manual steps with the expected result.
- **Docs to update:** wiki/player, feature-inventory, CHANGELOG
- **Risks:** —
```

Use `—` for empty fields.

### Files

- **`tasks/backlog.md`** is the index (template: `templates/backlog-index.md`). Every task appears as one row with: ID, title, phase, priority, type, status, blocked by.
- **`tasks/phase-NN-<slug>.md`** holds the full task blocks.
- **`tasks/README.md`** (template: `templates/tasks-README.md`) explains how the task system works:
  - picking work from the ready frontier, highest priority first
  - updating statuses
  - adding new tasks with the next free ID
  - the definition of done
  
  It also lists the current ready frontier and the recommended first task.

Mirror tasks to GitHub Issues only if the user chose that in the workflow area and `gh` is authenticated. The local files stay the source of truth and record the issue numbers.

## Reconciliation

Check all of the following before moving on:

- every in-scope feature (anything not N/A or Deferred) has at least one task
- every build task lists at least one feature
- task ↔ feature links agree in both directions
- walking DESIGN.md section by section, every requirement maps to a feature
- priorities make sense: no P0 or P1 task is blocked by a P2 or P3 task, and MVP features have their tasks in MVP phases
- the dependency graph has no cycles, and the ready frontier isn't empty

## Final audit

Before reporting, confirm each item below and fix whatever fails:

- DESIGN.md reflects every Decided and Delegated decision, and the Delegated calls are listed for review
- every significant requirement is in the inventory and has tasks
- the roadmap order matches the task dependencies
- the README orients a newcomer and links the docs
- CLAUDE.md sets the working rules and includes the git rules
- the wiki is navigable, and every section separates planned from implemented
- the architecture docs describe no infrastructure as existing that doesn't exist yet
- limitations, risks, open questions and deferred items are all recorded
- CHANGELOG and VERSION agree
- the checker script has been run and its errors fixed
- nothing was implemented during the kickoff

Files existing with the right names isn't completion. The real test is whether a fresh session could read CLAUDE.md, pick the first task, and run with it.
