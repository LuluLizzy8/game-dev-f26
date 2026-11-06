# Evaluation

Status: held-out suite run 2026-11-06. Tables are filled with the `ddz-eval-run` skill.

## Declared suite (frozen before tuning)

Declared in `DESIGN.md` §6, frozen by commit `6795857` on 2026-10-28 and posted in my Week 3 thread.

- Situations: **S1** agent is landlord; **S2** peasant after the landlord; **S3** peasant before the landlord.
- Opponents: heuristic (all runs); random (held-out opponent condition, S1, seeds 200–209).
- Seeds: heuristic development 0–99; prompt tuning 100–104; **held out 200–229**.
- Players: `heuristic`, `random`, `model-history` (full public history), `model-obs` (no history),
  `model-notes` (history + its own notes; added 2026-10-29, see change log).
- Live runs: `model-history` 3 × 30 × 1 trial + 2nd trial on 200–209 (3 × 10); `model-obs` 3 × 30;
  `model-notes` 3 × 30 (added 2026-10-29); random-opponent condition 10 = **310 live episodes**.
  Baselines once per (situation, seed).

## Frozen versions before the held-out run

Frozen 2026-11-06, before any held-out seed was run.

| Item | Commit / hash |
|---|---|
| `players/model.py` (prompt) | `fa58165`: the round 2 prompt (`27e56eb`); rule 4 from round 3 removed because it made play worse |
| `players/heuristic.py` | `253e79f` (unchanged since it was written) |
| `agent-config.json` (config hash in every trace) | `cb6d27a`, config hash `13e067d04638` |
| Game commit | the commit recorded in each held-out trace header (`game_commit`) |

## Measurements on non-held-out seeds (2026-10-28, `python tools/measure.py`)

Seeds 0–104, all seats heuristic:
- opening legal-list size: median 67, max 215
- steps per deal: median 41, max 70 (step limit 200 is a backstop; bound 154)
- non-forced decisions per seat per deal: median 11, max 22 (call limit 60 covers 22 × 2 attempts)
- estimated input tokens per call (chars / 4): `model-history` median 587, max 1675; `model-obs` median 403, max 1653

Baseline strength on development seeds 0–99 (agent seat heuristic vs random, opponents heuristic), wins out
of 100: S1 58 vs 4; S2 42 vs 30; S3 42 vs 36.

## Known bounds of the runner (from the 2026-10-28 runner review)

- The wall clock is checked before each model call, so one call can overrun the limit by up to the
  30 s HTTP timeout, and an episode whose clock runs out after the agent's last decision ends normally.
- Thinking tokens vs the 256-token output cap: checked on the first live episode, ~30 output tokens per reply.
- `model-notes` output tokens against the same 256-token cap: checked 2026-11-06 on tuning seeds 100–101
  (S1, 10 calls, `traces/notes-check/`): median 68, max 76, so notes are not truncated.

## Results

### 2026-10-28: first live episode (tuning seed 100, S1), checkpoint evidence

Table: `results/tuning-2026-10-28.md`; traces: `traces/tuning/`. One live episode, so this shows the
pipeline working, not which player is better.

| Player | Mode | Result | Agent score | Calls | Invalid | Fallbacks | Forced | Latency median / max | Tokens in / out (est. cost) |
|---|---|---|---|---|---|---|---|---|---|
| heuristic | — | landlord wins | +2 | 0 | 0 | 0 | 2 | — | — |
| model-history | live, `gemini-3.5-flash-lite` (id returned by API) | landlord wins (rocket played, ×2) | +4 | 6 | 0 | 0 | 1 | 0.84 s / 2.28 s | 4,940 / 186 (≈ $0.0019) |

The report shows `pairs 0/1` for this run: the live episode was labeled game commit `ed6502c` and the
heuristic run `ed6502c-dirty`, because writing the first trace made the folder look modified. That is a
real bug, now a regression test (`test_regressions.FoundInFirstLiveRun20261028`, failing commit `5a002a0`,
fix `8379355`). The engine and players are identical between the two labels; the pair above is matched
by hand. Output tokens (~30 per reply) are far under the 256 cap, so thinking tokens did not truncate replies.

### 2026-10-28: tuning round 1 (seeds 100–104, all situations, prompt as of `eeb053f`)

Full table: `results/tuning-r1-2026-10-28.md`; traces: `traces/tuning-r1/`. 5 deals per cell, so these
are tuning observations, not results. Live cost ≈ $0.075 for 30 episodes.

