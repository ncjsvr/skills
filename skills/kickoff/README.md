# kickoff

A Claude Code skill for the planning stage of a software project. Run `/kickoff` and Claude researches your idea to work out what needs deciding, asks you in multiple-choice rounds, and keeps researching and adapting its questions as you answer, until nothing is left unanswered. It then writes the design doc, ADRs, glossary, a wiki folder for each section of the project, a feature inventory, a roadmap and a dependency-ordered task backlog, verifies the result, and stops before any building starts.

## Install

You need Node.js 22.20 or later. Then run:

```text
npx skills add ncjsvr/skills --skill kickoff -g
```

The CLI detects your coding agents (Claude Code, Codex, Cursor and others) and asks which to install into; add `-a <agent>` to pick one directly. `-g` installs it for all your projects; leave it off to install into the current project only.

To install by hand instead, copy this folder into your agent's skills folder. For Claude Code, that's `~/.claude/skills/kickoff/` (on Windows: `%USERPROFILE%\.claude\skills\kickoff\`).

## Use

```text
/kickoff                                    start (or resume) in the current repo
/kickoff a recipe-sharing app for families  give it the pitch up front
/kickoff see notes/idea.md                  seed it from your notes
```

## Your conventions

Kickoff follows the git and coding rules in your global `~/.claude/CLAUDE.md` and the project's `CLAUDE.md` (for example, commit message style, or who pushes). Put personal rules there.

To check a kickoff's output by hand, run:

```text
python scripts/check_kickoff.py --root <project>
```

## What's inside

| Path | Purpose |
|---|---|
| `SKILL.md` | The workflow: orient → research → grill (ask, adapt, re-research) → challenge → lock → document → plan → verify → report |
| `references/documentation.md` | Doc set layout and rules |
| `references/backlog.md` | Feature, roadmap and task rules, plus the final audit |
| `templates/` | Starting files for every output document |
| `scripts/check_kickoff.py` | Consistency checker (Python 3, standard library only) |

## Background

Kickoff is my own design. It grew out of the prompt I wrote to bootstrap new game projects in Claude Code: understand the idea completely, document it properly, plan the work, and only then start building. Kickoff turns that into a reusable skill that works for any software project and finds its own questions instead of following a fixed list.
