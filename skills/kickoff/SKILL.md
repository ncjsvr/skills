---
name: kickoff
description: Pre-implementation kickoff for software projects. Researches the idea to discover every question that needs answering, grills the user in multiple-choice rounds, and keeps researching and adapting its questions until nothing is left unanswered, then writes the design doc, ADRs, glossary, a wiki folder per section, feature inventory, roadmap and a dependency-ordered task backlog, and stops before any code is written. Use when the user runs /kickoff, or asks to kick off, scope, spec or plan a new software project or major feature before building it.
---

# Kickoff

Take a software project from idea to fully decided, documented and planned before any code is written. You ask, the user decides, you document and plan, then you stop.

Kickoff is always about **software engineering**: what the software does, how it is built, and how it is delivered. Business topics (pricing, marketing, budgets, costs) are out of scope.

Kickoff produces **decisions, documents and tasks**. Reading the repo, lightweight environment checks, research, writing docs and task files, `git init` and commits are all part of it. Product code, scaffolding, installing dependencies and creating framework or engine projects wait until the user explicitly authorises development after the final report. A decision that can only be settled by building something becomes a spike task in the backlog.

## Principles

- **Facts are yours, decisions are theirs.** Look facts up (repo, files, CLIs, MCP tools, web) rather than asking for them. Put every decision to the user.
- **Never invent.** Requirements, versions, capabilities and completed work come from the user, the environment or a cited source. Mark each fact *verified* (source, date) or *assumed*.
- **One home per fact.** DESIGN.md says what and why, ADRs record hard trade-offs, the wiki explains how each section works and links back, and tasks say what to build. Link instead of copying.
- **Research finds the questions; the user answers them.** There is no fixed question list. Research what this particular idea needs decided, ask, then let every answer reshape the questions and send you back to research. Research also supplies the facts behind the options, but never makes the decision.
- **Preserve.** Keep existing code, docs, history and config. Record what exists rather than reshaping it.
- **Follow the user's rules.** Apply the git and coding conventions in the user's global and project `CLAUDE.md`.

## Asking: always multiple choice

Put every decision as a multiple-choice question so the user can click instead of typing.

- **In Claude Code, use `AskUserQuestion`.** That means up to 4 questions per call, 2–4 options each, and a header of 12 characters or fewer. Put your recommended option first and end its label with " (Recommended)". Use each option's description for its one-line trade-off. Set `multiSelect` when choices combine (platforms, MVP features). The tool adds an "Other" row for free text, so don't add your own.
- **On other surfaces**, use whatever multiple-choice tool exists. If there is none, print numbered questions with lettered options, mark the recommendation ⭐, and tell the user they can reply in shorthand (`1a 2c 3b`, or `ok` to accept every ⭐).
- **Before each call**, write one or two lines covering the area, why it matters, and any facts you found that bear on it.
- **Make the options good.** They are your thinking. Each should be distinct, concrete and realistic, built from the user's own words and from what you found. Offer ranges for quantities. If you're unsure of the space, include a broader option rather than forcing a narrow choice.
- **The only free-text moment** is the opening pitch, and only if the user didn't supply one.
- **Read every "Other" answer carefully.** It may open new branches, contradict an earlier decision, or carry an instruction such as pause, skip or "you decide".

## Process

Work through the phases in order. After every round, update `docs/kickoff/state.md` and `docs/kickoff/decision-log.md` (templates in `templates/`) so the session can be resumed from disk at any point.

### 1. Orient (silently, before the first question)

1. **Resume check.** If `docs/kickoff/state.md` exists, read it and the decision log, then ask:
   - resume where we left off (Recommended)
   - refine the locked design
   - start over (archive the old state to `docs/kickoff/archive/`)

   A design that is already Locked or Complete defaults to **refine mode**: ask only about gaps and requested changes, then update the docs and tasks in place.
2. **Read** the global and project `CLAUDE.md` files if accessible, plus anything the user passed with the command (text, file paths, links).
3. **Audit the workspace.** Check:
   - the repo root and git status
   - existing README, CLAUDE.md, design docs, notes, task lists and changelogs
   - source, assets and config
   - available toolchains, engines, CLIs and MCP servers (inspect what they actually expose)

   Then set the **mode**:
   - *greenfield*: nothing built yet
   - *brownfield*: an existing implementation; document what is real versus planned
   - *feature*: a major addition to an existing project; extend its docs and backlog and continue its numbering
