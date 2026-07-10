"""Completeness + correctness validator for the extracted dataset.

The ground truth is the izah PDF itself: DİM prints an
"A variantı N saylı test tapşırığı" metadata line for every item, so the
PDF text layer is a complete, deterministic inventory of what must have
been captured. We reconcile that inventory against the extracted items,
then run correctness checks that need no LLM.

Checks
  1. completeness  — every (page, variant-A number) in the PDF has a
                     captured item; missing ones are listed page-by-page
  2. gold          — gold_answer_label must point at the choice whose text
                     equals gold_answer_text (self-consistency)
  3. missing gold  — MCQ with no gold label at all
  4. fidelity      — each item's question stem is locatable word-for-word
                     in the PDF text layer (math-heavy stems may not be;
                     reported as unlocated, not as errors)
  5. etalon        — summary of answer-key cross-check flags

Usage
    uv run python -m azdim.validate            # full report
    uv run python -m azdim.validate --fast     # skip the fidelity pass

Outputs
    data/items/validation_report.json   full machine-readable detail
    data/items/reextract_targets.json   {source_id: [pages needing re-extraction]}
    data/items/coverage.html            visual bubble-grid coverage report
"""

import json
import re
import subprocess
import sys
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path

from azdim.boxes import _norm, item_box

ROOT = Path(__file__).resolve().parents[2]
ITEMS_FILE = ROOT / "data" / "items" / "items_v0.jsonl"
RAW_PDFS = ROOT / "data" / "raw_pdfs"
QC_FLAGS = ROOT / "data" / "items" / "qc_flags.json"
REPORT = ROOT / "data" / "items" / "validation_report.json"
TARGETS = ROOT / "data" / "items" / "reextract_targets.json"
COVERAGE = ROOT / "data" / "items" / "coverage.html"

VARIANT_A_RE = re.compile(r"A\s+variant[ıi]\s+(\d+)\s+sayl[ıi]", re.IGNORECASE)
PAGE_TOL = 3          # item start page vs metadata-line page tolerance
GOLD_SIM = 0.85       # similarity threshold for gold label<->text agreement


# ---------------------------------------------------------------- inventory

def pdf_inventory(source_id: str) -> list[tuple[int, int]]:
    """All (page, variant_A_number) metadata lines in the izah text layer."""
    pdf = RAW_PDFS / f"{source_id}.pdf"
    text = subprocess.run(["pdftotext", str(pdf), "-"],
                          capture_output=True, text=True).stdout
    out = []
    for pageno, page_text in enumerate(text.split("\f"), start=1):
        for m in VARIANT_A_RE.finditer(page_text):
            out.append((pageno, int(m.group(1))))
    return out


def check_completeness(items: list[dict], source_id: str) -> dict:
    expected = pdf_inventory(source_id)
    captured = [it for it in items if it["source_id"] == source_id]
    numbered = [(it["source_page"], (it.get("variant_map") or {}).get("A"), it)
                for it in captured]
    numbered = [(p, n, it) for p, n, it in numbered if isinstance(n, int)]
    unnumbered = len(captured) - len(numbered)

    used = [False] * len(numbered)
    missing = []
    for page, num in sorted(expected):
        best, best_d = None, None
        for i, (ip, inum, _) in enumerate(numbered):
            if used[i] or inum != num:
                continue
            d = abs(ip - page)
            if d <= PAGE_TOL and (best_d is None or d < best_d):
                best, best_d = i, d
        if best is None:
            missing.append({"page": page, "variant_a_number": num})
        else:
            used[best] = True
    extra = sum(1 for u in used if not u)
    return {
        "expected": len(expected),
        "captured": len(captured),
        "matched": len(expected) - len(missing),
        "missing": missing,
        "extra_numbered": extra,      # captured but not tied to a metadata line
        "unnumbered": unnumbered,     # captured without a variant-A number
    }


# --------------------------------------------------------------- gold checks

def check_gold(items: list[dict]) -> dict:
    inconsistent, missing = [], []
    for it in items:
        if it["question_type"] != "mcq":
            continue
        label = it.get("gold_answer_label")
        if not label:
            missing.append(it["item_id"])
            continue
        choices = it.get("choices") or {}
        gold_text = it.get("gold_answer_text") or ""
        choice_text = choices.get(label) or ""
        if not gold_text or not choice_text:
            continue
        sim = SequenceMatcher(None, _norm(choice_text).split(),
                              _norm(gold_text).split()).ratio()
        if sim < GOLD_SIM:
            inconsistent.append({
                "item_id": it["item_id"], "label": label, "similarity": round(sim, 2),
                "choice_text": choice_text[:80], "gold_text": gold_text[:80],
            })
    return {"label_text_mismatch": inconsistent, "no_gold_label": missing}


# ----------------------------------------------------------------- fidelity

def check_fidelity(items: list[dict], source_id: str) -> dict:
    pdf = str(RAW_PDFS / f"{source_id}.pdf")
    located, unlocated = 0, []
    for it in items:
        if it["source_id"] != source_id:
            continue
        box = item_box(pdf, it["source_page"], it.get("question_text") or "")
        if box:
            located += 1
        else:
            unlocated.append(it["item_id"])
    return {"located": located, "unlocated": unlocated}


