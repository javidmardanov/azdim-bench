"""Aggregate raw eval outputs into metric tables.

Usage:
    uv run python -m azdim.eval.metrics

Reads results/raw/*.jsonl, joins with canonical items, writes
results/metrics_v0.json and prints a leaderboard.
"""

import json
import random
from collections import defaultdict
from pathlib import Path

from azdim.eval.parse import parse_answer

ROOT = Path(__file__).resolve().parents[2].parent
ITEMS_FILE = ROOT / "data" / "items" / "items_v0.jsonl"
RAW_DIR = ROOT / "results" / "raw"
OUT = ROOT / "results" / "metrics_v0.json"


def bootstrap_ci(flags: list[bool], n: int = 2000,
                 seed: int = 0) -> tuple[float, float]:
    if not flags:
        return (0.0, 0.0)
    rng = random.Random(seed)
    means = sorted(
        sum(rng.choices(flags, k=len(flags))) / len(flags)
        for _ in range(n))
    return (means[int(0.025 * n)], means[int(0.975 * n)])


def main() -> None:
    items = {json.loads(line)["item_id"]: json.loads(line)
             for line in ITEMS_FILE.read_text().splitlines()}
    rows = []
    for path in sorted(RAW_DIR.glob("*.jsonl")):
        recs = [json.loads(line) for line in path.read_text().splitlines()
                if line]
        recs = [r for r in recs if "error" not in r and r["item_id"] in items]
        if not recs:
            continue
        for r in recs:  # re-parse so parser fixes apply retroactively
            r["parsed"] = parse_answer(r.get("raw", ""))
            r["correct"] = r["parsed"] == r["gold"]
        model_key = recs[0]["model_key"]
        track = recs[0]["track"]
        flags = [bool(r["correct"]) for r in recs]
        acc = sum(flags) / len(flags)
        lo, hi = bootstrap_ci(flags)
        by_subject = defaultdict(list)
        by_year = defaultdict(list)
        for r in recs:
            it = items[r["item_id"]]
            by_subject[str(it["subject"])].append(bool(r["correct"]))
            by_year[str(it["exam_date"])[:4]].append(bool(r["correct"]))
        rows.append({
            "model_key": model_key,
            "track": track,
            "n": len(recs),
            "accuracy": round(acc, 4),
            "ci95": [round(lo, 4), round(hi, 4)],
            "invalid_rate": round(
                sum(r["parsed"] is None for r in recs) / len(recs), 4),
            "acc_by_subject": {k: round(sum(v) / len(v), 4)
                               for k, v in sorted(by_subject.items())},
            "acc_by_year": {k: round(sum(v) / len(v), 4)
                            for k, v in sorted(by_year.items())},
        })
    OUT.write_text(json.dumps(rows, indent=2))
    rows.sort(key=lambda r: (-r["accuracy"]))
    print(f"{'model':<28}{'track':<7}{'n':>5}{'acc':>8}{'95% CI':>18}"
          f"{'invalid':>9}")
    for r in rows:
        print(f"{r['model_key']:<28}{r['track']:<7}{r['n']:>5}"
              f"{r['accuracy']:>8.3f}"
              f"{str(r['ci95']):>18}{r['invalid_rate']:>9.3f}")
    print(f"\n-> {OUT}")


if __name__ == "__main__":
    main()
