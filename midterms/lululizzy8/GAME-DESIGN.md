# Dou Dizhu midterm: design document

Status: DRAFT rev 4, 2026-11-06: the game now uses **two decks** (§2.2, which overrides one-deck numbers
elsewhere in this doc: 54 cards, 17/20-card hands, the 154-step bound, the R10 bomb wording). Rev 3 was 2026-10-28. Rev 1 was reviewed by two independent read-only reviewers
(`reviews/2026-10-28-design-review.md`); rev 2 by a third (`reviews/2026-10-28-design-review-rev2.md`).
Accepted findings are applied here.
Written before the runner, baseline and model player exist.
Sections marked **[student voice]** must be rewritten by me (LuluLizzy) before submission;
the rubric treats agent-voiced text there as missing authorship.

The rule/source map stays in `README.md` (single source of truth); this doc refers to it by rule
number (R1–R16 with R1a, R13a; new rows in §2.1).

Working rule: all changes stay local (no push, no PR) until the submission is complete. See §13 for
what that means for CI and the dated freeze.

---

## 0. Rubric coverage at a glance

| Check | Where it is met | Status |
|---|---|---|
| 1a labels | `README.md` map R1–R16 + new rows in §2.1 (runner rules included) | Pagat locators to verify |
| 1b scope | §1; README scope statement | needs my voice + Week 3 post |
| 1c sources | §9: Pagat, course-repo skill/reviewer/narrator pattern, google-genai | Pagat locators and RLCard/DouZero licences to open |
| 2a core loop | engine + `play.py` human mode (§12) | built (`play.py`) |
| 2b model player | `players/model.py` called only by `runner.py` (§4–§5) | built; first live episode TODO |
| 2c information | `observe`/`legal_actions` per seat; reshuffle tests on observation *and* prompt (§3, §7) | built + tested (`test_game`, `test_view`, `test_runner.Prompt`) |
| 3a runs | README commands for PowerShell and bash, pinned `requirements.txt`, no-credential fixture run (§8) | README done; fresh-clone check TODO |
| 3b limits | `runner.py` step / call / HTTP-timeout / wall-clock / invalid limits, explicit reasons (§5) | built + tested (`test_runner.Limits`) |
| 3c CI | five check kinds in the folder workflow (§7) | all five kinds present locally (55 tests); CI first runs at push |
| 3d agent team | folder-local `CLAUDE.md`, skills, reviewer, `reviews/`, `sessions/` (§10) | config + 5 reviews done; first session export in `sessions/` |
| 4a choices | §11 decision table with the alternative each beat | this doc |
| 4b experiment | heuristic baseline, paired deals, 30 held-out seeds per situation (§4.1, §6) | baseline built; runs TODO |
| 5a comparison | `EVALUATION.md`; suite frozen by a dated local commit before tuning (§6) | TODO |
| 5b authorship | `AGENT-TEAM.md`, limitations, peer notes **[student voice]** | TODO |
| 5c recording | 3–5 min script (§12) | TODO |

---

## 1. Game and scope (1b, 2a)

**Game.** Three-player Dou Dizhu (斗地主), a Chinese climbing card game: one landlord against two
peasants in a team. Classic reconstruction, built from scratch in Python 3.12; the engine uses only
the standard library, and only the model player needs a provider SDK.

**One episode = one deal.** The seed shuffles the deck and picks the landlord. The deal ends when any
player empties their hand (`hand_empty`) or a runner limit fires (§5).

**Included:** two full decks, 108 cards (§2.2); all 14 standard combination kinds (R7); bombs and rocket (R10);
pass and lead-return (R11); landlord/peasant win (R12); bomb and spring multipliers (R13).

**Excluded, with reason:**

| Cut | Why |
|---|---|
| Bidding for landlord | Adds a second phase and more model calls; the seed picks the landlord (R4) and the runner seats the agent relative to it (§6). |
| Bid stakes (1/2/3) | Follows from no bidding; base stake 1 (R13a). |
| Multi-deal match / running score | One deal is already a complete win/loss; matches multiply cost without new decisions. |
| 4-player variant | Different seats and teams; out of scope (§2.2). |
| Suits | No combination uses suits, so dropping them changes no legal move (R1a). |
| Graphics / sound | Optional per brief; a text table is enough to play and to record. |

**Scope change history:** the Week 3 header said Guandan. Changed to Dou Dizhu because a Guandan match
(two decks, wild cards, levels, tribute) does not fit one bounded episode. **TODO: post the change in
the Week 3 thread and rewrite the README scope statement in my voice.**

