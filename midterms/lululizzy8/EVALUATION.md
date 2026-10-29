# Evaluation

Status: in progress. One live tuning episode so far. Tables are filled with the `ddz-eval-run` skill.

## Declared suite (frozen before tuning)

Declared in `DESIGN.md` §6, frozen by commit `6795857` on 2026-10-28 and posted in my Week 3 thread.

- Situations: **S1** agent is landlord; **S2** peasant after the landlord; **S3** peasant before the landlord.
- Opponents: heuristic (all runs); random (held-out opponent condition, S1, seeds 200–209).
- Seeds: heuristic development 0–99; prompt tuning 100–104; **held out 200–229**.
- Players: `heuristic`, `random`, `model-history` (full public history), `model-obs` (no history).
- Live runs: `model-history` 3 × 30 × 1 trial + 2nd trial on 200–209 (3 × 10); `model-obs` 3 × 30;
  random-opponent condition 10. Baselines once per (situation, seed).

## Frozen versions before the held-out run

| Item | Commit / hash |
|---|---|
| `players/model.py` (prompt) | TODO |
| `players/heuristic.py` | TODO |
| `agent-config.json` (config hash in every trace) | TODO |
| Game commit | TODO |

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

### Held-out results

TODO: after the prompt, heuristic and config are frozen (table above).

**Price used:** Gemini 3.5 Flash-Lite on Vertex AI, location `global`, standard (not batch) rate:
**$0.30 per 1M input tokens, $2.50 per 1M output tokens** (text output includes reasoning tokens).
Source: https://cloud.google.com/vertex-ai/generative-ai/pricing, checked 2026-10-28. Cached input
($0.03) is not used. Cost = tokens × price, via `python report.py <dirs> --price-in 0.30 --price-out 2.50`.
These are estimates from API-reported tokens, not billed amounts.

First live episode: 4,940 in + 186 out tokens ≈ **$0.0019**.
Budget estimate for the rest of the suite at ~5k in / ~200 out tokens per episode: tuning (~30 episodes)
≈ $0.06; held-out (220 episodes) ≈ $0.45.

## Traces

TODO: `traces/heldout/` (committed) and `traces/tuning/`.

## CI evidence

TODO: link to the green Actions run for the submitted commit. Locally:
`python -m unittest discover -s tests -v` → 56 tests OK on 2026-10-28.

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

## Limitations **[student voice — TODO]**
