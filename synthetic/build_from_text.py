"""
Build a synthetic series (e.g. SYN002) from plain-text files written by a
person, in the same format as SYN001 (build_synthetic.py), so the existing
pipeline loads and scores it unchanged.

WHY: SYN002 is the HELD-OUT test of the contradiction-detection method. It
must be written by a teammate who has not seen that method's prompts or
outputs, with the ground truth fixed BEFORE the system runs. Writing Python
like build_synthetic.py is not needed: plain text and three small CSVs are.
See evaluation/synthetic/SYN002_AUTHORING_GUIDE.md.

INPUT  data/synthetic/<SERIES>/
  meeting_a.txt, meeting_b.txt, ...   one turn per line:  "Name: what they said"
                                      Mark the line where a decision is AGREED with
                                      its gold id, e.g. "... Agreed? [[G3]]", and the
                                      line where an idea is raised but NOT agreed
                                      with [[N1]]. Tags are removed from the text.
  decisions.csv      gold_id, meeting, text                 (G1, a, "Host on AWS.")
  relations.csv      later, earlier, relation, rationale    (G5, G2, REVISED, "...")
  ambiguous.csv      later, earlier, note                   (optional)
  non_decisions.csv  id, meeting, text                      (optional; N1, a, "...")
  provenance.txt     who wrote it, when, with what help      (required)

OUTPUT data/synthetic/<SERIES>a.json ... and <SERIES>_gold.json (never overwritten).

Usage:
    python data/synthetic/build_from_text.py SYN002
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RELATIONS = {"SAME", "REVISED", "CONTRADICTORY", "REFINES"}
PROTECTED = {"ES2002", "ES2004", "ES2011", "SYN001"}
TAG = re.compile(r"\[\[\s*([GN]\d+)\s*\]\]")
TURN = re.compile(r"^\s*([^:]{1,40}):\s*(.+?)\s*$")


class SeriesError(ValueError):
    pass


def read_rows(path: Path, columns: list[str], required: bool = True) -> list[dict]:
    if not path.exists():
        if required:
            raise SeriesError(f"Missing {path.name}.")
        return []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = [{k.strip(): (v or "").strip() for k, v in row.items() if k} for row in csv.DictReader(handle)]
    if rows and set(columns) - set(rows[0]):
        raise SeriesError(f"{path.name} needs the columns {columns}.")
    return [r for r in rows if any(r.values())]


def parse_meeting(path: Path) -> tuple[list[dict], dict[str, int]]:
    """Turns, and {tag: index of the turn carrying it}."""

    turns, anchors = [], {}
    for number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
        if not line.strip():
            continue
        match = TURN.match(line)
        if not match:
            raise SeriesError(f"{path.name} line {number}: expected 'Name: text', got {line[:60]!r}")
        speaker, content = match.group(1).strip(), match.group(2)
        for tag in TAG.findall(content):
            tag = tag.upper()
            if tag in anchors:
                raise SeriesError(f"{path.name} line {number}: tag [[{tag}]] used twice.")
            anchors[tag] = len(turns)
        content = " ".join(TAG.sub(" ", content).split())
        if not content:
            raise SeriesError(f"{path.name} line {number}: no text besides the tag.")
        turns.append({"speaker": speaker, "content": content})
    if not turns:
        raise SeriesError(f"{path.name} has no turns.")
    return turns, anchors


def build(series: str, source: Path) -> tuple[dict[str, dict], dict]:
    if series.upper() in PROTECTED:
        raise SeriesError(f"{series} is an existing evaluation series and is never rebuilt.")
    if not re.fullmatch(r"[A-Z]{2,}\d{3}", series):
        raise SeriesError(f"Series id {series!r} must look like SYN002.")

    meeting_files = sorted(source.glob("meeting_*.txt"))
    letters = [p.stem.split("_", 1)[1] for p in meeting_files]
    if len(letters) < 3:
        raise SeriesError("Write at least 3 meetings (meeting_a.txt, meeting_b.txt, meeting_c.txt).")
    if letters != [chr(ord("a") + i) for i in range(len(letters))]:
        raise SeriesError(f"Meetings must be named meeting_a.txt, meeting_b.txt, ... in order; got {letters}.")

    provenance_path = source / "provenance.txt"
    if not provenance_path.exists() or not provenance_path.read_text(encoding="utf-8-sig").strip():
        raise SeriesError("provenance.txt is required: who wrote this, when, and with what help.")
    provenance = " ".join(provenance_path.read_text(encoding="utf-8-sig").split())

    meetings, anchors = {}, {}
    for letter, path in zip(letters, meeting_files):
        turns, found = parse_meeting(path)
        meetings[letter] = turns
        for tag, index in found.items():
            if tag in anchors:
                raise SeriesError(f"Tag [[{tag}]] appears in two meetings.")
            anchors[tag] = (letter, index)

    sequence = {letter: i for i, letter in enumerate(letters, start=1)}

    decisions = []
    for row in read_rows(source / "decisions.csv", ["gold_id", "meeting", "text"]):
        gid, letter = row["gold_id"].upper(), row["meeting"].lower()
        if not re.fullmatch(r"G\d+", gid):
            raise SeriesError(f"decisions.csv: gold_id {row['gold_id']!r} must look like G1.")
        if letter not in sequence:
            raise SeriesError(f"decisions.csv {gid}: unknown meeting {row['meeting']!r}.")
        if not row["text"]:
            raise SeriesError(f"decisions.csv {gid}: text is empty.")
        if gid not in anchors or anchors[gid][0] != letter:
            raise SeriesError(f"{gid}: mark its agreement line in meeting_{letter}.txt with [[{gid}]].")
        decisions.append({"gold_id": gid, "meeting": letter, "sequence_index": sequence[letter],
                          "text": row["text"], "anchor_turn": anchors[gid][1]})
    ids = [d["gold_id"] for d in decisions]
    if len(ids) != len(set(ids)):
        raise SeriesError("decisions.csv lists a gold_id twice.")
    meeting_of = {d["gold_id"]: d["sequence_index"] for d in decisions}

    def pair(row, file):
        later, earlier = row["later"].upper(), row["earlier"].upper()
        for gid in (later, earlier):
            if gid not in meeting_of:
                raise SeriesError(f"{file}: unknown decision {gid}.")
        if meeting_of[earlier] >= meeting_of[later]:
            raise SeriesError(f"{file}: {earlier} must come from an EARLIER meeting than {later}.")
        return later, earlier

    relations, seen = [], set()
    for row in read_rows(source / "relations.csv", ["later", "earlier", "relation", "rationale"]):
        later, earlier = pair(row, "relations.csv")
        relation = row["relation"].upper()
        if relation not in RELATIONS:
            raise SeriesError(f"relations.csv {later}-{earlier}: relation must be one of {sorted(RELATIONS)} "
                              "(unlisted pairs are UNRELATED).")
        if (later, earlier) in seen:
            raise SeriesError(f"relations.csv lists {later}-{earlier} twice.")
        seen.add((later, earlier))
        relations.append({"later": later, "earlier": earlier, "relation": relation,
                          "rationale": row["rationale"]})

    ambiguous = []
    for row in read_rows(source / "ambiguous.csv", ["later", "earlier", "note"], required=False):
        later, earlier = pair(row, "ambiguous.csv")
        if (later, earlier) in seen:
            raise SeriesError(f"{later}-{earlier} is in relations.csv AND ambiguous.csv.")
        ambiguous.append({"later": later, "earlier": earlier, "note": row["note"]})

    non_decisions = []
    for row in read_rows(source / "non_decisions.csv", ["id", "meeting", "text"], required=False):
        nid, letter = row["id"].upper(), row["meeting"].lower()
        if nid not in anchors or anchors[nid][0] != letter:
            raise SeriesError(f"{nid}: mark its line in meeting_{letter}.txt with [[{nid}]].")
        non_decisions.append({"meeting": letter, "text": row["text"], "anchor_turn": anchors[nid][1]})

    listed = set(ids) | {r["id"].upper() for r in read_rows(source / "non_decisions.csv",
                                                             ["id", "meeting", "text"], required=False)}
    unlisted = sorted(set(anchors) - listed)
    if unlisted:
        raise SeriesError(f"Tags {unlisted} are in the transcripts but not in decisions.csv / non_decisions.csv.")

    files = {f"{series}{letter}.json": {"topic_list": [], "general_query_list": [],
                                        "specific_query_list": [], "meeting_transcripts": turns}
             for letter, turns in meetings.items()}
    gold = {"series_id": series, "provenance": provenance, "decisions": decisions,
            "relations": relations, "ambiguous": ambiguous, "non_decisions": non_decisions}
    return files, gold


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("series")
    parser.add_argument("--source", help="input folder (default data/synthetic/<SERIES>)")
    args = parser.parse_args()

    series = args.series.upper()
    source = Path(args.source) if args.source else HERE / series
    try:
        files, gold = build(series, source)
    except SeriesError as error:
        sys.exit(f"Not built: {error}")

    outputs = {**files, f"{series}_gold.json": gold}
    existing = [name for name in outputs if (HERE / name).exists()]
    if existing:
        sys.exit(f"Not built: {existing} already exist. Ground truth is never overwritten; "
                 "delete them by hand only if they were never used for an evaluation.")
    for name, content in outputs.items():
        (HERE / name).write_text(json.dumps(content, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    counts = {r: sum(1 for x in gold["relations"] if x["relation"] == r) for r in sorted(RELATIONS)}
    print(f"{series}: {len(files)} meetings, {len(gold['decisions'])} decisions, relations {counts}, "
          f"{len(gold['ambiguous'])} ambiguous, {len(gold['non_decisions'])} non-decisions.")
    # Never the whole folder: that would import SYN001 a second time.
    print("Next, load EACH new meeting file on its own (see the authoring guide):")
    for name in files:
        print(f"  python -m app.pipeline.load_qmsum data/synthetic/{name}")


if __name__ == "__main__":
    main()
