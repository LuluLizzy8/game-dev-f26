# Dou Dizhu with two decks: one deal, landlord against two peasants

## Scope statement

DRAFT, rewrite in your own words. (Scope change from Guandan posted in the Week 3 thread; change to two
decks on 2026-11-06 TODO: post in the Week 3 thread.)

One episode is one deal of three-player Dou Dizhu (斗地主) played with **two decks** (108 cards). The seed
shuffles the cards and picks the landlord; there is no bidding. Each player gets 33 cards and the landlord
takes the 9-card kitty. The deal ends when one player empties their hand. Changed from Guandan because a
Guandan match (wild cards, levels, tribute) does not fit one bounded episode; this keeps Guandan's two
decks and long bombs on Dou Dizhu's one-deal structure. Two decks replaced the one-deck game on 2026-11-06
(DESIGN.md §2.2); the one-deck results are kept in EVALUATION.md as history.

**Excluded:** bidding for landlord (seed decides), bid-based stakes (base stake is 1), multi-deal
matches, the four-player variant, one-deck play.

## Commands

All commands run from `midterms/lululizzy8/`. Python 3.12. The engine, baselines and tests use only the
standard library; the live model player also needs `google-genai` (pinned in `requirements.txt`).

Recording: TODO link.

**Test** (no credentials, no network; the same command CI runs):
```
python -m unittest discover -s tests -v
```

**Play** one deal yourself against two heuristic players (type a number from the list, or the cards):
```
python play.py --seat 0 --seed 7
```

**Play in a browser** (desktop or phone; same engine and heuristic opponents, run in the browser by Pyodide):
```
python -m http.server 8000
```
then open http://localhost:8000/web/ (from a phone on the same Wi-Fi, add `--bind 0.0.0.0` and use this
computer's IP address). The first load downloads Pyodide (about 10 MB) and needs internet. Tap cards, then Play.

**Run players without credentials** (heuristic, random, and the model player with a scripted fixture that
is not a model):
```
python runner.py --player heuristic --situation S1 --seeds 0-9 --out traces/scratch
python runner.py --player model-history --fixture --situation S1 --seeds 0-2 --out traces/scratch
python report.py traces/scratch --out results/scratch.md
python tools/measure.py
```

**Live model player** (Vertex AI, `gemini-3.5-flash-lite`; spends cloud credit):
```
pip install -r requirements.txt
gcloud auth application-default login
```
PowerShell:
```
$env:COURSE_PROVIDER='vertex'; $env:COURSE_MODEL='gemini-3.5-flash-lite'
$env:GOOGLE_CLOUD_PROJECT='<your project id>'; $env:GOOGLE_CLOUD_LOCATION='global'
python runner.py --player model-history --situation S1 --seeds 100-100 --out traces/tuning
```
bash: the same variables with `export NAME=value`. Missing variables stop the run; it never falls back to
the fixture. Situations: `S1` agent is landlord, `S2` peasant after the landlord, `S3` peasant before.
Players: `heuristic`, `random`, `model-history`, `model-obs`, `model-notes`. See `EVALUATION.md` for the declared suite.

## Rule/source map

Source **[Pagat]**: John McLeod, "Dou Dizhu", pagat.com, https://www.pagat.com/climbing/doudizhu.html.
Locators name the section of that page; check each against the page before submitting.
Engine: `doudizhu/engine.py`. Tests: `tests/`.

