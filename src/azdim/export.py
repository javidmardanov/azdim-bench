"""Export the canonical dataset to a HuggingFace-ready layout.

Usage:
    uv run python -m azdim.export

Writes release/ with:
    azdim_bench.jsonl   one record per item (public fields only)
    README.md           dataset card skeleton (counts filled in)
"""

import json
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ITEMS_FILE = ROOT / "data" / "items" / "items_v0.jsonl"
VERIFIED_FILE = ROOT / "data" / "verified" / "items_v0_verified.jsonl"
RELEASE_DIR = ROOT / "release"

PUBLIC_FIELDS = [
    "item_id", "exam_date", "exam_type", "group", "subject",
    "subject_section", "topic", "grade_level_tag", "language",
    "question_type", "question_text", "choices", "gold_answer_label",
    "gold_answer_text", "explanation_text", "requires_image",
    "image_description", "variant_map", "source_id", "source_page",
    "extraction_confidence", "verification_status",
]


def main() -> None:
    source = VERIFIED_FILE if VERIFIED_FILE.exists() else ITEMS_FILE
    items = [json.loads(line) for line in source.read_text().splitlines()]
    RELEASE_DIR.mkdir(exist_ok=True)
    out = RELEASE_DIR / "azdim_bench.jsonl"
    with open(out, "w") as f:
        for it in items:
            rec = {k: it.get(k) for k in PUBLIC_FIELDS}
            rec.setdefault("verification_status", "unverified")
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    by_subject = Counter(it["subject"] for it in items)
    by_lang = Counter(it["language"] for it in items)
    by_type = Counter(it["question_type"] for it in items)
    card = f"""---
license: other
license_name: dim-derived
license_details: >-
  Question content © State Examination Center of the Republic of Azerbaijan
  (DİM, dim.gov.az), reproduced from official public post-exam publications
  for research purposes with attribution. Metadata and annotations CC-BY-4.0.
language: [az, ru, en, de, fr, ar]
task_categories: [question-answering, multiple-choice]
pretty_name: AzDIM-Bench
---

# AzDIM-Bench (v0, exported {date.today().isoformat()})

Benchmark of Azerbaijani state exam questions (DİM school-leaving and
university entrance exams, 2025-2026) for evaluating LLMs.

- **{len(items)} items**: {dict(by_type)}
- **Languages**: {dict(by_lang)}
- **Subjects**: {dict(by_subject)}

Source: official DİM "izah" PDFs (see `source_id` + `source_page` per item;
URL manifest in the project repository). Gold answers are DİM's own published
answers. Extraction: vision-LLM transcription, human-verified where
`verification_status = "human_verified"`.

Fields: {", ".join(PUBLIC_FIELDS)}
"""
    (RELEASE_DIR / "README.md").write_text(card)
    print(f"exported {len(items)} items from {source.name} -> {out}")


if __name__ == "__main__":
    main()
