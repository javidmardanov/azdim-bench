# AzDIM-Bench — Path to Public Release (v1.0)

*Written 2026-07-07, after the four-agent data-integrity audit and the first
run of the completeness validator. This is the working plan to take the
project from v0-preview to public release: HuggingFace + Kaggle dataset,
website, GitHub v1.0, and the arXiv paper.*

---

## Where we stand (measured, not guessed)

| Dimension | State | Evidence |
|---|---|---|
| Items extracted | 2,249 | `data/items/items_v0.jsonl` |
| **Completeness** | **84.1%** — 1,845/2,194 items matched to the PDFs' own metadata lines; **349 missing on 224 identified pages** | `azdim.validate`, `reextract_targets.json` |
| Gold correctness | ~2% true wrong-gold; 99 label↔text consistency flags; 62 MCQ without gold; 29 etalon mismatches | validator + correctness audit |
| Answer-key cross-check | 682/1,572 MCQ covered (~96% agreement); parser fixes prototyped that extend coverage to ~98% of all MCQ | etalon audit, scratchpad prototypes |
| Transcription fidelity | Sampled hand-audit: zero math corruption, zero dropped choices, zero mistranslation; dominant error is wrong gold *letter* with right gold *text* | correctness audit |
| Eval v0 | 14 models × 3 tracks complete; numbers provisional (computed on incomplete data) | `results/metrics_v0.json` |
| Spend | $34.24 of $50 cap | `manifest/api_usage.jsonl` |
| Public surfaces | Site + repo live with WIP banners | github.com/javidmardanov/azdim-bench |

Tooling in place: extraction pipeline, batch runner, align/dedup, eval
harness, DİM 700-point scorer, verify app **with per-item bounding boxes**,
**completeness validator** (`azdim.validate` → console + JSON +
`coverage.html` visual report + page-targeted re-extraction list).

---

## Quality doctrine for v1.0

No published benchmark is error-free; the publishable standard is
**auditable**: machine-certify everything possible, dual-source what the
machine can't certify, human-adjudicate the residue, and **publish the
measured residual error rate**. Concretely:

1. **Completeness by construction** — validator must show 100% of the PDFs'
   metadata-line inventory captured (or a documented exception list, e.g.
   voided items).
2. **Gold by independent key** — every closed/coded item cross-checked
   against DİM's separately-published etalon.
3. **Text by double-entry** — question/choice text certified by PDF text
   layer where locatable; a second, different-family vision model
   (double-entry) elsewhere; human adjudication of every disagreement.
4. **Residual error measured** — a 10% random human-audited sample gives the
   error rate we report in the paper.
5. **Fidelity by construction (Track V)** — a vision track where models see
   the cropped original question image; transcription drops out of the loop
   entirely. Comparing Track A vs Track V quantifies transcription impact.

---

## Phase A — Deterministic repairs ($0, ~1 session)

- [ ] Land the two etalon parser fixes from the audit prototypes:
      joint-sitting (2026-05-24, +1,440 records) and school-leaving flat-title
      (+~7,000 records, all 6 languages). Include the `subject_of()`
      multi-word-token bug fix.
- [ ] Re-run the full cross-check → refreshed `qc_flags.json` covering ~98%
      of MCQ; fix the known positional-drift noise (sequence alignment must
      skip voided `*` items).
- [ ] Gold self-consistency repair: where `gold_answer_label` disagrees with
      `gold_answer_text` but the text uniquely matches another choice,
      re-point the label automatically (audit trail field); queue the
      ambiguous rest for human review.
- [ ] Validator refinement: section-aware inventory for multi-sector sources
      (g3 / mixed show captured>expected because AZ+RU sections share
      numbering); per-subject segmentation of metadata lines.
- [ ] Etalon subject-label bug (2025-07-06 az-dili mislabeled "history").

**Exit criterion:** validator + cross-check agree on a single, exact list of
what is missing and what is suspect. Everything else is machine-certified.

## Phase B — Complete the dataset (~$4–6, 1–2 days elapsed)

- [ ] Targeted re-extraction of the ~224 gap pages via Batch API
      (Sonnet 5, fixed 2-page-forward window so answers printed on the
      following page are captured). Merge → align → **validate again**.
      Iterate until per-source completeness ≥99.5% or exceptions documented.
      (~$2–3)
- [ ] Second-reader pass: Gemini 3.5 Flash re-transcribes every item's page
      (batch, cheap); field-level diff vs our extraction → disagreement
      queue. Agreements = certified by double-entry. (~$2–3)
- [ ] Auto-crop figures for `requires_image` items (geometry from
      `boxes.py`, $0) → `data/items/images/`; build Track V crops.

