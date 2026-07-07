"""Simulate DİM 700-point admission scores from model eval results.

Formulas from DİM's official "Balların hesablanma qaydası (I-IV ixtisas
qrupları üzrə)" (dim.gov.az/storage/iblock/aef/aef09c85301866f15711ed07abc00518.pdf):

Stage 2, per subject (22 closed + 5 coded-open + 3 written tasks):
    NB_q = max(0, (D_q - Y_q/4)) * 100/33      # closed, negative marking
    NB_a = (D_kod + 2*D_yazili) * 100/33       # open, no penalty
    NB   = NB_q + NB_a                          # max 100
    total = 1.5*NB_1 + 1.5*NB_2 + 1.0*NB_3      # max 400

Stage 1 (buraxılış, no negative marking), per subject max 100, total 300:
    az/ru language: (5/2)  * (2*n_yazili + n_qapali)         # 20 closed, 10 written
    foreign lang:   (100/37)* (2*n_yazili + n_qapali)        # 23 closed, 7 written
    mathematics:    (25/8) * (2*n_yazili + n_kod + n_qapali) # 13 closed, 5 coded, 7 written

We measured closed-MCQ performance only, so per model we report:
    central  — open tasks answered at the model's closed-task rate (stated
               extrapolation; written tasks all-or-nothing at that rate)
    floor    — every open task scored 0

Usage:
    uv run python -m azdim.dim_score
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ITEMS = ROOT / "data" / "items" / "items_v0.jsonl"
RAW = ROOT / "results" / "raw"
OUT = ROOT / "results" / "dim_scores_v0.json"

GROUPS = {
    "I (RK)": [("mathematics", 1.5), ("physics", 1.5), ("chemistry", 1.0)],
    "I (Rİ)": [("mathematics", 1.5), ("physics", 1.5), ("informatics", 1.0)],
    "II": [("mathematics", 1.5), ("geography", 1.5), ("history", 1.0)],
    "III (DT)": [("azerbaijani_language", 1.5), ("history", 1.5),
                 ("literature", 1.0)],
    "IV": [("biology", 1.5), ("chemistry", 1.5), ("physics", 1.0)],
}

# stage-1 subject -> (closed, coded, written) task counts
STAGE1 = {
    "azerbaijani_language": (20, 0, 10),
    "foreign_language": (23, 0, 7),  # pooled en/de/fr items
    "mathematics": (13, 5, 7),
}
FOREIGN = ("english", "german", "french")


def subject_rates() -> dict:
    """(model_key, exam_kind, subject) -> (p_correct, p_wrong, n).
    exam_kind: 'ue2' (stage 2) or 'sl11' (stage 1). Track A only."""
    items = {json.loads(line)["item_id"]: json.loads(line)
             for line in ITEMS.read_text().splitlines()}
    rates: dict = {}
    by_model: dict = {}
    for path in sorted(RAW.glob("*__[AF].jsonl")):
        recs = [json.loads(line) for line in path.read_text().splitlines()]
        recs = [r for r in recs if "error" not in r and r["item_id"] in items]
        if recs:
            by_model.setdefault(recs[0]["model_key"], []).extend(recs)
    for model_key, recs in by_model.items():
        buckets: dict = {}
        for r in recs:
            it = items[r["item_id"]]
            kind = ("ue2" if it["exam_type"] == "university_entrance_stage2"
                    else "sl11" if it["exam_type"] == "school_leaving_11yr"
                    else None)
            if kind is None:
                continue
            buckets.setdefault((kind, it["subject"]), []).append(r)
        for subj in FOREIGN:  # pool foreign languages for stage 1
            rs = buckets.get(("sl11", subj))
            if rs:
                buckets.setdefault(("sl11", "foreign_language"),
                                   []).extend(rs)
        for (kind, subj), rs in buckets.items():
            n = len(rs)
            p_c = sum(r["correct"] for r in rs) / n
            p_w = sum(r["parsed"] is not None and not r["correct"]
                      for r in rs) / n
            rates[(model_key, kind, subj)] = (p_c, p_w, n)
    return rates


def stage2_subject(p_c: float, p_w: float, central: bool) -> float:
    nb_q = max(0.0, (22 * p_c - 22 * p_w / 4)) * 100 / 33
    nb_a = (5 * p_c + 2 * 3 * p_c) * 100 / 33 if central else 0.0
    return min(100.0, nb_q + nb_a)


def stage1_subject(counts: tuple, p_c: float, central: bool) -> float:
    closed, coded, written = counts
    total_max = 2 * written + coded + closed
    raw = closed * p_c + (coded * p_c + 2 * written * p_c if central else 0)
    return min(100.0, raw * 100 / total_max)


def main() -> None:
    rates = subject_rates()
    models = sorted({k[0] for k in rates})
    results = []
    for m in models:
        def rate(kind, subj):
            return rates.get((m, kind, subj))

        # stage 1: az language + foreign (english) + mathematics from sl11
        s1 = {}
        for variant in ("central", "floor"):
            tot, ok = 0.0, True
            for subj, counts in STAGE1.items():
                r = rate("sl11", subj)
                if r is None or r[2] < 10:
                    ok = False
                    break
                tot += stage1_subject(counts, r[0], variant == "central")
            s1[variant] = round(tot, 1) if ok else None

        groups_out = {}
        for gname, triad in GROUPS.items():
            g = {}
            for variant in ("central", "floor"):
                tot, min_n, ok = 0.0, 10 ** 9, True
                for subj, weight in triad:
                    r = rate("ue2", subj)
                    if r is None or r[2] < 10:
                        ok = False
                        break
                    tot += weight * stage2_subject(r[0], r[1],
                                                   variant == "central")
                    min_n = min(min_n, r[2])
                if not ok:
                    g = None
                    break
                g[variant] = round(tot, 1)
                g["min_n"] = min_n
            if g:
                s1c, s1f = s1["central"], s1["floor"]
                g["total700_central"] = (round(g["central"] + s1c, 1)
                                         if s1c is not None else None)
                g["total700_floor"] = (round(g["floor"] + s1f, 1)
                                       if s1f is not None else None)
            groups_out[gname] = g
        results.append({"model_key": m, "stage1_300": s1,
                        "groups": groups_out})

    OUT.write_text(json.dumps(results, indent=1))
    # print a compact table: central 700-totals per group
    gnames = list(GROUPS)
    print(f"{'model':<22}{'S1/300':>8}" + "".join(f"{g:>11}" for g in gnames)
          + "   (700-total, central | floor)")
    def sort_key(r):
        g = r["groups"].get("I (RK)") or {}
        return -(g.get("total700_central") or 0)

    for r in sorted(results, key=sort_key):
        s1 = r["stage1_300"]["central"]
        row = f"{r['model_key']:<22}{s1 if s1 is not None else '—':>8}"
        for g in gnames:
            gg = r["groups"].get(g)
            if gg and gg.get("total700_central") is not None:
                row += f"{gg['total700_central']:>11}"
            elif gg:  # stage-2/400 only
                row += f"{str(gg['central']) + '*':>11}"
            else:
                row += f"{'—':>11}"
        print(row)
    print(f"\n-> {OUT}")


if __name__ == "__main__":
    main()