| Player | S1 wins / mean | S2 wins / mean | S3 wins / mean | Invalid | Fallbacks | Latency median / p95 |
|---|---|---|---|---|---|---|
| heuristic | 4/5, +1.6 | 1/5, −0.8 | 1/5, −0.8 | — | — | — |
| random | 1/5, −1.6 | 1/5, −1.2 | 1/5, −1.2 | — | — | — |
| model-history | 1/5, −3.2 | 2/5, −0.6 | 1/5, −0.8 | 0 | 0 | ~0.8 s / 1.4–2.3 s |
| model-obs | 1/5, −1.6 | 1/5, −0.6 | 1/5, −0.8 | 0 | 0 | ~0.8 s / 4–24 s |

Observations:
- As landlord (S1) the model is far below the heuristic (paired diff −4.8 history, −3.2 no history).
  Example, seed 104: it led its rocket while it already held the lead (wasting it), then led a single 2
  into a bomb; the heuristic saved the jokers and won.
- Same seed, same prompt, temperature 0 is not deterministic: seed 100 S1 won +4 in the first run and
  lost −4 here.
- No invalid replies or fallbacks in 30 episodes; one slow call (p95 24 s in model-obs S1) stayed under
  the 30 s timeout.

### 2026-10-29: tuning round 2 (same seeds, prompt `27e56eb`: three strategy rules added)

Change: the system prompt gained a "Strategy" section: (1) never play a bomb or rocket when you already
have the lead; (2) don't lead 2s or jokers as singles early; (3) check the rest of the hand can still be
played out. Full table: `results/tuning-r2-2026-10-29.md`; traces: `traces/tuning-r2/`. Live cost ≈ $0.106.

| Player | S1 wins / mean | S2 wins / mean | S3 wins / mean | Invalid | Fallbacks | Latency median / p95 |
|---|---|---|---|---|---|---|
| heuristic | 4/5, +1.6 | 1/5, −0.8 | 1/5, −0.8 | — | — | — |
| model-history | 4/5, +2.4 (r1: 1/5, −3.2) | 3/5, +0.2 (r1: 2/5) | 2/5, −0.4 (r1: 1/5) | 0 | 0 | ~0.8 s / 1.3–1.9 s |
| model-obs | 2/5, −0.8 (r1: 1/5, −1.6) | 2/5, −0.2 (r1: 1/5) | 1/5, −1.0 (r1: 1/5) | 0 | 0 | ~0.8 s / ~1 s |

Observations:
- Bomb/rocket played while already holding the lead (rough count over model leads after two passes):
  1 of 66 in round 1, 0 of 68 in round 2.
- `model-history` moved from well below the heuristic to level with or above it on these 5 deals per
  situation; `model-obs` improved less. With 5 deals and the run-to-run variation seen in round 1, this
  may be partly noise; the held-out suite is what tests it.
- Calls per episode rose (S1: 44 → 56 total over 5 deals), still far under the 60-per-episode limit.

### 2026-10-29: tuning round 3 (same seeds, prompt `2257ca7`: rule 4 added)

Change: rule 4, "When you lead, play a combination you think you can win back ... Among those, start with
your lowest." Full table: `results/tuning-r3-2026-10-29.md`; traces: `traces/tuning-r3/`. Live cost ≈ $0.107.

| Player | S1 wins / mean | S2 wins / mean | S3 wins / mean | Invalid | Fallbacks |
|---|---|---|---|---|---|
| heuristic | 4/5, +1.6 | 1/5, −0.8 | 1/5, −0.8 | — | — |
| model-history | 2/5, −0.4 (r2: 4/5, +2.4) | 2/5, −0.2 (r2: 3/5) | 1/5, −1.0 (r2: 2/5) | 0 | 0 |
| model-obs | 1/5, −1.2 (r2: 2/5) | 1/5, −0.8 (r2: 2/5) | 1/5, −0.8 (r2: 1/5) | 0 | 0 |

Observation: worse than round 2 everywhere. Seed 104 S1 shows why: in round 2 the model opened with its
15-card plane; in round 3 it led a single 3 ("lead a low single card"), then played singles one at a time,
broke up its hand and lost. "Start with your lowest" seems to override "lead long combinations first".

### Held-out results

### 2026-11-06: held-out suite (seeds 200–229), frozen versions

Full table (every field, every condition): `results/heldout-2026-11-06.md`; traces: `traces/heldout/`
(510 episodes: 310 live, 200 baseline). Live model `gemini-3.5-flash-lite` (id as returned by the API),
Vertex AI `global`, config hash `13e067d04638`, game commit `eed053e` in every trace header.
Price: the dated rate below. Live cost ≈ **$1.27** (estimate was $0.65; history prompts grew longer than
measured on development seeds).

**Main comparison, trial 1 only, so every player has the same 30 deals per situation, opponents heuristic.**
Wins out of 30 and mean agent score.

