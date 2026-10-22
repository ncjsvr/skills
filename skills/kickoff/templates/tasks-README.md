# Tasks

How work is planned and tracked for <Project>. The [backlog](backlog.md) indexes every task, and each `phase-NN-*.md` file holds the full specs.

## Picking work

1. Find the **ready frontier**: tasks that are `Not started` and whose `Blocked by` tasks are all `Done`.
2. Take the highest priority (P0 before P1, and so on), then the lowest ID.
3. Read the task's linked features, DESIGN.md sections, wiki section and ADRs before starting.

## Statuses

Not started · In progress · Blocked · Done · Deferred · Cancelled

**Done** means every acceptance criterion was verified as described under **Verify**.

## Definition of done

- The acceptance criteria are verified, with evidence.
- Everything listed under **Docs to update** is updated in the same change.
- The task status, feature status and `backlog.md` row are updated.
- A CHANGELOG entry is added under Unreleased for any user-visible change.
- The work is committed following the git rules in CLAUDE.md.

## Adding tasks

Use the next free `T-` ID. Never reuse or renumber IDs. Link at least one feature (except for chores, spikes and decisions), set `Blocked by`, and add a row to `backlog.md`.

## Ready frontier now

| ID | Title | Priority | Type |
|---|---|---|---|
| T-001 | <title> | P0 | chore |

**Recommended first task:** T-<NNN>, because <reason>.
