# Runner and rule-change review, 2026-10-28

Reviewer: `ddz-rules-reviewer` instructions (`.claude/agents/ddz-rules-reviewer.md`), run as a read-only
subagent (Read, Grep, Glob) that did not write the code and was not asked to approve it.
Target: commits `7168315`..`253e79f` (engine fixes, R16–R22, runner, players, report, tests).
The reviewer could not run tests or git. Findings as returned, condensed.

| # | Sev | Where | Finding | Applied |
|---|---|---|---|---|
| 1 | should fix | players/model.py, runner.py | API-error text (may include `projects/<id>/…`) goes into public traces and the retry prompt; retry prompt says "your reply was rejected" for a call that never replied. | yes: only exception type + status code logged; API errors not fed back to the prompt |
| 2 | should fix | report.py | `losses` includes forfeits, which are also in their own columns. | yes: losses exclude forfeits |
| 3 | should fix | report.py | fallback-free stats give wins only, not mean score. | yes |
| 4 | should fix | report.py | no tests for report.py. | yes: `tests/test_report.py` |
| 5 | should fix | report.py | paired diff averaged over matched subset silently; pairing ignores game commit / config. | yes: pair count shown; pairs match on commit + config hash |
| 6 | should fix | runner.py | `assert outcome["ok"]` vanishes under `python -O`; a refused step would loop forever. | yes: explicit `RuntimeError` |
| 7 | should fix | tests/test_runner.py | forfeit tests check only `reason`; bomb multiplier in forfeit untested. | yes: direct forfeit test with a bomb played, scores checked |
| 8 | should fix | tests/test_runner.py | fallback test doesn't check the played action is the heuristic's choice for the agent's own view. | yes |
| 9 | should fix | tests/test_runner.py | leak test calls `build_prompt` directly, not what `run_episode` sends. | yes: test checks every prompt the runner sends equals `build_prompt(observe(agent), legal_actions(agent))` |
| 10 | note | DESIGN §4.2 | says observation goes "as JSON"; code sends the text table. | yes: DESIGN updated |
| 11 | note | runner.py | header model id is the configured one; steps lack `accepted`. | yes: header `model_requested`, result `models_returned`, steps `accepted` |
| 12 | note | runner.py | wall clock checked only before calls; one call can overrun by ≤ 30 s. | recorded in EVALUATION known bounds |
| 13 | note | report.py | latency excludes API-error attempts. | yes: latency over all attempts |
| 14 | note | model.py | no thinking config; thinking may hit the 256-token cap → invalid replies. | to check on tuning seeds (EVALUATION TODO) |
| 15 | note | tests/test_regressions.py | non-string test checks only `steps`. | yes: full snapshot compared |
| 16 | note | tests/test_runner.py | baselines only exercised in S1 vs heuristic. | yes: all situations, both opponent types |
| 17 | note | README / DESIGN §0 | stale "TODO, not built" line; stale status table. | README already fixed in `c458036`; DESIGN §0 updated |
| 18 | note | runner.py / report.py | random-opponent RNG depends on trial, so trial-1 runs don't pair with trial-0 baselines. | not needed: the suite runs random opponents at trial 0 only; noted |

Files read by the reviewer: `.claude/agents/ddz-rules-reviewer.md`, CLAUDE.md, README.md, GAME-DESIGN.md,
agent-config.json, doudizhu/engine.py, doudizhu/view.py, runner.py, players/*, report.py, play.py,
tools/measure.py, tests/test_runner.py, tests/test_game.py, tests/test_regressions.py.

## My decisions

I accepted the fixes the implementation agent applied for findings 1 to 11, 13, 15, 16 and 17.

- 1 was the most important one: an API error message could put my project ID into public traces. Logging
  only the error type and status code is enough to debug.
- 2 to 5 (report.py): accepted. Forfeits shouldn't count twice, and pairs should only match runs of the
  same code and config.
- 6 to 9 (runner and tests): accepted. A refused move must stop the run instead of looping, and the leak
  test has to check the prompts the runner actually sends.
- 12 (one call can overrun the wall clock by up to 30 s): accepted as a known limit, written in EVALUATION.md.
- 14 (thinking tokens vs the 256-token cap): checked on the first live episode. Replies used about 30
  tokens, so nothing to change.
- 18 (random-opponent pairing across trials): no change. The suite only runs random opponents at trial 0.