| # | Rule | Label | Evidence | Engine / test |
|---|---|---|---|---|
| R1 | 108 cards (two decks): eight each of 3–2, two black and two red jokers. | design | DESIGN.md §2.2: two decks chosen 2026-11-06 for longer hands and longer bombs. The one-deck game (54 cards) is [Pagat] Players and cards. | `reset` / `test_game.Deal` |
| R1a | Suits are not tracked. | design | No Dou Dizhu combination uses suits, so dropping them changes no legal move. | `reset` |
| R2 | Rank order 3 < 4 < … < K < A < 2 < black joker < red joker. | manual | [Pagat] Players and cards | `LABELS` / `test_combos.Beats` |
| R3 | 33 cards to each player, 9 face down as the kitty (the landlord holds 42). | design | DESIGN.md §2.2: one deck deals 17 + kitty 3 [Pagat] Deal; 33 + 9 uses all 108 cards with three hands of equal size. | `reset` / `test_game.Deal` |
| R4 | The seed picks the landlord; there is no bidding. | design | Bidding adds a second phase and more model calls. The suite controls the player's role by seating the agent relative to the seeded landlord (DESIGN.md §6). | `reset` / `test_game.Deal` |
| R5 | The landlord takes the kitty, which is shown to everyone. | manual | [Pagat] Bidding | `reset`, `observe` / `test_game.Deal` |
| R6 | The landlord leads first. | manual | [Pagat] Play | `reset` / `test_game.Turns` |
| R7 | Combinations: single; pair; triple; triple + single; triple + pair; straight of 5+ singles; sequence of 3+ pairs; sequence of 2+ triples ("plane"); plane + one single per triple; plane + one pair per triple; four + two singles; four + two pairs; bomb (R10a); rocket (R10a). Sequences use 3 through A only. | manual | [Pagat] Combinations | `all_moves` / `test_combos.Lead`, `test_combos.Rejected` |
| R8 | Attached cards ("kickers") must differ in rank from the main cards and from each other. Jokers may be kickers. | design | Variants disagree on attached cards. Distinct ranks make every card set mean exactly one combination, so a move string never means two plays. Consequences: both jokers may be kickers together (`3 3 3 3 BJ RJ` is four + two); four + a pair as the two singles (`3 3 3 3 5 5`) is rejected; with two decks the whole rocket can be two kicker pairs (`3 3 3 3 BJ BJ RJ RJ` is four + two pairs). TODO: note where Pagat differs. | `all_moves` / `test_combos.Rejected`, `test_combos.Invariants` |
| R9 | To follow, play the same kind and length with a higher main rank. A triple + kicker ranks by its triple; a sequence ranks by its lowest card. | manual | [Pagat] Play | `beats` / `test_combos.Beats` |
| R10 | A bomb beats any non-bomb; a higher bomb beats a lower one (order between bombs: R10a); the rocket beats everything. | manual | [Pagat] Combinations | `beats` / `test_combos.Beats` |
| R10a | Two decks: a bomb is 4 to 8 cards of one rank; a bomb with more cards beats one with fewer, and bombs of the same size compare by rank. The rocket is all four jokers (`BJ BJ RJ RJ`); one black and one red joker together is not a combination; `BJ BJ` and `RJ RJ` are ordinary pairs. Four + two keeps exactly four of the rank. | design | DESIGN.md §2.2. TODO: compare with Pagat's two-deck (four-player) variant. | `all_moves`, `beats` / `test_combos.Lead`, `Rejected`, `Beats`; `test_game.Scoring.test_rocket_doubles` |
| R11 | A follower may pass. After two passes in a row, the last player who played leads anything. The leader cannot pass. | manual | [Pagat] Play | `step`, `legal_actions` / `test_game.Turns` |
| R12 | The deal ends when a player empties their hand. The landlord wins alone, or both peasants win. | manual | [Pagat] Play | `step`, `outcome` / `test_game.Scoring` |
| R13 | Score: base 1, doubled for each bomb or rocket played, doubled for a spring (landlord wins before any peasant plays a card, or peasants win after the landlord's opening lead only). Landlord gets ±2× the stake; each peasant gets ∓1×. | manual | [Pagat] Scoring | `outcome` / `test_game.Scoring` |
| R13a | The base stake is 1. | design | Follows from R4: with no bid there is no bid value. | `outcome` |
| R14 | An episode stops with reason `step_limit` after `max_steps` accepted actions, including passes (default 400); no one wins. | design | A hard bound for the runner. Natural play cannot reach it: the deal ends when one hand empties, so at most 106 plays with at most 2 passes between them, ≤ 316 steps, so it is a backstop. | `step` / `test_game.Limits` |
| R15 | A player observes their own hand, the kitty, every player's card count, whose turn it is, the play to beat and the public play history. Never another player's hand. | design | Matches what a player at a real table can see. | `observe` / `test_game.Information` |
| R16 | An action is a space-separated card list (`3 3 3 4`, `BJ BJ RJ RJ`) or `pass`. Card order does not matter. A refused action, including a non-text action, changes nothing. | design | Card lists are readable by a model and by a TA. | `step` / `test_game.Turns`, `test_regressions` |
| R17 | (Dropped: forced landlord seat. The runner seats the agent relative to the seeded landlord.) | — | DESIGN.md §2.1 | — |
| R18 | The runner ends an episode as a forfeit when the agent seat exceeds its model-call limit (`call_limit`), the episode wall clock (`timeout`) or its invalid-reply limit (`invalid_limit`). The agent's side loses at the current bomb multiplier, no spring. The engine's `outcome()` is unchanged. | design | DESIGN.md §5: a run that ran out of budget did not succeed and must not look like a draw. | `runner.forfeit` / `test_runner.Limits` |
| R19 | The observation names the seat's `teammate`: the other peasant for a peasant, `None` for the landlord. | design | Derivable from the public `landlord` field; stops a player misreading teams. | `observe` / `test_game.Information.test_teammate_is_named` |
| R20 | When a seat has exactly one legal action, the runner plays it without calling the player, labeled `forced`. | design | DESIGN.md §5: not a decision; calling the model would only spend budget. | `runner.run_episode` / `test_runner.Forced` |
| R21 | After a failed reply and a failed retry, the runner plays the heuristic's choice from that seat's own observation and legal list, labeled `fallback`. | design | DESIGN.md §5: keeps the deal playable; the label keeps results honest. | `runner.run_episode` / `test_runner.Fallback` |
| R22 | Observation variants: `model-history` sees the full public history (≤ 316 entries); `model-obs` sees the same observation with `history` removed. | design | DESIGN.md §4.3: required history vs observation-only comparison. | `players/model.py` / `test_runner.Prompt` |
| R23 | `model-notes` sees everything `model-history` sees plus its own note from its previous turn (at most 300 characters, collapsed to one line). The runner stores the note. The note shown is the last accepted model reply's note, or "(none)" if that reply had none; notes from rejected replies are dropped; fallback and forced moves leave it unchanged. No other variant sees notes. | design | DESIGN.md §4.3: tests whether the model's own memory helps beyond the public history. The note is the model's own text, built from its own view, so it carries no hidden information. | `runner.run_episode`, `players/model.py` / `test_runner.Notes` |

## Sources and reuse terms

- [Pagat] rules page (copyrighted site): linked and used for rule facts only; no text or code copied.
- Course repository (columbia-university-ai-games/game-dev-f26 at `66f051b`): `.claude/skills/rule-change`
  and `.claude/agents/rules-reviewer.md` are the basis for this folder's adapted `ddz-` copies;
  `course_game/narrator.py` is the pattern for the provider call. Adapted files name their source.
- google-genai (Apache-2.0, https://github.com/googleapis/python-genai): Vertex client library, installed, not vendored.
- Pyodide 0.26.4 (MPL-2.0, https://pyodide.org): loaded by `web/index.html` from cdn.jsdelivr.net, not vendored.
- Fonts Young Serif, Figtree and Ma Shan Zheng (SIL Open Font License) from Google Fonts. Card art is drawn
  in CSS in `web/index.html`; no image assets.
- No code or assets reused. TODO: cite RLCard and DouZero if you mention them in the evaluation.
