# Documentation set

Read this in phase 6. Adapt the layout to the repo's existing conventions, and create a file only when it has real content.

```text
README.md
CLAUDE.md
CHANGELOG.md
VERSION                         only if the project is versioned
docs/
├── README.md                   map of all documentation (templates/docs-README.md)
├── DESIGN.md                   what and why: the authoritative design
├── GLOSSARY.md                 project vocabulary
├── decisions/NNNN-slug.md      ADRs
├── wiki/
│   ├── README.md               wiki home: sections, one line each, with status
│   └── <section>/
│       ├── README.md           section overview
│       └── <topic>.md          only when a section has distinct sub-systems
├── development/
│   ├── feature-inventory.md    see backlog.md
│   ├── roadmap.md              see backlog.md
│   ├── risks.md
│   ├── limitations.md
│   └── open-questions.md
└── kickoff/
    ├── state.md
    ├── decision-log.md
    ├── research.md             sources and findings that shaped the questions
    └── report.md
tasks/                          see backlog.md
```

**An existing GDD, spec or design doc** stays where it is. Either make it the authoritative source or fold it into DESIGN.md, but never keep two conflicting versions. `docs/README.md` states which one is authoritative.

**Planned versus real.** In greenfield mode everything is planned. Never describe a system that doesn't exist yet in the present tense as if it's built. Every wiki section carries a status line.

## DESIGN.md (`templates/DESIGN.md`)

The single source of truth for intent.

- Write decisions as plain statements tagged with their decision IDs, e.g. `[D-014]`.
- Mark facts *verified (source, date)* or *assumed*.
- Delete template sections that don't apply. Where a reader would expect a section, state its absence in one line instead ("Single-player only [D-020]").
- Section 3 holds the behaviour detail: core loop for a game, user stories for an app, the command set for a CLI, the public API for a library. Give each major feature area its own subsection.
- After Architecture, add one section per area of the question map that produced decisions. The areas come from research, so the sections differ from project to project.
- Collect Delegated calls in their own section so the user can review them in one place.

## ADRs (`templates/adr.md`)

Write an ADR only when **all three** apply:

1. it is hard to reverse
2. it would surprise a future reader without context
3. it came from a real trade-off

Typical subjects: platform, engine or stack; architectural shape; data store; network or authority model; hosting; auth provider; deliberate deviations from the obvious path; constraints that aren't visible in code; rejected alternatives whose rejection isn't obvious.

Number them from `0001`, and link each ADR from DESIGN.md and the relevant wiki section.

## GLOSSARY.md (`templates/GLOSSARY.md`)

- Project-specific terms only; general programming terms don't belong.
- Be opinionated: pick one term per concept and list the synonyms to avoid.
- Definitions are one or two sentences saying what the thing *is*, with no implementation detail.
- Use these terms everywhere: DESIGN.md, the wiki, task titles, and later in code names.

## Wiki (`templates/wiki-section.md`)

**Sections.** Create one section folder per major part of the software, as the user would think about it. Derive them from DESIGN.md, not from a fixed list. Examples:

| Project type | Example sections |
|---|---|
| Game | `core-loop`, `player`, `combat`, `world`, `multiplayer`, `persistence`, `ui`, `audio`, `server-infrastructure`, `build-and-release` |
| Web app | `accounts`, `<core-domain>`, `notifications`, `admin`, `api`, `infrastructure` |
| CLI or library | `commands` or `public-api`, `configuration`, `<core-domain>`, `distribution` |

Add cross-cutting sections only when they have content: `development-setup`, `configuration`, `build-and-deployment`, `testing`, `troubleshooting`.

**Rules.**
- Folder names are lowercase-kebab.
- Each folder's README follows the template. Add subpages only for distinct sub-systems that have enough to say.
- The wiki explains *how* each part works or will work; DESIGN.md says *what* and *why*. Summarise and link to the DESIGN section and ADRs rather than restating requirements.
- Use Mermaid for architecture, flows, state machines and sequences wherever a picture is clearer than prose.
- The wiki home (`docs/wiki/README.md`) lists every section with a one-line description and its status.

## Development docs

**`risks.md`** is a table:

| ID | Risk | Likelihood | Impact | Mitigation (decision, task or ADR) | Status |
|---|---|---|---|---|---|

Include everything the pre-mortem surfaced. IDs follow the pattern `R-01`.

**`limitations.md`** records environment and tooling limits found during the audit or the interview. For each limit, record the evidence, its impact, alternatives tried, and the workaround. Don't call a limit inherent to the platform when it's really a limit of the installed tooling. Also list useful capabilities you discovered (MCP tools, CLIs, automations), so future sessions know what they can automate.

**`open-questions.md`** lists every Open and Deferred decision with:
- the question
- why it matters
- the recommended default
- the trigger: "decide before T-0NN starts"
- who answers it
- the matching spike or decision task

## README.md (`templates/README.md`)

Written for someone opening the repo for the first time. Keep it under about 80 lines and put detail in the wiki. Never claim the project is playable, buildable or deployable until that has been verified.

## CLAUDE.md (`templates/CLAUDE.md`)

Concise, actionable working rules for future sessions. If a CLAUDE.md already exists, merge into it: keep its rules, never weaken them, and note any conflicts. Include the git and coding conventions decided in the workflow area, plus any from the user's global CLAUDE.md.

## CHANGELOG.md

Keep a Changelog style, written for a public audience.

- Start with `## [Unreleased]` and `### Added — Project design, documentation and development plan.`
- Later entries use the categories Added, Changed, Fixed, Removed, Security and Performance.
- No secrets or internal operational detail.

## VERSION

Create it only if the project ships versions.

- Use SemVer, staying on `0.x` during early development.
- Use `0.0.0` until the first build lands, and note that choice in the README.
- Keep any existing version as it is.
- No tags or releases during kickoff.
