"""Generate site/data.js from metrics, items, and the model registry.

Usage:
    uv run python -m azdim.site_data

Re-run whenever metrics_v0.json changes; the site is static otherwise.
"""

import json
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
METRICS = ROOT / "results" / "metrics_v0.json"
DIM_SCORES = ROOT / "results" / "dim_scores_v0.json"
ITEMS = ROOT / "data" / "items" / "items_v0.jsonl"
MODELS = ROOT / "manifest" / "models.json"
USAGE = ROOT / "manifest" / "api_usage.jsonl"
OUT = ROOT / "site" / "data.js"

DISPLAY = {
    "gpt-5.5": ("GPT-5.5", "OpenAI"),
    "gpt-5.4-mini": ("GPT-5.4 mini", "OpenAI"),
    "claude-opus-4-8": ("Claude Opus 4.8", "Anthropic"),
    "claude-sonnet-5": ("Claude Sonnet 5", "Anthropic"),
    "claude-haiku-4-5": ("Claude Haiku 4.5", "Anthropic"),
    "gemini-3.1-pro": ("Gemini 3.1 Pro", "Google"),
    "gemini-3.5-flash": ("Gemini 3.5 Flash", "Google"),
    "deepseek-v4-pro": ("DeepSeek v4 Pro", "DeepSeek"),
    "qwen3-max": ("Qwen3 Max", "Alibaba"),
    "qwen3-235b": ("Qwen3 235B-A22B", "Alibaba"),
    "llama-4-maverick": ("Llama 4 Maverick", "Meta"),
    "mistral-large-2512": ("Mistral Large 2512", "Mistral"),
    "gemma-4-31b": ("Gemma 4 31B", "Google"),
    "llama-3.1-8b": ("Llama 3.1 8B", "Meta"),
}
OPEN_TIERS = {"open_frontier", "open_large", "open_small", "open_tiny"}


def main() -> None:
    metrics = json.loads(METRICS.read_text())
    specs = json.loads(MODELS.read_text())
    items = [json.loads(line) for line in ITEMS.read_text().splitlines()]

    models: dict[str, dict] = {}
    for row in metrics:
        key = row["model_key"]
        name, org = DISPLAY.get(key, (key, "?"))
        m = models.setdefault(key, {
            "key": key, "name": name, "org": org,
            "open_weights": specs.get(key, {}).get("tier") in OPEN_TIERS,
            "tracks": {},
        })
        m["tracks"][row["track"]] = {
            "n": row["n"], "acc": row["accuracy"], "ci": row["ci95"],
            "invalid": row["invalid_rate"],
            "by_subject": row["acc_by_subject"],
            "by_year": row["acc_by_year"],
        }

    mcq = [it for it in items if it["question_type"] == "mcq"]
    spend = sum(json.loads(line)["cost_usd"]
                for line in USAGE.read_text().splitlines())
    data = {
        "generated": date.today().isoformat(),
        "spend_usd": round(spend, 2),
        "dataset": {
            "n_items": len(items),
            "n_mcq": len(mcq),
            "by_type": dict(Counter(it["question_type"] for it in items)),
            "by_language": dict(Counter(it["language"] for it in items)),
            "by_subject": dict(Counter(it["subject"]
                                       for it in items).most_common()),
            "by_year": dict(Counter(str(it["exam_date"])[:4]
                                    for it in items)),
            "n_sources": len({it["source_id"] for it in items}),
            "requires_image": sum(bool(it.get("requires_image"))
                                  for it in items),
        },
        "models": sorted(models.values(),
                         key=lambda m: -m["tracks"].get("A", {})
                         .get("acc", 0)),
        "dim_scores": [],
    }
    if DIM_SCORES.exists():
        for row in json.loads(DIM_SCORES.read_text()):
            name, org = DISPLAY.get(row["model_key"],
                                    (row["model_key"], "?"))
            data["dim_scores"].append({
                "key": row["model_key"], "name": name, "org": org,
                "s1": row["stage1_300"], "groups": row["groups"],
            })
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("window.AZDIM = "
                   + json.dumps(data, ensure_ascii=False, indent=1) + ";\n")
    print(f"{OUT} written: {len(models)} models, {len(items)} items, "
          f"${spend:.2f} spend")


if __name__ == "__main__":
    main()
