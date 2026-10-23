# Labelling guide: cross-meeting decision pairs

`pair_labels.csv` holds every (earlier, later) pair of decisions from
different meetings of the same series, 57 pairs in total (ES2004: 38,
ES2011: 19). It is **blind**: you won't see similarity scores or the
tracker's verdicts, so your labels don't get anchored to the system
you're grading. Do not open `pair_scores.csv` or `decision_links` before
you finish labelling.

## What to fill in

| Column | Value |
|---|---|
| `gold_relation` | one of the labels below |
| `annotator` | your initials |
| `notes` | optional; required if you choose `UNSURE` |

Ask one question: **how does the LATER decision relate to the EARLIER one?**

| Label | Meaning | Example |
|---|---|---|
| `SAME` | Same decision restated or re-confirmed. Nothing in it changes. | "Exclude teletext" -> "Teletext stays out" |
| `REVISED` | Same subject, but the chosen option **changed**, so the earlier decision no longer stands. | "Rechargeable battery + dock" -> "Kinetic battery" |
| `CONTRADICTORY` | Conflicts with the earlier decision, and **both appear to stand** (nobody acknowledged the change). | "Target teenagers" -> "Target retirees", no discussion of the switch |
| `REFINES` | Keeps the earlier decision and adds detail or narrows its scope. | "No on-remote screen" -> "Show the menu on the TV instead" |
| `UNRELATED` | Different subject, even if the wording overlaps ("remote control", "the team"). | "Exclude teletext" -> "Kinetic battery" |
| `UNSURE` | You can't decide. The pair is excluded from scoring and counted. Explain in `notes`. | |

## Rules

1. **Judge substance, not wording.** Shared boilerplate isn't a relation.
2. **Multi-part decisions:** if *any* part of the later decision relates to
   *any* part of the earlier one, label that relation. If one part
   refines and another revises, choose `REVISED` (it changes the earlier
   decision's status) and note the split.
3. **"Proceed with the current design"**-style decisions: label `SAME` only
   if the earlier decision is actually part of the design being
   confirmed. If you'd need to guess, use `UNSURE`.
4. If the decision text or evidence is unclear, check
   `meeting_reference.md` (QMSum's human-written summaries, independent of
   our system) and then the transcript in `data/qmsum/heldout/`.
5. The evidence column shows segments chosen by our RoBERTa model. It's
   context, not proof. Don't assume it's the right evidence.
6. Label every row, including the obviously unrelated ones. Most pairs
   *should* be `UNRELATED`, and that's what makes precision measurable.

## Two annotators (recommended)

Agreement between two annotators is what makes "hand-labelled" defensible
in a review.

1. Copy `pair_labels.csv` to `pair_labels_B.csv` before anyone starts.
2. Annotator A fills `pair_labels.csv` and annotator B fills
   `pair_labels_B.csv`, **independently**.
3. Run the evaluation with `--second` to get Cohen's kappa and a list of
   disagreements.
4. Discuss the disagreements and settle the final label in `pair_labels.csv`.
   Report kappa from **before** you adjudicated.

## Excel

Opening the CSV in Excel is fine. When saving, choose **CSV UTF-8**. The
scorer also accepts plain CSV.

## Then

```powershell
.venv\Scripts\python.exe -m app.evaluation.evaluate_tracker
.venv\Scripts\python.exe -m app.evaluation.evaluate_tracker --second evaluation\pair_labels_B.csv
```

The results go to `evaluation/results.md`.

Scope: these labels grade **relation detection between extracted
decisions**. They can't measure decisions Gemini never extracted (for
example, ES2004b's flip-top design agreement doesn't appear as a decision).
Report that as a separate extraction-recall limitation.
