# AzDIM-Bench v0 — design decisions log

Working notes; feeds the paper's Methods section. Dates are decision dates.

## Dataset construction (2026-07-05)

- **Sources**: official DİM "izah" PDFs (question text + choices + topic +
  grade + explanation + correct answer + A/B/C/D variant map), 2025–2026,
  from `manifest/sources.json` (39/41 URLs live, SHA256 recorded).
- **Extraction**: vision-LLM transcription (claude-sonnet-5, thinking
  disabled, page images at 150 dpi, 3-page sliding window: prev page for
  variant-map/heading context, next page for continuations). Plain-text PDF
  extraction is disqualified: DİM PDFs' text layer corrupts math (dropped
  minus signs, collapsed fractions; verified on ue2_2025-07-13_g1).
- **Structured outputs**: extraction responses are schema-constrained
  (union-free JSON schema) after ~17% of free-form batch pages failed JSON
  parsing on LaTeX escape sequences. 1/1990 items showed silent escape
  corruption in the free-form run.
- **Batch API** used for the bulk run (50% price).
- **Canonicalization** (`align.py`): drop question-less fragments, dedup by
  (subject, variant_map) then by normalized question prefix, forward-fill
  subjects from section headers, assign traceable item_ids.
- **Known caveat for the paper**: the extractor is a Claude model and Claude
  models are also evaluated — mitigations: verbatim transcription, gold
  answers from DİM's own explanations, human verification pass (Javid, AZ+RU),
  planned inter-extractor agreement check with an open-source pipeline
  (MinerU) on a sample.

## Evaluation design (2026-07-05)

- **Main condition: reason-then-answer.** Model may reason visibly; last
  line must be `Cavab: <letter>` / `Ответ: <letter>`. Rationale: bare-letter
  prompts conflate instruction compliance with ability — measured on 8 pilot
  math items: gpt-5.4-mini scored 1/8 letter-only vs 8/8 reasoning-allowed;
  Haiku 4.5 ignored the letter-only instruction, reasoned anyway, scored 8/8.
  Letter-only is kept as a robustness probe (Track E), not the headline.
- **Hidden/extended reasoning minimized everywhere** for comparability and
  cost: Anthropic `thinking: disabled`, OpenAI `reasoning_effort: "none"`,
  Gemini `thinking_level: "low"`. The visible scratchpad is the equalizer.
- **Tracks**: A = native AZ text (headline), B = native RU text,
  D = multimodal (requires_image items, vision models, later),
  E = robustness probes (letter-only, option shuffle; sampled).
- **Eval set**: MCQ items with unambiguous gold label, `requires_image:
  false`. Parsing: explicit answer-marker regex, then first/last-line and
  unique-letter fallbacks; unparseable = invalid (counted, not scored).
- **Panel** (manifest/models.json): 14 models across frontier/mid/small
  closed (GPT-5.5, GPT-5.4-mini, Claude Opus 4.8/Sonnet 5/Haiku 4.5,
  Gemini 3.1 Pro/3.5 Flash) and open weights (DeepSeek v4 Pro, Qwen3-Max,
  Qwen3-235B, Llama-4 Maverick, Mistral Large 2512, Gemma-4-31B,
  Llama-3.1-8B). Random baseline = 1/#choices analytically.
- **Budget guardrail**: $50 total API cap (hard). Expensive frontier models
  may run on a fixed stratified core subset if full-set projections
  threaten the cap; cheap models run the full set. Same core items for all
  models to keep comparisons clean.
- **Contamination angle**: 2025 sittings (likely in training data) vs 2026
  sittings (post-cutoff for several panel models) reported separately.

## Deviations from the original plan

- Etalon answer-key cross-check demoted from "all items" to "sampled"
  (budget); izah PDFs carry their own printed gold answers, and human
  verification covers flagged items at 100%.
- Auto-cropping of figures deferred; multimodal track will use full page
  images (crops are a later refinement).
