"""Summarize an extracted-items JSONL: counts, subjects, flags.

Usage:
    uv run python -m azdim.report <source_id>

Subjects are derived by forward-filling section headers in page order
(izah PDFs print the subject heading once at the start of each section).
"""

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXTRACTED_DIR = ROOT / "data" / "extracted"


def load_with_subjects(source_id: str) -> list[dict]:
    path = EXTRACTED_DIR / f"{source_id}.jsonl"
    items = [json.loads(line) for line in path.read_text().splitlines()]
    items.sort(key=lambda it: it["source_page"])
    current = None
    for it in items:
        if it.get("section_header"):
            current = it["section_header"]
        it["subject_section"] = current
    return items


def summarize(source_id: str) -> None:
    items = load_with_subjects(source_id)
    print(f"{source_id}: {len(items)} items\n")
    for field, label in [("subject_section", "subject section"),
                         ("question_type", "question type"),
                         ("language", "language"),
                         ("extraction_confidence", "confidence")]:
        counts = Counter(str(it.get(field)) for it in items)
        print(f"by {label}:")
        for k, v in counts.most_common():
            print(f"  {v:>4}  {k}")
        print()
    n_img = sum(bool(it["requires_image"]) for it in items)
    n_nogold = sum(it["question_type"] == "mcq" and not it["gold_answer_label"]
                   for it in items)
    n_nomap = sum(not it.get("variant_map") for it in items)
    print(f"requires_image: {n_img}")
    print(f"mcq without gold label: {n_nogold}")
    print(f"missing variant_map: {n_nomap}")
    flagged = [it for it in items
               if it["extraction_confidence"] != "high" or it.get("notes")]
    if flagged:
        print(f"\nflagged items ({len(flagged)}):")
        for it in flagged:
            print(f"  p{it['source_page']:>3} conf={it['extraction_confidence']}"
                  f" note={it.get('notes')}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python -m azdim.report <source_id>")
    summarize(sys.argv[1])
