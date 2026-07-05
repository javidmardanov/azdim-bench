"""Vision-LLM extraction of exam items from rendered izah PDF pages.

For each page N we send the model page N plus page N+1 (continuation context)
and ask for every item that STARTS on page N, as strict JSON. Output goes to
data/extracted/<source_id>.jsonl, one record per extracted item.

Usage:
    uv run python -m azdim.extract <source_id> [--pages 1-5]

Requires ANTHROPIC_API_KEY in the environment or in <repo>/.env.
"""

import argparse
import base64
import json
import os
import sys
from pathlib import Path

import anthropic

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "manifest" / "sources.json"
PAGES_DIR = ROOT / "data" / "pages"
EXTRACTED_DIR = ROOT / "data" / "extracted"
USAGE_LOG = ROOT / "manifest" / "api_usage.jsonl"

MODEL = os.environ.get("AZDIM_EXTRACT_MODEL", "claude-sonnet-5")

# USD per million tokens (input, output). Sonnet 5 intro pricing through 2026-08-31.
PRICES = {
    "claude-sonnet-5": (2.00, 10.00),
    "claude-haiku-4-5": (1.00, 5.00),
    "claude-opus-4-8": (5.00, 25.00),
}

SYSTEM_PROMPT = """\
You are a meticulous transcriber of official Azerbaijani state exam (DİM) \
"izah" PDFs. These documents reproduce real exam items: question text, answer \
choices, topic, grade level, an explanation, and the correct answer, plus a \
mapping of the item to its position in the A/B/C/D exam variants.

You will receive images of two consecutive pages. Transcribe EVERY exam item \
that STARTS on the FIRST page. Use the second page only to complete an item \
that continues across the page break. If no item starts on the first page \
(e.g., it is a title page or only continuation text), return an empty list.

Typical item layout (labels appear in Azerbaijani, or Russian on \
Russian-sector pages):
- variant mapping lines: "A variantı N saylı test tapşırığı" (Russian: \
"задание N варианта A")
- the question text, possibly with answer choices "A) ... B) ... C) ... D) ... E) ..."
- "Mövzu:" (topic), "Sinif:" (grade level)
- "İzah:" (worked explanation)
- "Doğru cavab:" (correct answer)

Transcription rules:
1. Copy text EXACTLY as printed (Azerbaijani, Russian, English, etc.). Do not \
translate, correct, or paraphrase.
2. Write all mathematical notation as LaTeX (inline $...$). Reconstruct \
fractions, exponents, roots, and inequality signs faithfully from the visual \
rendering.
3. If the item depends on a figure, diagram, graph, table, map, or picture \
that cannot be fully represented in text, set "requires_image": true and \
describe the visual briefly in "image_description". Simple tables you CAN \
reproduce in Markdown do not count.
4. question_type: "mcq" if it has lettered choices; "codable_open" if the \
answer is a number/short string without choices; "written_open" if it demands \
free-form written work (essay, proof, extended response).
5. For MCQ, derive "gold_answer_label" by matching the "Doğru cavab" value to \
the choices; keep the printed answer value in "gold_answer_text". If you \
cannot match unambiguously, leave the label null and lower confidence.
6. "section_header": if a subject/section heading (e.g. "Riyaziyyat", \
"Fizika", "Kimya", "Azərbaycan dili", "Русский язык", "Listening") appears on \
the first page at or above this item, copy it verbatim; otherwise null.
7. "language": the language the question itself is written in ("az", "ru", \
"en", "de", "fr", ...).
8. "extraction_confidence": "high" if everything was clearly legible and \
complete; "medium" if minor uncertainty; "low" if the item is cut off, \
blurry, or otherwise doubtful. Explain any problem in "notes".

Return ONLY a JSON object of the form:
{"items": [ { ... }, ... ]}

Each item object must have exactly these keys:
start_on_first_page (true), continues_to_next_page (bool), section_header \
(string|null), variant_map (object like {"A": 1, "B": 3} or null), \
question_text (string), choices (object with keys A-E, or null), \
question_type (string), topic (string|null), grade_level_tag (string|null), \
explanation_text (string|null), gold_answer_label (string|null), \
gold_answer_text (string|null), requires_image (bool), image_description \
(string|null), language (string), extraction_confidence (string), notes \
(string|null)
"""


