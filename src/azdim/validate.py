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

from azdim.boxes import _match, _norm, _page_words, item_box

ROOT = Path(__file__).resolve().parents[2]
ITEMS_FILE = ROOT / "data" / "items" / "items_v0.jsonl"
RAW_PDFS = ROOT / "data" / "raw_pdfs"
QC_FLAGS = ROOT / "data" / "items" / "qc_flags.json"
REPORT = ROOT / "data" / "items" / "validation_report.json"
TARGETS = ROOT / "data" / "items" / "reextract_targets.json"
COVERAGE = ROOT / "data" / "items" / "coverage.html"
CONFIRMED = ROOT / "data" / "items" / "confirmed_numbers.json"

VARIANT_A_RE = re.compile(r"A\s+variant[ıi]\s+(\d+)\s+sayl[ıi]", re.IGNORECASE)
PAGE_TOL = 3          # item start page vs metadata-line page tolerance
GOLD_SIM = 0.85       # similarity threshold for gold label<->text agreement


# ---------------------------------------------------------------- inventory

def pdf_inventory(source_id: str) -> list[tuple[int, int, float, float]]:
    """All "A variantı N saylı" metadata lines in the izah text layer,
    WITH coordinates: (page, number, x, y)."""
    pdf = str(RAW_PDFS / f"{source_id}.pdf")
    n_pages = int(subprocess.run(
        ["pdfinfo", pdf], capture_output=True, text=True)
        .stdout.split("Pages:")[1].split()[0])
    out = []
    for page in range(1, n_pages + 1):
        words, pw, ph = _page_words(pdf, page)
        for i in range(len(words) - 3):
            if (words[i][0] == "a"
                    and words[i + 1][0].startswith("variant")
                    and words[i + 2][0].isdigit()
                    and words[i + 3][0].startswith("sayl")):
                out.append((page, int(words[i + 2][0]),
                            words[i][1], words[i][2]))
    return out


def check_completeness(items: list[dict], source_id: str) -> dict:
    """Reconcile captured items against the PDF's own metadata lines.

    Binding is GEOMETRIC and does not trust the LLM's variant_map: a
    metadata line belongs to the item whose question stem sits nearest
    ABOVE it in the same column (stems located via the text layer).
    The LLM variant_map is only a fallback for items whose stem could
    not be located (math-heavy), and any geometric/variant_map
    disagreement is flagged.
    """
    pdf = str(RAW_PDFS / f"{source_id}.pdf")
    expected = pdf_inventory(source_id)
    captured = [it for it in items if it["source_id"] == source_id]

    # locate each item's stem on its page (absolute coordinates)
    anchors = []       # (page, x_center, y_top, item)
    unlocated = []
    for it in captured:
        page = it["source_page"]
        box = item_box(pdf, page, it.get("question_text") or "")
        if box:
            _, pw, ph = _page_words(pdf, page)
            x, y, w, h = box
            anchors.append((page, (x + w / 2) * pw, y * ph, it))
        else:
            unlocated.append(it)

    def col(x: float, pw: float) -> int:
        return 0 if x < pw * 0.5 else 1

    # geometric binding: the metadata block is the item's HEADER, so a
    # line belongs to the nearest located stem BELOW it in the same column
    confirmed: dict[str, int] = {}
    vm_conflicts: list[str] = []
    bound_lines: set[int] = set()
    best_bind: dict[str, tuple[float, int, int]] = {}  # iid -> (gap, li, num)
    for li, (page, num, mx, my) in enumerate(expected):
        _, pw, ph = _page_words(pdf, page)
        cands = [(y, it) for (p, x, y, it) in anchors
                 if p == page and col(x, pw) == col(mx, pw) and y >= my - 4]
        if not cands:
            continue
        y_best, it = min(cands, key=lambda c: c[0])
        iid = it["item_id"]
        gap = y_best - my
        if iid not in best_bind or gap < best_bind[iid][0]:
            best_bind[iid] = (gap, li, num)
    for iid, (gap, li, num) in best_bind.items():
        confirmed[iid] = num
        bound_lines.add(li)
        it = next(a[3] for a in anchors if a[3]["item_id"] == iid)
        vm_a = (it.get("variant_map") or {}).get("A")
        if isinstance(vm_a, int) and vm_a != num:
            vm_conflicts.append(iid)

    # fallback for unbound lines: variant_map match among unlocated items
    used = set()
    missing = []
    for li, (page, num, mx, my) in enumerate(expected):
        if li in bound_lines:
            continue
        best, best_d = None, None
        for it in unlocated:
            if id(it) in used:
                continue
            if (it.get("variant_map") or {}).get("A") != num:
                continue
            d = abs(it["source_page"] - page)
            if d <= PAGE_TOL and (best_d is None or d < best_d):
                best, best_d = it, d
        if best is None:
            missing.append({"page": page, "variant_a_number": num})
        else:
            used.add(id(best))
            confirmed.setdefault(best["item_id"], num)
    return {
        "expected": len(expected),
        "captured": len(captured),
        "matched": len(expected) - len(missing),
        "missing": missing,
        "n_unlocated_stems": len(unlocated),
        "vm_conflicts": vm_conflicts,   # variant_map disagrees with geometry
        "confirmed": confirmed,
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
    all_confirmed = {}
    for c in per_source.values():
        all_confirmed.update(c.pop("confirmed"))
    CONFIRMED.write_text(json.dumps(all_confirmed, indent=0, sort_keys=True))
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
