# Design review, 2026-10-28

Target: `DESIGN.md` draft of 2026-10-28 (before runner, baseline and model player exist).
Two independent read-only reviewers, run from a Claude Code session; neither wrote the design,
neither was asked to approve. Findings are recorded as returned (lightly condensed); decisions are mine
and go in the last section.

## Reviewer 1: rules-reviewer (`.claude/agents/rules-reviewer.md`, tools: Read, Grep, Glob)

Scope: rules vs engine/map, information boundary, proposed R17–R19, rule correctness vs Pagat, engine bugs.
No medium/high engine bugs found.

| # | Sev | Where | Finding | Suggested fix |
|---|---|---|---|---|
| 1 | med | DESIGN §3/§5, engine.py:105 | `reset()` returns the landlord's observation (full hand); if the runner hands it to a peasant agent, it leaks 20 cards. | Runner ignores `reset`'s return, always calls `observe(agent_seat)`; test that S2's first prompt lacks the landlord hand. |
| 2 | med | DESIGN §2 vs §2.1/§5 | §2 says runner limits score 0; R18/§5 say agent side loses. | Only `step_limit` scores 0. |
| 3 | med | R18 | Forfeit outcome unspecified: score vector, multiplier, `winner`, heuristic teammate, engine still "ongoing". Metrics would fold forfeits into losses. | Give exact outcome dict; count forfeits separately. |
| 4 | med | R17 | Unneeded: S1–S3 can be chosen relative to the seeded landlord. As written it's ambiguous (does the kitty move?) and conflicts with R4. | Drop R17; pick seats relative to landlord in the runner. |
| 5 | med | §5 call limit | Forced passes (`["pass"]` only) would use model calls; a seat can face ~54 turns, so `call_limit=60` can trip in normal deals. | Auto-play single-option turns as `source: forced`; recompute budget. |
| 6 | med | §3, §7 | "Copies" don't stop an in-process Python player reaching the engine; the real boundary for the model is the prompt. "Assert on prompt text" can't detect a leak (card labels repeat). | Reword; test prompt is byte-identical after reshuffling other hands; assert seed/trace path absent. |
| 7 | low | §5 | Fallback inputs unstated. | Fallback heuristic gets only the agent seat's observation + legal list. |
| 8 | low | engine.py:179 | `step_limit` outcome lacks `spring`/`multiplier` keys. | Add defaults or document. |
| 9 | low | engine.py:107 | `observe(-1)` returns seat 2's hand. | Validate seat. |
| 10 | low | engine.py:143 | Non-string action raises AttributeError. | Refuse non-strings in `step` or runner. |
| 11 | low | R8 | Both jokers allowed as kickers (`3333 BJ RJ`); four+2 with a pair rejected. Rule sets differ. | Note difference from Pagat in R8 evidence after checking page. |
| 12 | low | R14 | "accepted moves" unclear; passes count. 200 unreachable naturally (~162). | Say "accepted actions, including passes"; note it's a backstop. |
| 13 | low | §3, §6 | Legal-list figures have no committed script; ~2k tokens/call likely low for `model-history` late in a deal. | Commit measurement; measure prompt sizes on tuning seeds. |
| 14 | low | tests | Missing: landlord win without spring, rocket doubling, two bombs ×4. | Add as regression guards. |
| 15 | low | §0 | Cross-ref slips (R17+ are in §2.1; R1a/R13a omitted). | Fix text. |
| 16 | low | R19 | Sound, no leak; needs map row and test. | Add. |

Checked, no issue: deal sizes, kitty, landlord leads; lead return after two passes; leader can't pass;
card order/case; 14 combination kinds and sequence bounds; kicker distinctness; `beats`; multiplier and
zero-sum scoring; spring and anti-spring; refused actions change nothing; label uniqueness; `observe` and
`legal_actions` reveal only own hand + public info; seat order for S2/S3; suite arithmetic;
history-vs-observation comparison meets the brief; fallback labeling.
Not checked: tests not run; Pagat page not fetched.

