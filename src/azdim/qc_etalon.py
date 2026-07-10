"""QC: cross-check izah gold answers against etalon answer-key PDFs.

Etalon grids have a clean digital text layer (no math), so they are parsed
DETERMINISTICALLY from pdftotext -tsv word coordinates — no LLM involved,
which also makes this an extractor-independent check.

Grid model per page: a title line names sector/variant (and group, for
entrance exams); header rows of ascending task numbers define column
x-centers; the answer tokens below a header row map to the nearest column;
subject names sit in the right margin ("Fənlər" column) vertically aligned
with their block.

Title forms handled:
  1. entrance, per-group:   "II qrup, Azərbaycan bölməsi, A variantı"
                            "II группа, Русский сектор, Вариант A"
  2. entrance, joint:       "... II və III qruplar (I cəhd) ..." on one
     line + "Azərbaycan bölməsi, A variantı" on the next (2026-05-24).
     One physical grid serves both groups; blocks are attributed per
     subject (math -> II, language/literature -> III, history/geography
     shared -> "II+III").
  3. school-leaving / mixed, flat (no group): "Azərbaycan bölməsi,
     A variantı" / "Русский сектор, Вариант A"; group recorded as "".

check() compares only items whose variant-A task number was CONFIRMED by
azdim.validate against the izah PDF's own metadata lines
(data/items/confirmed_numbers.json) — immune to sequence drift from
missing items. Unconfirmed items are already in the re-extraction queue.

Usage:
    uv run python -m azdim.qc_etalon extract all|<etalon_source_id> [...]
    uv run python -m azdim.qc_etalon check   all|<etalon_source_id> [...]
"""

import json
import re
import subprocess
import sys
from pathlib import Path

from azdim.align import subject_of

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw_pdfs"
ETALON_DIR = ROOT / "data" / "etalon"
ITEMS_FILE = ROOT / "data" / "items" / "items_v0.jsonl"
CONFIRMED = ROOT / "data" / "items" / "confirmed_numbers.json"
FLAGS = ROOT / "data" / "items" / "qc_flags.json"

TITLE_RES = [
    re.compile(
        r"(?P<group>I{1,3}|IV)\s*qrup\b\s*,\s*(?P<sector>Azərbaycan|rus)"
        r"[^,]*,\s*(?P<variant>[A-D])\s*variantı", re.IGNORECASE),
    re.compile(
        r"(?P<group>I{1,3}|IV)\s*группа\s*,\s*(?P<sector_ru>Русский)[^,]*,\s*"
        r"Вариант\s*(?P<variant_ru>[A-D])", re.IGNORECASE),
    # joint sitting: plural "II və III qruplar", sector/variant on next line
    re.compile(
        r"(?P<group>I{1,3}|IV)\s*və\s*(?:I{1,3}|IV)\s*qruplar\b.*?"
        r"(?:(?P<sector>Azərbaycan)\s*bölməsi|(?P<sector_ru>Русский)\s*сектор)"
        r"\s*,\s*(?:(?P<variant>[A-D])\s*variantı"
        r"|Вариант\s*(?P<variant_ru>[A-D]))",
        re.IGNORECASE | re.DOTALL),
    # school-leaving / mixed: flat title, no group token at all
    re.compile(
        r"(?P<sector>Azərbaycan)\s*bölməsi\s*,\s*(?P<variant>[A-D])\s*variantı",
        re.IGNORECASE),
    re.compile(
        r"(?P<sector_ru>Русский)\s*сектор\s*,\s*Вариант\s*(?P<variant_ru>[A-D])",
        re.IGNORECASE),
    # sector-less title used on sector-shared pages (2026 school-leaving
    # foreign-language sections): the ENTIRE line is just "A variantı";
    # anchored to avoid matching "... variantı" inside longer lines
    re.compile(r"^\s*(?P<variant>[A-D])\s*variantı\s*$", re.IGNORECASE),
    re.compile(r"^\s*Вариант\s*(?P<variant_ru>[A-D])\s*$", re.IGNORECASE),
]