def load_env() -> None:
    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip().strip('"'))


def image_block(path: Path) -> dict:
    return {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": "image/png",
            "data": base64.standard_b64encode(path.read_bytes()).decode(),
        },
    }


def parse_items(raw: str) -> list[dict]:
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        text = text.removeprefix("json").strip()
    return json.loads(text)["items"]


def log_usage(usage, context: str) -> float:
    """Append token usage to the ledger; return this call's cost in USD."""
    inp, out = usage.input_tokens, usage.output_tokens
    price_in, price_out = PRICES.get(MODEL, (5.00, 25.00))
    cost = inp * price_in / 1e6 + out * price_out / 1e6
    with open(USAGE_LOG, "a") as f:
        f.write(json.dumps({
            "model": MODEL, "context": context,
            "input_tokens": inp, "output_tokens": out,
            "cost_usd": round(cost, 6),
        }) + "\n")
    return cost


def total_spend() -> float:
    if not USAGE_LOG.exists():
        return 0.0
    return sum(json.loads(line)["cost_usd"]
               for line in USAGE_LOG.read_text().splitlines() if line)


def extract_page(client: anthropic.Anthropic, source_meta: dict,
                 page: Path, next_page: Path | None) -> list[dict]:
    content: list[dict] = [image_block(page)]
    if next_page is not None:
        content.append(image_block(next_page))
    content.append({
        "type": "text",
        "text": (
            f"Document: DİM {source_meta['exam_type']} exam, "
            f"date {source_meta['exam_date']}, group {source_meta.get('group')}. "
            f"First image is page {page_number(page)}"
            + (f", second is page {page_number(next_page)}." if next_page else
               "; there is no following page.")
            + " Extract all items that start on the first page."
        ),
    })
    for attempt in (1, 2):
        resp = client.messages.create(
            model=MODEL,
            max_tokens=16000,
            # transcription needs fidelity, not reasoning; disabling thinking
            # keeps output tokens (and cost) down
            thinking={"type": "disabled"},
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": content}],
        )
        log_usage(resp.usage, f"extract:{page.parent.name}:{page.name}")
        text = next((b.text for b in resp.content if b.type == "text"), "")
        try:
            return parse_items(text)
        except (json.JSONDecodeError, KeyError) as e:
            if attempt == 2:
                raise RuntimeError(
                    f"unparseable model output for {page}: {e}") from e
    return []


def page_number(path: Path) -> int:
    return int(path.stem.split("-")[1])


def extract_source(source_id: str, page_range: tuple[int, int] | None) -> Path:
    load_env()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY not set (env or .env)")
    sources = {s["source_id"]: s
               for s in json.loads(MANIFEST.read_text())["sources"]}
    meta = sources[source_id]
    pages = sorted((PAGES_DIR / source_id).glob("page-*.png"), key=page_number)
    if not pages:
        sys.exit(f"no rendered pages for {source_id}; run azdim.render first")
    if page_range:
        pages_todo = [p for p in pages
                      if page_range[0] <= page_number(p) <= page_range[1]]
    else:
        pages_todo = pages
    by_number = {page_number(p): p for p in pages}

    EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = EXTRACTED_DIR / f"{source_id}.jsonl"
    client = anthropic.Anthropic()
    n_items = 0
    with open(out_path, "a") as out:
        for page in pages_todo:
            n = page_number(page)
            items = extract_page(client, meta, page, by_number.get(n + 1))
            for item in items:
                item["source_id"] = source_id
                item["source_page"] = n
                item["extractor_model"] = MODEL
                out.write(json.dumps(item, ensure_ascii=False) + "\n")
            n_items += len(items)
            print(f"page {n:>3}: {len(items)} items"
                  f"  (cumulative spend ${total_spend():.2f})")
    print(f"\n{n_items} items -> {out_path}")
    print(f"total API spend so far: ${total_spend():.2f}")
    return out_path


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("source_id")
    ap.add_argument("--pages", help="e.g. 1-5 (1-based, inclusive)")
    ns = ap.parse_args()
    rng = None
    if ns.pages:
        a, _, b = ns.pages.partition("-")
        rng = (int(a), int(b or a))
    extract_source(ns.source_id, rng)