# ----------------------------------------------------------------- coverage html

def write_coverage_html(per_source: dict) -> None:
    rows = []
    for src, comp in sorted(per_source.items()):
        miss_pages = defaultdict(list)
        for m in comp["missing"]:
            miss_pages[m["page"]].append(m["variant_a_number"])
        pct = 100.0 * comp["matched"] / comp["expected"] if comp["expected"] else 0
        color = "#2e6e4e" if pct >= 99.5 else ("#b5892c" if pct >= 90 else "#b31b34")
        chips = "".join(
            f'<span class="pg">p{p}<b>{" ".join(str(n) for n in sorted(ns))}</b></span>'
            for p, ns in sorted(miss_pages.items()))
        rows.append(
            f'<tr><td class="src">{src}</td>'
            f'<td class="num" style="color:{color}">{comp["matched"]}/{comp["expected"]}'
            f' <small>({pct:.1f}%)</small></td>'
            f'<td>{chips or "<i>complete</i>"}</td></tr>')
    total_exp = sum(c["expected"] for c in per_source.values())
    total_match = sum(c["matched"] for c in per_source.values())
    html = f"""<!doctype html><meta charset="utf-8"><title>AzDIM coverage</title>
<style>
body{{font-family:ui-monospace,monospace;background:#f7f5f0;color:#191713;
     max-width:1080px;margin:40px auto;padding:0 20px;font-size:14px}}
h1{{font-size:18px}} .tot{{font-size:15px;margin-bottom:18px}}
table{{border-collapse:collapse;width:100%}}
td{{border-top:1px solid #d8d3c8;padding:8px 10px;vertical-align:top}}
.src{{white-space:nowrap}} .num{{white-space:nowrap;font-weight:600}}
.pg{{display:inline-block;margin:2px 6px 2px 0;padding:2px 7px;
    background:#efece4;border-radius:4px}}
.pg b{{color:#b31b34;margin-left:5px}}
i{{color:#2e6e4e;font-style:normal}}
</style>
<h1>AzDIM-Bench — capture coverage vs PDF inventory</h1>
<div class="tot">TOTAL: <b>{total_match}/{total_exp}</b>
 ({100.0 * total_match / total_exp:.1f}%) items matched to the PDFs' own
 "A variantı N saylı" metadata lines. Red chips = page &amp; variant-A numbers
 of items not yet captured.</div>
<table>{"".join(rows)}</table>"""
    COVERAGE.write_text(html)


# --------------------------------------------------------------------- main

def main() -> None:
    fast = "--fast" in sys.argv
    items = [json.loads(line) for line in ITEMS_FILE.read_text().splitlines()]
    sources = sorted({it["source_id"] for it in items})

    per_source, fidelity = {}, {}
    for src in sources:
        per_source[src] = check_completeness(items, src)
        if not fast:
            fidelity[src] = check_fidelity(items, src)

    gold = check_gold(items)
    qc = json.loads(QC_FLAGS.read_text()) if QC_FLAGS.exists() else {}

    # -------- console summary
    print(f"{'source':38s} {'captured':>9} {'expected':>9} {'missing':>8} "
          f"{'located':>8}")
    for src in sources:
        c = per_source[src]
        loc = (f"{fidelity[src]['located']}/{c['captured']}"
               if not fast else "-")
        print(f"{src:38s} {c['captured']:>9} {c['expected']:>9} "
              f"{len(c['missing']):>8} {loc:>8}")
    total_exp = sum(c["expected"] for c in per_source.values())
    total_miss = sum(len(c["missing"]) for c in per_source.values())
    print(f"\nCOMPLETENESS: {total_exp - total_miss}/{total_exp} "
          f"({100.0 * (total_exp - total_miss) / total_exp:.1f}%) — "
          f"{total_miss} items in the PDFs are not yet captured")
    print(f"GOLD: {len(gold['label_text_mismatch'])} label/text mismatches, "
          f"{len(gold['no_gold_label'])} MCQ without gold label")
    print(f"ETALON: {len(qc)} answer-key mismatch flags pending review")

    # -------- artifacts
    report = {"per_source": per_source, "gold": gold,
              "etalon_flags": len(qc),
              "fidelity": {s: {"located": f["located"],
                               "n_unlocated": len(f["unlocated"]),
                               "unlocated": f["unlocated"]}
                           for s, f in fidelity.items()} if not fast else None}
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=1))
    targets = {s: sorted({m["page"] for m in c["missing"]})
               for s, c in per_source.items() if c["missing"]}
    TARGETS.write_text(json.dumps(targets, indent=1))
    write_coverage_html(per_source)
    print(f"\nwrote {REPORT.relative_to(ROOT)}, {TARGETS.relative_to(ROOT)}, "
          f"{COVERAGE.relative_to(ROOT)}")
    print(f"open the visual report:  open {COVERAGE}")


if __name__ == "__main__":
    main()
