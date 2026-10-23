You are helping build a test dataset for a research project on meeting analysis. Your job: write
four realistic meetings of one made-up project, plus the correct answers about the decisions made
in them. Read everything below before you start.

## 1. The project to invent

Invent a project in ANY domain EXCEPT these (they are already used): fleet maintenance software,
TV remote controls, online shops, hospital or clinic appointment apps. Good examples: a city bus
ticketing system, a school timetable app, a warehouse inventory system, a library app, a farm
irrigation controller. Give it 4-6 people with names and roles.

## 2. What to write

- 4 meetings of the same project, in order (meeting a, b, c, d), a week or so apart.
- Each meeting 30-60 lines, one line per turn: `Name: what they said`
- Make it sound like a real meeting: small talk, interruptions, people disagreeing, a topic dropped
  and picked up later, questions that never get answered. Not every line is about a decision.
- Some people can miss a meeting (say so at the start of that meeting).
- 15 to 20 decisions in total across the 4 meetings. A decision is something the group actually
  AGREES on, not just discusses.

## 3. Relations between decisions in different meetings

For every pair of decisions from different meetings, exactly one of these is true:

| Relation | Meaning |
|---|---|
| SAME | The later decision restates or re-confirms the earlier one. Nothing changes. |
| REVISED | Same subject, the chosen option CHANGED, and someone in a meeting EXPLICITLY ACKNOWLEDGES the change (refers to the earlier choice, or to "what we agreed before", and the group agrees to change it). |
| CONTRADICTORY | The later decision conflicts with the earlier one and NOBODY acknowledges the change: the earlier choice is never referred to, so both appear to stand. |
| REFINES | The later decision keeps the earlier one and adds detail or narrows it. |
| UNRELATED | Different subjects (even if the words look similar). |

## 4. Cases you MUST include

| Case | At least |
|---|---|
| CONTRADICTORY | 3 |
| ...of which the two decisions share almost NO words (different vocabulary for the same choice; for example "Tickets are sold only at kiosks" vs "Riders pay by tapping their phone on the bus") | 2 of the 3 |
| ...of which the earlier option IS mentioned in an in-between meeting, but nobody agrees to change it, and the conflicting decision comes later anyway | 1 of the 3 |
| REVISED | 3 |
| ...of which the change is agreed in one meeting and only RE-CONFIRMED in a later meeting (then the re-confirming decision is REVISED versus the original too) | 1 of the 3 |
| ...of which the earlier option is not named, only referred to ("the plan from the first meeting won't work...") | 1 of the 3 |
| SAME | 2 |
| REFINES | 2 |
| Look-alike pairs: share words but are about different things (UNRELATED; do not list them) | 2 |
| Ideas raised but NOT agreed (parked, rejected or postponed) | 2 |
| One decision that settles two things at once (e.g. a place AND a date) | 1 |
| A change of a date, and a change of a number (either REVISED or CONTRADICTORY) | 1 each |

Do not use the words SAME, REVISED, CONTRADICTORY or REFINES in the meeting dialogue.

## 5. Marking decisions in the transcripts

At the END of the line where the group agrees on a decision, add its id in double brackets:
`[[G1]]`, `[[G2]]`, ... Numbers must be unique across all four meetings. At the end of the line
where a not-agreed idea is RAISED, add `[[N1]]`, `[[N2]]`, ... Each tag appears exactly once.

Example:
```
Meera: So reminders go out by post, three days before. Everyone happy? [[G1]]
Ravi: Fine by me.
Meera: Someone suggested an app, but let's park that for now. [[N1]]
```

## 6. Output format (follow exactly)

Output EIGHT files, each in its own code block, with the file name on the line just before the
block, in this order:

1. `meeting_a.txt`, 2. `meeting_b.txt`, 3. `meeting_c.txt`, 4. `meeting_d.txt`
   (lines `Name: text` only, no headings, no blank-line rules needed)
5. `decisions.csv`, with header `gold_id,meeting,text`: one row per decision, meeting is a/b/c/d,
   text is the decision written as meeting minutes would write it. Put text in double quotes if it
   contains a comma.
6. `relations.csv`, with header `later,earlier,relation,rationale`: one row per RELATED pair (SAME,
   REVISED, CONTRADICTORY or REFINES only), later decision first, the later one from a later
   meeting. Leave out unrelated pairs. Every pair you list must follow the definitions in section 3;
   also list the pairs implied by your design (for example, if G7 revises G2 and G13 re-confirms
   G7, then G13-G7 is SAME and G13-G2 is REVISED).
7. `non_decisions.csv`, with header `id,meeting,text`: one row per `[[N..]]` tag.
8. `provenance.txt`: one paragraph saying which AI system and model wrote this, and the date.

Then, after the files, a short checklist showing how each case in section 4 is covered (which ids).

If your answer would be cut off, stop after a COMPLETE file and wait; I will say "continue".
