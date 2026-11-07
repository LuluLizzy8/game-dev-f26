# Dou Dizhu with two decks and Revolution

## Scope statement

One episode is one deal of three-player Dou Dizhu (斗地主) with two decks (108 cards). The seed shuffles
and picks the landlord; there is no bidding. Each player gets 33 cards, the landlord takes the 9-card kitty,
and the deal ends when someone empties their hand. I started with Guandan, but a Guandan match (wild
cards, levels, tribute) doesn't fit one bounded episode, so this keeps Guandan's two decks and long bombs
on Dou Dizhu's one-deal structure. Two decks replaced the one-deck game on 2026-11-06 (GAME-DESIGN.md §2.2).

My twist is Revolution (2026-11-07, GAME-DESIGN.md §2.3, rule R10b): a bomb of 6 or more cards reverses
the order of 3 through 2, so 3 is highest and 2 lowest, until another 6+ bomb flips it back. Jokers stay
on top. Someone holds a 6+ bomb in about half of all deals, so a weak hand of low cards can turn strong
mid-deal. The idea comes from the revolution in Daifugō. In the browser the first landlord is random and
the role passes to the next seat each deal.

Excluded: bidding (the seed decides), bid-based stakes (base stake is 1), multi-deal scoring, the
four-player game, one-deck play.

Earlier versions and their results stay in EVALUATION.md as history.

## Commands

Run everything from `midterms/lululizzy8/` with Python 3.12. The engine, players and tests use only the
standard library; the live model also needs `google-genai` (pinned in `requirements.txt`).

Recording (3 to 5 min, the AI playing the game): https://youtu.be/zRIMSmfkGlA

Tests (no credentials or network; CI runs the same command):
```
python -m unittest discover -s tests -v
```

Play one deal in the terminal against two heuristic players (type a number from the list, or the cards):
```
python play.py --seat 0 --seed 7
```

Play in the browser:
```
python web/serve.py
```
Then open http://localhost:8000/web/. The home screen has Start game, Watch the baseline, Watch the AI,
and the rule handbook (also top right on every screen). Click cards to pick them, then Play; drag to
reorder your hand. Start game, the baseline and the handbook run in the browser through Pyodide with the
same engine and heuristic (the first load downloads about 10 MB). Watch the AI runs `runner.run_episode`
on your computer with the evaluation's limits, saves a trace to `traces/watch/`, sends the page only the AI
seat's view, and spends cloud credit. It needs `gcloud auth application-default login` once; settings you
haven't set are filled from `agent-config.json` and `gcloud config get-value project`. The server only
listens on this computer. For a phone on the same Wi-Fi, use `--host 0.0.0.0` (anyone on that network
could then start live games).

Run players without credentials (the fixture is a scripted stand-in, not a model):
```
python runner.py --player heuristic --situation S1 --seeds 0-9 --out traces/scratch
python runner.py --player model-history --fixture --situation S1 --seeds 0-2 --out traces/scratch
python report.py traces/scratch --out results/scratch.md
python tools/measure.py
```

Live model player (Vertex AI, `gemini-3.5-flash-lite`; spends cloud credit):
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
In bash, set the same variables with `export NAME=value`. If one is missing the run stops; it never falls
back to the fixture. Situations: `S1` the agent is landlord, `S2` peasant after the landlord, `S3` peasant
before. Players: `heuristic`, `random`, `model-history`, `model-obs`, `model-notes`. The declared suite is
in `EVALUATION.md`.

## Other documents

- `GAME-DESIGN.md`: design, limits and decisions. `EVALUATION.md`: suites, results, limitations.
- `AGENT-TEAM.md`: the agents, what each could do, and what I decided. `reviews/`: review findings.
- `PRODUCT.md`: who the browser game is for (used by the design tool).
- [`playtest.txt`](playtest.txt): anonymous peer playtest notes (played `play.py`).
- `sessions/`: exported Claude Code conversations, with the project ID, local paths and LAN address removed.

## Rule/source map

[Pagat]: John McLeod, "Dou Dizhu", pagat.com, https://www.pagat.com/climbing/doudizhu.html (checked
2026-11-07). Locators are its section headings: Players, Cards and Deal; Auction; Play; Scoring;
Four-Player Game. Engine: `doudizhu/engine.py`. Tests: `tests/`.

