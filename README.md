# Meeting decision tracking data

Data released with the paper **"Evidence-Grounded Cross-Meeting Decision Tracking and Organizational Memory Using Large Language Models"** (Dr. Vishwanath Karad MIT World Peace University, Pune, 2026).

It contains the two datasets created for that paper:

1. **`real_pairs/`**: 57 cross-meeting decision pairs from two AMI design-team series (ES2004, ES2011),
   each labelled independently by two annotators and then adjudicated.
2. **`synthetic/`**: three synthetic four-meeting series (SYN001, SYN002, SYN003) with ground-truth
   decisions and cross-meeting relations fixed before the system was run on them.

Relations between an earlier decision *a* and a later decision *b*:

| Label | Meaning |
|---|---|
| `SAME` | The same decision, restated or re-confirmed; no change in substance. |
| `REVISED` | About the same subject, but the chosen option changed. |
| `CONTRADICTORY` | Directly conflicts with the earlier decision, and both appear to stand (the change was not acknowledged). |
| `REFINES` | Keeps the earlier decision and adds detail or narrows its scope. |
| `UNRELATED` | Different subjects, even if the wording looks similar. |
| `UNSURE` | Used by annotators only; such pairs are excluded from scoring. |

The full definitions given to the annotators are in `real_pairs/LABELLING_GUIDE.md`.

---

## 1. `real_pairs/`: real decision pairs (AMI ES2004 and ES2011)

The units are all ordered pairs of decisions extracted from different meetings of the same series:
38 pairs in ES2004 and 19 in ES2011. The decisions themselves were extracted by the system described in
the paper (so they are system outputs); the relation labels are human.

| File | Contents |
|---|---|
| `pair_labels.csv` | Labels of annotator A, 57 rows. |
| `pair_labels_B.csv` | Labels of annotator B, 57 rows, made independently. |
| `adjudication.csv` | The 14 pairs on which the annotators differed (12) or one marked UNSURE (2): both original labels, the settled label and the reason. |
| `pair_labels_settled.csv` | The final gold labels (57 rows): `UNRELATED` 43, `SAME` 8, `REFINES` 4, `REVISED` 2, no `CONTRADICTORY`. |
| `LABELLING_GUIDE.md` | The guide given to both annotators. |
| `meeting_reference.md` | Per meeting: the QMSum gold summary and the decisions extracted by the system, used by annotators when a pair was unclear. |
| `pair_scores.csv` | **System outputs, not labels**: embedding similarity, its rank, whether the pair was retrieved, the cross-evidence score and whether it passed stage 2 of the tracker. These are the stage-1/2 outputs, so the retrieval and gating part of the paper's tracker results (e.g. 18 of the 57 pairs reach the LLM judge) can be recomputed; the stage-3 LLM verdicts are not included. |

Columns of the three label files: `pair_id, series, earlier_id, earlier_meeting, earlier_decision,
earlier_evidence, later_id, later_meeting, later_decision, later_evidence, gold_relation, annotator, notes`.
`earlier_id`/`later_id` and the `D…` numbers in `pair_id` identify decisions within this release only.
The `*_evidence` columns are verbatim transcript turns from the AMI corpus (via QMSum). In `pair_labels_settled.csv`, the `annotator` column reads `A` for the 43 pairs on which both annotators agreed (the shared label) and `A+B (settled)` for the 14 adjudicated pairs. All CSV files are UTF-8 with a byte-order mark (read them as `utf-8-sig`).

Agreement before adjudication: the annotators agreed on 43 of the 55 pairs that both labelled (UNSURE
excluded); Cohen's kappa is 0.55 on the five relation types and 0.66 on related vs. unrelated.

Annotators: both are authors of the paper. The labelling sheet showed the decisions and the
system's evidence turns, but not similarity scores or the system's verdicts. The examples in the labelling
guide were taken from three of the pairs (D5-D3, D16-D14, D5-D1) and shown with the labels the system
had given them (REVISED, REFINES, UNRELATED), as reported in the paper. The two annotators are identified only as `A` and `B`.

