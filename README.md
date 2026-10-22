# Skills

Agent skills for software engineering. They work with Claude Code and any other agent supported by [skills.sh](https://skills.sh).

## Install

```text
npx skills add ncjsvr/skills --skill kickoff -g
```

This needs Node.js 22.20 or later. The CLI detects your coding agents and asks which to install into. Leave off `-g` to install into the current project only.

## Skills

| Skill | What it does |
|---|---|
| [kickoff](skills/kickoff/) | Pre-implementation kickoff for software projects. Researches your idea to find every question that needs answering, asks them as multiple choice, adapts as you answer, then writes the design, ADRs, glossary, a per-section wiki, feature inventory, roadmap and task backlog, and stops before any code is written. |

## Licence

[MIT](LICENSE)