| # | Rule | Label | Evidence | Engine / test |
|---|---|---|---|---|
| R1 | 108 cards (two decks): eight each of 3 to 2, two black and two red jokers. | design | GAME-DESIGN.md §2.2: chosen 2026-11-06 for longer hands and bombs. The standard game uses one 54-card deck ([Pagat] Players, Cards and Deal); Pagat's two-deck game is 108 cards with four jokers ([Pagat] Four-Player Game). | `reset` / `test_game.Deal` |
| R1a | Suits are not tracked. | design | No combination uses suits, so dropping them changes no legal move. | `reset` |
| R2 | Rank order 3 < 4 < ... < K < A < 2 < black joker < red joker. A revolution reverses 3 through 2 (R10b). | manual | [Pagat] Players, Cards and Deal | `LABELS` / `test_combos.Beats` |
| R3 | 33 cards each, 9 face down as the kitty; the landlord holds 42. | design | GAME-DESIGN.md §2.2. One deck deals 17 each plus 3 ([Pagat] Players, Cards and Deal); Pagat's four-player game deals 25 each plus 8. 33 + 9 uses all 108 cards in three equal hands. | `reset` / `test_game.Deal` |
| R4 | The seed picks the landlord; no bidding. In the browser each next deal uses a seed whose landlord is the next seat, so the role rotates (`web/session.py:seed_with_landlord`). | design | Pagat chooses the landlord by auction ([Pagat] Auction). Bidding adds a phase and more model calls; the suite seats the agent relative to the seeded landlord (GAME-DESIGN.md §6). | `reset` / `test_game.Deal` |
| R5 | The landlord takes the kitty, shown to everyone. | manual | [Pagat] Auction. Pagat gives showing the kitty as a common custom; older practice takes it unseen. | `reset`, `observe` / `test_game.Deal` |
| R6 | The landlord leads first. | manual | [Pagat] Play | `reset` / `test_game.Turns` |
| R7 | Combinations: single; pair; triple; triple + single; triple + pair; straight of 5+; 3+ pairs in a row; 2+ triples in a row ("plane"); plane + one single per triple; plane + one pair per triple; four + two singles; four + two pairs; bomb and rocket (R10a). Sequences run 3 to A only. | manual | [Pagat] Play (the numbered list of combination types; no 2s or jokers in sequences) | `all_moves` / `test_combos.Lead`, `test_combos.Rejected` |
| R8 | Kickers (attached cards) must differ in rank from the main cards and from each other. Jokers may be kickers. | design | Distinct ranks make every card set mean one combination, so a move string never means two plays. Results: `3 3 3 3 BJ RJ` is four + two; `3 3 3 3 5 5` as four + two singles is rejected; with two decks `3 3 3 3 BJ BJ RJ RJ` is four + two pairs. Where Pagat differs ([Pagat] Play): it forbids both jokers as kickers together in a plane or four + two, and a plane's single kickers may form a pair. It agrees that four + two takes singles of different ranks. | `all_moves` / `test_combos.Rejected`, `test_combos.Invariants` |
| R9 | To follow, play the same kind and length with a higher main rank in the current order (R10b). A triple + kicker ranks by its triple; a sequence by its lowest card. | manual | [Pagat] Play | `beats` / `test_combos.Beats` |
| R10 | A bomb beats any non-bomb; a higher bomb beats a lower one (R10a); the rocket beats everything. | manual | [Pagat] Play | `beats` / `test_combos.Beats` |
| R10a | Two decks: a bomb is 4 to 8 cards of one rank. More cards beat fewer; same size compares by rank. The rocket is all four jokers (`BJ BJ RJ RJ`). One black and one red joker is not a combination; `BJ BJ` and `RJ RJ` are pairs. Four + two keeps exactly four of the rank. | design | GAME-DESIGN.md §2.2. Matches Pagat's two-deck game on bomb order (more cards win regardless of rank), the four-joker rocket and joker pairs ([Pagat] Four-Player Game). That game differs: four players, no single kickers, no four + two, and 4- or 5-card bombs don't double the stake; here every bomb doubles. | `all_moves`, `beats` / `test_combos.Lead`, `Rejected`, `Beats`; `test_game.Scoring.test_rocket_doubles` |
| R10b | Revolution: a bomb of 6+ cards reverses the order of 3 through 2 (3 highest, 2 lowest) for every comparison, bombs included; jokers stay highest. Another 6+ bomb reverses it back. It lasts across tricks and resets each deal; sequences still run 3 to A (R7). The bomb doubles the stakes like any bomb (R13). | design | GAME-DESIGN.md §2.3. Not on Pagat; borrowed from the revolution in Daifugō. On 1,000 deals (seeds 1000-1999) someone holds a 6+ bomb in 54% (5+: 98%, 7+: 9%). | `beats`, `strength`, `step`, `observe`; `players/heuristic.py:wants_flip` / `test_revolution` |
| R11 | A follower may pass. After two passes in a row, the last player who played leads anything. The leader can't pass. | manual | [Pagat] Play | `step`, `legal_actions` / `test_game.Turns` |
| R12 | The deal ends when a player empties their hand. The landlord wins alone, or both peasants win. | manual | [Pagat] Scoring | `step`, `outcome` / `test_game.Scoring` |
| R13 | Score: base 1, doubled for each bomb or rocket and for a spring (the landlord wins before any peasant plays, or the peasants win after only the landlord's opening lead). The landlord gets ±2× the stake; each peasant ∓1×. | manual | [Pagat] Scoring | `outcome` / `test_game.Scoring` |
| R13a | The base stake is 1. | design | Follows from R4: no bid, so no bid value. | `outcome` |
| R14 | An episode stops with reason `step_limit` after `max_steps` accepted actions, passes included (default 400); no one wins. | design | A backstop: the deal ends when one hand empties, so at most 106 plays with up to 2 passes between them, 316 steps. | `step` / `test_game.Limits` |
| R15 | A player sees their own hand, the kitty, every player's card count, whose turn it is, the play to beat, the public history and whether a revolution is on (R10b). Never another hand. | design | What a player at a real table can see. | `observe` / `test_game.Information` |
| R16 | An action is a space-separated card list (`3 3 3 4`, `BJ BJ RJ RJ`) or `pass`, in any order. A refused action, including a non-text one, changes nothing. | design | Readable by a model and by a TA. | `step` / `test_game.Turns`, `test_regressions` |
| R17 | Dropped (forced landlord seat). The runner seats the agent relative to the seeded landlord. | n/a | GAME-DESIGN.md §2.1 | n/a |
| R18 | The runner ends an episode as a forfeit when the agent goes over its model-call limit (`call_limit`), the wall clock (`timeout`) or its invalid-reply limit (`invalid_limit`). The agent's side loses at the current bomb multiplier, no spring. `outcome()` is unchanged. | design | GAME-DESIGN.md §5: running out of budget is a loss, not a draw. | `runner.forfeit` / `test_runner.Limits` |
| R19 | The observation names the seat's `teammate`: the other peasant, or `None` for the landlord. | design | Follows from the public `landlord` field; stops a player misreading teams. | `observe` / `test_game.Information.test_teammate_is_named` |
| R20 | When a seat has exactly one legal action, the runner plays it without asking the player, labeled `forced`. | design | GAME-DESIGN.md §5: not a decision, so no model call. | `runner.run_episode` / `test_runner.Forced` |
| R21 | After a failed reply and a failed retry, the runner plays the heuristic's choice from that seat's own view, labeled `fallback`. | design | GAME-DESIGN.md §5: keeps the deal going; the label keeps results honest. | `runner.run_episode` / `test_runner.Fallback` |
| R22 | `model-history` sees the full public history (up to 316 entries); `model-obs` sees the same observation without `history`. | design | GAME-DESIGN.md §4.3: the history vs observation-only comparison. | `players/model.py` / `test_runner.Prompt` |
| R23 | `model-notes` also sees its own note from its previous turn (up to 300 characters, one line), stored by the runner. The note shown is the last accepted reply's note, or "(none)"; notes from rejected replies are dropped; fallback and forced moves leave it unchanged. No other player sees notes. | design | GAME-DESIGN.md §4.3: does the model's own memory help beyond the public history? The note is built from its own view, so it holds nothing hidden. | `runner.run_episode`, `players/model.py` / `test_runner.Notes` |

## Sources and reuse terms

- [Pagat]: copyrighted site, linked and used for rule facts only; no text or code copied.
- Course repository (columbia-university-ai-games/game-dev-f26 at `66f051b`): `.claude/skills/rule-change`
  and `.claude/agents/rules-reviewer.md` are the basis for this folder's `ddz-` copies, and
  `course_game/narrator.py` is the pattern for the provider call. Adapted files name their source.
- google-genai (Apache-2.0, https://github.com/googleapis/python-genai): installed, not vendored.
- Pyodide 0.26.4 (MPL-2.0, https://pyodide.org): loaded by `web/index.html` from cdn.jsdelivr.net.
- Fonts Young Serif, Figtree and Ma Shan Zheng (SIL Open Font License), from Google Fonts. The cards are
  drawn in CSS; there are no image assets.
- No other code or assets reused.