# joint-sitting block attribution by subject; shared subjects stay "II+III"
GROUP_BY_SUBJECT = {
    "mathematics": "II",
    "literature": "III",
    "azerbaijani_language": "III",
    "russian_language": "III",
}


def words_by_page(pdf: Path) -> dict[int, list[dict]]:
    tsv = subprocess.run(["pdftotext", "-tsv", str(pdf), "-"],
                         capture_output=True, text=True, check=True).stdout
    pages: dict[int, list[dict]] = {}
    for line in tsv.splitlines()[1:]:
        parts = line.split("\t")
        if len(parts) != 12 or parts[0] != "5":
            continue
        w = {"page": int(parts[1]), "x": float(parts[6]),
             "y": float(parts[7]), "w": float(parts[8]),
             "h": float(parts[9]), "text": parts[11]}
        w["xc"] = w["x"] + w["w"] / 2
        pages.setdefault(w["page"], []).append(w)
    return pages


def group_lines(words: list[dict], tol: float = 4.0) -> list[list[dict]]:
    lines: list[list[dict]] = []
    for w in sorted(words, key=lambda w: (w["y"], w["x"])):
        if lines and abs(lines[-1][0]["y"] - w["y"]) < tol:
            lines[-1].append(w)
        else:
            lines.append([w])
    return lines


def header_cols(line: list[dict]) -> dict[int, float] | None:
    """Task-number columns if the line contains a run of >=4 consecutive
    ascending integers (subject labels etc. may share the line)."""
    ordered = sorted(line, key=lambda w: w["x"])
    ints = [(int(w["text"]), w["xc"]) for w in ordered
            if w["text"].isdigit()]
    best: list[tuple[int, float]] = []
    run: list[tuple[int, float]] = []
    for n, xc in ints:
        if run and n == run[-1][0] + 1:
            run.append((n, xc))
        else:
            run = [(n, xc)]
        if len(run) > len(best):
            best = run
    return dict(best) if len(best) >= 4 else None


JOINT_PATTERN = 2      # index in TITLE_RES of the two-line joint form


def _try_title(text: str) -> tuple[int, re.Match] | None:
    for idx, pattern in enumerate(TITLE_RES):
        m = pattern.search(text)
        if m:
            return idx, m
    return None


def parse_page(words: list[dict]) -> list[dict]:
    """A page may stack several grids; split at each title line. Joint
    sitting titles span two physical lines ("... II və III qruplar ..." /
    "Azərbaycan bölməsi, A variantı"), so merged line-pairs are tried too;
    a merged match is accepted only for the joint pattern, and its second
    line is consumed so the flat pattern doesn't re-match it."""
    lines = group_lines(words)
    texts = [" ".join(w["text"] for w in sorted(ln, key=lambda w: w["x"]))
             for ln in lines]
    titles = []
    consumed: set[int] = set()
    for i, ln in enumerate(lines):
        if i in consumed:
            continue
        hit = _try_title(texts[i])
        if not hit and i + 1 < len(lines):
            merged = _try_title(texts[i] + " " + texts[i + 1])
            if merged and merged[0] == JOINT_PATTERN:
                hit = merged
                consumed.add(i + 1)
        if hit:
            titles.append((ln[0]["y"], hit[1]))
    grids = []
    for i, (y_start, m) in enumerate(titles):
        y_end = titles[i + 1][0] if i + 1 < len(titles) else 1e9
        segment = [w for w in words if y_start < w["y"] < y_end]
        grid = parse_grid(segment, m)
        if grid:
            grids.append(grid)
    return grids


