# Agent team log

I was Executive Producer and Creative Director. The agents proposed and built; I decided. None of them
could push, open a PR, merge, approve its own work, or spend cloud credit unless I said so in the session.

## The agents

| Agent | Role | Could | Couldn't | Evidence |
|---|---|---|---|---|
| Claude Code with `CLAUDE.md` | Implementation (programmer, producer) | Edit this folder and its workflow file, run tests, run live episodes when I asked, commit locally | Push, open a PR, edit other folders, review its own changes, write my sections | `CLAUDE.md`; commits on `lululizzy8/midterm`; `sessions/` |
| `ddz-rule-change` skill | Rules process | Walk any rule change through a README map row, a failing test, the engine and the reviewer | n/a | `.claude/skills/ddz-rule-change/SKILL.md`; R18 to R23, three regression fixes, and Revolution (R10b, called by name on Nov 7) |
| `ddz-eval-run` skill | QA and evaluation | Run episodes with the seed ranges, freeze versions before held-out seeds, label live vs fixture | n/a | `.claude/skills/ddz-eval-run/SKILL.md`; tuning rounds 1 to 3 and the three held-out runs (the revolution run called it by name on Nov 7) |
| `ddz-rules-reviewer` subagent | Independent review (QA) | Read and search only, on changes it didn't write | Edit, run code, approve | `.claude/agents/ddz-rules-reviewer.md`; `reviews/` runner (18 findings), notes (13), two-deck (14), revolution (12) |
| Design reviewers | Independent design review | Read the assignment, design doc, README, engine and tests | Edit, approve | `reviews/2026-10-28-design-review.md` (two reviewers on rev 1), `reviews/2026-10-28-design-review-rev2.md` |
| UI research and mockups (implementation agent) | Art direction | Search for free card art and table layouts; build a 4-style mockup | Publish anything I hadn't chosen | `web/`; README sources |
| Impeccable design skill | Product and UX direction | Interview me for `PRODUCT.md`; flag design problems after UI edits | Write my design doc or choose for me | `PRODUCT.md`; my design doc became `GAME-DESIGN.md` so the tool's `DESIGN.md` can't overwrite it |
| Browser testing (implementation agent in Chrome) | QA for the UI | Click through full deals, time the bot pauses, check phone width | Spend credits on Watch the AI | The Nov 7 bug fixes below |

The agent that plays the game (`gemini-3.5-flash-lite` on Vertex AI) isn't part of this team. It only sees
`observe` and `legal_actions` (plus the history or its own notes, depending on the variant) and has no
tools. See `EVALUATION.md` and `GAME-DESIGN.md` §4.

## What they recommended and what I decided

| Date | Recommendation (who) | My decision | Why [your words] |
|---|---|---|---|
| Oct 28 | Guandan is too big for one bounded episode (implementation agent) | Switched to Dou Dizhu; posted in Week 3 | [Basically the same game, easier to implement 2 bots than 3 and less worried about team dynamics] |
| Oct 28 | Drop the forced-landlord rule R17 and seat the agent relative to the seeded landlord (rules reviewer) | Accepted | [Landlord bidding is complicated and not that important to the game] |
| Oct 28 | Use Vertex `gemini-3.5-flash-lite` at temperature 0 | Accepted | [assignment requirement] |
| Oct 28 | Show whose turn it is, the play to beat and who made it | My request; built in `doudizhu/view.py` | [visual indicators] |
| Oct 29 | The model wasted its rocket as landlord in round 1: add strategy rules to the prompt | Tried in round 2: best result | [better prompting for performance reasons] |
| Nov 6 | My idea: two decks. The agent warned it was a second scope change with about 5× bigger prompts, a new suite and no time to tune | Two decks, three players | [two decks makes it more fun because you can play bigger / weirder chains of hands] |
| Nov 6 | Playtest ([`playtest.txt`](playtest.txt)): rules unclear to newcomers, text table hard to read, other turns too fast, about 200 choices with two decks. The agent suggested extending the web page instead of Pyxel, and replaying traces for Watch the AI | My 9-point card-table list; the web page; Watch the AI live through a local server (`web/serve.py`) | [playtest pointed out the text-based game was very hard to play so emphasized a UI through web browser] |
| Nov 7 | My playtest: after "See the table" there was no way to keep playing | Fixed with a "Show result" button | [bug after testing] |
| Nov 7 | My request: replace "Seat 0/1/2". The agent proposed names by role and side (You, Landlord, Your teammate, Left/Right peasant) | Accepted for the browser; `play.py`, prompts and traces keep seat numbers | [numbers are harder to read and less immersive] |
| Nov 7 | My request: a home screen without seat or deal pickers | Start game, Watch the baseline, Watch the AI | [abstract away seat picking and seed choosing] |
| Nov 7 | A bigger twist. The agent listed Revolution, wild cards, a secret partner, tribute and one-time powers, recommended Revolution, and measured how often each trigger size is held (6+: 54% of deals, 5+: 98%, 7+: 9%) | Revolution with a 6+ trigger (R10b) | [2 decks didn't feel like enough of an innovative change, revolution adds more complexity] |

## What I would change

I think there are smaller things that can be changed to enhance a players experience like UI design, flow design, gameplay decisions, etc. The big thing that I did change after getting feedback from playtesting notes was that the text-based game is almost entirely unplayable.