## Reviewer 2: rubric / experiment reviewer (Plan agent, read-only instructions, graded as a strict TA)

| # | Check | Finding | Suggested fix |
|---|---|---|---|
| 1 | 5a/3c/3a | Nothing committed: suite "frozen" date unverifiable, CI never ran, `__pycache__/` would be committed. | Folder `.gitignore`; commit + push; draft PR so CI runs. |
| 2 | 4b | 10 paired seeds per situation likely too few: most pairs agree, few discordant deals. Budget allows more (cents–$1; ~2 h wall time). | 30+ held-out seeds per situation; report paired score difference and discordant-pair count. |
| 3 | 4b/5a | In S2/S3 the baseline's teammate is a copy of itself (shared conventions); the model's isn't. | Disclose; describe teammate conventions in the prompt, or add a random-teammate condition. |
| 4 | 5a/4a | `model-obs` marked "cut first", but the brief requires the comparison. | Run it on the same held-out seeds; state history bound. |
| 5 | 3d | Root skill/agent point at starter files (`world.py`, `docs/rule-source-map.md`); no `design` label; local sessions have no links; `agents/` prompts not invocable. | Adapted copies in `midterms/lululizzy8/.claude/`; commit exported transcripts under `sessions/`; invoke `eval-run` twice; drop or move role agents. |
| 6 | 3c | Regression test still TODO; must be real. | Commit failing test first when a real bug appears; keep provider SDK out of CI tests. |
| 7 | 3b | (a) `step_limit` 200 unreachable (~156 max); (b) timeout must be the HTTP client's; (c) SDK auto-retries must be off or counted; (d) forced moves unspecified; (e) runner reasons shouldn't be written into the engine. | Fix each; `source: forced`; runner-level result for limits. |
| 8 | 5a | Fallbacks use the heuristic, so a failing model drifts toward baseline play. | Report over all episodes and fallback-free episodes; separate columns for limit breaches; say whether API errors count toward `invalid_limit`. |
| 9 | 5a | Heuristic written after freeze could be tuned on held-out deals. | Develop heuristic on seeds 0–99; record commit hashes before held-out run. |
| 10 | 4b | Paired design valid but not bridge-style duplicate; card luck still dominates. R17 unnecessary. | More seeds (item 2); drop R17. |
| 11 | 1a | Pagat locators unverified; no rows for runner rules. | Verify headings/quote phrases; add rows for limits, forced moves, fallback, variants. |
| 12 | 1c | "TODO confirm licenses" = Weak. | State Pagat is copyrighted, only rule facts used; link RLCard/DouZero licence files or drop them. |
| 13 | 3a | Bash-only env syntax; Vertex auth undocumented; no no-credentials command. | Document auth + PowerShell; add `--fixture` run; pin `requirements.txt`; cap thinking tokens. |
| 14 | — | Hand-in boundary: no violation as planned. | Keep root files untouched; no caches/credentials in diff. |
| 15 | — | Schedule risk high; Oct 26 checkpoint items missing; `play.py` needed by ~Nov 1 for peer playtest. | Proposed day-by-day order; cut self-play, vocabulary ablation, role agents first. |
| 16 | 5b | Student-voice pieces all TODO. | Write them; use peer notes. |

Per-check grade of the plan as written: Met — 2a (if `play.py` ships), 2b, 2c, 4a, 5c; Met with fixes — 3b;
Weak — 1a, 1c, 3c, 3d, 4b; Weak risk — 3a, 5a; Weak → Met — 1b; Missing now — 5b.
Not checked: tests/workflow not run; Pagat and licence pages not opened; token/cost figures estimated.

## Overlap between reviewers

Both independently flagged: R17 unnecessary; forced passes burning the call budget; forfeit outcomes
needing their own reporting.

## My decisions **[student voice — TODO]**

For each finding: accept / reject / defer, and why.

Record: on 2026-10-28 I accepted all findings from both reviewers; they are applied in DESIGN.md rev 2.
Reasons per finding: TODO (my words).
