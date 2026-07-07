#!/usr/bin/env python3
"""Run YOUR model on AzDIM-Bench in one command.

Works with any OpenAI-compatible endpoint — Ollama, LM Studio, vLLM,
llama.cpp server, OpenRouter, OpenAI, Groq, ...

    pip install openai

    # Ollama (local)
    python run_azdim.py --model llama3.2 --base-url http://localhost:11434/v1

    # OpenRouter
    OPENAI_API_KEY=$OPENROUTER_API_KEY python run_azdim.py \
        --model qwen/qwen3-max --base-url https://openrouter.ai/api/v1

    # OpenAI
    python run_azdim.py --model gpt-5.4-mini

Dataset: azdim_bench.jsonl next to this script (or --data PATH).
Protocol: the official AzDIM-Bench condition — the model may reason freely,
the last line must be "Cavab: <letter>" (AZ) / "Ответ: <буква>" (RU) /
"Answer: <letter>" (EN/DE/FR). Scoring is exact match on the parsed letter.
Results: accuracy by track and subject, plus a per-item outputs file you can
submit to the leaderboard (see repository README).
"""

import argparse
import json
import os
import re
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    sys.exit("pip install openai")

INSTR = {
    "az": ("Sualı həll et. İstəsən qısa izah verə bilərsən, amma cavabının "
           "SON sətri mütləq bu formatda olmalıdır:\nCavab: <hərf>\n"
           "burada <hərf> A, B, C, D və ya E-dir."),
    "ru": ("Реши задачу. Можешь кратко объяснить решение, но ПОСЛЕДНЯЯ "
           "строка твоего ответа должна иметь строго такой формат:\n"
           "Ответ: <буква>\nгде <буква> — A, B, C, D или E."),
    "en": ("Solve the task. You may explain briefly, but the LAST line of "
           "your answer must have exactly this format:\nAnswer: <letter>\n"
           "where <letter> is A, B, C, D or E."),
}
INSTR["de"] = INSTR["fr"] = INSTR["en"]

MARKER = re.compile(
    r"(?:cavab|ответ|answer)\s*[:\-–]?\s*\**\s*([A-E])(?![A-Za-z])",
    re.IGNORECASE)
STANDALONE = re.compile(r"(?<![A-Za-z])([A-E])(?![A-Za-z])")


def parse_answer(raw: str):
    text = (raw or "").strip()
    if not text:
        return None
    markers = MARKER.findall(text)
    if markers:
        return markers[-1]
    bare = re.sub(r"[\s*_.()\[\]\"'`:]+", "", text)
    if len(bare) == 1 and bare in "ABCDE":
        return bare
    lines = [ln for ln in text.splitlines() if ln.strip()]
    for line in (lines[0], lines[-1]):
        found = STANDALONE.findall(line)
        if len(set(found)) == 1:
            return found[0]
    found = STANDALONE.findall(text)
    if len(set(found)) == 1:
        return found[0]
    return None


def eval_pool(data_path: Path):
    items = [json.loads(line) for line in data_path.read_text().splitlines()]
    return [it for it in items
            if it["question_type"] == "mcq"
            and it.get("gold_answer_label") in tuple("ABCDE")
            and not it.get("requires_image")
            and it.get("language") in INSTR
            and it.get("extraction_confidence") == "high"]


def prompt_of(item: dict) -> str:
    lines = [INSTR[item["language"]], "", item["question_text"].strip(), ""]
    for letter in "ABCDE":
        choice = (item.get("choices") or {}).get(letter)
        if choice and str(choice).strip():
            lines.append(f"{letter}) {choice}")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--base-url", default=None,
                    help="OpenAI-compatible endpoint; default: OpenAI")
    ap.add_argument("--data", default=None, help="path to azdim_bench.jsonl")
    ap.add_argument("--max-tokens", type=int, default=2048)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--limit", type=int, default=None,
                    help="run only the first N items (smoke test)")
    args = ap.parse_args()

    data_path = Path(args.data) if args.data else \
        Path(__file__).parent / "azdim_bench.jsonl"
    if not data_path.exists():
        sys.exit(f"dataset not found: {data_path}\n"
                 "download azdim_bench.jsonl next to this script")
    items = eval_pool(data_path)
    if args.limit:
        items = items[:args.limit]
    print(f"{len(items)} eval items · model={args.model}")

    client = OpenAI(base_url=args.base_url,
                    api_key=os.environ.get("OPENAI_API_KEY", "ollama"))
    out_path = Path(f"azdim_out__{args.model.replace('/', '_')}.jsonl")
    done = set()
    if out_path.exists():
        done = {json.loads(line)["item_id"]
                for line in out_path.read_text().splitlines()}
        items = [it for it in items if it["item_id"] not in done]
        print(f"resuming: {len(done)} cached, {len(items)} to run")

    def one(it):
        raw = ""
        for attempt in range(3):
            try:
                resp = client.chat.completions.create(
                    model=args.model,
                    max_completion_tokens=args.max_tokens,
                    messages=[{"role": "user", "content": prompt_of(it)}])
                raw = resp.choices[0].message.content or ""
                break
            except Exception as e:  # noqa: BLE001
                if attempt == 2:
                    return {"item_id": it["item_id"], "error": str(e)[:300]}
                time.sleep(4 * 2 ** attempt)
        parsed = parse_answer(raw)
        return {"item_id": it["item_id"], "raw": raw, "parsed": parsed,
                "gold": it["gold_answer_label"],
                "correct": parsed == it["gold_answer_label"],
                "language": it["language"], "subject": it["subject"]}

    n = 0
    with open(out_path, "a") as out, ThreadPoolExecutor(args.workers) as pool:
        for rec in pool.map(one, items):
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")
            out.flush()
            n += 1
            if n % 25 == 0:
                print(f"  {n}/{len(items)}")

    recs = [json.loads(line) for line in out_path.read_text().splitlines()]
    ok = [r for r in recs if "error" not in r]
    by = defaultdict(list)
    for r in ok:
        by[("track", {"az": "AZ", "ru": "RU"}.get(r["language"], "FL"))] \
            .append(r["correct"])
        by[("subject", r["subject"])].append(r["correct"])
    print(f"\n=== {args.model} on AzDIM-Bench ===")
    print(f"overall: {sum(r['correct'] for r in ok)}/{len(ok)} "
          f"= {sum(r['correct'] for r in ok) / max(len(ok), 1):.3f}   "
          f"invalid: {sum(r['parsed'] is None for r in ok) / max(len(ok), 1):.3f}"
          f"   errors: {len(recs) - len(ok)}")
    for (kind, key), flags in sorted(by.items()):
        if kind == "track":
            print(f"  track {key:<22}{sum(flags) / len(flags):.3f}  (n={len(flags)})")
    for (kind, key), flags in sorted(by.items()):
        if kind == "subject":
            print(f"  {key:<28}{sum(flags) / len(flags):.3f}  (n={len(flags)})")
    print(f"\nper-item outputs: {out_path}")


if __name__ == "__main__":
    main()
