---
name: ddz-rule-change
description: "Use when adding, changing or removing a Dou Dizhu rule, legal action, observation, outcome or runner rule in midterms/lululizzy8. Ties each change to a README map row, a test written first, and a summary for ddz-rules-reviewer."
---

<!-- Adapted from the course repository's .claude/skills/rule-change/SKILL.md
     (columbia-university-ai-games/game-dev-f26 @ 66f051b) for this project's files and the `design` label. -->

# Change a Dou Dizhu rule with evidence

The engine (`doudizhu/engine.py`) and the runner (`runner.py`) own state. A rule change touches
three things together: the code, its test and the rule/source map in `README.md`.

## Steps

1. Find the rule in the `README.md` map. Quote its row and label. If it is missing, add a row first
   with the strongest label you have: `code`, `manual`, `observed`, `assumed`, or `design` for a
   rule LuluLizzy chose (point to `GAME-DESIGN.md` and give the reason). Never promote a label without
   new evidence.
2. Write the test first (`tests/`). Run it and confirm it fails for the reason you expect. If the
   change is a regression for a real bug, put it in `tests/test_regressions.py` with the date and
   where the bug was found, and commit it failing before the fix.
3. Change the code. Keep the change to the one rule.
4. Check the player boundary:
   - `observe(seat)` returns only what that seat could know;
   - `legal_actions(seat)` depends only on that seat's hand and public state;
   - a refused action changes nothing;
   - the model prompt (`players/model.py`) is unchanged when hidden hands are reshuffled.
   Add or adjust a test if the change moves any of these.
5. Update the map row: rule, label, evidence, code / test locator.
6. Run `python -m unittest discover -s tests -v` from `midterms/lululizzy8/`. All pass, or stop
   and report.
7. Write the reviewer summary, in this order:
   - the rule as it now reads, with label and evidence;
   - the test that proves it, and that it failed before the change;
   - any boundary effect from step 4, or "none";
   - anything assumed.

## Do not

- make a rule and its test agree on something no evidence or design decision supports;
- give a player file access, the engine object or the map;
- mark your own work reviewed. `ddz-rules-reviewer` does that, in a session that did not write it.
