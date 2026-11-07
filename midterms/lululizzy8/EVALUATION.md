# Evaluation

The current game is two decks with Revolution (GAME-DESIGN.md §2.2 and §2.3, README R10b). The first
section evaluates it. The two older suites below it (two decks without Revolution, and one deck) are kept as
history; their numbers don't describe the current game. I ran every suite with the `ddz-eval-run` skill.

## Two decks with Revolution (current version)

### Declared suite (2026-11-07, before any revolution evaluation episode)

- Same structure as the two-deck suite: situations S1-S3; players `heuristic`, `random`,
  `model-history`, `model-obs`, `model-notes`; opponents heuristic, plus a random-opponent condition
  (S1, 10 seeds); `model-history` gets a second trial on the first 10 seeds. 310 live episodes.
- Held-out seeds 400-429, never run on any version before. Development seeds 0-99 and tuning seeds
  100-104 as before; 200-229 and 300-329 are already used.
- No prompt tuning for revolution. The prompt is the frozen two-deck prompt plus the revolution rules
  sentence and the two corrections from the revolution review (teammate habit, strategy rule 1 exception).
  No live model episode was run on the revolution game before this suite.

### Measurements (2026-11-07, `python tools/measure.py`, seeds 0-104, all seats heuristic)

- opening legal-list size: median 2,425, max 5,921 (unchanged: revolution changes order, not the opening list)
- steps per deal: median 63, max 94 (step limit 400)
- non-forced decisions per seat per deal: median 18, max 29 (call limit 120)
- estimated input tokens per call: `model-history` median ~1,000, max ~54k; `model-obs` median ~720, max ~54k
- revolution happens in 44% of heuristic self-play deals (development seeds 0-99; GAME-DESIGN.md §2.3)

### Frozen versions

Frozen 2026-11-07, before any revolution held-out seed was run.

| Item | Commit / hash |
|---|---|
| `players/model.py` (prompt) | `d3564aa`: two-deck prompt + revolution rules sentence + review corrections; not re-tuned |
| `players/heuristic.py` | `d3564aa`: smallest bomb first; plays a 6+ bomb to flip the order when most remaining 3-2 cards gain (R10b) |
| `doudizhu/engine.py` | `d3564aa`: R10b |
| `agent-config.json` | unchanged, config hash `9540bd7658e1` (call_limit 120, max_steps 400) |
| Game commit | the commit recorded in each held-out trace header (`game_commit`) |

### Results

#### 2026-11-07: revolution held-out suite (seeds 400-429)

Full table: `results/heldout-revolution-2026-11-07.md`. Traces: `traces/heldout-revolution/` (510 episodes,
310 live and 200 baseline). Model `gemini-3.5-flash-lite` as returned by the API, Vertex AI `global`, config
hash `9540bd7658e1`. Cost about $6.85 (6,116 calls, 20.9M input and 230k output tokens at the dated price).
Longest episode 66 s.

Version labels: 230 traces say `deb95b1` and 280 say `deb95b1-dirty`. The dirty ones started after I edited
README.md, AGENT-TEAM.md and EVALUATION.md and added two chat exports during the run. `git diff deb95b1`
shows no other changes, so every episode ran the frozen code.

Main comparison: first trial only, so every player gets the same 30 deals per situation, opponents
heuristic. Wins out of 30, then mean agent score.

| Player | S1 (landlord) | S2 (peasant after landlord) | S3 (peasant before landlord) |
|---|---|---|---|
| heuristic (baseline) | **14/30, -1.07** | **16/30, +0.53** | **16/30, +0.53** |
| random | 2/30, -6.73 | 9/30, -1.37 | 14/30, -0.33 |
| model-history | 7/30, -1.60 | 8/30, -1.63 | 13/30, +0.50 |
| model-obs (no history) | 4/30, -5.00 | 8/30, -1.77 | 11/30, -0.47 |
| model-notes (history + own notes) | 5/30, -2.40 | 10/30, -1.03 | 14/30, +0.13 |

Failures over all 310 live episodes: no forfeits and no step-limit endings. 3 API errors: two slow (16 s and
28 s, landlord turns with long move lists) and one quick. 5 invalid replies, all fixed on the retry. 1
fallback move (heuristic move, labeled `fallback`) in `model-notes` S2 seed 415; without it that cell is
9/29. Latency median 0.8 to 0.9 s, p95 at most 1.5 s.

