# Product

<!-- impeccable:product-schema 1 -->

Note: the course game design document is `GAME-DESIGN.md`. `DESIGN.md` is free for the visual design
system (impeccable).

## Platform

web

## Users

Primary: course graders and classmates (peer playtesters, silent playtesters on the recording) judging
the COMS E6998 Dou Dizhu midterm. They need to understand the game quickly, play a deal, and watch the
AI agent play without manual moves. When needs conflict, this group wins.

Secondary: players new to Dou Dizhu (the peer playtest showed the rules are not obvious), and the
student, who acts as Executive Producer and Creative Director and records the 3–5 minute demo.

## Product Purpose

A two-deck, three-player Dou Dizhu (one landlord against two peasants) where a language-model agent plays
one seat through the same observation and legal-action interface as every other player. The web table
lets a person play a deal, read the rules, watch the heuristic baseline, and watch the live model.
Success: a grader can follow every move, see that hidden hands stay hidden, and connect what they watch to
the evaluation results.

## Positioning

The game code owns all state; the model only picks from the legal list. Watch the AI runs the same runner
as the evaluation (same limits, retries, labeled fallbacks and traces), so what is shown on screen is what
was measured.

## Operating Context

- Midterm only, due Nov 7, 2026. Run locally: `python web/serve.py`, opened in a desktop browser on the
  student's computer (a phone on the same Wi-Fi is a secondary option).
- Live model play needs Vertex settings in the server's terminal and spends cloud credits.
- Used in the demo recording and peer playtests.

## Capabilities and Constraints

- Home screen: play, rule handbook, watch the baseline, watch the AI.
- Play: other seats show only card backs and counts; the pile shows the current round; other players pause
  to "think"; no timer on the human turn; hand sorted ascending and reorderable by drag; Play only for a
  legal pick, with a plain-words reason otherwise.
- Engine and heuristic run in the browser through Pyodide; the page fetches the Python files from this
  folder. Live AI goes through the local server only; credentials never reach the page.
- Rules or observation changes follow the folder's rule-change process and independent review; UI work
  must not change them.
- Not decided: publishing beyond local use (out of scope for the midterm).

## Brand Commitments

- Cards are drawn in code (no image card decks); chosen by the student.
- Chinese titles and role marks (斗地主, 地 landlord, 农 peasant, 大王/小王 jokers) are part of the identity.

## Evidence on Hand

- Peer playtest notes: `playtest.txt` (anonymous).
- Evaluation results and traces: `EVALUATION.md`, `results/`, `traces/heldout-2deck/`.
- No user testimonials or usage data beyond these; do not invent any.

## Product Principles

1. Every move is legible: who is acting, what they played, and why a pick is not allowed.
2. Hidden information stays hidden; the page only shows one seat's hand.
3. What is shown matches what was evaluated; no fixture or replay passed off as live.
4. Teach as you play; the rules are one tap away.

## Accessibility & Inclusion

Desktop with a mouse first: graders and the demo recording use a computer browser. Phone and touch must
still work but are secondary, and their compromises (small card targets in a 42-card hand) are accepted.
Not keyboard-first (existing keyboard shortcuts may stay as a secondary path). Respect reduced motion.
