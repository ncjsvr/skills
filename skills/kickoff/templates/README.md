# <Project>

<What it is, in one or two sentences.>

**Status:** Pre-implementation. The design and development plan are complete; development hasn't started. <Version 0.0.0 until the first build lands.>

## Purpose

<2–4 lines: who uses it, the problem it solves, the principles.>

## What it does

<The core loop, core journey or core job, in a few lines.>

## Tech

| Area | Decision |
|---|---|
| <Engine / framework> | <choice> ([ADR-0001](docs/decisions/0001-slug.md)) |

## Repository layout

```text
docs/    design, glossary, ADRs, wiki, development docs
tasks/   backlog and phase task specs
```

## Documentation

- [Design](docs/DESIGN.md)
- [Wiki](docs/wiki/README.md)
- [Decisions](docs/decisions/)
- [Roadmap](docs/development/roadmap.md)
- [Tasks](tasks/README.md)

## How development works

Work is planned as tasks with dependencies and acceptance criteria in [tasks/](tasks/). Claude Code works from [CLAUDE.md](CLAUDE.md): it picks the next ready task, implements and verifies it, and updates the docs and changelog in the same change. <Build and run instructions get added here once they have been verified.>

## Versioning

<SemVer; 0.x during early development. Changes are recorded in [CHANGELOG.md](CHANGELOG.md).>
