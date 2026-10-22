# <Project>: instructions for Claude

<One-line description of the project.>

**Development status: NOT YET AUTHORISED.** Kickoff finished on <YYYY-MM-DD>. Don't start any task until the user says development can begin; then change this line to record the date it was authorised.

## Read first

- [docs/DESIGN.md](docs/DESIGN.md): what we're building and why. It is authoritative.
- [docs/GLOSSARY.md](docs/GLOSSARY.md): use these terms in docs, task titles and code names.
- [docs/wiki/README.md](docs/wiki/README.md): how each part works.
- [tasks/README.md](tasks/README.md): how to pick, do and finish work.
- [docs/decisions/](docs/decisions/): the ADRs. Follow them.

## Each session

1. Check `git status` and the current task states.
2. Take the highest-priority task from the ready frontier, unless the user names another.
3. Read the task's linked design sections, wiki section and ADRs. Inspect the existing code before changing it.
4. Implement it, then verify it against the acceptance criteria. Report success only with evidence.
5. In the same change, update the task and feature statuses, the wiki section, the CHANGELOG (Unreleased), and everything listed under the task's "Docs to update".
6. Commit, then end the session with a short report: what was done, how it was verified, what's next, and anything blocked.

## Rules

- Follow DESIGN.md and the ADRs. Before diverging from a decision, record the change as a new decision or ADR.
- Do as much as the available tools allow. Ask the user only for things that genuinely need them.
- Record limitations, failed approaches and workarounds in [docs/development/limitations.md](docs/development/limitations.md).
- Preserve existing work. Use only non-destructive git operations.
- Keep verification proportionate: run the checks that prove the task.
- Suggest a version bump at milestones. Tag or release only when asked.

## Git

<The git and commit conventions decided during kickoff, plus any from the user's global CLAUDE.md.>
