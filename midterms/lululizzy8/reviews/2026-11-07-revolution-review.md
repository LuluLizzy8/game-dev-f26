# Revolution (R10b) rule review, 2026-11-07

Reviewer: `ddz-rules-reviewer` instructions, run read-only by an independent agent in a separate context
(it did not write the change). Scope: README R2, R9, R10b, R15; `doudizhu/engine.py`, `doudizhu/view.py`,
`players/heuristic.py`, `players/model.py`, `web/session.py`, `tests/test_revolution.py`, `tests/test_runner.py`.

Verdict: the rule is implemented correctly, is public, and a refused bomb changes nothing. No must-fix findings.

## Findings and what the implementation agent did

| # | Severity | Finding | Applied |
|---|---|---|---|
| 1 | should-fix | Model prompt said the scripted teammate "bombs only when an opponent has 4 or fewer cards"; it now also plays a 6+ revolution bomb at any time. Strategy rule 1 argued against a revolution lead. | Teammate description and rule 1 now name the revolution exception (`players/model.py`). The prompt hash changes. |
| 2 | should-fix | GAME-DESIGN.md §4.1 baseline spec ("never lead a bomb", "bomb only at ≤ 4 cards") contradicted §2.3. | §4.1 gained the revolution exception and a Revolution bullet. |
| 3 | should-fix | `test_runner.Limits` assertions `-2 * multiplier` would pass before and after the change. | Both tests pin multiplier 2 and score −4 on seed 0, with the reason in a comment. |
| 4 | should-fix | `Session.explain` bomb-versus-bomb message lacked the reversed-order note. | Added. |
| 5 | should-fix | The 43% revolution rate was measured on seeds 0–299, which include the used one-deck held-out seeds 200–229 (the 54% holding figure used 0–999, which includes 200–229 and 300–329). | Re-measured away from evaluation seeds: holding 54% / 98% / 9% on seeds 1000–1999; revolution in 44% of heuristic self-play on development seeds 0–99. Docs updated. The threshold (6+) was chosen from the holding figures, which did not change. |
| 6 | should-fix | README R2 still stated the fixed order. | R2 points to R10b. |
| 7 | note | "Lasts across rounds" is ambiguous: the flag resets each deal. | R10b: "across tricks within the deal and resets each deal". |
| 8 | note | R10b did not say sequences still run 3–A. | Added. |
| 9 | note | No test for "never flips over its teammate"; `test_keeps_the_order_with_a_high_hand` passed before the change. | Added `test_never_flips_over_its_teammate`; the other is marked as a regression guard. |
| 10 | note | `beats` tests did not cover pair sequences, planes, triple/four + kickers under revolution. | Added `test_every_ranked_kind_flips`. |
| 11 | note | `legal_actions` stays in normal rank order during a revolution (strongest-first for the model). | Not changed: ordering does not affect legality; left for my decision. |
| 12 | note | EVALUATION results predate R10b; README scope statement does not mention the twist. | EVALUATION.md says so with a TODO; the scope statement is student voice. |

Tests after fixes: 102, all pass.

## My decisions

I accepted the fixes for findings 1 to 10 and 12.

- 1 and 2 were the important ones: the prompt and the design doc still described the teammate before
  Revolution, so the model would have been told something false. Fixed before the evaluation run.
- 3 (a loosened test): accepted. The forfeit tests check the exact stakes on seed 0 again.
- 5 (stats measured on held-out seeds): accepted. Re-measured on seeds 1000-1999 and 0-99; the numbers
  barely changed and the 6+ trigger stays.
- 11 (move-list order during a revolution): no change. The order doesn't change which moves are legal, and
  changing it would make the prompt differ from the frozen one.
- Re-running the evaluation: yes. I ran the full suite on new held-out seeds 400-429 (EVALUATION.md).