Repeat trial: `model-history` played seeds 400-409 twice. Both trials gave the same win or loss on 8/10
deals as landlord, 6/10 in S2 and 10/10 in S3.

Random opponents (S1, seeds 400-409): heuristic 10/10, `model-history` 6/10, random 4/10.

How often Revolution came up: a 6+ bomb was played in 18 to 27 of the 90 first-trial deals per player
(about 20 to 30%). The model started a revolution itself only once in 270 deals (`model-obs`). Every other
revolution came from a heuristic player.

What I take from it (30 deals per cell, so these are tendencies, not proof):
- As landlord the model is still weaker than the heuristic, but the gap shrank. Paired on the same deals,
  `model-history` scores 1.10 per deal below the heuristic over its 40 S1 episodes (3.85 without
  Revolution). The heuristic won 14/30 here, down from 19/30, partly because peasants now flip the order
  against it.
- As a peasant the heuristic did best in both seats. The model players sit between random and the
  heuristic, and in S3 everyone is close (11 to 16 wins).
- History helped a little this time: `model-history` matched or beat `model-obs` in every situation (7 vs 4,
  8 vs 8, 13 vs 11). Notes were about as good as history.
- The model knows the rule (it's in the prompt and the table says REVOLUTION) but almost never uses it. It
  plays along with revolutions other players start and doesn't start its own.
- Timeouts dropped from 13 to 2 compared with the run without Revolution, on the same call limit and
  prompt size. I can't say why from these runs.

## Two decks without Revolution (superseded 2026-11-07, game commit `83c5dcf`)

### Declared suite (2026-11-06, before any two-deck evaluation episode)

- Same structure as the one-deck suite: S1-S3; `heuristic`, `random`, `model-history`, `model-obs`,
  `model-notes`; heuristic opponents plus a random-opponent condition (S1, 10 seeds); a second
  `model-history` trial on the first 10 seeds. 310 live episodes.
- Held-out seeds 300-329, new for this suite. Development seeds 0-99 and tuning seeds 100-104 as before.
- No prompt tuning on two decks: the frozen round 2 prompt with its rules paragraph rewritten for two
  decks. The only two-deck model episodes before this suite were 2 size and latency checks on tuning seeds
  100-101, S1 (`traces/tuning-2deck/`), run before the prompt and config were frozen.

### Measurements (2026-11-06, `python tools/measure.py`, seeds 0-104, all seats heuristic)

- opening legal-list size: median 2,425, max 5,921 (one deck: median 67, max 215)
- steps per deal: median 59, max 94 (step limit 400, bound 316)
- non-forced decisions per seat per deal: median 17, max 28; max 20 with a random agent (call limit 120)
- estimated input tokens per call: `model-history` median ~850, max ~54k; `model-obs` median ~590, max ~54k
- live check, tuning seeds 100-101, S1, `model-history`: 37 calls, latency median 0.9 s and max 3.0 s, max
  output 49 tokens (cap 256), 167k input tokens; 2 invalid replies (a straight not in the list), both
  fixed on the retry.

### Frozen versions

Frozen 2026-11-06, before any two-deck held-out seed was run.

| Item | Commit / hash |
|---|---|
| `players/model.py` (prompt) | `e9fb2d8`: round 2 strategy rules, rules paragraph rewritten for two decks; not re-tuned |
| `players/heuristic.py` | `e9fb2d8`: smallest bomb first (fewest cards, then lowest rank) |
| `agent-config.json` | `e9fb2d8`, config hash `9540bd7658e1` (call_limit 120, max_steps 400) |
| Game commit | recorded in each held-out trace header (`game_commit`) |

### Results

#### 2026-11-06: two-deck held-out suite (seeds 300-329)

Full table: `results/heldout-2deck-2026-11-06.md`. Traces: `traces/heldout-2deck/` (510 episodes, 310 live
and 200 baseline). Model `gemini-3.5-flash-lite` as returned by the API, Vertex AI `global`, config hash
`9540bd7658e1`, game commit `83c5dcf` in every trace. Cost about $6.0; I had estimated $2-3, but the
history and notes prompts grew with the long two-deck histories. Longest episode 101 s.

Main comparison: first trial only, same 30 deals per situation, heuristic opponents. Wins out of 30, then
mean agent score.

| Player | S1 (landlord) | S2 (peasant after landlord) | S3 (peasant before landlord) |
|---|---|---|---|
| heuristic (baseline) | **19/30, +0.87** | 11/30, -0.43 | 11/30, -0.43 |
| random | 1/30, -4.73 | **14/30, -0.27** | 8/30, -1.67 |
| model-history | 3/30, -3.67 | 6/30, -0.93 | 9/30, -0.50 |
| model-obs (no history) | 5/30, -3.13 | 10/30, -0.90 | 8/30, -1.13 |
| model-notes (history + own notes) | 5/30, -2.40 | 5/30, -1.57 | 9/30, **-0.40** |

Failures over 310 live episodes: no forfeits and no step-limit endings. 15 failed API calls: 13 hit the
30 s call timeout on landlord turns with very long move lists, 2 failed quickly. 4 fallback moves, each
after both tries of a turn failed, all in S1 (`model-history` s306 t1, `model-notes` s300, `model-obs` s300
and s308); the full table has fallback-free figures. 8 invalid replies, all fixed on the retry. Latency
median 0.8-0.9 s, p95 at most 1.9 s.

Repeat trial on seeds 300-309: same win or loss on 6/10 deals in S1, 8/10 in S2, 10/10 in S3.

Random opponents (S1, seeds 300-309): heuristic 9/10, `model-history` 8/10, random 7/10. Scores run high
here (up to +39.6) because random opponents play lots of bombs and each one doubles the stake.

What I took from it:
- Two decks made the model much weaker as landlord: the heuristic won 19/30, the model players 3-5/30,
  close to random (1/30). Paired on the same deals, `model-history` scored 3.85 per deal below the heuristic
  over its 40 S1 episodes. All timeouts and fallbacks happened on landlord turns with up to ~5,900 moves.
- As a peasant everyone was close. Random even did best in S2 (14/30), which shows how much a peasant's
  result depends on the teammate and the deal.
- History vs no history showed no consistent difference (S1 3 vs 5, S2 6 vs 10, S3 9 vs 8). Notes had the
  best mean score of the model players in S1 and S3 but not S2, and notes change more than one thing
  (GAME-DESIGN.md §4.3).
- Compared with one deck, the model's landlord wins fell from 8/30 to 3/30 and the heuristic's rose from
  17/30 to 19/30. The prompt wasn't re-tuned for two decks.

## One-deck version (superseded 2026-11-06, game commit `eed053e`)

This section covers the one-deck game: 54 cards, 17-card hands (20 for the landlord), held-out seeds 200-229.

### Declared suite (frozen before tuning)

Declared in `GAME-DESIGN.md` §6, frozen by commit `6795857` on 2026-10-28 and posted in my Week 3 thread.

- Situations: S1 the agent is landlord, S2 peasant after the landlord, S3 peasant before the landlord.
- Opponents: heuristic in every run; random in the held-out random-opponent condition (S1, seeds 200-209).
- Seeds: heuristic development 0-99, prompt tuning 100-104, held out 200-229.
- Players: `heuristic`, `random`, `model-history` (full public history), `model-obs` (no history),
  `model-notes` (history plus its own notes, added 2026-10-29; see the change log).
- Live runs: `model-history` 3 × 30 plus a second trial on 200-209 (3 × 10); `model-obs` 3 × 30;
  `model-notes` 3 × 30; random-opponent condition 10. 310 live episodes. Baselines once per situation and seed.

### Frozen versions before the held-out run

Frozen 2026-11-06, before any held-out seed was run.

| Item | Commit / hash |
|---|---|
| `players/model.py` (prompt) | `fa58165`: the round 2 prompt (`27e56eb`); rule 4 from round 3 removed because it made play worse |
| `players/heuristic.py` | `253e79f`, unchanged since it was written |
| `agent-config.json` | `cb6d27a`, config hash `13e067d04638` (in every trace) |
| Game commit | recorded in each held-out trace header (`game_commit`) |

### Measurements on non-held-out seeds (2026-10-28, `python tools/measure.py`)

Seeds 0-104, all seats heuristic:
- opening legal-list size: median 67, max 215
- steps per deal: median 41, max 70 (step limit 200, bound 154)
- non-forced decisions per seat per deal: median 11, max 22 (call limit 60 covers 22 × 2 attempts)
- estimated input tokens per call (characters / 4): `model-history` median 587, max 1675; `model-obs`
  median 403, max 1653

Baseline strength on development seeds 0-99 (heuristic vs random in the agent seat, heuristic opponents),
wins out of 100: S1 58 vs 4, S2 42 vs 30, S3 42 vs 36.

### Known limits of the runner (from the 2026-10-28 runner review)

- The wall clock is checked before each model call, so one call can run past the limit by up to the 30 s
  HTTP timeout, and an episode whose clock runs out after the agent's last decision ends normally.
- Output cap: replies used about 30 of the 256 output tokens in the first live episode, so thinking
  tokens didn't cut replies off.
- `model-notes` replies against the same cap, checked 2026-11-06 on tuning seeds 100-101 (S1, 10 calls,
  `traces/notes-check/`): median 68, max 76 tokens, so notes aren't truncated.

### Results

#### 2026-10-28: first live episode (tuning seed 100, S1)

Table: `results/tuning-2026-10-28.md`; traces: `traces/tuning/`. One episode, so it shows the pipeline
working, not which player is better.

| Player | Mode | Result | Agent score | Calls | Invalid | Fallbacks | Forced | Latency median / max | Tokens in / out (est. cost) |
|---|---|---|---|---|---|---|---|---|---|
| heuristic | - | landlord wins | +2 | 0 | 0 | 0 | 2 | - | - |
| model-history | live, `gemini-3.5-flash-lite` (id returned by API) | landlord wins (rocket played, ×2) | +4 | 6 | 0 | 0 | 1 | 0.84 s / 2.28 s | 4,940 / 186 (about $0.0019) |

The report shows `pairs 0/1` for this run because the live episode was labeled `ed6502c` and the heuristic
run `ed6502c-dirty`: writing the first trace made the folder look modified. That was a bug, and it became a
regression test (`test_regressions.FoundInFirstLiveRun20261028`, failing commit `5a002a0`, fix `8379355`).
The code was the same under both labels, so I matched the pair by hand.

#### 2026-10-28: tuning round 1 (seeds 100-104, prompt as of `eeb053f`)

Full table: `results/tuning-r1-2026-10-28.md`; traces: `traces/tuning-r1/`. 5 deals per cell, so these are
tuning notes, not results. Cost about $0.075 for 30 episodes.

| Player | S1 wins / mean | S2 wins / mean | S3 wins / mean | Invalid | Fallbacks | Latency median / p95 |
|---|---|---|---|---|---|---|
| heuristic | 4/5, +1.6 | 1/5, -0.8 | 1/5, -0.8 | - | - | - |
| random | 1/5, -1.6 | 1/5, -1.2 | 1/5, -1.2 | - | - | - |
| model-history | 1/5, -3.2 | 2/5, -0.6 | 1/5, -0.8 | 0 | 0 | ~0.8 s / 1.4-2.3 s |
| model-obs | 1/5, -1.6 | 1/5, -0.6 | 1/5, -0.8 | 0 | 0 | ~0.8 s / 4-24 s |

- As landlord the model was far below the heuristic (paired difference -4.8 with history, -3.2 without).
  On seed 104 it led its rocket while it already had the lead, wasting it, then led a single 2 into a bomb.
  The heuristic kept its jokers and won.
- Temperature 0 isn't deterministic: seed 100 S1 won +4 in the first run and lost -4 here.
- No invalid replies or fallbacks in 30 episodes. The slowest call (24 s, `model-obs` S1) stayed under the
  30 s timeout.

#### 2026-10-29: tuning round 2 (same seeds, prompt `27e56eb`: three strategy rules)

The prompt gained three rules: never play a bomb or rocket when you already have the lead; don't lead 2s or
jokers as singles early; check that the rest of the hand can still be played out. Full table:
`results/tuning-r2-2026-10-29.md`; traces: `traces/tuning-r2/`. Cost about $0.106.

| Player | S1 wins / mean | S2 wins / mean | S3 wins / mean | Invalid | Fallbacks | Latency median / p95 |
|---|---|---|---|---|---|---|
| heuristic | 4/5, +1.6 | 1/5, -0.8 | 1/5, -0.8 | - | - | - |
| model-history | 4/5, +2.4 (r1: 1/5, -3.2) | 3/5, +0.2 (r1: 2/5) | 2/5, -0.4 (r1: 1/5) | 0 | 0 | ~0.8 s / 1.3-1.9 s |
| model-obs | 2/5, -0.8 (r1: 1/5, -1.6) | 2/5, -0.2 (r1: 1/5) | 1/5, -1.0 (r1: 1/5) | 0 | 0 | ~0.8 s / ~1 s |

- Bombs or rockets played while already holding the lead (rough count over model leads after two passes):
  1 of 66 in round 1, 0 of 68 in round 2.
- `model-history` went from well below the heuristic to level with it or above on these 5 deals per
  situation; `model-obs` improved less. With 5 deals and the variation seen in round 1, part of this may be
  noise.
- Calls per episode rose (S1: 44 to 56 over 5 deals), still far under the limit of 60.

#### 2026-10-29: tuning round 3 (same seeds, prompt `2257ca7`: rule 4)

Rule 4: "When you lead, play a combination you think you can win back ... Among those, start with your
lowest." Full table: `results/tuning-r3-2026-10-29.md`; traces: `traces/tuning-r3/`. Cost about $0.107.

| Player | S1 wins / mean | S2 wins / mean | S3 wins / mean | Invalid | Fallbacks |
|---|---|---|---|---|---|
| heuristic | 4/5, +1.6 | 1/5, -0.8 | 1/5, -0.8 | - | - |
| model-history | 2/5, -0.4 (r2: 4/5, +2.4) | 2/5, -0.2 (r2: 3/5) | 1/5, -1.0 (r2: 2/5) | 0 | 0 |
| model-obs | 1/5, -1.2 (r2: 2/5) | 1/5, -0.8 (r2: 2/5) | 1/5, -0.8 (r2: 1/5) | 0 | 0 |

Worse than round 2 everywhere. On seed 104 S1 the round 2 prompt opened with its 15-card plane; with rule 4
it led a single 3, then played singles one at a time, broke up its hand and lost. "Start with your lowest"
seems to override "lead long combinations first", so I dropped rule 4.

#### 2026-11-06: held-out suite (seeds 200-229)

Full table: `results/heldout-2026-11-06.md`; traces: `traces/heldout/` (510 episodes, 310 live and 200
baseline). Model `gemini-3.5-flash-lite` as returned by the API, Vertex AI `global`, config hash
`13e067d04638`, game commit `eed053e` in every trace. Cost about $1.27; I had estimated $0.65, but history
prompts grew longer than on the development seeds.

Main comparison: first trial only, same 30 deals per situation, heuristic opponents. Wins out of 30, then
mean agent score.

| Player | S1 (landlord) | S2 (peasant after landlord) | S3 (peasant before landlord) |
|---|---|---|---|
| heuristic (baseline) | **17/30, +0.27** | **13/30, -0.13** | 13/30, -0.13 |
| random | 2/30, -2.00 | 9/30, -0.40 | 10/30, -0.47 |
| model-history | 8/30, -1.20 | 8/30, -0.53 | 12/30, -0.30 |
| model-obs (no history) | 3/30, -1.93 | 11/30, -0.30 | **14/30, -0.07** |
| model-notes (history + own notes) | 10/30, -0.53 | 12/30, -0.30 | 11/30, -0.50 |

Failures over 310 live episodes: no forfeits, no step-limit endings, no fallback moves. 3 invalid replies,
all fixed on the retry, and 1 API error (retried). Latency median 0.8-1.0 s, p95 at most 2.3 s.

Repeat trial on seeds 200-209: same win or loss on 7/10 deals in S1, 5/10 in S2, 9/10 in S3. Temperature 0
isn't deterministic, and single deals vary a lot.

Random opponents (S1, seeds 200-209): heuristic 10/10 (+2.2), `model-history` 7/10 (+0.4), random 3/10.

What I took from it:
- The heuristic was the strongest landlord: 17/30 against 8-10/30 for the model players. Paired on the
  same deals, `model-history` scored 1.55 per deal below the heuristic over its 40 S1 episodes. The round 2
  prompt's gains on the 5 tuning deals didn't hold up on held-out deals.
- As a peasant everyone was close (8-14 wins), inside the trial-to-trial variation, and the result also
  depends on the heuristic teammate.
- History helped as landlord (8 vs 3 wins) but not as a peasant. Notes did best as landlord (10/30), but
  notes also change the system prompt and reply format (GAME-DESIGN.md §4.3), so it isn't a clean
  comparison, and `model-notes` was never tuned.
- The suite separates the players: random is far below the heuristic as landlord (2 vs 17 wins) and the
  model sits between them.

## Price

Gemini 3.5 Flash-Lite on Vertex AI, location `global`, standard rate: $0.30 per 1M input tokens and $2.50
per 1M output tokens (output includes reasoning tokens). Source:
https://cloud.google.com/vertex-ai/generative-ai/pricing, checked 2026-10-28. Cached input ($0.03) isn't
used. Cost = tokens × price, from `python report.py <dirs> --price-in 0.30 --price-out 2.50`. These are
estimates from the tokens the API reports, not billed amounts.

## Traces

- `traces/heldout-revolution/`: revolution held-out suite (current game).
- `traces/heldout-2deck/` and `traces/tuning-2deck/`: two decks without Revolution.
- `traces/heldout/`, `traces/tuning*/`, `traces/notes-check/`: one-deck game.
- `traces/watch/`: games from Watch the AI in the browser, if any were played. Not part of the evaluation.

Each file has one JSON object per line: a header, one line per step (every model attempt with its raw reply,
latency and tokens, and whether the move came from the `model`, was `forced` or was a `fallback`), then the
result.

## CI evidence

TODO: link to the green Actions run for the submitted commit. Locally,
`python -m unittest discover -s tests -v` passes all 102 tests (2026-11-07).

| CI check kind (rubric 3c) | Tests |
|---|---|
| Rule invariants | `test_combos.Invariants`; `test_game.Turns.test_full_games_end_and_conserve_cards` |
| Legal / illegal actions | `test_combos.Lead`, `Rejected`, `Beats`; `test_game.Turns`; `test_revolution`; `test_runner.Fallback` |
| Terminal outcome | `test_game.Scoring`; `test_runner.Baselines` |
| Observed regression | `test_regressions`: two bugs found by review (failing `7168315`, fixed `72bfc27`); one found in the first live run (failing `5a002a0`, fixed `8379355`) |
| Episode limits | `test_game.Limits`; `test_runner.Limits` (call, invalid, timeout, step, forfeit scoring) |
| Information boundary | `test_game.Information`; `test_view`; `test_runner.Prompt`; `test_web` and `test_serve` (the browser only gets one seat's view) |

## Change log after the freeze

- 2026-10-28: none.
- 2026-10-29: added the `model-notes` player (R23), before any held-out seed was run. Each model call is
  independent, so `model-history` can't remember its own plan; this tests whether its own notes help.
  Adds 90 held-out episodes (about $0.2).
- 2026-11-06: prompt frozen at the round 2 version.
- 2026-11-06: game changed to two decks (GAME-DESIGN.md §2.2) after the one-deck held-out run. New suite
  with held-out seeds 300-329; call limit 60 to 120, step limit 200 to 400.
- 2026-11-07: Revolution added (R10b) after the two-deck held-out run. The prompt gained the rule and two
  corrections from the review. New suite with held-out seeds 400-429; limits unchanged.

## Limitations

I tested one model, gemini-3.5-flash-lite on Vertex AI, at temperature 0. A stronger model, or one tuned for card games, could do very differently. I also didn't re-tune the prompt for two decks or for Revolution: I only added rule sentences to the prompt that was tuned on the one-deck game.

The opponents and the teammate are always my heuristic. A peasant's result depends a lot on that teammate, which is why even the random player did well as a peasant. The results say how each player does alongside this particular heuristic, not against people.

The rules are simplified. There's no bidding: the deal number picks the landlord, so the stakes start at 1 and the AI never chooses its role. 

Revolution is my own addition. The heuristic needed a new habit to use it, and with that habit a revolution happens in about 44% of heuristic-only deals. How often a revolution happens in the evaluation depends on that habit.

One overall limitation that the playtester noted that is hard to address (besides the
major glaring issue that once was the text-based game), is the fact that Doudizhu
is a difficult game with many rules that are hard to comprehend simply from reading a
manual. I have tried to address this with a handbook but players will still have a 
significant learning curve when playing this game.

