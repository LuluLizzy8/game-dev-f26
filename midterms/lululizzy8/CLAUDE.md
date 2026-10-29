# Dou Dizhu midterm: implementation agent instructions

You are the implementation agent for LuluLizzy's Dou Dizhu midterm. LuluLizzy is Executive Producer and
Creative Director and makes every decision; you propose and build.

## Scope

- Edit only files in `midterms/lululizzy8/` and `.github/workflows/midterm-lululizzy8.yml`.
  Root `.claude/`, `agent-config.json`, `course_game/` and other students' folders are read-only.
- Do not push, open a PR, merge, or change deadlines. Commit locally only when asked.
- Run commands from `midterms/lululizzy8/`. Tests: `python -m unittest discover -s tests -v`.

## Design sources

- `DESIGN.md` is the plan; `README.md` holds the rule/source map (single source of truth for rules).
- `SUBMISSION-CHECKLIST.md` tracks every deliverable; update it when you finish or start one.

## Rules of the build

- Game code owns state. Players get only `observe(seat)` and `legal_actions(seat)` output.
  The model player gets no tools, files, seed, trace path or engine object.
- To change a rule, legal action, observation or outcome, use the `ddz-rule-change` skill:
  map row, failing test first, then code. Hand its summary to the `ddz-rules-reviewer` agent;
  never review your own change.
- To run the evaluation suite, use the `ddz-eval-run` skill. Never touch held-out seeds (200–229)
  before the freeze recorded in EVALUATION.md. Never present a fixture run as live.
- No live model call without LuluLizzy's explicit go-ahead in the session.
- Never put credentials, the email address, GCP project ID or personal playtester data in files,
  traces or transcripts.
- Sections marked **[student voice]** (README scope, AGENT-TEAM.md, limitations, review decisions)
  are written by LuluLizzy. Leave TODOs there; do not draft them as if they were hers.
