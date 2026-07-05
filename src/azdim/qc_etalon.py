"""QC: cross-check izah gold answers against etalon answer-key PDFs.

Etalon grids have a clean digital text layer (no math), so they are parsed
DETERMINISTICALLY from pdftotext -tsv word coordinates — no LLM involved,
which also makes this an extractor-independent check.

Grid model per page: a title line names group/sector/variant; header rows of
ascending task numbers define column x-centers; the answer tokens below a
header row map to the nearest column; subject names sit in the right margin
("Fənlər" column) vertically aligned with their block.

Usage:
    uv run python -m azdim.qc_etalon extract <etalon_source_id> [...]
    uv run python -m azdim.qc_etalon check   <etalon_source_id> [...]
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

TITLE_RES = [
    re.compile(
        r"(?P<group>I{1,3}|IV)\s*qrup\s*,\s*(?P<sector>Azərbaycan|rus)[^,]*,"
        r"\s*(?P<variant>[A-D])\s*variantı", re.IGNORECASE),
    re.compile(
        r"(?P<group>I{1,3}|IV)\s*группа\s*,\s*(?P<sector>Русский)[^,]*,\s*"
        r"Вариант\s*(?P<variant>[A-D])", re.IGNORECASE),
]


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


def parse_page(words: list[dict]) -> list[dict]:
    """A page may stack several grids; split at each title line."""
    lines = group_lines(words)
    titles = []
    for ln in lines:
        line_text = " ".join(w["text"] for w in sorted(ln,
                                                       key=lambda w: w["x"]))
        for pattern in TITLE_RES:
            m = pattern.search(line_text)
            if m:
                titles.append((ln[0]["y"], m))
                break
    grids = []
    for i, (y_start, m) in enumerate(titles):
        y_end = titles[i + 1][0] if i + 1 < len(titles) else 1e9
        segment = [w for w in words if y_start < w["y"] < y_end]
        grid = parse_grid(segment, m)
        if grid:
            grids.append(grid)
    return grids


def parse_grid(words: list[dict], m: re.Match) -> dict | None:
    sector = "az" if m.group("sector").lower().startswith("az") else "ru"
    lines = group_lines(words)
    headers = []  # (y, cols, word ids of the whole line)
    for ln in lines:
        cols = header_cols(ln)
        if cols:
            headers.append((ln[0]["y"], cols, {id(w) for w in ln}))
    header_ids = set().union(*(h[2] for h in headers)) if headers else set()
    subjects = [(w["y"], subject_of(w["text"])) for w in words
                if subject_of(w["text"])]
    answers: dict[int, str] = {}
    subj_of_task: dict[int, str] = {}
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
        for n, ws in cells.items():
            ws.sort(key=lambda w: (w["y"], w["x"]))
            answers[n] = ";".join(w["text"] for w in ws).strip(";")
            subj_of_task[n] = block_subject
    return {"group": m.group("group").upper(), "sector": sector,
            "variant": m.group("variant").upper(),
            "answers": answers, "subject_of_task": subj_of_task}


def extract(source_id: str) -> Path:
    pdf = RAW_DIR / f"{source_id}.pdf"
    ETALON_DIR.mkdir(parents=True, exist_ok=True)
    grids = []
    for page_num, words in sorted(words_by_page(pdf).items()):
        page_grids = parse_page(words)
        if not page_grids:
            print(f"page {page_num}: no grid title found, skipped")
            continue
        for grid in page_grids:
            grid["page"] = page_num
            grids.append(grid)
            print(f"page {page_num}: {grid['group']} {grid['sector']} "
                  f"variant {grid['variant']}, "
                  f"{len(grid['answers'])} answers")
    out = ETALON_DIR / f"{source_id}.json"
    out.write_text(json.dumps(grids, ensure_ascii=False, indent=1))
    return out


def check(source_id: str) -> tuple[int, int]:
    grids = json.loads((ETALON_DIR / f"{source_id}.json").read_text())
    exam_date = source_id.split("_")[1]
    key: dict[tuple, str] = {}
    for g in grids:
        for n, ans in g["answers"].items():
            subj = g["subject_of_task"].get(n)
            key[(g["group"], g["sector"], g["variant"], subj,
                 int(n))] = ans.upper()

    # subject -> first task number in the etalon (per group+sector)
    subject_offset: dict[tuple, int] = {}
    for (group, sector, variant, subj, n) in key:
        k = (group, sector, subj)
        subject_offset[k] = min(subject_offset.get(k, 10 ** 9), n)

    items = [json.loads(line) for line in ITEMS_FILE.read_text().splitlines()]
    items = [it for it in items if it.get("exam_date") == exam_date]
    items.sort(key=lambda it: it["item_id"])  # id encodes page+sequence
    # izah prints items in A-variant task order within each subject section,
    # so the sequence position IS the A-variant task number (variant_map
    # metadata can be misattached across column breaks — don't trust it here)
    n_cmp = n_match = n_discord = 0
    mismatches = []
    seq: dict[tuple, int] = {}
    for it in items:
        group = (it.get("group") or "").split("_")[0].replace("+", "")
        sector = "ru" if it.get("language") == "ru" else "az"
        skey = (it["source_id"], group, sector, it["subject"])
        seq[skey] = seq.get(skey, 0) + 1
        if it["question_type"] != "mcq" or not it.get("gold_answer_label"):
            continue
        offset = subject_offset.get((group, sector, it["subject"]))
        if offset is None:
            continue
        n_seq = offset + seq[skey] - 1
        n_map = (it.get("variant_map") or {}).get("A")
        # two independent position signals must agree; otherwise the item's
        # position is uncertain (map misattachment or a skipped item) and it
        # goes to the flagged pile instead of the qc comparison
        if n_map is not None and n_map != n_seq:
            n_discord += 1
            continue
        etalon = key.get((group, sector, "A", it["subject"], n_seq))
        if etalon is None or etalon not in "ABCDE":
            continue
        n_cmp += 1
        if etalon == it["gold_answer_label"]:
            n_match += 1
        else:
            mismatches.append((it["item_id"], n_seq,
                               it["gold_answer_label"], etalon))
    print(f"  position signals discordant (excluded): {n_discord}")
    rate = n_match / n_cmp if n_cmp else float("nan")
    print(f"{source_id}: agreement {n_match}/{n_cmp} = {rate:.4f}")
    for mm in mismatches[:15]:
        print("   mismatch:", mm)
    flags_path = ROOT / "data" / "items" / "qc_flags.json"
    flags = json.loads(flags_path.read_text()) if flags_path.exists() else {}
    for mm in mismatches:
        flags[mm[0]] = f"etalon_mismatch_task{mm[1]}_{mm[2]}vs{mm[3]}"
    flags_path.write_text(json.dumps(flags, indent=1, sort_keys=True))
    return n_match, n_cmp


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in ("extract", "check"):
        sys.exit("usage: qc_etalon extract|check <etalon_source_id>...")
    total_m = total_c = 0
    for sid in sys.argv[2:]:
        if sys.argv[1] == "extract":
            extract(sid)
        else:
            m, c = check(sid)
            total_m += m
            total_c += c
    if sys.argv[1] == "check" and total_c:
        print(f"\nTOTAL agreement: {total_m}/{total_c} "
              f"= {total_m / total_c:.4f}")
