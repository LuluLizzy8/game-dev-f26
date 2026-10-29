# Design re-review (rev 2), 2026-10-28

Target: `DESIGN.md` rev 2. One fresh independent read-only reviewer (Plan agent, strict-TA instructions),
not the session that wrote the doc, not asked to approve. It read Assignment.md, DESIGN.md, README.md,
engine.py, tests, .gitignore, the rev 1 review, the folder workflow and git state, and ran the 21 existing
tests (pass). No network. Findings condensed as returned; decisions are mine (last section).

## (A) Status of rev 1 findings

Fixed: rules 1–10, 12, 14–16; rubric 2–5, 7–10, 12–14.
Partly: rules 11 (Pagat check pending), 13 (`tools/measure.py` not written; re-runs on held-out seeds);
rubric 1 (.gitignore done, freeze commit not made), 6 (regression candidate not named), 11 (locators),
15 (Oct 29–30 overloaded, peer appointment not booked).
Not fixed: rubric 16 (student-voice pieces still TODO).

## (B) Projected grades if the plan is carried out

| Check | Grade | Note |
|---|---|---|
| 1a | Met | after Pagat locators + README rows R18–R22 (Weak today) |
| 1b | Met | Week 3 post + README scope in my voice |
| 1c | **Weak** | §9 says "all code written here", but adapted course skill/reviewer and starter-style provider code are not; google-genai uncredited |
| 2a, 2b, 2c | Met | |
| 3a | Met (risk) | add fresh-clone dry run; PowerShell 5.1 `>` writes UTF-16, use `--out` |
| 3b | Met | |
| 3c | **Weak** | regression kind not yet certain |
| 3d | Met (risk) | folder skill/agent names collide with root copies |
| 4a, 4b | Met | |
| 5a | Met (risk) | freeze commit not made; local date is self-set; price date TODO |
| 5b | Met if done | all scheduled Nov 6–7 |
| 5c | Met | |

Projected: Research 3, Design/AI 4, Production 3, Creativity 4, Reflection 4 = **18/20**; 20 with C3 + C4.
In today's state Production and Reflection would score 1.

## (C) New problems in rev 2

1. (5a) Freeze not committed; local commit date is unverifiable. → commit today; post suite + hash in Week 3 thread; never rebase/squash.
2. (5a/4b) `tools/measure.py` re-run on held-out seeds before the freeze peeks at them. → measure on 0–104 only.
3. (3c) Real regressions already exist: `observe(-1)` returns seat 2's hand; non-string action crashes. → failing-first tests in `tests/test_regressions.py`, citing rev 1 rules findings 9–10.
4. (1c) §9 claim false. → credit course skill/reviewer (path + commit), starter provider pattern, google-genai (Apache-2.0).
5. (3d) Name collision with root `rule-change` / `rules-reviewer`. → rename `ddz-rule-change`, `ddz-rules-reviewer`.
6. (1a) Step bound: plays ≤ 20+16+16 = 52, passes ≤ 2 between plays → steps ≤ 154, not ≈162.
7. (1a) README conflicts: R4 evidence says "fixed landlord seat"; "standard library only"; R14 "moves"; R8 lacks consequences.
8. (5a) No temperature/sampling settings recorded. → fix in agent-config.json, record in trace header.
9. (3b/5a) 10-min wall clock binds before 60 × 30 s; 4 s latency is from a 246-token check. → measure p95 on tuning seeds; disclose slowness counts as forfeit.
10. Push timing contradicts "local until done"; CI must be green on the **last** push. → state Nov 6 push as deliberate exception.
11. Oct 29–30 overloaded; peer appointment and notes-given not scheduled. → book now; rebalance.
12. `sessions/` transcripts will contain email and GCP project ID. → clean before committing.

## (D) Omissions

Recording host and viewability; PR description contents; per-finding decision reasons in §13; link to
green Actions run in EVALUATION.md; fresh-clone check; dependency/course-material credits; prompt hash
per trace step; re-record fixtures after the freeze.

Not checked: Pagat and licence pages, real token/latency figures, nested `.claude/` loading behavior.

## My decisions **[student voice — TODO]**
