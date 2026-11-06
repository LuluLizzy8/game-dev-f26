# Submission checklist (Assignment.md "What you submit" + rubric)

Due **Sat 2026-11-07 11:59 p.m.** Graded version = last push to the PR branch before the deadline.
Status: ✅ done · 🔨 in progress · ⬜ not started · 👤 only LuluLizzy can do it.

## Hand-in

| Item | Where | Status |
|---|---|---|
| One PR to `columbia-university-ai-games/game-dev-f26` `main`, only this folder + one workflow | branch `lululizzy8/midterm` | ⬜ (local only until done; push and open by Nov 6) |
| PR description: GitHub login, project title, links to README, EVALUATION, AGENT-TEAM, peer notes, recording | PR | ⬜ 👤 |
| PR URL submitted on CourseWorks | CourseWorks | ⬜ 👤 |
| Workflow runs this folder's checks on PRs, no secrets | `.github/workflows/midterm-lululizzy8.yml` | ✅ (green run link: ⬜ after push) |
| No caches, credentials, personal data, large generated files in the diff | `.gitignore`, review before push | 🔨 |

## Required files in this folder

| File | Contents required | Status |
|---|---|---|
| `README.md` | setup / play / test / evaluation commands from a fresh clone, working dir for each; scope statement; rule/source map with labels; sources + reuse terms; recording link | 🔨 (scope 👤 in my voice; recording link ⬜) |
| `EVALUATION.md` | declared suite, comparison table, traces/links, CI evidence for this version, limitations paragraph | 🔨 (limitations 👤) |
| `AGENT-TEAM.md` | one-page log: each agent, what it could see/do, what it recommended, what I decided, where the evidence is | 🔨 draft from the repo history; rewrite in my voice 👤 |
| Peer playtest notes, received and given | `peer-notes/` | ⬜ 👤 (playtest week of Nov 2, notes by Nov 6) |
| Recording, 3–5 min, agent playing without manual moves, limits stated | link in README + PR | ⬜ 👤 |
| Game, executable player, baseline, tests, agent configs, reports, traces | this folder | 🔨 |

## Agent-team evidence (check 3d)

| Role | Artifact | Evidence of use | Status |
|---|---|---|---|
| Implementation agent | `CLAUDE.md` | exported session transcripts in `sessions/` (cleaned) | ✅ `sessions/2026-11-game-creation.txt` (project ID, LAN IP and local paths removed); other sessions optional 👤 |
| Reusable skill | `.claude/skills/ddz-rule-change/SKILL.md` | used for each rule change; invoked by name in ≥ 2 sessions | 🔨 (steps followed for R19 + regressions in this session; named invocations 👤 in folder sessions) |
| Reusable skill | `.claude/skills/ddz-eval-run/SKILL.md` | invoked by name in ≥ 2 sessions | 🔨 (steps followed for tuning and held-out runs; named invocations need a session started in this folder 👤) |
| Independent review | `.claude/agents/ddz-rules-reviewer.md` | findings in `reviews/` (`2026-10-28-runner-review.md`) | ✅ first run (decisions 👤) |
| Design reviews | `reviews/2026-10-28-design-review*.md` | 3 reviewers on rev 1–2 | ✅ (my decisions 👤) |

Skills are found by Claude Code only when a session is started in `midterms/lululizzy8/`.

## Rubric checks

| Check | Evidence | Status |
|---|---|---|
| 1a labels | README map, every rule labeled with locator | 🔨 (Pagat locators to verify 👤) |
| 1b scope | README scope + Week 3 post | 🔨 (Week 3 post ✅; README scope 👤) |
| 1c sources | README + DESIGN §9 | 🔨 (RLCard/DouZero licences if cited) |
| 2a core loop (two decks since 2026-11-06; Week 3 post 👤) | `play.py` start to end; browser version `web/` (same engine via Pyodide, `tests/test_web.py`) | ✅ built (peer playtest 👤) |
| 2b model player | `players/model.py` via `runner.py`, trace shows choices, fallbacks labeled | 🔨 built; held-out runs ✅ 2026-11-06, two decks (`traces/heldout-2deck/`, 310 live, 4 labeled fallbacks) |
| 2c information | `tests/test_game.Information`, `test_view`, `test_runner.Prompt` | ✅ |
| 3a runs | fresh-clone dry run of README commands | ⬜ |
| 3b limits | `runner.py` + `tests/test_runner.py` | ✅ |
| 3c CI | all five kinds present, 55 tests (map in EVALUATION.md) | 🔨 green run on GitHub ⬜ after push |
| 3d agent team | table above | 🔨 |
| 4a choices | DESIGN §11 | ✅ |
| 4b experiment | heuristic baseline, paired deals, 30 held-out seeds; three memory variants | ✅ run and interpreted in EVALUATION |
| 5a comparison | EVALUATION table with all fields, dated suite (`6795857`), held-out | ✅ two-deck held-out 2026-11-06 (`results/heldout-2deck-2026-11-06.md`); one-deck kept as superseded |
| 5b authorship | AGENT-TEAM + limitations in my voice, peer notes used | ⬜ 👤 |
| 5c recording | 3–5 min | ⬜ 👤 |

## Other dated obligations

- ✅ Week 3 post with the scope change.
- ⬜ 👤 Book the 15-minute peer playtest (week of Nov 2); send notes to partner by Nov 6.
- ⬜ 👤 Before Nov 16: silent-playtester notes on three assigned recordings (assigned Nov 9).
