# Submission checklist (Assignment.md "What you submit" and the rubric)

Due Sat 2026-11-07 11:59 p.m. The graded version is the last push to the PR branch before the deadline.
Status: ✅ done · 🔨 in progress · ⬜ not started · 👤 only I can do it.

## Hand-in

| Item | Where | Status |
|---|---|---|
| One PR to `columbia-university-ai-games/game-dev-f26` `main`, only this folder and one workflow | branch `lululizzy8/midterm` | ⬜ local commits only so far; push and open the PR tonight |
| PR description: GitHub login, project title, links to README, EVALUATION, AGENT-TEAM, playtest notes, recording | PR | ⬜ 👤 |
| PR URL submitted on CourseWorks | CourseWorks | ⬜ 👤 |
| Workflow runs this folder's checks on PRs, no secrets | `.github/workflows/midterm-lululizzy8.yml` | ✅ (green run link ⬜ after the push) |
| No caches, credentials, personal data or large generated files in the diff | `.gitignore`; session exports cleaned | 🔨 final check before the push |

## Required files in this folder

| File | Contents required | Status |
|---|---|---|
| `README.md` | commands from a fresh clone, scope statement, rule/source map with labels, sources and reuse terms, recording link | ✅ recording linked |
| `EVALUATION.md` | declared suite, comparison table, traces, CI evidence, limitations | ✅ revolution suite written up; CI link ⬜ after the push |
| `AGENT-TEAM.md` | each agent, what it could see and do, what it recommended, what I decided, evidence | 🔨 "why" column and "What I would change" 👤 |
| Peer playtest notes, received and given | [`playtest.txt`](playtest.txt) | ✅ received (in this folder); my notes for my partner sent to them directly |
| Recording, 3 to 5 min, agent playing without manual moves, limits stated | link in README and PR | ✅ https://youtu.be/zRIMSmfkGlA (add to the PR) |
| Game, model player, baseline, tests, agent config, reports, traces | this folder | ✅ |

## Agent-team evidence (check 3d)

| Role | Artifact | Evidence of use | Status |
|---|---|---|---|
| Implementation agent | `CLAUDE.md` | cleaned session exports in `sessions/` | ✅ three exports (email, project ID, local paths and LAN address removed) |
| Reusable skill | `.claude/skills/ddz-rule-change/SKILL.md` | used for each rule change, called by name | ✅ called by name for Revolution (Nov 7, in `sessions/`) |
| Reusable skill | `.claude/skills/ddz-eval-run/SKILL.md` | called by name | ✅ called by name for the revolution held-out run (Nov 7) |
| Independent review | `.claude/agents/ddz-rules-reviewer.md` | findings in `reviews/` | ✅ runner, notes, two-deck and revolution reviews ("My decisions" 👤) |
| Design reviews | `reviews/2026-10-28-design-review*.md` | 3 reviewers on rev 1 and 2 | ✅ ("My decisions" 👤) |

## Rubric checks

| Check | Evidence | Status |
|---|---|---|
| 1a labels | README map, every rule labeled with a locator | ✅ Pagat locators checked against the page headings (2026-11-07) |
| 1b scope | README scope and Week 3 posts | 🔨 Week 3 posts for two decks and Revolution 👤 |
| 1c sources | README sources and reuse terms | ✅ |
| 2a core loop | `play.py`; browser card table `web/` (Pyodide; home screen, handbook, watch baseline, watch AI via `web/serve.py`; `tests/test_web.py`, `tests/test_serve.py`) | ✅ reworked after the [playtest](playtest.txt) |
| 2b model player | `players/model.py` via `runner.py`; traces show choices; fallbacks labeled | ✅ revolution held-out run 2026-11-07 (`traces/heldout-revolution/`, 310 live, 1 labeled fallback) |
| 2c information | `test_game.Information`, `test_view`, `test_runner.Prompt`, `test_web`, `test_serve` | ✅ |
| 3a runs | fresh-clone dry run of the README commands | ✅ 2026-11-07: clean clone, tests, runner, fixture, report, measure, play.py |
| 3b limits | `runner.py` and `tests/test_runner.py` | ✅ |
| 3c CI | all five kinds, 102 tests (map in EVALUATION.md) | 🔨 green run on GitHub ⬜ after the push |
| 3d agent team | table above | ✅ |
| 4a choices | GAME-DESIGN.md §11 | ✅ |
| 4b experiment | heuristic baseline, paired deals, 30 held-out seeds, three memory variants | ✅ |
| 5a comparison | EVALUATION table with all fields, dated suite, held-out | ✅ revolution held-out 2026-11-07 (`results/heldout-revolution-2026-11-07.md`); older suites kept as superseded |
| 5b authorship | AGENT-TEAM and limitations in my voice, playtest notes used | 🔨 limitations ✅; AGENT-TEAM "why" column 👤 |
| 5c recording | 3 to 5 min | ✅ https://youtu.be/zRIMSmfkGlA |

## Other dated obligations

- ✅ Week 3 post with the scope change from Guandan.
- ⬜ 👤 Week 3 posts for two decks (Nov 6) and Revolution (Nov 7).
- ✅ Peer playtest done; notes received in [`playtest.txt`](playtest.txt); my notes sent to my partner.
- ⬜ 👤 Before Nov 16: silent-playtester notes on three assigned recordings (assigned Nov 9).