4. **Create** `docs/kickoff/state.md` and `docs/kickoff/decision-log.md`. Don't touch anything else yet.

### 2. Frame

1. **Seed.** Take the pitch from the user's message or files. Otherwise ask for a few sentences.
2. **Play it back** in under 150 words: what the software is, who uses it and what it must do. Add anything from the audit that changes the picture, such as a constraint, a conflict or an existing implementation. If it's really several independent projects, say so and propose doing them one at a time.
3. **Research the territory.** Find every question that must be answered before *this* idea can be built. Use web search and fetch (WebSearch/WebFetch in Claude Code), run several lines of research in parallel subagents if available, and prefer primary sources such as official docs. Look at:
   - similar products and open-source projects: their features, how they're built, and what users complain about
   - architecture and stack write-ups for this kind of software, and the docs of technologies likely to be involved
   - postmortems, "lessons learned" posts and common failure modes
   - the repo and any notes the user gave you

   Research stays on engineering. Findings about pricing, markets or competitors' business models don't become questions. Record each useful finding in `docs/kickoff/research.md` (template in `templates/`) with its source and date. If there's no web access, research from the repo and your own knowledge, and say so in the report.
4. **Build the question map.** Turn the research and the idea into areas named for this project (for example "Matchmaking", "Offline sync", "Plugin API"). Under each area, list its open questions with why each matters, its door type and the source that raised it. Save the map in state.md. Show it in a few lines (areas and question counts), and confirm it with one question: looks right / add an area / drop an area.
5. **Explain the format once, briefly.** Questions come in rounds with the recommended answer first, and "Other" covers anything else. At any point the user can type *pause*, *status*, *you decide this area*, *skip area* or *back to <area>*. Progress is saved after every round.

### 3. Grill

The question map is a **design tree**: each decision branches into the decisions that depend on it. The **frontier** is every open question whose prerequisites are settled. Repeat the steps below until the exit criterion holds.

Be **relentless**. Ask every question that would change what gets built or how, and keep looking for more. The interview ends when the exit criterion holds, not when it starts to feel long. If the user is flagging, offer to delegate or defer the remaining low-stakes areas. Never skip them silently.

1. **Pick the batch** of up to 4 frontier questions.
   - Ask **one-way doors** first. These are decisions that are expensive to reverse: platform, language, framework or engine, architecture, data store, network or authority model, scope.
   - Next, ask whatever unblocks the most other decisions.
   - Go breadth-first across purpose, scope, platform and architecture before going deep anywhere.
   - If a question depends on another question in the same batch, hold it for a later batch.