| Player | S1 (landlord) | S2 (peasant after landlord) | S3 (peasant before landlord) |
|---|---|---|---|
| heuristic (baseline) | **17/30, +0.27** | **13/30, −0.13** | 13/30, −0.13 |
| random | 2/30, −2.00 | 9/30, −0.40 | 10/30, −0.47 |
| model-history | 8/30, −1.20 | 8/30, −0.53 | 12/30, −0.30 |
| model-obs (no history) | 3/30, −1.93 | 11/30, −0.30 | **14/30, −0.07** |
| model-notes (history + own notes) | 10/30, −0.53 | 12/30, −0.30 | 11/30, −0.50 |

Failures over all 310 live episodes: 0 forfeits (call limit, timeout, invalid limit), 0 step-limit
endings, 0 fallback moves, 3 invalid replies (each fixed on the retry), 1 API error (retried).
Latency median 0.8–1.0 s, p95 ≤ 2.3 s. Tokens and cost per condition are in the full table.

Repeated trials: `model-history` ran a second trial on seeds 200–209 in every situation. The two trials
gave the same win/loss on 7/10 (S1), 5/10 (S2) and 9/10 (S3) deals, so temperature 0 is not deterministic
and single deals vary a lot.

Random opponents (S1, seeds 200–209): heuristic 10/10 (+2.2), `model-history` 7/10 (+0.4), random 3/10.

Reading (10 or 30 deals per cell; no statistical certainty implied):
- The heuristic baseline is the strongest player as landlord (S1): 17/30 vs 8–10/30 for the model
  players. Paired on the same deals, `model-history` scores −1.55 per deal below the heuristic over
  all 40 S1 episodes. The round 2 prompt's gains on the 5 tuning deals did not hold on held-out deals.
- As a peasant (S2, S3) all players are close (8–14 wins out of 30), with differences inside the
  trial-to-trial variation above. A peasant's result also depends on the heuristic teammate.
- History vs observation only: history helped as landlord (8 vs 3 wins, −1.20 vs −1.93) and not as a
  peasant. Own notes helped most as landlord (10/30, −0.53), but notes also change the system prompt and
  reply format (DESIGN §4.3), so this is not a one-variable comparison, and `model-notes` was never tuned.
- The experiment separates the players: random is clearly below the heuristic in S1 (2 vs 17 wins), and
  the model is between them.

**Price used:** Gemini 3.5 Flash-Lite on Vertex AI, location `global`, standard (not batch) rate:
**$0.30 per 1M input tokens, $2.50 per 1M output tokens** (text output includes reasoning tokens).
Source: https://cloud.google.com/vertex-ai/generative-ai/pricing, checked 2026-10-28. Cached input
($0.03) is not used. Cost = tokens × price, via `python report.py <dirs> --price-in 0.30 --price-out 2.50`.
These are estimates from API-reported tokens, not billed amounts.

First live episode: 4,940 in + 186 out tokens ≈ **$0.0019**.
Budget estimate for the rest of the suite at ~5k in / ~200 out tokens per episode: tuning (~30 episodes)
≈ $0.06; held-out (310 episodes incl. `model-notes`) ≈ $0.65.

## Traces

`traces/heldout/` (held-out suite), `traces/tuning*/` (tuning rounds), `traces/notes-check/`. One JSON object per line: header, steps (with every model attempt, raw reply, latency, tokens, source `model`/`forced`/`fallback`), result.

## CI evidence

TODO: link to the green Actions run for the submitted commit. Locally:
`python -m unittest discover -s tests -v` → 68 tests OK on 2026-10-29.

| CI check kind (rubric 3c) | Tests |
|---|---|
| Rule invariants | `test_combos.Invariants`; `test_game.Turns.test_full_games_end_and_conserve_cards` |
| Legal / illegal actions | `test_combos.Lead`, `Rejected`, `Beats`; `test_game.Turns`; `test_runner.Fallback` |
| Terminal outcome | `test_game.Scoring`; `test_runner.Baselines` |
| Observed regression | `test_regressions`: two bugs found by review (failing `7168315`, fixed `72bfc27`); one found in the first live run (failing `5a002a0`, fixed `8379355`) |
| Episode limits | `test_game.Limits`; `test_runner.Limits` (call, invalid, timeout, step, forfeit scoring) |
| Information boundary | `test_game.Information`; `test_view`; `test_runner.Prompt` |

## Change log after the freeze

- 2026-10-28: none.
- 2026-11-06: prompt frozen at the round 2 version (see the frozen-versions table).
- 2026-10-29: added the `model-notes` player (R23) at my request, before any held-out seed was run.
  Reason: every model call is independent, so `model-history` cannot remember its own plan; this tests
  whether its own notes help beyond the public history. Adds 90 held-out episodes (≈ $0.2).

## Limitations **[student voice — TODO]**
