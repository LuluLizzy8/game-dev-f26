# Evaluation

Status: skeleton. No live episodes yet. Tables are filled with the `ddz-eval-run` skill.

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

## Results

TODO: comparison table from `report.py` (tuning seeds, then held-out), with model id as returned by the API,
config hash, game commit, latency, tokens, and cost.

**Price used:** TODO (source URL and date).

## Traces

TODO: `traces/heldout/` (committed) and `traces/tuning/`.

## CI evidence

TODO: link to the green Actions run for the submitted commit. Locally:
`python -m unittest discover -s tests -v` → 47 tests OK on 2026-10-28.

## Change log after the freeze

- 2026-10-28: none.

## Limitations **[student voice — TODO]**