2. **Facts first.** If a question needs a fact (current versions, a library's capability, what the repo already does), find it before asking. Dispatch a subagent if available, and ask the questions that don't depend on it in the meantime.
3. **Ask**, following the rules above.
4. **Record.** Append each answer to the decision log as `D-NNN`, with area, answer, status, door type and rationale. Statuses:
   - *Decided*: the user chose, including picking your recommendation
   - *Delegated*: the user handed it to you; it's your call, flagged for review
   - *Deferred*: consciously postponed, with the trigger that will force it
   - *Open* or *N/A*
5. **Adapt the map.** After every batch:
   - add the questions the answers raised
   - drop the questions the answers made irrelevant
   - reword questions whose options have changed

   When an answer brings in something new (a technology, a platform, a feature, a constraint), research it before the next batch: its limits, its gotchas, and the decisions it forces. Add what you find to research.md and the map. Then recompute the frontier.
6. **Sharpen as you go.**
   - **Big forks** (stack, architecture, data store, hosting): first write a short message laying out 2–3 real approaches, what each trades off and your recommendation. Then ask, using those approaches as the options. Note the decision as an ADR candidate.
   - **Scenarios.** Stress-test rules and boundaries with concrete edge cases, still as multiple choice. For example: "Two users save the same record at once: a) last write wins b) the second save is rejected c) changes merge". Draw scenarios from the failure modes your research found.
   - **Fuzzy terms.** When a word is vague or overloaded, offer precise canonical terms as options and record the winner as a glossary candidate.
   - **Contradictions.** When an answer conflicts with an earlier decision, put the conflict to the user in the next batch.
   - **Unknowable by talking** (feel, performance, whether an API really works): mark the decision Deferred → spike, and record the question the spike must answer.
   - **Low-stakes areas.** When an area is mostly two-way doors, open it with one question: ask me each / use your recommendations and show me the list / defer the area. Recommendations accepted this way are *Delegated*.
7. **Play back** each area as it completes, in under 200 words. State the user's decisions as theirs and mark your delegated calls as yours. End with one confirm question: correct / something's wrong / reopen a decision.

**Exit criterion.** All of these must hold:
- every question in the map is answered (Decided, Delegated or N/A) or Deferred with a trigger
- no one-way door is still Open
- no contradictions are unresolved
- a **final research sweep** against the decided design (the pitfalls of the chosen stack, how similar projects failed, anything the design touches that no question has covered) turns up no new question that would change what gets built. If it does, add those questions and keep going.

**Long sessions.** State is saved on disk, so when the context gets heavy, suggest the user continue in a fresh session by running `/kickoff` again.

### 4. Challenge

1. **Draft** `docs/DESIGN.md` from the decision log, using `templates/DESIGN.md`.
2. **Builder check.** Dispatch a fresh subagent, or do it yourself if none is available, with this prompt: *"Act as the engineer who will build this, working only from docs/DESIGN.md with no chance to ask its author anything. Before you could write a build plan, what would you have to guess? List those gaps, most damaging first, each with what goes wrong if the guess is wrong. Leave out choices the design hands to the builder and anything a competent engineer would settle alone."* Sort what comes back into three piles:
   - already answered: fix the doc
   - minor: decide it yourself and mark it Delegated
   - theirs: ask the user
3. **Pre-mortem.** Assume it's six months from now and the build has stalled or the software keeps breaking. Generate the 5–7 most likely technical causes given this design and ask which are real concerns (multiSelect). Give each selected cause a mitigation: a decision, a task or a risk entry.
4. **MVP cut.** Propose where the line falls between MVP and later, and confirm it (multiSelect for anything the user wants to move).
5. **Resolve.** Ask the "theirs" questions and settle whatever the pre-mortem raised. If this opens up new areas, add them to the map and return to the Grill loop.

### 5. Lock

Show a one-screen **design brief** containing:
- what the software is and what it must do
- the ~10 decisions that shape everything else
- the list of Delegated calls, so the user can veto any of them
- Deferred items and the top risks

Ask: lock it (Recommended) / change something / keep going on an area. On lock, set the state to Locked and commit `docs/kickoff/` and `docs/DESIGN.md`.

### 6. Document

Read `references/documentation.md` and produce the doc set, adapted to any existing repo conventions:
- README, CLAUDE.md, CHANGELOG, and VERSION if the project is versioned
- the docs index and the finished DESIGN.md
- ADRs and GLOSSARY.md
- a wiki folder for each section of the software
- the development docs: risks, limitations and open questions

### 7. Plan

Read `references/backlog.md` and produce the feature inventory, roadmap and task backlog. The backlog needs:
- phases ordered by real dependencies, with a walking skeleton early
- tracer-bullet vertical slices
- a spike or decision task for every Deferred item
- objective acceptance criteria and explicit blocking edges
- the ready frontier: tasks whose blockers are all done

Then reconcile: every in-scope feature has tasks, and every build task traces back to a feature.

### 8. Verify

Run `python3 "${CLAUDE_SKILL_DIR}/scripts/check_kickoff.py" --root .`. The script lives in this skill's `scripts/` folder; on Windows use `python` or `py`.

It checks IDs, cross-references, dependency cycles, links, leftover placeholders, status values and Open one-way doors, and prints the ready frontier. Fix every error and judge each warning. If Python isn't available, do the same checks by hand and say so.

Then run the final audit in `references/backlog.md`. Report only checks you actually ran.

### 9. Report and stop

Write `docs/kickoff/report.md` from `templates/report.md` and commit, following the user's git conventions. Then give the user a short summary covering:
- what was created, with real counts
- phases and key dependencies
- the recommended first task
- Delegated calls worth a second look
- open and deferred items
- verification results
- anything only the user can do

Then stop. Development starts only when the user explicitly says so.