def _margin_subjects(words: list[dict], x_min: float) -> list[tuple[float, str]]:
    """Subject labels in the right margin. The column is narrow, so
    multi-word labels stack vertically ("Azərbaycan" / "dili") — try each
    line alone, then joined with the next line when they are close."""
    margin = [w for w in words if w["xc"] > x_min]
    lines = group_lines(margin)
    texts = [" ".join(w["text"] for w in sorted(ln, key=lambda w: w["x"]))
             for ln in lines]
    out, consumed = [], set()
    for i, ln in enumerate(lines):
        if i in consumed:
            continue
        slug = subject_of(texts[i])
        if not slug and i + 1 < len(lines) \
                and lines[i + 1][0]["y"] - ln[0]["y"] < 25:
            slug = subject_of(texts[i] + " " + texts[i + 1])
            if slug:
                consumed.add(i + 1)
        if slug:
            out.append((ln[0]["y"], slug))
    return out


def parse_grid(words: list[dict], m: re.Match) -> dict | None:
    gd = m.groupdict()
    if gd.get("sector"):
        sector = "az" if gd["sector"].lower().startswith("az") else "ru"
    elif gd.get("sector_ru"):
        sector = "ru"
    else:
        sector = "both"     # sector-less title on a sector-shared page
    variant = (gd.get("variant") or gd.get("variant_ru") or "").upper()
    group_raw = (gd.get("group") or "").upper()
    is_joint = bool(group_raw and re.search(r"\bvə\b", m.group(0),
                                            re.IGNORECASE))
    group_label = "II+III" if is_joint else group_raw   # "" for flat titles

    lines = group_lines(words)
    headers = []  # (y, cols, word ids of the whole line)
    for ln in lines:
        cols = header_cols(ln)
        if cols:
            headers.append((ln[0]["y"], cols, {id(w) for w in ln}))
    if not headers:
        return None
    header_ids = set().union(*(h[2] for h in headers))
    max_col_x = max(max(c.values()) for _, c, _ in headers)
    subjects = _margin_subjects(words, max_col_x + 20)
    answers: dict[int, str] = {}
    subj_of_task: dict[int, str] = {}
    group_of_task: dict[int, str] = {}
    for hi, (y0, cols, _) in enumerate(headers):
        y1 = headers[hi + 1][0] if hi + 1 < len(headers) else 1e9
        # tokens between this header row and the next
        zone = [w for w in words
                if y0 + 1 < w["y"] < y1 and w["xc"] < max(cols.values()) + 40
                and id(w) not in header_ids
                and not subject_of(w["text"])]
        spacing = min((b - a for a, b in zip(sorted(cols.values()),
                                             sorted(cols.values())[1:])),
                      default=30)
        cells: dict[int, list[dict]] = {}
        for w in zone:
            n, xc = min(cols.items(), key=lambda kv: abs(kv[1] - w["xc"]))
            if abs(xc - w["xc"]) <= spacing * 0.6:
                cells.setdefault(n, []).append(w)
        block_subject = None
        if subjects:
            yc = (y0 + min(y1, y0 + 200)) / 2
            block_subject = min(subjects, key=lambda s: abs(s[0] - yc))[1]
        resolved = (GROUP_BY_SUBJECT.get(block_subject, "II+III")
                    if is_joint else group_label)
        for n, ws in cells.items():
            ws.sort(key=lambda w: (w["y"], w["x"]))
            answers[n] = ";".join(w["text"] for w in ws).strip(";")
            subj_of_task[n] = block_subject
            group_of_task[n] = resolved
    return {"group": group_label, "sector": sector, "variant": variant,
            "answers": answers, "subject_of_task": subj_of_task,
            "group_of_task": group_of_task}


def etalon_ids(pattern: str) -> list[str]:
    if pattern != "all":
        return [pattern]
    return sorted(p.stem for p in RAW_DIR.glob("*_etalon.pdf"))


