# Writing SYN002: the held-out test for contradiction detection

> **Note (11 Oct 2026):** SYN002 itself was written by the AI assistant that designed the method (not blind; see `data/synthetic/SYN002/provenance.txt`). This guide stays for a **blind** series written by a teammate: use the id **SYN003** wherever it says SYN002 below (it is already protected from uploads and resolutions).

Thanks for writing this. It's the test that decides whether our new
contradiction detection really works, so it has to be written **without
knowing how the method works**. Part A is for you (the author). Part B is
the pipeline Jinesha runs afterwards.

## Part A: for the author

### Stay blind (this is what makes the test count)

- **Don't open** `app/tracker/frames.py`, `app/tracker/acknowledgement.py`,
  `app/tracker/conflict.py`, or anything in `evaluation/frames/`,
  `evaluation/acknowledgements/`, or the `conflict_signals.csv` files.
- **Don't discuss your cases** with Jinesha until you've handed over the files.
- **Don't use Gemini** in any way (it's the model under test). If you use any
  other AI writing help, say so in `provenance.txt`. That's allowed, but it
  has to be reported.
- Write the ground truth (`decisions.csv`, `relations.csv`) **at the same
  time as** the transcripts, before anyone runs the system on them.

### What to write

A new project in a **new domain**. Not FleetCare (SYN001), not a remote
control (AMI), and not an online shop (used in the method's examples). For
example a hospital appointment app, a school timetable system, or city bus
ticketing.

- **4 meetings** of the same project, each **30 to 60 turns**.
- **15 to 20 decisions** in total. A decision is something the group actually
  agrees on, not just discusses.
- Realistic talk: small talk, people interrupting, a topic left and picked up
  again later. Don't make every decision a neat one-liner.

Each of these must appear **at least** the number of times shown:

| Case | At least | What it looks like |
|---|---|---|
| CONTRADICTORY | 3 | A later decision conflicts with an earlier one, and **nobody mentions the change**: the earlier choice is never referred to (for example, the person who made it is absent). |
| ...worded very differently | 1 of those 3 | The two decisions share almost no words. For example "Reminders go out by post" and "Patients get a WhatsApp message the day before". |
| REVISED | 3 | The choice changes and **someone says so**, in your own words. Vary how they say it. |
| ...changed in between | 1 of those 3 | Agreed as a change in meeting 2, then only **re-confirmed** in meeting 3. Label meeting 3 vs meeting 1 as REVISED too. |
| ...referred to indirectly | 1 of those 3 | The old option is not named, only referred to (as "last time's plan", for example). |
| SAME | 2 | The same decision re-confirmed in a later meeting. |
| REFINES | 2 | Keeps an earlier decision and adds detail ("touch cards" → "touch cards, sold at every station"). |
| Hard negative | 2 | Two decisions that share words but are about different things. These are UNRELATED, so you don't list them. |
| Not agreed | 2 | An idea someone raises that the group parks or rejects. Tag it `[[N1]]`, `[[N2]]`... |
| Multi-part | 1 | One decision that settles two things at once ("Open the clinic on Saturdays, 9 to 1"). |
| Date or number change | 1 each | One change of a date and one of a number, either revised or contradictory. |

**Optional (good to have):** someone mentions the earlier choice, but the
group never agrees to change it, and later a conflicting decision is made
anyway. Label it however you honestly read it. If you can't decide, put it
in `ambiguous.csv`.

### Relation definitions (the same as our labelling guide)

| Relation | Meaning |
|---|---|
| `SAME` | The same decision restated or re-confirmed. |
| `REVISED` | Same subject, the chosen option **changed**, and the change was acknowledged. |
| `CONTRADICTORY` | Conflicts with the earlier decision, and **both appear to stand**: nobody acknowledged the change. |
| `REFINES` | Keeps the earlier decision and adds detail or narrows its scope. |
| (UNRELATED) | Anything you don't list. |

### The files

Put everything in a new folder `data/synthetic/SYN002/`:

```
data/synthetic/SYN002/
  meeting_a.txt  meeting_b.txt  meeting_c.txt  meeting_d.txt
  decisions.csv  relations.csv  non_decisions.csv  ambiguous.csv (optional)
  provenance.txt
```

**Transcripts:** one turn per line, `Name: what they said`. Put the decision's
id at the end of **the line where the group agrees**. The tags are removed
from the text automatically.

```
Meera: So reminders go out by post, three days before. Everyone happy? [[G1]]
Ravi: Fine by me.
Meera: Someone suggested an app, but let's park that for now. [[N1]]
```

**decisions.csv:** one row per decision. Write the text as the outcome, the
way minutes would.

```
gold_id,meeting,text
G1,a,Appointment reminders are sent by post three days before.
```

**relations.csv:** one row per related pair, **later decision first**. List
only SAME / REVISED / CONTRADICTORY / REFINES; everything else counts as
UNRELATED. Give a short reason.

```
later,earlier,relation,rationale
G9,G1,CONTRADICTORY,"switch to WhatsApp never discussed; Meera absent"
```

**non_decisions.csv:** `id,meeting,text` for each `[[N..]]` tag.

**ambiguous.csv** (optional): `later,earlier,note` for pairs you genuinely
can't label. These are excluded from scoring.

**provenance.txt:** who wrote it, when, and any help used.

### Check and hand over

```
python data/synthetic/build_from_text.py SYN002
```

It checks everything: every tag has a row, every row has its tag, relations
point from a later meeting to an earlier one, and the relation names are
valid. Fix whatever it reports and run it again. When it prints the summary,
send the `data/synthetic/SYN002/` folder to Jinesha. **Don't run the tracker
or any other script on it.**

## Part B: for Jinesha (after the hand-over)

Ground truth is fixed at this point: never edit the author's files. SYN002
becomes a protected evaluation series, so it's never uploaded into.

```
# 1. Build the JSON files (refuses to overwrite)
python data/synthetic/build_from_text.py SYN002

# 2. Load EACH meeting file on its own (loading the folder would re-import SYN001)
python -m app.pipeline.load_qmsum data/synthetic/SYN002a.json
python -m app.pipeline.load_qmsum data/synthetic/SYN002b.json
python -m app.pipeline.load_qmsum data/synthetic/SYN002c.json
python -m app.pipeline.load_qmsum data/synthetic/SYN002d.json

# 3. Extract decisions and evidence (Gemini + RoBERTa)
python -m app.pipeline.run_knowledge_batch --series SYN002

# 4. Gold pair labels; CHECK decision_mapping.csv by hand before going on
python -m app.evaluation.synthetic_gold SYN002 --outdir evaluation/syn002
python -m app.evaluation.export_pairs SYN002 --outdir evaluation/syn002

# 5. One verdict per pair, one pinned model (resumable, a few days of quota)
python -m app.evaluation.judge_all_pairs SYN002 --model gemini-3.6-flash

# 6. Frame-ack signals and acknowledgement checks
python -m app.evaluation.build_frames SYN002 --model gemini-3.5-flash
python -m app.evaluation.export_conflict_signals SYN002 --outdir evaluation/syn002
python -m app.evaluation.judge_acknowledgement SYN002 --verdicts evaluation/judgements/SYN002.csv --model gemini-3.5-flash

# 7. Score: baseline vs frame-ack, once
python -m app.evaluation.ablation --labels evaluation/syn002/gold_pair_labels.csv \
    --scores evaluation/syn002/pair_scores.csv --verdicts evaluation/judgements/SYN002.csv \
    --signals evaluation/syn002/conflict_signals.csv \
    --acks evaluation/acknowledgements/SYN002.csv --out evaluation/syn002/ablation.md
```

Report the result **once**, whatever it is. The prompts are frozen (`frames-v1`,
`ack-v1`). If anything is changed after seeing SYN002, the change gets a new
version and SYN002 stops being held-out.
