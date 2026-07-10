"""Deterministic gold-answer repair with a full audit trail.

Two machine signals, no LLM:
  * text-match — the choice whose text matches gold_answer_text
    (unique winner, similarity >= 0.90, margin >= 0.10 over runner-up)
  * etalon — DİM's own published answer key, looked up via the
    geometry-confirmed variant-A task number (azdim.validate)

Repairs applied automatically:
  1. MCQ with NO gold label: label filled from etalon (or from text-match
     when the etalon is unavailable and the match is unambiguous).
  2. MCQ whose label CONTRADICTS its own gold text: re-pointed to the
     text-match winner, unless the etalon explicitly disagrees with the
     winner (then it is left alone and flagged for human review).

Every change is recorded on the item ("gold_repair": {from, to, method})
and in data/items/gold_repairs.json. Conflicts that cannot be resolved
deterministically are added to qc_flags.json for the human queue.

Usage:
    uv run python -m azdim.repair_gold          # apply
    uv run python -m azdim.repair_gold --dry    # report only
"""

import json
import sys
from difflib import SequenceMatcher
from pathlib import Path

from azdim.boxes import _norm
from azdim.qc_etalon import _key_for

ROOT = Path(__file__).resolve().parents[2]
ITEMS_FILE = ROOT / "data" / "items" / "items_v0.jsonl"
ETALON_DIR = ROOT / "data" / "etalon"
CONFIRMED = ROOT / "data" / "items" / "confirmed_numbers.json"
FLAGS = ROOT / "data" / "items" / "qc_flags.json"
AUDIT = ROOT / "data" / "items" / "gold_repairs.json"

SIM_OK = 0.85       # below this, label and gold text disagree
SIM_WIN = 0.90      # a text-match winner must be at least this similar
MARGIN = 0.10       # ... and beat the runner-up by at least this


def _sim(a: str, b: str) -> float:
    return SequenceMatcher(None, _norm(a).split(), _norm(b).split()).ratio()


def _etalon_keys() -> dict[str, dict]:
    """exam-date-prefixed etalon lookup: '<kind>_<date>' -> key dict."""
    out = {}
    for path in ETALON_DIR.glob("*_etalon.json"):
        grids = json.loads(path.read_text())
        if grids:
            out[path.stem.replace("_etalon", "")] = _key_for(grids)
    return out


def _etalon_id(source_id: str) -> str:
    # ue2_2026-06-07_g1_izah -> ue2_2026-06-07 ; sl11_..._izah -> sl11_...
    parts = source_id.split("_")
    return "_".join(parts[:2])


def etalon_answer(item: dict, n_a: int | None,
                  keys: dict[str, dict]) -> str | None:
    if n_a is None:
        return None
    key = keys.get(_etalon_id(item["source_id"]))
    if not key:
        return None
    group = (item.get("group") or "").split("_")[0].replace("+", "")
    sector = "ru" if item.get("language") == "ru" else "az"
    for grp_try in (group, "II+III", ""):
        ans = key.get((grp_try, sector, "A", item["subject"], n_a))
        if ans is not None:
            return ans if ans in "ABCDE" else None
    return None


def text_match(item: dict) -> str | None:
    gold_text = item.get("gold_answer_text") or ""
    choices = item.get("choices") or {}
    if not gold_text or not choices:
        return None
    scored = sorted(((label, _sim(text or "", gold_text))
                     for label, text in choices.items()),
                    key=lambda kv: -kv[1])
    if scored and scored[0][1] >= SIM_WIN and \
            (len(scored) == 1 or scored[0][1] - scored[1][1] >= MARGIN):
        return scored[0][0]
    return None


def main() -> None:
    dry = "--dry" in sys.argv
    items = [json.loads(line) for line in ITEMS_FILE.read_text().splitlines()]
    confirmed = json.loads(CONFIRMED.read_text())
    keys = _etalon_keys()
    flags = json.loads(FLAGS.read_text()) if FLAGS.exists() else {}
    repairs, conflicts = [], []

    for it in items:
        if it["question_type"] != "mcq" or not it.get("choices"):
            continue
        label = it.get("gold_answer_label")
        et = etalon_answer(it, confirmed.get(it["item_id"]), keys)
        tm = text_match(it)

        if not label:                                   # case 1: missing gold
            new, method = None, ""
            if et and (tm is None or tm == et):
                new, method = et, "etalon"
            elif et is None and tm:
                new, method = tm, "text_match"
            elif et and tm and et != tm:
                conflicts.append((it["item_id"], f"fill_conflict_{tm}vs{et}"))
                continue
            if new:
                repairs.append((it, None, new, method))
            continue

        choice_text = (it["choices"] or {}).get(label) or ""
        gold_text = it.get("gold_answer_text") or ""
        if not gold_text or not choice_text:
            continue
        if _sim(choice_text, gold_text) >= SIM_OK:
            continue                                    # self-consistent
        # case 2: label contradicts its own answer text
        if tm and (et is None or et == tm):
            method = "text_match+etalon" if et else "text_match"
            repairs.append((it, label, tm, method))
        else:
            conflicts.append((it["item_id"],
                              f"gold_text_mismatch_label{label}"
                              + (f"_etalon{et}" if et else "")))

    print(f"repairs: {len(repairs)}, unresolved conflicts: {len(conflicts)}")
    for it, old, new, method in repairs[:12]:
        print(f"  {it['item_id']}: {old} -> {new}  [{method}]")
    if dry:
        return

    for it, old, new, method in repairs:
        it["gold_answer_label"] = new
        it["gold_repair"] = {"from": old, "to": new, "method": method}
    for iid, reason in conflicts:
        flags[iid] = reason
    with open(ITEMS_FILE, "w") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    FLAGS.write_text(json.dumps(flags, indent=1, sort_keys=True))
    AUDIT.write_text(json.dumps(
        [{"item_id": it["item_id"], "from": old, "to": new, "method": m}
         for it, old, new, m in repairs], ensure_ascii=False, indent=1))
    print(f"applied; audit -> {AUDIT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