**Exit criterion:** every item is (a) certified by text-layer match, or
(b) certified by two-model agreement, or (c) in the human queue.

## Phase C — Human verification (Javid, ~2–4 evenings)

- [ ] Review the disagreement/flag queue in the verify app (bounding boxes
      make this fast). Expected queue size after Phase A/B auto-repairs:
      ~300–500 items.
- [ ] 10% random audit sample of machine-certified items → measured residual
      error rate for the paper.
- [ ] Export `items_v1.jsonl` with per-item `verification_status`
      provenance: `text_layer | double_entry | human_verified`.

**Exit criterion:** human queue empty; residual error rate measured and
recorded (target ≤0.5% on the audit sample).

## Phase D — Freeze v1.0 + final eval (~$12–15 → **budget decision**)

- [ ] Freeze dataset v1.0: splits (2025-public / 2026-fresh; az / ru /
      foreign tracks), stats, datasheet.
- [ ] Re-run the 14-model panel on the final data (same staged design:
      cheap models full pool, frontier on stratified core). Fresh run, clean
      provenance — the paper's numbers come from this run only.
- [ ] Recompute metrics, CIs, DİM 700-point simulation; regenerate site
      data; **remove the WIP banners**.

**Budget honesty:** $34.24 spent + Phase B (~$5) + this rerun (~$12) ≈
**$51–55 total, slightly over the $50 cap.** Decision needed before Phase D:
raise the cap to ~$60–75, or trim (rerun frontier models on core only,
~$6–8, keeps us under $50 at some cost to statistical power on the final
numbers). **Ask Javid; do not proceed past the cap without sign-off.**

## Phase E — Release artifacts (~2–3 sessions)

- [ ] **HuggingFace dataset**: final card (license, datasheet, croissant
      metadata, per-field docs), `datasets`-loadable, images included
      MMMU-style (`requires_image` + PNG folder).
- [ ] **Kaggle dataset** mirror (same card, links back).
- [ ] **lm-evaluation-harness task YAML** so anyone can run
      `lm_eval --tasks azdim` — the "prepackaged benchmark" contract.
- [ ] Update `release/run_azdim.py` (hobbyist path) for v1.0; add DİM
      attribution header.
- [ ] GitHub: tag `v1.0`, final README (remove WIP), CITATION.cff with
      arXiv ID once live, Zenodo DOI snapshot.
- [ ] Website: final numbers, Item Explorer (P0 from visual roadmap),
      AZ/EN bilingual toggle (P1 — decide scope), og-image, print
      stylesheet.
- [ ] Move raw DİM PDFs out of git history? (decision: keep with
      attribution vs. download-script-only; current stance = keep, carve-out
      in LICENSE).

## Phase F — The paper (~1–2 weeks part-time; the long pole)

- [ ] `paper/azdim.mplstyle` + `paper/figures.py` — all figures generated
      from the same JSONs the site reads.
- [ ] Write sections (skeleton exists; related-work survey done):
      pipeline & validation methodology (our differentiator — the
      completeness validator, double-entry, measured error rate),
      eval design (reason-then-answer with the 12.5%→100% evidence),
      results, contamination split analysis, DİM-score simulation,
      language gap, limitations (written-open simulated, single-country
      scope, residual error rate).
- [ ] Internal red-team pass: re-run the four audit agents against the
      *final* dataset as a pre-submission check.
- [ ] arXiv mechanics: cs.CL primary; first-time submitter may need
      endorsement — start that early; license CC BY 4.0; link HF + GitHub +
      site; upload after HF/Kaggle are live so the paper's links resolve.
- [ ] After arXiv: consider venue submission later (LREC, ACL Findings,
      NeurIPS Datasets & Benchmarks).

---

## Sequencing & realistic timeline

| Week | Work |
|---|---|
| Now → +3 days | Phase A (deterministic repairs) + Phase B (re-extraction batches; 24h turnaround each) |
| +3 → +7 days | Phase C (Javid's verification evenings) in parallel with Phase D prep; budget decision; final eval run |
| +1 → +2 weeks | Phase E (HF/Kaggle/site/GitHub v1.0) |
| +2 → +4 weeks | Phase F (paper writing → arXiv) |

**Models needed:** Sonnet 5 (reader 1, batch), Gemini 3.5 Flash (reader 2,
batch), existing 14-model panel for the final eval. Nothing new.

**Hard gates:** (1) no eval rerun before validator shows ≥99.5%
completeness and the human queue is empty; (2) no WIP-banner removal before
the audit sample error rate is measured; (3) no arXiv upload before HF and
GitHub v1.0 are live; (4) no spend past $50 without explicit sign-off.