---

## 2. Game specification (1a, 2a)

The engine (`doudizhu/engine.py`) is the authoritative spec; the README map points each rule to code
and tests. Summary:

- **Initial state.** 54 cards shuffled by `random.Random(seed)`; 17 to each seat; the 3-card kitty
  goes to the landlord and is shown to all. Landlord = `rng.randrange(3)`. The landlord leads.
- **Actions.** A space-separated card list (`3 3 3 4`, `10 J Q K A`, `BJ BJ RJ RJ`) or `pass`. Order does
  not matter; text is case-insensitive.
- **Transitions.** A legal play removes cards and becomes the play to beat; a pass passes. After two
  passes in a row the last player to play leads anything. The leader may not pass.
- **Legality.** Lead: any combination in hand. Follow: same kind and length with a higher main rank,
  or a bomb, or the rocket. Kickers must be distinct ranks from the body and from each other (R8,
  `design`: every card list means exactly one combination). Consequences to state in R8's evidence
  once checked against Pagat: both jokers may be kickers together (`3 3 3 3 BJ RJ`, and with two decks the whole rocket as two pairs, `3 3 3 3 BJ BJ RJ RJ`), and four + a pair
  as the "two singles" (`3 3 3 3 5 5`) is rejected.
- **Scoring.** Stake 1 × 2^(bombs + rockets + spring). Landlord ±2×, each peasant ∓1×. Zero-sum.
- **Engine termination.** `hand_empty` (winner decided) or `step_limit` (no winner, scores 0).
  Runner-level forfeits (`call_limit`, `timeout`, `invalid_limit`) are not engine outcomes; see §5.

### 2.1 Rule and map changes (each through the rule-change skill: map row → failing test → code → independent review)

