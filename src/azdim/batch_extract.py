"""Batch-API extraction of all izah PDFs (50% of direct-API price).

One Message Batch per source PDF; each request is one target page built by
extract.build_request. Results land in data/extracted/<source_id>.jsonl,
usage in manifest/api_usage.jsonl with the batch discount applied.

Usage:
    uv run python -m azdim.batch_extract submit [<source_id> ...]
    uv run python -m azdim.batch_extract status
    uv run python -m azdim.batch_extract collect
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import anthropic

from azdim.extract import (EXTRACTED_DIR, MANIFEST, MODEL, PAGES_DIR, PRICES,
                           USAGE_LOG, build_request, load_env, page_number,
                           parse_items)
from azdim.render import izah_source_ids, render

ROOT = Path(__file__).resolve().parents[2]
BATCHES = ROOT / "manifest" / "batches.json"

BATCH_DISCOUNT = 0.5


def load_state() -> dict:
    return json.loads(BATCHES.read_text()) if BATCHES.exists() else {}


def save_state(state: dict) -> None:
    BATCHES.write_text(json.dumps(state, indent=2))


def submit(source_ids: list[str]) -> None:
    load_env()
    client = anthropic.Anthropic()
    sources = {s["source_id"]: s
               for s in json.loads(MANIFEST.read_text())["sources"]}
    state = load_state()
    for sid in source_ids:
        if sid in state and state[sid].get("status") != "collected":
            print(f"skip {sid}: batch already submitted "
                  f"({state[sid]['batch_id']})")
            continue
        pages = sorted((PAGES_DIR / sid).glob("page-*.png"), key=page_number)
        if not pages:
            render(sid)
            pages = sorted((PAGES_DIR / sid).glob("page-*.png"),
                           key=page_number)
        by_number = {page_number(p): p for p in pages}
        requests = [
            {"custom_id": f"{sid}--{n:03d}",
             "params": build_request(sources[sid], by_number, n)}
            for n in sorted(by_number)
        ]
        batch = client.messages.batches.create(requests=requests)
        state[sid] = {
            "batch_id": batch.id,
            "n_pages": len(requests),
            "submitted_at": datetime.now(timezone.utc).isoformat(),
            "status": "submitted",
        }
        save_state(state)
        print(f"{sid}: submitted {len(requests)} pages as {batch.id}")


def status() -> dict:
    load_env()
    client = anthropic.Anthropic()
    state = load_state()
    counts: dict[str, int] = {}
    for sid, rec in state.items():
        if rec["status"] == "collected":
            counts["collected"] = counts.get("collected", 0) + 1
            continue
        batch = client.messages.batches.retrieve(rec["batch_id"])
        rec["status"] = batch.processing_status
        counts[batch.processing_status] = counts.get(
            batch.processing_status, 0) + 1
        print(f"{sid}: {batch.processing_status} "
              f"(ok={batch.request_counts.succeeded}"
              f" err={batch.request_counts.errored})")
    save_state(state)
    print(counts)
    return counts


def collect() -> None:
    load_env()
    client = anthropic.Anthropic()
    state = load_state()
    price_in, price_out = PRICES.get(MODEL, (5.0, 25.0))
    for sid, rec in state.items():
        if rec["status"] == "collected":
            continue
        batch = client.messages.batches.retrieve(rec["batch_id"])
        if batch.processing_status != "ended":
            print(f"{sid}: still {batch.processing_status}, skipping")
            continue
        by_page: dict[int, list[dict]] = {}
        failed: list[str] = []
        cost = 0.0
        for result in client.messages.batches.results(rec["batch_id"]):
            page_n = int(result.custom_id.rsplit("--", 1)[1])
            if result.result.type != "succeeded":
                failed.append(result.custom_id)
                continue
            msg = result.result.message
            cost += (msg.usage.input_tokens * price_in / 1e6
                     + msg.usage.output_tokens * price_out / 1e6
                     ) * BATCH_DISCOUNT
            text = next((b.text for b in msg.content if b.type == "text"), "")
            try:
                items = parse_items(text)
            except (json.JSONDecodeError, KeyError):
                failed.append(result.custom_id)
                continue
            for item in items:
                item["source_id"] = sid
                item["source_page"] = page_n
                item["extractor_model"] = MODEL
            by_page[page_n] = items
        out_path = EXTRACTED_DIR / f"{sid}.jsonl"
        EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w") as out:
            for n in sorted(by_page):
                for item in by_page[n]:
                    out.write(json.dumps(item, ensure_ascii=False) + "\n")
        with open(USAGE_LOG, "a") as f:
            f.write(json.dumps({
                "model": MODEL, "context": f"batch_extract:{sid}",
                "cost_usd": round(cost, 6), "batch": True,
            }) + "\n")
        n_items = sum(len(v) for v in by_page.values())
        rec["status"] = "collected"
        rec["n_items"] = n_items
        rec["failed_pages"] = failed
        rec["cost_usd"] = round(cost, 4)
        save_state(state)
        print(f"{sid}: {n_items} items, {len(failed)} failed pages, "
              f"${cost:.2f}")
    total = sum(r.get("cost_usd", 0) for r in state.values())
    print(f"\nbatch extraction cost so far: ${total:.2f}")


def retry_failed() -> None:
    """Re-run failed pages via the direct API with schema-constrained output."""
    from concurrent.futures import ThreadPoolExecutor

    from azdim.extract import extract_page
    load_env()
    client = anthropic.Anthropic()
    sources = {s["source_id"]: s
               for s in json.loads(MANIFEST.read_text())["sources"]}
    state = load_state()
    jobs = []
    for sid, rec in state.items():
        for cid in rec.get("failed_pages", []):
            jobs.append((sid, int(cid.rsplit("--", 1)[1])))
    print(f"{len(jobs)} failed pages to retry")

    def one(job: tuple) -> tuple:
        sid, n = job
        pages = sorted((PAGES_DIR / sid).glob("page-*.png"), key=page_number)
        by_number = {page_number(p): p for p in pages}
        try:
            return sid, n, extract_page(client, sources[sid], by_number, n)
        except Exception as e:  # noqa: BLE001 — report, don't abort the rest
            print(f"  RETRY FAILED {sid} p{n}: {str(e)[:200]}")
            return sid, n, None

    results: dict[str, list] = {}
    with ThreadPoolExecutor(4) as pool:
        for sid, n, items in pool.map(one, jobs):
            if items is None:
                continue
            for item in items:
                item["source_id"] = sid
                item["source_page"] = n
                item["extractor_model"] = MODEL
            results.setdefault(sid, []).extend(items)
            print(f"  {sid} p{n}: {len(items)} items")

    for sid, new_items in results.items():
        path = EXTRACTED_DIR / f"{sid}.jsonl"
        existing = [json.loads(line)
                    for line in path.read_text().splitlines()]
        merged = sorted(existing + new_items,
                        key=lambda it: it["source_page"])
        with open(path, "w") as f:
            for item in merged:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        state[sid]["failed_pages"] = [
            cid for cid in state[sid]["failed_pages"]
            if int(cid.rsplit("--", 1)[1])
            not in {it["source_page"] for it in new_items}]
        state[sid]["n_items"] = len(merged)
    save_state(state)
    left = sum(len(r.get("failed_pages", [])) for r in state.values())
    print(f"retry done; {left} pages still failed")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "submit":
        ids = sys.argv[2:] or izah_source_ids()
        submit(ids)
    elif cmd == "status":
        status()
    elif cmd == "collect":
        collect()
    elif cmd == "retry":
        retry_failed()
    else:
        sys.exit("usage: batch_extract submit|status|collect|retry")
