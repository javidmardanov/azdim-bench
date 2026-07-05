"""Canonicalize extracted items: drop fragments, fill subjects, dedup, ID.

Reads every data/extracted/<source_id>.jsonl, writes:
    data/items/items_v0.jsonl      canonical items with item_id + subject
    data/items/excluded_v0.jsonl   dropped records with exclusion_reason

Usage:
    uv run python -m azdim.align
"""

import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXTRACTED_DIR = ROOT / "data" / "extracted"
ITEMS_DIR = ROOT / "data" / "items"
MANIFEST = ROOT / "manifest" / "sources.json"

# verbatim section headers -> canonical subject slugs
SUBJECT_MAP = {
    "riyaziyyat": "mathematics", "математика": "mathematics",
    "fizika": "physics", "физика": "physics",
    "kimya": "chemistry", "химия": "chemistry",
    "biologiya": "biology", "биология": "biology",
    "informatika": "informatics", "информатика": "informatics",
    "tarix": "history", "история": "history",
    "cografiya": "geography", "coğrafiya": "geography",
    "география": "geography",
    "edebiyyat": "literature", "ədəbiyyat": "literature",
    "литература": "literature",
    "azerbaycan dili": "azerbaijani_language",
    "azərbaycan dili": "azerbaijani_language",
    "rus dili": "russian_language", "русский язык": "russian_language",
    "ingilis dili": "english", "английский язык": "english",
    "alman dili": "german", "немецкий язык": "german",
    "fransız dili": "french", "французский язык": "french",
    "ereb dili": "arabic", "ərəb dili": "arabic",
    "fars dili": "persian",
    "xarici dil": "foreign_language",
    # verbatim headers used inside foreign-language exam sections
    "english": "english", "deutsch": "german",
    "le français": "french", "français": "french",
}

# items with no recognizable section header: infer from question language
LANG_SUBJECT = {"en": "english", "de": "german", "fr": "french",
                "ar": "arabic", "fa": "persian"}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", (s or "").strip().lower())
    # Azerbaijani dotted İ lowercases to "i" + combining dot (U+0307)
    s = s.replace("̇", "")
    return re.sub(r"\s+", " ", s)


def subject_of(header: str | None) -> str | None:
    """Slug for a section heading, or None if it isn't a subject heading
    (topic lines, reading-passage instructions, fragments...)."""
    if not header or len(header) > 60:
        return None
    h = norm(header)
    for key, slug in SUBJECT_MAP.items():
        if key in h:
            return slug
    return None


def question_key(item: dict) -> str:
    return norm(item.get("question_text") or "")[:80]


def canonicalize() -> None:
    sources = {s["source_id"]: s
               for s in json.loads(MANIFEST.read_text())["sources"]}
    ITEMS_DIR.mkdir(parents=True, exist_ok=True)
    kept_all: list[dict] = []
    excluded_all: list[dict] = []

    for path in sorted(EXTRACTED_DIR.glob("*.jsonl")):
        sid = path.stem
        items = [json.loads(line) for line in path.read_text().splitlines()]
        items.sort(key=lambda it: it["source_page"])

        current_section = None
        current_subject = None
        seen_variant: dict[tuple, dict] = {}
        seen_question: dict[str, dict] = {}
        seq_by_page: Counter = Counter()
        for it in items:
            header_subject = subject_of(it.get("section_header"))
            if header_subject:  # only real subject headings advance the fill
                current_section = it["section_header"]
                current_subject = header_subject
            it["subject_section"] = current_section
            it["subject"] = (current_subject
                             or LANG_SUBJECT.get(it.get("language") or "")
                             or "unknown")
            meta = sources.get(sid, {})
            it["exam_date"] = meta.get("exam_date")
            it["exam_type"] = meta.get("exam_type")
            it["group"] = meta.get("group")

            def exclude(reason: str) -> None:
                it["exclusion_reason"] = reason
                excluded_all.append(it)

            qtext = (it.get("question_text") or "").strip()
            if len(qtext) < 3:
                exclude("no_question_text")
                continue
            if it["question_type"] == "mcq" and not it.get("choices"):
                exclude("mcq_without_choices")
                continue

            vmap = it.get("variant_map") or {}
            vkey = (it["subject"],) + tuple(sorted(vmap.items()))
            if vmap and vkey in seen_variant:
                exclude(f"duplicate_variant_map_of_p"
                        f"{seen_variant[vkey]['source_page']}")
                continue
            qkey = f"{it['subject']}|{question_key(it)}"
            if qkey in seen_question:
                exclude(f"duplicate_question_of_p"
                        f"{seen_question[qkey]['source_page']}")
                continue
            if vmap:
                seen_variant[vkey] = it
            seen_question[qkey] = it

            page = it["source_page"]
            seq_by_page[page] += 1
            it["item_id"] = f"azdim_{sid}_p{page:03d}_{seq_by_page[page]:02d}"
            kept_all.append(it)

    with open(ITEMS_DIR / "items_v0.jsonl", "w") as f:
        for it in kept_all:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    with open(ITEMS_DIR / "excluded_v0.jsonl", "w") as f:
        for it in excluded_all:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")

    print(f"kept {len(kept_all)} items, excluded {len(excluded_all)}")
    print("\nby source:")
    for sid, n in Counter(it["source_id"] for it in kept_all).items():
        print(f"  {n:>4}  {sid}")
    print("\nby subject:")
    for subj, n in Counter(str(it["subject"])
                           for it in kept_all).most_common():
        print(f"  {n:>4}  {subj}")
    print("\nexclusions:")
    for reason, n in Counter(
            it["exclusion_reason"].split("_of_p")[0]
            for it in excluded_all).most_common():
        print(f"  {n:>4}  {reason}")


if __name__ == "__main__":
    canonicalize()
