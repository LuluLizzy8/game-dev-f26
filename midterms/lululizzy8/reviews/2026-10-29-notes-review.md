# Review of R23 (`model-notes`), 2026-10-29

Reviewer: `ddz-rules-reviewer` instructions, read-only subagent (Read, Grep, Glob), did not write the
change, not asked to approve. Target: commit `5729dd6`. Ran nothing.

Answers to the questions asked: no path for hidden information into a note; no path for notes into other
variants; notes from an invalid reply are not stored (but untested); not a one-variable comparison;
suite change logged, totals not updated.

| # | Sev | Finding | Applied |
|---|---|---|---|
| 1 | should fix | "changes exactly one thing" is false: notes also change the system prompt, the response schema and the output task. | yes: DESIGN lists all differences as confounds |
| 2 | should fix | 300-char note + reason under `max_output_tokens` 256 may truncate replies (→ invalid). | measure on tuning seeds before held-out (EVALUATION to-check) |
| 3 | should fix | No test that an invalid reply's notes are not stored. | yes: test added |
| 4 | should fix | agent-config `prompts_or_system_instructions` omits the notes addendum and schema. | yes |
| 5 | should fix | Suite totals and budget omit the 90 `model-notes` episodes; suite change not posted to Week 3; `model-notes` never tuned. | totals fixed; untuned disclosed; Week 3 post 👤 |
| 6 | should fix | Accepted reply without `notes` keeps a stale note. | yes: rule is "the note shown is the last accepted reply's note, or none"; tested |
| 7 | note | runner-path test only covers the "(none)" path. | covered by `test_note_is_carried_to_the_next_prompt` |
| 8 | note | `test_other_variants_never_see_notes` would pass before the change. | yes: declared as a regression guard |
| 9 | note | system-prompt test weak; `schema()` and non-string notes untested. | yes |
| 10 | note | Notes keep newlines and can imitate prompt sections. | yes: whitespace collapsed to single spaces |
| 11 | note | prompt hash omits schema; stored note not in trace. | yes: step records `notes_in` |
| 12 | note | `notes` written after `action`, so it plans later moves only. | yes: stated in DESIGN §4.3 |
| 13 | note | stale doc lines (DESIGN §4.3 "only the history field", broken list; EVALUATION test count). | yes |

## My decisions **[student voice — TODO]**