| Change | Label | Why |
|---|---|---|
| ~~R17 forced landlord seat~~ | — | **Dropped.** The runner seats the agent at `(landlord + k) % 3` using the landlord the seed already picks, so no engine change is needed and R4 stands. |
| R14 wording: "after `max_steps` accepted actions, *including passes*". Natural play cannot reach 200: at most 20 + 16 + 16 = 52 plays (the deal ends when one hand empties) with at most 2 passes between plays, so ≤ 52 + 2 × 51 = 154 steps. It is a backstop; `test_game.Limits` proves it with `max_steps=3`. | design | Reviewer: "moves" was ambiguous. (README updated.) |
| R18 Runner forfeit rule: `call_limit`, `timeout`, `invalid_limit` end the episode in `runner.py`; the agent's side loses (exact result in §5). The engine's `outcome()` is untouched. | design | A budget failure must not look like a draw; keeping it in the runner keeps the engine pure. |
| R19 Observation adds `teammate` (the other peasant's seat, or `None` for the landlord). | design | Derivable from public `landlord`; stops the model misreading teams. Test: peasant gets the other peasant, landlord gets `None`, reshuffle test still passes. |
| R20 Forced move: when a seat has exactly one legal action, the runner plays it without a player call, `source: forced`. | design | A forced pass is not a decision; calling the model would waste budget and could trip `call_limit`. |
| R21 Fallback: after a failed retry the runner plays the heuristic's choice, computed from that seat's observation and legal list only, `source: fallback`. | design | Keeps the deal playable; labeled so it is never counted as a model move. |
| R22 Observation variants: `model-history` gets full public history (≤ 154 entries); `model-obs` gets the same observation with `history` removed. | design | Required partial-observation comparison (§4.3). |
| Engine bugs (regressions, done 2026-10-28, failing test committed before the fix): `observe(-1)` returned seat 2's hand; `step` crashed on a non-string action. Now `observe` rejects seats outside 0–2 and `step` refuses non-strings with `ok=False`. | — | Rules reviewer findings 9–10; `tests/test_regressions.py`. |
| `step_limit` outcome gains `spring: False, multiplier: 1` so both terminal shapes match. | — | Rules reviewer finding 8. |
| New scoring tests: landlord win without spring, rocket doubling, two bombs ×4. | — | Regression guards (pass on current engine). |

---

### 2.2 Two-deck change (2026-11-06, my decision)

The one-deck game was finished and evaluated (EVALUATION.md, superseded section). I then changed it to
two decks with three players. Rules (all `design`; README rows R1, R3, R7, R10a, R14):

| Item | One deck (before) | Two decks (now) | Why this choice |
|---|---|---|---|
| Cards | 54 | 108: eight of each rank, two of each joker | two standard decks |
| Deal | 17 each, kitty 3, landlord 20 | 33 each, kitty 9, landlord 42 | uses all 108 cards with three equal hands |
| Bomb | four of a rank | 4 to 8 of a rank; more cards beat fewer, then rank | with eight of a rank, longer bombs exist; size-first is the usual climbing-game rule (as in Guandan) |
| Rocket | BJ RJ | all four jokers `BJ BJ RJ RJ`; `BJ RJ` is not a play; `BJ BJ` and `RJ RJ` are pairs | keeps the rocket unique and on top |
| Step limit | 200 (natural max 154) | 400 (the deal ends when one hand empties: at most 106 plays + 2 × 105 passes = 316) | still a backstop only |
| Call limit | 60 | 120 (measured max non-forced decisions per seat per deal on seeds 0–104: 28 with the heuristic as agent, 20 with random; raised on the 2026-11-06 review so a passive player is not forfeited) | margin for a player that passes more |

Alternatives considered: four players with two decks (the common two-deck form: 25 each, kitty 8)
would change seats, teams, situations and every runner test; 31 each + 15 kitty would make the landlord
hand even larger. Rejected for time.

Consequences: the opening legal list grows from median 74 to median 2,425 (max 5,921) moves, so a
landlord prompt can reach about 54k input tokens (`tools/measure.py`). Heuristic change: it plays its
smallest bomb first (fewest cards, then lowest rank). The model prompt's rules paragraph now describes
two decks; the strategy rules are unchanged from the round 2 prompt and were not re-tuned.

### 2.3 Revolution (2026-11-07, my decision; README R10b)

The twist, borrowed from the revolution in Daifugō: a bomb of 6 or more cards reverses the order of 3
through 2 (3 highest, 2 lowest) for every comparison, bombs included; jokers stay highest. Another 6+ bomb
reverses it back. It is public (`observe()["revolution"]`, a REVOLUTION line in the table text) and the
bomb doubles the stakes like any bomb.

| Choice | Alternatives | Why |
|---|---|---|
| Trigger: bomb of 6+ | 4+ (every bomb), 5+, 7+ | On 1,000 two-deck deals (seeds 1000–1999, away from every evaluation seed) someone holds a 6+ bomb in 54% (5+: 98%, 7+: 9%): a real threat that still feels special |
| Jokers stay on top | flip jokers too | keeps the rocket and joker pairs unambiguous |
| Lasts until the next 6+ bomb | until the round ends | the swing is the strategy: holding a second big bomb matters |
| Bombs compare by size, then flipped rank | flip bombs only by rank | size-first stays as R10a |

Heuristic: it plays its smallest 6+ bomb to start (or end) a revolution when most of the 3–2 cards it
would keep are 3–9 (or, in a revolution, 10–2), never over its teammate's play; otherwise it ranks every
choice in the current order. Without this habit it would almost never play a 6+ bomb (0% of heuristic
self-play deals before the change); after it, a revolution happens in 44% of heuristic self-play deals
(development seeds 0–99; the review on 2026-11-07 had it re-measured there, since a first count used seeds 0–299). The model prompt gained one rules sentence; strategy rules unchanged.
The evaluation in EVALUATION.md predates this rule.

## 3. Machine-playable interface (2b, 2c)

The engine already provides the five operations:

```
reset(seed)              -> observation for the leader (the runner discards it; see below)
observe(seat)            -> own hand, kitty, card counts, turn, play to beat, public history, status
legal_actions(seat)      -> sorted card-list strings (+ "pass" when following); [] if not your turn
step(seat, action)       -> {"ok": bool, ...}; a refused action changes nothing
outcome()                -> ongoing | terminal + reason, winner, spring, multiplier, scores
```

**Where the boundary is.** `runner.py` owns the only `DouDizhu` instance. For the model player the
enforced boundary is the prompt: the API request is built only from `observe(agent_seat)` and
`legal_actions(agent_seat)`, carries no tool definitions, and never includes the seed, the trace path
or other hands. In-process Python players (heuristic, random) are my own code and could technically
reach the engine through introspection; they are written to use only their arguments, and a test
checks that their choices do not change when the other hands are reshuffled.

**`reset` leaks the landlord's view.** `reset()` returns `observe(self.turn)`, i.e. the landlord's
full hand. The runner ignores that return value and always calls `observe(agent_seat)`. Test: in S2
the first prompt does not change when the landlord's hand is reshuffled.

**Action-list design choice (4a).** Opening hands offer a median of 68 and up to 215 legal plays
(seeds 0–199, measured 2026-10-28 with an ad-hoc command). `tools/measure.py` will reproduce it and
measure prompt sizes and latency on seeds 0–104 only; it never touches held-out seeds before the freeze.

1. *Full legal list every turn* — chosen. The worst case is ~1.5k tokens and most follow turns have a
   handful of options; the model never has to invent a combination, so invalid actions measure
   attention, not rules recall.
2. *Vocabulary + validation feedback only* — rejected as default (tests rules knowledge the engine
   already enforces). Optional ablation, cut first.
3. *Grouped/truncated list* — rejected: truncation hides legal moves and biases play.

**Leakage argument.** `legal_actions(seat)` depends only on that seat's hand and the public play to
beat; off-turn it returns `[]` for everyone. `test_game.Information` reshuffles the two other hands and
checks the viewer's observation and legal list are unchanged; §7 extends this to the exact prompt.

---

## 4. Players (2b, 4b)

All players use `choose(observation, legal_actions) -> str` and see the same inputs, except the
declared `model-obs` variant, which sees less (§4.3).

### 4.1 Baseline: rule-based heuristic (`players/heuristic.py`)

Deterministic, no model calls, developed and debugged on **seeds 0–99 only** (never on tuning or
held-out seeds). Its commit hash is recorded before any held-out run.

- **Lead:** play the combination that sheds the most cards at the lowest main rank, preferring
  straights/planes/pair-sequences over singles; never lead a bomb or rocket unless it empties the hand,
  except a 6+ revolution bomb (below).
- **Follow:** play the cheapest beating move of the same kind.
- **Teamwork:** a peasant passes on its teammate's play unless it can go out.
- **Bombs:** use a bomb/rocket only when an opponent has ≤ 4 cards or it empties the hand.
- **Revolution (R10b, since 2026-11-07):** play the smallest 6+ bomb, leading or following (never over the
  teammate), when most of the remaining 3–2 cards gain from the flipped order; rank everything in the current order.
- **Endgame:** if one legal play empties the hand, play it.

`players/random_player.py` (uniform over legal actions) is a floor, showing whether the heuristic is
actually strong, and an alternative opponent for one held-out condition (§6).

**Teammate asymmetry (disclosed).** In S2/S3 the agent's teammate is the heuristic. When the
heuristic itself is the agent, its teammate is a copy with identical conventions, which helps it for
reasons that are not skill. Mitigation: the model's system prompt describes the teammate's conventions
in plain words (the bullets above), so both have the same knowledge of the partner. The remaining
asymmetry is stated in EVALUATION.md limitations.

### 4.2 Model player (`players/model.py`)

- **Input per turn:** system prompt with a rules summary, the teammate's conventions and the output
  format; user message with the observation rendered as a text table (`doudizhu/view.py`) and the numbered legal list.
- **Output:** JSON `{"action": "<exact string from the list>"}`. An optional `"reason"` field is logged
  but never used for control.
- **No tools.** No file, shell, repository or evaluator access; no tool definitions in the request.
- **Provider.** Vertex `gemini-3.5-flash-lite`, location `global`, on my course-credit project;
  live setup check passed 2026-10-28 (one request, 4.3 s, 246 tokens). Chosen explicitly with
  `COURSE_PROVIDER`/`COURSE_MODEL`/`GOOGLE_CLOUD_PROJECT`/`GOOGLE_CLOUD_LOCATION`, matching the starter.
  Thinking/output tokens capped and logged. Sampling: temperature 0, top_p 1, fixed output-token cap;
  the second trial on seeds 200–209 then measures the provider's residual nondeterminism. These
  settings live in this folder's `agent-config.json`, and its hash is written to every trace header.
- **Request controls.** The 30 s timeout is the HTTP client's timeout (not a check after the call);
  SDK automatic retries are off (`max_retries=0` as in the starter), so every attempt is one counted call.
- **Fixture mode** replays recorded replies for CI and for a TA without credentials; reports never mix
  fixture and live results. The provider SDK is imported lazily so CI never needs it.

### 4.3 Memory / history variants (required comparison for partial observation)

Dou Dizhu is partially observed (hidden hands), so all three model variants run on the **same held-out
seeds** with the same frozen strategy prompt:

- **`model-history`**: full public play history (bounded by the deal: ≤ 154 entries).
- **`model-obs`**: no history; current play to beat, card counts, own hand, kitty. Differs from
  `model-history` only in the `history` field.
- **`model-notes`** (added 2026-10-29, R23): the same as `model-history`, plus the model's own note from
  its previous turn (≤ 300 characters, one line). It writes a new note in a required `notes` field with
  each move; the runner stores it (the model still has no memory). The note shown is the last accepted
  reply's note, or "(none)"; notes from rejected replies are dropped. `notes` comes after `action` in
  the reply, so a note plans later moves, not the current one.

Disclosed: `model-obs` sees less than the heuristic and `model-history` (the heuristic ignores history
anyway, so this only handicaps the model). `model-notes` vs `model-history` is **not** a one-variable
change: besides the note itself, `model-notes` has a longer system prompt (`NOTES_ADDENDUM`), a different
response schema (`notes` required) and a longer reply to write under the same output-token cap. A
difference between them is the effect of "notes as a whole", not of memory alone. It was also added after
tuning rounds 1–3, so its addendum was not tuned.

No variant has memory across episodes. Each model call is independent; everything the model knows is in
that turn's message.

---

## 5. Runner and episode limits (3b)

`runner.py` holds the only `DouDizhu` instance and loops: whose turn → `observe` + `legal_actions` →
forced? play it : that seat's `choose` → `step`. Limits (values in `agent-config.json`):

| Limit | Value | On breach |
|---|---|---|
| Steps (all seats, incl. passes) | 400 (engine R14; backstop, natural max 316 with two decks) | engine terminal `step_limit`, no winner, scores 0 |
| Model calls, agent seat | 120 (§2.2); forced moves cost none | runner forfeit `call_limit` |
| Per-call timeout | 30 s, enforced by the HTTP client | counts as a failed call |
| Episode wall clock | 30 min, checked between calls (two-deck calls measured at ≤ 3 s, so ≤ 10 min for 120 calls in practice) | runner forfeit `timeout` |
| Invalid replies | 10 per episode (bad JSON or string not in the list; API errors/timeouts count as calls but not here) | runner forfeit `invalid_limit` |

**Failed call handling.** Every attempt counts as one call. On a bad reply or failed call the model
gets one retry with the error text. If the retry fails too, the runner plays the heuristic's move
(R21, `source: fallback`). Fallbacks never count as model moves.

**Forfeit result (R18), produced by the runner, not `engine.outcome()`:**

```
{"status": "terminal", "reason": "call_limit" | "timeout" | "invalid_limit",
 "forfeit": true, "winner": <the side opposing the agent>, "spring": false,
 "multiplier": 2 ** bombs_played_so_far, "scores": <as if that side won at that multiplier>}
```

A peasant agent's forfeit is a loss for both peasants (team game). The trace still stores
`engine.outcome()` ("ongoing") beside the runner result.

Disclosed: provider slowness or outages count against the model (timeouts are failed calls and can
end in a forfeit). The only latency figure so far is one 246-token setup request (4.3 s); median and
p95 are measured on tuning seeds before the held-out run, and the limits are re-checked against them.

**Trace format.** One JSONL file per episode: header (seed, situation, seats, player ids, model id as
requested (`model_requested`), game version = git commit, config hash), one line per step (seat, source
`model|fallback|forced|heuristic|random`, action, accepted, and per model attempt: prompt hash,
latency, input/output tokens, raw reply, model id returned by the API),
then the final result with its terminal reason and `models_returned`. API-error text is reduced
to the exception type and status code (provider messages can contain the project ID).

---

## 6. Evaluation suite, declared before tuning (4b, 5a)

**Freeze:** this section is frozen by a local git commit on 2026-10-28 before any prompt tuning.
Because a local commit date is self-set, I also post the suite and that commit hash in my Week 3
thread the same day, which gives a third-party timestamp. This branch is never rebased or squashed,
so the commit keeps its date when pushed. Later changes are logged in EVALUATION.md with a reason.

**Paired design.** Every player plays the same seed, in the same seat relative to the landlord,
against the same deterministic opponents. Differences come from decisions and the opponents' replies
to them. This is not bridge-style duplicate (no side swap), so card luck still decides many deals; the
seed count below is sized for that.

| Situation | Agent seat | What it tests |
|---|---|---|
| S1 Landlord | landlord (42 cards, leads) | solo play, tempo, bomb timing |
| S2 Peasant after landlord | landlord + 1 | blocking the landlord, team passing |
| S3 Peasant before landlord | landlord + 2 | supporting the teammate, feeding them the lead |

**Seeds.**
- Heuristic development: 0–99.
- Prompt tuning: 100–104.
- Held out: **200–229** (30 per situation), untouched until the prompt, heuristic and config commits
  are frozen and their hashes recorded in EVALUATION.md.

**Runs.**

| Player | Opponents | Episodes |
|---|---|---|
| heuristic, random | heuristic | 3 situations × 30 seeds, one run each (deterministic / seeded) |
| `model-history` | heuristic | 3 × 30 × 1 trial, plus a 2nd trial on seeds 200–209 (3 × 10) to measure run-to-run variation = 120 |
| `model-obs` | heuristic | 3 × 30 × 1 = 90 |
| `model-notes` (added 2026-10-29, before any held-out run) | heuristic | 3 × 30 × 1 = 90 |
| `model-history` vs heuristic, held-out opponent | random | S1, seeds 200–209 = 10 each |

Each situation gets ≥ 30 live trials, above the brief's minimum of two.

**Budget (two decks, 2026-11-06).** ~16–18 non-forced calls per episode. Input tokens per call: median
~850, max ~54k (landlord openings with up to 5,921 legal moves); per episode ~10–35k by situation
(`tools/measure.py`; live check on tuning seeds 100–101, S1: 37 calls, 167k input tokens, latency
median 0.9 s, max 3.0 s, output ≤ 49 tokens). 310 live episodes → ≈ $2–3 at the dated price.
(One-deck budget was ≈ $0.65; the one-deck run actually cost ≈ $1.27.)

**Metrics per player × situation:**
- wins / losses / no-result, with forfeits by reason (`call_limit`, `timeout`, `invalid_limit`) in
  their own columns
- mean score; **paired** score difference vs the heuristic and the number of discordant pairs
  (deals where the two players' results differ), per situation and pooled
- the same win and score figures over fallback-free episodes only, plus fallbacks per episode
- illegal/invalid replies, forced moves, latency (median, p95), input/output tokens, cost with price
  date
- seeds, model id, config hash, game commit

**Interpretation rule.** Counts and paired differences, no significance claims. "Model beats
heuristic on S1" describes this sample only.

**Self-play (optional, cut first).** Model in all three seats on 5 seeds, described as behavior, not
improvement.

---

## 7. Deterministic CI (3c)

`.github/workflows/midterm-lululizzy8.yml` runs `python -m unittest discover -s tests -v` from this
folder on PRs touching it. No secrets, no network, no provider SDK. It first runs on GitHub when the
branch is pushed (§13).

| Kind | Tests | Status |
|---|---|---|
| Rule invariants | `test_combos.Invariants`; card conservation and zero-sum in `test_game.Turns.test_full_games_end_and_conserve_cards` | done |
| Legal / illegal actions | `test_combos.Lead`, `Rejected`, `Beats`; `test_game.Turns.test_refused_actions_change_nothing`; new: non-string action refused, bad seat refused | partly done |
| Terminal outcome | `test_game.Scoring` + new landlord-no-spring, rocket, two-bomb cases; full-deal loop | partly done |
| Observed regression | `tests/test_regressions.py`: two real bugs found by the 2026-10-28 rules review: `observe(-1)` leaked seat 2's hand, and a non-string action crashed `step`. Each test was committed failing before the fix commit. Later bugs get the same treatment. | done |
| Episode limits | `test_game.Limits` (step); `tests/test_runner.py` with a fixture model: `call_limit`, `timeout`, `invalid_limit`, forfeit result shape, fallback and forced labeling | step done |

Also in `test_runner.py`:
- **Prompt leak test:** build the agent's prompt, reshuffle the other two hands, rebuild, assert the two
  prompts are byte-identical; assert the seed and trace path never appear. Includes S2's first turn
  (the `reset` return case).
- Heuristic and random complete 50 deals with no illegal action, and their choices are unchanged by
  reshuffling other hands.

---

## 8. Commands and file layout (3a)

All commands from `midterms/lululizzy8/`.

```
python -m unittest discover -s tests -v                          # deterministic checks
python play.py --seat 0 --seed 7                                 # human vs two heuristics
python runner.py --player heuristic --situation S1 --seeds 200-229
python runner.py --player model-history --fixture --situation S1 --seeds 100-100   # no credentials
python report.py traces/ --out results.md                        # comparison table (UTF-8; PowerShell `>` would write UTF-16)
```

Live run (Vertex):

```
pip install -r requirements.txt                 # pinned google-genai
gcloud auth application-default login
```
PowerShell:
```
$env:COURSE_PROVIDER='vertex'; $env:COURSE_MODEL='gemini-3.5-flash-lite'
$env:GOOGLE_CLOUD_PROJECT='<your project>'; $env:GOOGLE_CLOUD_LOCATION='global'
python runner.py --player model-history --situation S1 --seeds 200-229
```
bash: the same with `export NAME=value`.

```
midterms/lululizzy8/
  README.md  GAME-DESIGN.md  EVALUATION.md  AGENT-TEAM.md  CLAUDE.md  .gitignore
  agent-config.json  requirements.txt
  doudizhu/engine.py
  players/heuristic.py  random_player.py  model.py
  runner.py  play.py  report.py  tools/measure.py
  tests/  traces/  reviews/  sessions/  playtest.txt
  .claude/skills/ddz-rule-change/  .claude/skills/ddz-eval-run/  .claude/agents/ddz-rules-reviewer.md
```

`.gitignore` excludes `__pycache__/` and scratch traces; held-out traces are committed (JSONL
compresses well), or a summary plus link if they exceed a few MB. No credentials in any trace.

---

## 9. Sources and reuse terms (1c)

- **Pagat**, John McLeod, "Dou Dizhu", https://www.pagat.com/climbing/doudizhu.html. The site is
  copyrighted; I link to it and use only rule facts (rules of a game are not copied text); no prose
  copied. **TODO: verify each README locator against the page headings, quoting a short phrase where a
  section has no anchor.**
- **RLCard** (Zha et al.) and **DouZero** (Zha et al., 2021): cited only if EVALUATION.md mentions
  them as background on Dou Dizhu AI; no code used. If cited, link their licence files
  (github.com/datamllab/rlcard, github.com/kwai/DouZero) after opening them; otherwise drop them.
- **Course repository material** (columbia-university-ai-games/game-dev-f26, instructor-owned, used as
  course material at commit `66f051b`):
  - `.claude/skills/rule-change/SKILL.md` and `.claude/agents/rules-reviewer.md` are the starting
    points for this folder's `ddz-rule-change` skill and `ddz-rules-reviewer` agent; each adapted copy
    names its source path and commit at the top.
  - `course_game/narrator.py`: the pattern for the provider call (env-var names, explicit provider
    choice, no automatic retries, HTTP timeout). Any code adapted from it says so in a comment.
- **google-genai** (Google, Apache-2.0, https://github.com/googleapis/python-genai): the Vertex client
  library, installed via `requirements.txt`, not vendored.
- No assets reused. Everything else (engine, players, runner, tests, docs) is written in this folder.

---

## 10. Building agent team (3d, 5b)

The repo-root skill and reviewer describe the course's sample game (`world.py`,
`docs/rule-source-map.md`) and are instructor-owned, so this folder gets adapted copies; root files stay
untouched. Sessions are run with this folder as the working directory.

| Role | Artifact | Allowed | Evidence |
|---|---|---|---|
| Implementation agent | `CLAUDE.md` in this folder (scope: only this folder + the workflow file) | read/write this folder, run tests | exported transcripts in `sessions/` |
| Reusable skill | `.claude/skills/ddz-rule-change/` adapted to README map, `engine.py`, `runner.py`, `tests/`, with the `design` label | — | invoked for each §2.1 change |
| Reusable skill | `.claude/skills/ddz-eval-run/`: run the frozen suite, refuse to mix fixture and live, record hashes and price date, fill the EVALUATION table | invoked in ≥ 2 sessions | `sessions/` |
| Independent review | `.claude/agents/ddz-rules-reviewer.md` adapted copy (Read, Grep, Glob), run in a session that did not write the code | read-only | `reviews/YYYY-MM-DD-*.md` |
| Role agents (optional, cut first) | design/QA/production reviewers as `.claude/agents/*.md` so they are invocable | read-only | recommendation + my decision in `AGENT-TEAM.md` |

The `ddz-` prefix keeps them distinct from the root copies, which Claude Code also loads, so a
transcript shows unambiguously which one ran.

**Transcript hygiene.** The repo is public. Before committing anything to `sessions/`, remove my email
address, the GCP project ID/number, local user paths and any credential file paths.

Already done: `reviews/2026-10-28-design-review.md` (two independent reviewers on rev 1) and
`reviews/2026-10-28-design-review-rev2.md` (one on rev 2).

**[student voice]** `AGENT-TEAM.md` is written by me: each agent, what it saw/did, what it
recommended, what I decided and why. No agent approves a gate or merges the PR.

---

## 11. Design decisions and the alternatives they beat (4a)

| Choice | Picked | Beat | Why |
|---|---|---|---|
| Game | Dou Dizhu | Guandan (Week 3) | One deck, no wild cards, one deal is a complete episode. |
| Landlord | seed picks it; agent seated relative to it | bidding; forcing the landlord seat (R17) | Controls the agent's role with no engine change. |
| Kickers | distinct ranks | any cards | One card list = one combination, so actions are unambiguous. |
| Action format | exact card list from the full legal list | free vocabulary; truncated list | Measures play, not rules recall; nothing hidden. |
| Forced moves | auto-played, labeled | ask the model every turn | Not a decision; saves budget; avoids false `call_limit`. |
| Baseline | rule-based heuristic (+ random floor) | random only; search/RL (DouZero) | Strong, cheap, explainable; RL is out of budget and not mine. |
| Opponents | heuristic (+ random as a held-out opponent) | model vs model | Fixed opponents make deals comparable across players. |
| Teammate knowledge | conventions described to the model | say nothing | Removes most of the "copy of itself" advantage. |
| Comparison | paired deals, 30 held-out seeds per situation | independent deals; 10 seeds | Reduces card luck; enough discordant pairs to show a difference. |
| History / memory | three variants: no history, full public history, history + own notes | one variant only | Each step adds one kind of information, so each comparison changes one thing. |
| Fallback | heuristic move, labeled, plus fallback-free stats | random move; skip turn | Keeps the deal playable; results stay honest. |
| Budget breach | runner forfeit = loss, own column | continue on fallback; draw | A run that ran out of budget did not succeed. |

---

## 12. Human playtests, peer notes, recording (2a, 5b, 5c)

- **`play.py`** (ready by Nov 1 for the peer playtest): text table; the human picks one seat, the
  other two are heuristics; shows hand, kitty, counts, play to beat and numbered legal plays (type a
  number or the cards).
- **Peer playtest (week of Nov 2):** my partner plays one deal as landlord and one as peasant; I record
  only what I observe: confusions, wrong guesses about rules, time per decision. Received notes are in
  [`playtest.txt`](playtest.txt), anonymized. Findings: the rules are not clear to a new player, the text
  table makes the hand hard to read and other players' turns too fast, and two decks give up to ~200
  legal plays per turn, too many to read as a list.
- **Changes after the playtest (Nov 6):** the browser version (`web/`) became the main way to play:
  a home screen (play, handbook, watch the baseline, watch the AI); a card table with three seats where
  the others show only card backs and counts; a pile in the middle (latest play, the rest of the round,
  earlier rounds face down); a turn highlight and a "thinking" pause of about 1–2 s before each other
  player's move, with no timer on yours; a handbook of every combination with pictures; a sorted hand you
  can reorder by dragging; and play by picking cards, with Play enabled only for a legal move and a
  plain-words reason otherwise (`Session.explain`). This replaces reading a 200-item list. I chose to
  extend the web page rather than port to Pyxel (a 42-card hand does not fit its low resolution), and
  to watch the AI live through a local server (`web/serve.py`, which reuses `runner.run_episode`) rather
  than replay recorded traces. No rule, observation or legal-action change.
- **Recording (3–5 min):** 0:00 scope + rules in 30 s → 0:30 human-mode table → 1:15 runner with the
  model as landlord on a held-out seed, trace scrolling, a refused action and retry if one occurs →
  3:00 comparison table → 3:45 limits (small sample, one provider, heuristic opponents, teammate
  asymmetry). Linked from the README and the PR: https://youtu.be/zRIMSmfkGlA

---

## 13. Plan and schedule (today 2026-10-28, due 2026-11-07 11:59 p.m.)

Local only until the submission is complete. Two consequences:
- **Freeze evidence:** commit locally (no push) as soon as §6 is final, so the commit date predates
  tuning. Commit dates are kept when pushed later.
- **CI evidence:** GitHub CI runs only after a push and a PR, so push and open the PR by **Nov 6** at
  the latest, leaving a day to fix a red run. Until then, run the same command locally.

| Date | Work |
|---|---|
| Oct 28 | `.gitignore`; local freeze commit; Week 3 post |
| Oct 29–30 | §2.1 changes via rule-change + reviewer; heuristic (seeds 0–99); runner, limits, forced/fallback; `test_runner.py`; `play.py` |
| Oct 31 | model player + fixtures; first live episode with trace; first small table; `tools/measure.py` |
| Nov 1 | tune on 100–104; freeze prompt/heuristic/config; record hashes |
| Nov 2–3 | held-out run (~5 h wall time, parallel by situation) |
| Nov 4 | `report.py`, `EVALUATION.md` |
| Nov 5–6 | peer playtest and notes; push, open PR, CI green |
| Nov 6–7 | **[student voice]** README scope, `AGENT-TEAM.md`, limitations; recording; PR links; CourseWorks URL |

Cut first if late: self-play, vocabulary ablation, role agents, random-opponent condition.