def extract(source_id: str) -> Path:
    pdf = RAW_DIR / f"{source_id}.pdf"
    ETALON_DIR.mkdir(parents=True, exist_ok=True)
    grids = []
    for page_num, words in sorted(words_by_page(pdf).items()):
        page_grids = parse_page(words)
        if not page_grids:
            print(f"  page {page_num}: no grid title found, skipped")
            continue
        for grid in page_grids:
            grid["page"] = page_num
            grids.append(grid)
    n_ans = sum(len(g["answers"]) for g in grids)
    subj = {}
    for g in grids:
        for s in g["subject_of_task"].values():
            subj[s] = subj.get(s, 0) + 1
    print(f"{source_id}: {len(grids)} grids, {n_ans} answers, "
          f"subjects={subj}")
    out = ETALON_DIR / f"{source_id}.json"
    out.write_text(json.dumps(grids, ensure_ascii=False, indent=1))
    return out


def _key_for(grids: list[dict]) -> dict[tuple, str]:
    key: dict[tuple, str] = {}
    ambiguous: set[tuple] = set()
    for g in grids:
        sectors = ["az", "ru"] if g["sector"] == "both" else [g["sector"]]
        for n, ans in g["answers"].items():
            grp = (g.get("group_of_task") or {}).get(n, g["group"])
            subj = g["subject_of_task"].get(n)
            for sector in sectors:
                k = (grp, sector, g["variant"], subj, int(n))
                if k in key and key[k] != ans.upper():
                    ambiguous.add(k)    # two grids claim this key differently
                key[k] = ans.upper()
    for k in ambiguous:
        del key[k]
    if ambiguous:
        print(f"  ({len(ambiguous)} ambiguous key entries dropped)")
    return key


def check(source_id: str) -> tuple[int, int]:
    """Compare gold answers of inventory-confirmed items against the key."""
    grids = json.loads((ETALON_DIR / f"{source_id}.json").read_text())
    key = _key_for(grids)
    exam_date = source_id.split("_")[1]
    confirmed = (json.loads(CONFIRMED.read_text())
                 if CONFIRMED.exists() else {})

    items = [json.loads(line) for line in ITEMS_FILE.read_text().splitlines()]
    items = [it for it in items if it.get("exam_date") == exam_date]
    n_cmp = n_match = n_unconfirmed = 0
    mismatches = []
    for it in items:
        if it["question_type"] != "mcq" or not it.get("gold_answer_label"):
            continue
        n_a = confirmed.get(it["item_id"])
        if n_a is None:
            n_unconfirmed += 1
            continue
        group = (it.get("group") or "").split("_")[0].replace("+", "")
        sector = "ru" if it.get("language") == "ru" else "az"
        etalon = None
        for grp_try in (group, "II+III", ""):
            etalon = key.get((grp_try, sector, "A", it["subject"], n_a))
            if etalon is not None:
                break
        if etalon is None or etalon not in "ABCDE":
            continue           # no key entry / voided (*) / coded-open
        n_cmp += 1
        if etalon == it["gold_answer_label"]:
            n_match += 1
        else:
            mismatches.append((it["item_id"], n_a,
                               it["gold_answer_label"], etalon))
    rate = n_match / n_cmp if n_cmp else float("nan")
    print(f"{source_id}: agreement {n_match}/{n_cmp} = {rate:.4f} "
          f"(unconfirmed skipped: {n_unconfirmed})")
    for mm in mismatches[:15]:
        print("   mismatch:", mm)
    flags = json.loads(FLAGS.read_text()) if FLAGS.exists() else {}
    for mm in mismatches:
        flags[mm[0]] = f"etalon_mismatch_task{mm[1]}_{mm[2]}vs{mm[3]}"
    FLAGS.write_text(json.dumps(flags, indent=1, sort_keys=True))
    return n_match, n_cmp


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in ("extract", "check"):
        sys.exit("usage: qc_etalon extract|check all|<etalon_source_id>...")
    ids = []
    for arg in sys.argv[2:]:
        ids.extend(etalon_ids(arg))
    total_m = total_c = 0
    for sid in ids:
        if sys.argv[1] == "extract":
            extract(sid)
        else:
            m, c = check(sid)
            total_m += m
            total_c += c
    if sys.argv[1] == "check" and total_c:
        print(f"\nTOTAL agreement: {total_m}/{total_c} "
              f"= {total_m / total_c:.4f}")
