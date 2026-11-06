# Agent team log

> **DRAFT written by the implementation agent from the repo history. Rewrite every sentence in your own
> words before submitting (rubric 5b treats an agent-voiced log as missing).** Facts and evidence links
> are checked; the "why" in brackets is for you to fill in or correct.

I (LuluLizzy) acted as Executive Producer and Creative Director: agents proposed and built, I decided.
No agent could push, open a PR, merge, approve its own work, or spend cloud credit without my go-ahead
in the session.

## The agents

| Agent | Role | Could see / do | Could not | Evidence |
|---|---|---|---|---|
| Claude Code with `CLAUDE.md` | Implementation (programmer, producer) | Read and edit this folder and its workflow file; run tests; run live episodes when I said so; commit locally | Push, open a PR, edit other folders, review its own changes, write my student-voice sections | `CLAUDE.md`; commits on `lululizzy8/midterm`; `sessions/2026-11-game-creation.txt` |
| `ddz-rule-change` skill | Reusable skill (rules process) | Steps for any rule change: README map row, failing test first, engine, reviewer | — | `.claude/skills/ddz-rule-change/SKILL.md`; used for R18–R23 and the three regression fixes |
| `ddz-eval-run` skill | Reusable skill (QA / evaluation) | Steps for running episodes: seed ranges, freeze before held-out seeds, live vs fixture labels | — | `.claude/skills/ddz-eval-run/SKILL.md`; tuning rounds 1–3 and the held-out run |
| `ddz-rules-reviewer` subagent | Independent review (QA) | Read, Grep, Glob only; reviewed changes it did not write; never asked to approve | Edit, run code, approve | `.claude/agents/ddz-rules-reviewer.md`; `reviews/2026-10-28-runner-review.md` (18 findings), `reviews/2026-10-29-notes-review.md` (13), `reviews/2026-11-06-two-deck-review.md` (14) |
| Design reviewers (rules reviewer + strict-TA rubric reviewer, then a fresh re-reviewer) | Independent design review (design, production) | Read-only: Assignment.md, DESIGN.md, README, engine, tests | Edit, approve | `reviews/2026-10-28-design-review.md` (two reviewers, rev 1), `reviews/2026-10-28-design-review-rev2.md` |
| UI research + mockup (implementation agent, web search) | Art direction | Searched for CC0 card art and Dou Dizhu table layouts; built a 4-style mockup | Publish anything without my choice | Mockup artifact (private); `web/`; README sources |

The game-playing agent (`gemini-3.5-flash-lite` on Vertex AI) is not part of the building team. It sees
only `observe` + `legal_actions` (plus history or its own notes, by variant) and has no tools; see
`EVALUATION.md` and `DESIGN.md` §4.

## What they recommended and what I decided

| Date | Recommendation (who) | My decision | Why [your words] |
|---|---|---|---|
| Oct 28 | Guandan is too big for one bounded episode (implementation agent) | Switched to Dou Dizhu; posted in Week 3 | [ ] |
| Oct 28 | 16 rules findings + 16 rubric findings on design rev 1 (two reviewers) | Accepted all; DESIGN rev 2 | [ ] |
| Oct 28 | Drop the forced-landlord rule R17; seat the agent relative to the seeded landlord (rules reviewer) | Accepted | [ ] |
| Oct 28 | Auto-play single-option turns as `forced` so passes don't use model calls (rules reviewer) | Accepted (R20) | [ ] |
| Oct 28 | Fix `observe(-1)` leaking seat 2's hand, and non-string actions crashing, failing tests first (rev 2 reviewer) | Accepted; these became my CI regressions | [ ] |
| Oct 28 | API error text could leak the project ID into traces (runner review) | Accepted: only error type + status logged | [ ] |
| Oct 28 | Use Vertex `gemini-3.5-flash-lite`, temperature 0 | Accepted | [ ] |
| Oct 28 | Show the player whose turn it is, the play to beat and who made it | My request; built in `doudizhu/view.py` | [ ] |
| Oct 29 | After round 1 the model wasted its rocket as landlord: add strategy rules to the prompt | Tried it (round 2): best result | [ ] |
| Oct 29 | My idea: "lead what you can win back, lowest first" (round 3) | Tried it; it made play worse | [ ] |
| Oct 29 | Use DouZero as the opponent/baseline? | Asked; kept my own heuristic baseline | [ ] |
| Oct 29 | My idea: a third player that keeps its own short notes between turns | Added `model-notes` (R23); reviewer found 6 should-fix issues, all fixed | [ ] |
| Oct 29 | Card art: draw cards in code rather than use CC0 decks (implementation agent) | Chose drawn cards; browser version in `web/` | [ ] |
| Nov 6 | Freeze the round 2 prompt for the held-out run (implementation agent) | Accepted | [ ] |
| Nov 6 | My idea: change to two decks. Agent warned: second scope change, ~5× prompts, new suite, no time to tune | Chose two decks, three players | [ ] |
| Nov 6 | Two-deck review: 1 must-fix, 7 should-fix (stale evaluation, call limit margin, prompt size, missing tests) | Applied all; call limit 120; new held-out seeds 300–329 | [ ] |
| Nov 6 | Peer playtest findings ([`playtest.txt`](playtest.txt)): rules unclear to newcomers, text table hard to read, other turns too fast, ~200 choices with two decks | [ ] | [ ] |

## What I would change

[Your words: e.g. what the review process caught that you would have missed, what you would delegate
differently, where an agent was wrong.]
