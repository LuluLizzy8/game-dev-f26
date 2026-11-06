# Review of the two-deck change (R1, R3, R7, R10a, R14), 2026-11-06

Reviewer: `ddz-rules-reviewer` instructions, read-only subagent (Read, Grep, Glob), did not write the
change, not asked to approve. Target: the uncommitted two-deck change (engine, heuristic, prompt rules
paragraph, config limits, tests, README/DESIGN). Could not run tests or git.

Answer to "can a card set mean two combinations?": no. Each kind has a distinct rank-count signature
(bomb n×1; four+2 4,1,1; four+2pairs 4,2,2; triple+1 3,1; triple+2 3,2; planes 3×L with L singles or
pairs; straight 1×n; pair_seq 2×n; rocket exactly BJ BJ RJ RJ); kickers are distinct ranks outside the body.
Player boundary: no change found.

| # | Sev | Finding | Applied |
|---|---|---|---|
| 1 | must fix | EVALUATION.md showed one-deck results, freeze and measurements with nothing marking them superseded; the shipped game had no evaluation. | yes: two-deck section declared on top, one-deck section marked superseded; new suite run on new held-out seeds |
| 2 | should fix | call_limit 60 reasoning came from heuristic-only deals; thin margin. | yes: measured random agent (max 20); raised to 120 |
| 3 | should fix | 54k-token prompts: latency vs 30 s timeout and output cap unmeasured; budget stale. | yes: live check on tuning seeds 100–101 (latency max 3.0 s, output ≤ 49 tokens); DESIGN budget updated. A capped legal list was not adopted (would change the interface). |
| 4 | should fix | bomb ordering not tested through legal_actions/step; "BJ RJ" refusal not tested at engine level. | yes: `test_game.TwoDeckBombs` |
| 5 | should fix | refused-action test used "BJ BJ", now a legal pair for some hands. | yes: uses "BJ RJ" |
| 6 | should fix | heuristic's smallest-bomb choice untested. | yes: `test_heuristic_spends_its_smallest_bomb` |
| 7 | should fix | R7 (`manual`) carried the `design` joker-pair rule. | yes: moved to R10a |
| 8 | should fix | one-deck text left in DESIGN.md (54-card deck, 2-deck exclusion, `BJ RJ` example, step limit 200, landlord 20 cards, budget). | yes |
| 9 | note | R10 wording vs size-first bombs. | yes: points to R10a |
| 10 | note | R8: whole rocket as kicker pairs not stated. | yes |
| 11 | note | web/session.py docstring used "bj rj". | yes |
| 12 | note | natural bound is 316, not 322. | yes: wording fixed everywhere |
| 13 | note | random hands rarely test rocket-as-kickers. | yes: fixed-hand test in `test_combos.Invariants` |
| 14 | note | measurement figures not recorded where a reader can check. | yes: EVALUATION two-deck measurements |

## My decisions **[student voice — TODO]**
