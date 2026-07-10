"""Second-reader pass: independent re-transcription with a DIFFERENT model
family (Gemini Flash), for double-entry certification of the dataset.

Reader 2 sees only the page image — none of our extraction — and returns a
minimal record per item (variant-A number, question start, choices, gold).
`diff` then binds reader-2 records to our items via the variant-A numbers
already confirmed geometrically by azdim.validate, and compares fields.
Agreement = certified by two independent readers; disagreement = flagged
for the human queue.

Usage:
    uv run python -m azdim.reader2 run [<source_id> ...]   # -> data/extracted2/
    uv run python -m azdim.reader2 diff                    # -> qc flags + report
"""

import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from difflib import SequenceMatcher
from pathlib import Path

from azdim.boxes import _norm
from azdim.extract import PAGES_DIR, USAGE_LOG, load_env, page_number
from azdim.render import izah_source_ids, render

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "data" / "extracted2"
ITEMS_FILE = ROOT / "data" / "items" / "items_v0.jsonl"
CONFIRMED = ROOT / "data" / "items" / "confirmed_numbers.json"
FLAGS = ROOT / "data" / "items" / "qc_flags.json"
REPORT = ROOT / "data" / "items" / "double_entry_report.json"

MODEL = "gemini-3.5-flash"
PRICE_IN, PRICE_OUT = 0.30, 1.20        # $/MTok, flash tier

PROMPT = """This is one page of an official Azerbaijani exam explanation \
("izah") PDF. Each exam item on the page has a metadata block reading \
"A variantı N saylı test tapşırığı" (with B/C/D lines) ABOVE the question.

Transcribe every item whose metadata block is on THIS page. For each, output:
- "n": the integer N from the "A variantı N saylı" line
- "q": the first 25 words of the question text, verbatim (LaTeX for math)
- "choices": object mapping letters to full choice texts ({} if open-ended)
- "gold": the correct answer letter per the page ("Doğru cavab"), else ""

Return ONLY a JSON array of these objects. No commentary."""


def transcribe_page(client, png: Path) -> list[dict]:
    from google.genai import types
    part = types.Part.from_bytes(data=png.read_bytes(), mime_type="image/png")
    resp = client.models.generate_content(
        model=MODEL,
        contents=[part, PROMPT],
        config=types.GenerateContentConfig(
            temperature=0.0,
            response_mime_type="application/json"),
    )
    usage = resp.usage_metadata
    cost = ((usage.prompt_token_count or 0) * PRICE_IN
            + (usage.candidates_token_count or 0) * PRICE_OUT) / 1e6
    with open(USAGE_LOG, "a") as f:
        f.write(json.dumps({"model": MODEL,
                            "context": f"reader2:{png.parent.name}:{png.stem}",
                            "cost_usd": round(cost, 6)}) + "\n")
    text = resp.text or "[]"
    text = re.sub(r"^```(json)?|```$", "", text.strip(), flags=re.MULTILINE)
    try:
        data = json.loads(text)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


def run(source_ids: list[str]) -> None:
    load_env()
    from google import genai
    client = genai.Client()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for sid in source_ids:
        out = OUT_DIR / f"{sid}.jsonl"
        if out.exists():
            print(f"skip {sid} (exists)")
            continue
        pages = sorted((PAGES_DIR / sid).glob("page-*.png"), key=page_number)
        if not pages:
            render(sid)
            pages = sorted((PAGES_DIR / sid).glob("page-*.png"),
                           key=page_number)

        def one(png: Path) -> list[dict]:
            items: list[dict] = []
            for attempt in (1, 2, 3):
                try:
                    items = transcribe_page(client, png)
                    break
                except Exception as e:  # noqa: BLE001 — retry then surface
                    if attempt == 3:
                        print(f"  FAILED {png.name}: {str(e)[:120]}")
                        return []
                    import time
                    time.sleep(5 * attempt)
            for it in items:
                it["source_page"] = page_number(png)
            return items

        rows: list[dict] = []
        with ThreadPoolExecutor(6) as pool:
            for items in pool.map(one, pages):
                rows.extend(items)
        with open(out, "w") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"{sid}: {len(rows)} reader-2 records")


def diff() -> None:
    items = [json.loads(line) for line in ITEMS_FILE.read_text().splitlines()]
    confirmed = json.loads(CONFIRMED.read_text())
    flags = json.loads(FLAGS.read_text()) if FLAGS.exists() else {}
    stats = {"bound": 0, "gold_agree": 0, "gold_diff": 0,
             "text_agree": 0, "text_diff": 0}
    diffs = []
    for path in sorted(OUT_DIR.glob("*.jsonl")):
        sid = path.stem
        r2 = [json.loads(line) for line in path.read_text().splitlines()]
        # bind on (page, n): our side uses geometry-confirmed numbers
        r2_by_key = {}
        for r in r2:
            try:
                n = int(str(r.get("n")).strip())
            except (ValueError, TypeError):
                continue
            r2_by_key.setdefault((int(r["source_page"]), n), r)
        for it in items:
            if it["source_id"] != sid:
                continue
            n_a = confirmed.get(it["item_id"])
            if n_a is None:
                continue
            p = it["source_page"]
            r = (r2_by_key.get((p, n_a)) or r2_by_key.get((p + 1, n_a))
                 or r2_by_key.get((p - 1, n_a)))
            if r is None:
                continue
            stats["bound"] += 1
            # gold comparison (MCQ with both sides present)
            g1, g2 = it.get("gold_answer_label"), (r.get("gold") or "").strip()
            if it["question_type"] == "mcq" and g1 and g2 in "ABCDE" and g2:
                if g1 == g2:
                    stats["gold_agree"] += 1
                else:
                    stats["gold_diff"] += 1
                    flags.setdefault(it["item_id"],
                                     f"double_entry_gold_{g1}vs{g2}")
                    diffs.append({"item_id": it["item_id"], "field": "gold",
                                  "ours": g1, "reader2": g2})
            # question-start comparison
            q1 = " ".join(_norm(it.get("question_text") or "").split()[:25])
            q2 = " ".join(_norm(r.get("q") or "").split()[:25])
            if q1 and q2:
                sim = SequenceMatcher(None, q1.split(), q2.split()).ratio()
                if sim >= 0.75:
                    stats["text_agree"] += 1
                else:
                    stats["text_diff"] += 1
                    flags.setdefault(it["item_id"],
                                     f"double_entry_text_{sim:.2f}")
                    diffs.append({"item_id": it["item_id"], "field": "text",
                                  "sim": round(sim, 2)})
    FLAGS.write_text(json.dumps(flags, indent=1, sort_keys=True))
    REPORT.write_text(json.dumps({"stats": stats, "diffs": diffs},
                                 ensure_ascii=False, indent=1))
    print(json.dumps(stats, indent=1))
    print(f"report -> {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "run":
        run(sys.argv[2:] or izah_source_ids())
    elif cmd == "diff":
        diff()
    else:
        sys.exit("usage: reader2 run|diff [<source_id> ...]")