`LABELLING_GUIDE.md` is reproduced as it was given to the annotators. It refers to parts of the project
repository that are not in this release (the scoring tool, the database and `data/qmsum/heldout/`, i.e.
QMSum's ES2004 and ES2011 files), and its step 4 names the file in which labels were settled; in this
release the settled labels are `pair_labels_settled.csv`.

## 2. `synthetic/`: synthetic series SYN001, SYN002, SYN003

| Series | Domain | Written by | Gold |
|---|---|---|---|
| SYN001 | Maintenance scheduling platform (FleetCare) | An LLM writing assistant (not Gemini, the model under evaluation) | 16 decisions; 10 relations (3 REVISED, 3 REFINES, 2 SAME, 2 CONTRADICTORY) |
| SYN002 | Hospital outpatient booking | An AI writing assistant that also designed the paper's contradiction-detection method, after its prompts were frozen. **Not blind.** | 20 decisions; 13 relations (3 CONTRADICTORY, 4 REVISED, 3 SAME, 3 REFINES) |
| SYN003 | City bus ticketing pilot (RideWave) | ChatGPT (reported model GPT-6), given only `authoring/SYN003_PROMPT.md` and one self-review request, with no access to the system or its method | 19 decisions; 13 relations (4 CONTRADICTORY, 5 REVISED, 2 SAME, 2 REFINES) |

The `provenance` field of each `*_gold.json` file and `SYN002/provenance.txt`, `SYN003/provenance.txt` are
the authoritative description of how each series was written. All companies, people and events in these
series are fictional.

| Path | Contents |
|---|---|
| `SYN00Xa.json` ... `SYN00Xd.json` | The four meetings of each series, in QMSum's JSON format (`meeting_transcripts`: speaker and content per turn). |
| `SYN00X_gold.json` | Ground truth: `decisions` (`gold_id`, `meeting`, `sequence_index`, `text`, `anchor_turn`), `relations` (`later`, `earlier`, `relation`, `rationale`), `ambiguous` pairs (excluded from scoring) and `non_decisions` (statements that look like decisions but are not). |
| `SYN002/`, `SYN003/` | The plain-text sources of those two series (`meeting_*.txt`, `decisions.csv`, `relations.csv`, `non_decisions.csv`) and their `provenance.txt`. |
| `build_synthetic.py` | Builds SYN001's JSON files from the data inside the script. |
| `build_from_text.py` | Builds a series' JSON files from the plain-text sources (used for SYN002 and SYN003). |
| `authoring/SYN002_AUTHORING_GUIDE.md` | The authoring format guide referred to by `build_from_text.py`. |
| `authoring/SYN003_PROMPT.md` | The exact prompt given to the independent author of SYN003. |

**Note:** the docstring of `build_from_text.py` and the authoring guide describe the *planned* procedure
(a teammate writing SYN002 blind). SYN002 was in the end written by the AI assistant described above, so it
is **not blind**; `SYN002/provenance.txt` and the paper report this. The guide's remark that it "stays for a
blind series written by a teammate" (id SYN003) also describes a plan: SYN003 was written by ChatGPT from
`authoring/SYN003_PROMPT.md`, not by a teammate. The pipeline commands (`python -m app...`) and paths such
as `evaluation/...` or `data/synthetic/...` inside these documents refer to the project repository;
`MANIFEST.csv` maps every original path to its path in this release (e.g. `evaluation/synthetic/SYN003_PROMPT.md`
is `synthetic/authoring/SYN003_PROMPT.md`). The last sentence of `SYN002/provenance.txt` (a reminder to
review the transcripts for realism) is reproduced as written.

**Rebuilding (checked).** The JSON files can be regenerated from the sources with Python 3 (standard
library only). The scripts never overwrite ground truth, so work on a copy and delete that series'
JSON files there first, e.g. for SYN003:

```
cd synthetic
rm SYN003a.json SYN003b.json SYN003c.json SYN003d.json SYN003_gold.json
python build_from_text.py SYN003
```

(`python build_synthetic.py` regenerates SYN001 the same way.) We checked this for all three series: the
regenerated meeting files and every decision and relation are identical to the released ones (on Windows
the files are written with CRLF line endings; the JSON content is the same). The one difference is the
`provenance` text of `SYN003_gold.json`: it keeps the original wording ("a neutral request"), whereas
`SYN003/provenance.txt` was later corrected to describe the self-review request more precisely (it named the
kinds of problem to check, but no pair or label). `SYN003/provenance.txt` is the accurate description; the
gold file was left unchanged because the evaluation used it.

## 3. Integrity

Every data file was copied unchanged from the project repository at commit `f38d673`, with one deliberate
exception: in `real_pairs/`, the annotators' internal identifiers were replaced by `A` and `B` (the
`annotator` column of the three label files and two column names of `adjudication.csv`); no other cell
was changed. `MANIFEST.csv` gives, for each file, the git blob id of the original in the project, the
SHA-256 of the file as released and whether it was modified.
`SHA256SUMS` can be checked with `sha256sum -c SHA256SUMS` (Linux/macOS/Git Bash). Both cover the 42 data
files; the documentation files (README, licences, notices, citation) were written for this release.

## 4. Licence and attribution

- Data: **Creative Commons Attribution 4.0 International** (`LICENSE`).
- Copyright 2026 the authors (Jinesha Gandhi, Gaurvi Jain, Tanmay Dhumal, Milind Muravane, Devendra Joshi).
- The two Python scripts: MIT License (`LICENSE-CODE`).
- The synthetic series are machine-generated text (SYN001 and SYN002 by an AI writing assistant, SYN003 by
  ChatGPT), with ground truth checked by the authors. Copyright in AI-generated text may be limited; the
  CC BY 4.0 licence applies to the extent that rights exist. All names and events in them are fictional.
- `real_pairs/` contains verbatim excerpts of the **AMI Meeting Corpus** (CC BY 4.0) and gold summaries
  from **QMSum** (MIT). See `THIRD_PARTY_NOTICES.md`; please credit both when you reuse those files.

## 5. Citation

If you use this data, please cite the paper (see `CITATION.cff`), the AMI Meeting Corpus and QMSum.
Contact: the authors, via the e-mail addresses given in the paper.
