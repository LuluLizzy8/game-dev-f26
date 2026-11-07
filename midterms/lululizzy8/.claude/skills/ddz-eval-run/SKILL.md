---
name: ddz-eval-run
description: "Use when running Dou Dizhu evaluation episodes (baseline, model-history, model-obs) for midterms/lululizzy8 and updating EVALUATION.md. Enforces the frozen suite, seed hygiene, and honest live/fixture labeling."
---

# Run the Dou Dizhu evaluation suite

The suite is declared in `GAME-DESIGN.md` §6 and frozen by commit `6795857` (2026-10-28).
Changes to it go in the EVALUATION.md change log with a reason, never silently.

## Before running

1. Run `python -m unittest discover -s tests -v` from `midterms/lululizzy8/`. Stop if anything fails.
2. Check the seed range against its purpose:
   - 0–99: heuristic development only;
   - 100–104: prompt tuning;
   - 200–229: one-deck held out (used 2026-11-06); 300–329: two-deck held out. Allowed only after EVALUATION.md records the frozen commit hashes of
     `players/model.py`, `players/heuristic.py` and `agent-config.json`. If they are not recorded, stop.
3. For a live run, confirm LuluLizzy asked for it in this session, and that `COURSE_PROVIDER`,
   `COURSE_MODEL`, `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION` are set. Never fall back to fixtures.
   Estimate the call count first (about 20 non-forced calls per episode) and say it.

## Run

```
python runner.py --player <heuristic|random|model-history|model-obs> --situation <S1|S2|S3> \
  --seeds <a-b> [--trials N] [--opponents heuristic|random] [--fixture] --out traces/<name>
python report.py traces/<name> [more dirs] --price-in <USD/1M in> --price-out <USD/1M out> \
  --out results/<name>.md
```

## After running

1. Copy the report table into EVALUATION.md under a dated heading, with: player, situation, seeds,
   trials, live or fixture, model id as returned by the API, config hash, game commit, price source
   and date.
2. Count failures as they are: forfeits by reason, fallbacks, invalid replies. Do not drop episodes.
3. Never call a fixture result live, and never relabel a fallback move as a model move.
4. Update `SUBMISSION-CHECKLIST.md`.
