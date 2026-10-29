# Dou Dizhu: one deal, landlord against two peasants

## Scope statement

DRAFT, rewrite in your own words. Scope changed from Guandan; post the change in the Week 3 thread.

One episode is one deal of three-player Dou Dizhu (斗地主). The seed shuffles the deck and picks the
landlord; there is no bidding. The deal ends when one player empties their hand. Changed from Guandan
because a Guandan match (two decks, wild cards, levels, tribute) does not fit one bounded episode; Dou
Dizhu keeps the same climbing-game core with a single deck and no wild cards.

**Excluded:** bidding for landlord (seed decides), bid-based stakes (base stake is 1), multi-deal
matches, the four-player and two-deck variants.

## Commands

All commands run from `midterms/lululizzy8/`. Python 3.12. The engine, baseline and tests use only the
standard library; the live model player will also need `google-genai` (pinned in `requirements.txt`).

```
python -m unittest discover -s tests -v
```

Play, baseline and model-player commands: TODO, not built yet.

## Rule/source map

Source **[Pagat]**: John McLeod, "Dou Dizhu", pagat.com, https://www.pagat.com/climbing/doudizhu.html.
Locators name the section of that page; check each against the page before submitting.
Engine: `doudizhu/engine.py`. Tests: `tests/`.

| # | Rule | Label | Evidence | Engine / test |
|---|---|---|---|---|
| R1 | 54-card deck: four each of 3–2, plus a black and a red joker. | manual | [Pagat] Players and cards | `reset` / `test_game.Deal` |
| R1a | Suits are not tracked. | design | No Dou Dizhu combination uses suits, so dropping them changes no legal move. | `reset` |
| R2 | Rank order 3 < 4 < … < K < A < 2 < black joker < red joker. | manual | [Pagat] Players and cards | `LABELS` / `test_combos.Beats` |
| R3 | 17 cards to each player, 3 face down as the kitty. | manual | [Pagat] Deal | `reset` / `test_game.Deal` |
| R4 | The seed picks the landlord; there is no bidding. | design | Bidding adds a second phase and more model calls. The suite controls the player's role by seating the agent relative to the seeded landlord (DESIGN.md §6). | `reset` / `test_game.Deal` |
| R5 | The landlord takes the kitty, which is shown to everyone. | manual | [Pagat] Bidding | `reset`, `observe` / `test_game.Deal` |
| R6 | The landlord leads first. | manual | [Pagat] Play | `reset` / `test_game.Turns` |
| R7 | Combinations: single; pair; triple; triple + single; triple + pair; straight of 5+ singles; sequence of 3+ pairs; sequence of 2+ triples ("plane"); plane + one single per triple; plane + one pair per triple; four + two singles; four + two pairs; bomb (four of a rank); rocket (both jokers). Sequences use 3 through A only. | manual | [Pagat] Combinations | `all_moves` / `test_combos.Lead`, `test_combos.Rejected` |
| R8 | Attached cards ("kickers") must differ in rank from the main cards and from each other. Jokers may be kickers. | design | Variants disagree on attached cards. Distinct ranks make every card set mean exactly one combination, so a move string never means two plays. Consequences: both jokers may be kickers together (`3 3 3 3 BJ RJ` is four + two); four + a pair as the two singles (`3 3 3 3 5 5`) is rejected. TODO: note where Pagat differs. | `all_moves` / `test_combos.Rejected`, `test_combos.Invariants` |
| R9 | To follow, play the same kind and length with a higher main rank. A triple + kicker ranks by its triple; a sequence ranks by its lowest card. | manual | [Pagat] Play | `beats` / `test_combos.Beats` |
| R10 | A bomb beats any non-bomb; a higher bomb beats a lower one; the rocket beats everything. | manual | [Pagat] Combinations | `beats` / `test_combos.Beats` |
| R11 | A follower may pass. After two passes in a row, the last player who played leads anything. The leader cannot pass. | manual | [Pagat] Play | `step`, `legal_actions` / `test_game.Turns` |
| R12 | The deal ends when a player empties their hand. The landlord wins alone, or both peasants win. | manual | [Pagat] Play | `step`, `outcome` / `test_game.Scoring` |
| R13 | Score: base 1, doubled for each bomb or rocket played, doubled for a spring (landlord wins before any peasant plays a card, or peasants win after the landlord's opening lead only). Landlord gets ±2× the stake; each peasant gets ∓1×. | manual | [Pagat] Scoring | `outcome` / `test_game.Scoring` |
| R13a | The base stake is 1. | design | Follows from R4: with no bid there is no bid value. | `outcome` |
| R14 | An episode stops with reason `step_limit` after `max_steps` accepted actions, including passes (default 200); no one wins. | design | A hard bound for the runner. Natural play cannot reach it: at most 52 plays with at most 2 passes between them is ≤ 154 steps, so it is a backstop. | `step` / `test_game.Limits` |
| R15 | A player observes their own hand, the kitty, every player's card count, whose turn it is, the play to beat and the public play history. Never another player's hand. | design | Matches what a player at a real table can see. | `observe` / `test_game.Information` |
| R16 | An action is a space-separated card list (`3 3 3 4`, `BJ RJ`) or `pass`. Card order does not matter. A refused action, including a non-text action, changes nothing. | design | Card lists are readable by a model and by a TA. | `step` / `test_game.Turns`, `test_regressions` |
| R17 | (Dropped: forced landlord seat. The runner seats the agent relative to the seeded landlord.) | — | DESIGN.md §2.1 | — |
| R18 | The runner ends an episode as a forfeit when the agent seat exceeds its model-call limit (`call_limit`), the episode wall clock (`timeout`) or its invalid-reply limit (`invalid_limit`). The agent's side loses at the current bomb multiplier, no spring. The engine's `outcome()` is unchanged. | design | DESIGN.md §5: a run that ran out of budget did not succeed and must not look like a draw. | `runner.forfeit` / `test_runner.Limits` |
| R19 | The observation names the seat's `teammate`: the other peasant for a peasant, `None` for the landlord. | design | Derivable from the public `landlord` field; stops a player misreading teams. | `observe` / `test_game.Information.test_teammate_is_named` |
| R20 | When a seat has exactly one legal action, the runner plays it without calling the player, labeled `forced`. | design | DESIGN.md §5: not a decision; calling the model would only spend budget. | `runner.run_episode` / `test_runner.Forced` |
| R21 | After a failed reply and a failed retry, the runner plays the heuristic's choice from that seat's own observation and legal list, labeled `fallback`. | design | DESIGN.md §5: keeps the deal playable; the label keeps results honest. | `runner.run_episode` / `test_runner.Fallback` |
| R22 | Observation variants: `model-history` sees the full public history (≤ 154 entries); `model-obs` sees the same observation with `history` removed. | design | DESIGN.md §4.3: required history vs observation-only comparison. | `players/model.py` / `test_runner.Prompt` |

## Sources and reuse terms

- [Pagat] rules page (copyrighted site): linked and used for rule facts only; no text or code copied.
- Course repository (columbia-university-ai-games/game-dev-f26 at `66f051b`): `.claude/skills/rule-change`
  and `.claude/agents/rules-reviewer.md` are the basis for this folder's adapted `ddz-` copies;
  `course_game/narrator.py` is the pattern for the provider call. Adapted files name their source.
- google-genai (Apache-2.0, https://github.com/googleapis/python-genai): Vertex client library, installed, not vendored.
- No code or assets reused. TODO: cite RLCard and DouZero if you mention them in the evaluation.
