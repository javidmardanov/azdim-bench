# AzDIM-Bench

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
uv run python -m azdim.download        # fetch PDFs, verify hashes
uv run python -m azdim.render          # PDF pages -> PNG
uv run python -m azdim.extract <id>    # vision-LLM extraction -> data/extracted/
```
