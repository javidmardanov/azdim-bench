# AzDIM-Bench

> ## ⚠️ WORK IN PROGRESS — v0 preview
>
> **This is an early preview, not a finished benchmark. Do not cite it or treat its
> numbers as final.**
>
> Known limitations in this build:
> - **Incomplete dataset.** ~20–35% of closed questions in the university-entrance
>   exams are not yet extracted (verified against DİM's own answer keys). Coverage
>   for these exams is a work in progress.
> - **Partially verified answers.** Gold answers are cross-checked against DİM's
>   separate answer keys for ~682 entrance-exam items (~96% agreement); a large pool
>   (school-leaving exams + one entrance sitting whose key failed to parse) is **not
>   yet independently verified**.
> - **Provisional results.** The leaderboard was computed on the above data. Rankings
>   are indicative and **will change** once coverage and verification are complete.
> - **No human verification pass yet.** The `verify_app` review of flagged items has
>   not been completed.
>
> Tracking issues and progress: see [`docs/eval_design.md`](docs/eval_design.md).

A public benchmark of Azerbaijani state examination questions (DİM — Dövlət İmtahan Mərkəzi)
for evaluating large language models.

Source material: official post-exam publications from [dim.gov.az](https://dim.gov.az) —
"izah" PDFs (question text, choices, explanations, correct answers, variant mappings) and
"etalon" PDFs (answer keys). Scope of v0: 2025–2026 school-leaving (buraxılış) and
university entrance (qəbul, stage 2, groups I–IV) exams, Azerbaijani and Russian sectors.

All question content © DİM, reproduced for research with source attribution.

## Layout

- `manifest/sources.json` — ledger of official source PDFs (URL, hash, classification)
- `data/` — pipeline stages: raw_pdfs → pages → extracted → items → verified
- `src/azdim/` — pipeline code (download, render, extract, align, dedup, verify)
- `src/azdim/eval/` — evaluation harness (model runners, prompts, parsing, metrics)
- `results/` — model outputs and metric tables
- `docs/research/` — background research on the exam system and source archive

## Pipeline

```
uv run python -m azdim.download               # fetch official PDFs + hashes
uv run python -m azdim.render --all-izah      # PDF pages -> PNG (150 dpi)
uv run python -m azdim.batch_extract submit   # vision-LLM extraction (Batch API)
uv run python -m azdim.batch_extract collect  # -> data/extracted/*.jsonl
uv run python -m azdim.batch_extract retry    # re-run failed pages directly
uv run python -m azdim.align                  # -> data/items/items_v0.jsonl
uv run python -m azdim.verify_app             # human review UI (localhost:5050)
uv run python -m azdim.eval.runner run --all  # model panel -> results/raw/
uv run python -m azdim.eval.metrics           # -> results/metrics_v0.json
uv run python -m azdim.export                 # -> release/ (HF dataset layout)
```

Design decisions and their rationale: [docs/eval_design.md](docs/eval_design.md).
