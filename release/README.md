---
license: other
license_name: dim-derived
license_details: >-
  Question content © State Examination Center of the Republic of Azerbaijan
  (DİM, dim.gov.az), reproduced from official public post-exam publications
  for research purposes with attribution. Metadata and annotations CC-BY-4.0.
language: [az, ru, en, de, fr, ar]
task_categories: [question-answering, multiple-choice]
pretty_name: AzDIM-Bench
---

# AzDIM-Bench (v0, exported 2026-07-07)

> **⚠️ WORK IN PROGRESS — v0 preview. Not final; do not cite yet.**
> This dataset is **incomplete** (~20–35% of university-entrance closed questions
> not yet extracted) and only **partially verified** (gold answers cross-checked
> against DİM's answer keys for ~682 items at ~96% agreement; a large pool not yet
> verified). Item counts, gold answers, and any derived leaderboard are
> **provisional and will change**.

Benchmark of Azerbaijani state exam questions (DİM school-leaving and
university entrance exams, 2025-2026) for evaluating LLMs.

- **2249 items**: {'mcq': 1634, 'codable_open': 449, 'written_open': 166}
- **Languages**: {'en': 129, 'az': 1390, 'ru': 423, 'fr': 142, 'de': 138, 'ar': 27}
- **Subjects**: {'english': 134, 'azerbaijani_language': 148, 'mathematics': 337, 'russian_language': 376, 'french': 142, 'german': 138, 'arabic': 29, 'geography': 205, 'history': 151, 'literature': 117, 'physics': 163, 'chemistry': 173, 'biology': 84, 'informatics': 52}

Source: official DİM "izah" PDFs (see `source_id` + `source_page` per item;
URL manifest in the project repository). Gold answers are DİM's own published
answers. Extraction: vision-LLM transcription, human-verified where
`verification_status = "human_verified"`.

Fields: item_id, exam_date, exam_type, group, subject, subject_section, topic, grade_level_tag, language, question_type, question_text, choices, gold_answer_label, gold_answer_text, explanation_text, requires_image, image_description, variant_map, source_id, source_page, extraction_confidence, verification_status
