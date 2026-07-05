#USER:

This is for an academic paper, that focuses on testing/benchmarking existing LLMs on Azerbaijani exams. What do you think? Do we have everything to do this project? And how should we do it? What is the plan, considering all the variables? Think like a professional scientist. Think clearly, directly, be precise. 

#GPT:
Yes — this is a real, publishable project, but we should be precise: we probably have enough public material for a strong pilot and a useful paper; we do not yet have enough to claim “all exact variants, all languages, all groups, all years” unless DİM cooperates or grants access/permission.
The strongest version of the paper would not be “LLMs on some Azerbaijani questions.” It should be:
Azerbaijani State Exams as a Multilingual, Multi-subject Benchmark for LLM Reasoning, Language Understanding, and Educational Validity
This is valuable because Azerbaijani remains under-benchmarked: recent Azerbaijani NLP work explicitly notes the lack of systematic benchmarking for Azerbaijani language models and multilingual models with Azerbaijani support. (arXiv)
1. Do we have everything?
We have enough to start. We do not yet have everything for the maximal version.
DİM’s public site confirms the key structure of the university admissions system: admission is run centrally by DİM in two stages; the first stage overlaps with the school-leaving exam for current graduates and includes Azerbaijani/Russian language, foreign language, and mathematics, with 85 tasks and 300 maximum points. (State Examination Center) The second stage is organized by specialty groups, with I, II, III, IV, and V groups; I, II, III, and IV have group-specific subject combinations, while V does not take the second-stage exam and competes based on first-stage results. (State Examination Center)
We also have official evidence that DİM publishes post-exam materials. For example, for the 7 June 2026 university entrance exam, DİM linked explanations for I group, IV group, III-group geography, and the correct answers. (State Examination Center) For 24 May 2026, DİM published explanations for II and III groups plus correct answers. (State Examination Center) I also opened one of the official PDFs; it contains the actual task text, answer choices, topic, grade level, explanation, correct answer, and A/B/C/D variant mapping. (State Examination Center)
For school-leaving exams, the situation is mixed. DİM published full explanations and correct answers for at least some 11-year school-leaving exams, such as the 15 March 2026 exam. (State Examination Center) But for some 9-year school-leaving exams, the public release I found is only the correct-answer standard for closed and codable open-type items, not necessarily full question text. (State Examination Center) That means the project is feasible, but the “all exact question images/PDFs” version probably requires either deeper archival recovery or DİM collaboration.
The language coverage is also real. DİM explicitly publishes 2026 second-stage university entrance programs in both Azerbaijani and Russian sections. (State Examination Center) DİM also publishes school-leaving exam programs for both Azerbaijani and Russian sections, including Azerbaijani/Russian language, mathematics, foreign languages, and Azerbaijani as state language. (State Examination Center)
2. My scientific judgment
I would not frame this as a simple leaderboard. A leaderboard alone is fragile and quickly outdated.
I would frame it as a measurement paper with five scientific questions:
	1	Can current LLMs solve Azerbaijani high-stakes exam questions?
	2	Where do they fail: language, reasoning, curriculum knowledge, math, visual interpretation, or exam format?
	3	Is performance different on Azerbaijani vs Russian versions of comparable exams?
	4	How much does performance change under prompt language, translation, option ordering, and multimodal access?
	5	Are public exam benchmarks contaminated because official PDFs are online?
That last point is critical. Public exam questions may already appear in web data used to train models. Modern benchmark work treats contamination as a serious threat; MMLU-CF, for example, was created specifically because open multiple-choice benchmarks are vulnerable to data leakage. (arXiv)
So the paper should separate:
Public historical benchmark Useful for transparency, reproducibility, and broad comparison.
Fresh / private held-out benchmark Needed for stronger claims about genuine reasoning and language ability. This requires either DİM partnership, newly written expert items, or post-model-release exams whose dates are carefully documented.
3. What exactly should be included?
I would build the benchmark in layers.
Layer A — Core DİM public benchmark
This is the safest starting point.
Include only official DİM materials with traceable URLs:
Exam type
Include?
Notes
11-year school-leaving / first-stage admission
Yes
Central for university admissions; often has language, foreign language, math.
University entrance second stage, I group
Yes
Math, physics, chemistry/informatics subgroups.
University entrance second stage, II group
Yes
Math, geography, history.
University entrance second stage, III group
Yes
Azerbaijani/Russian language, history, literature; or geography/history depending subgroup.
University entrance second stage, IV group
Yes
Biology, chemistry, physics.
V group
Treat separately
No second-stage test; often aptitude/specialty-dependent, not a clean LLM benchmark.
9-year school-leaving
Include when full questions are available; otherwise answer-key-only materials are insufficient
Public materials may not always include full question text.
Azerbaijani as state language exams
Include as separate language-proficiency benchmark
Important for Russian-sector students and language policy.
Foreign language tasks
Include cautiously
Listening/speaking/image-description tasks may require audio or images.
Layer B — Full archival benchmark
This is the “all years / all groups / all languages / all variants” version. It requires exhaustive crawling, manual verification, and likely DİM permission.
Layer C — Private held-out benchmark
This is the scientifically strongest layer. It prevents models from memorizing public PDFs. It could be built through:
	•	DİM partnership;
	•	newly authored exam-style questions by Azerbaijani subject experts;
	•	future public exams collected immediately after release, with model release dates documented.
4. The biggest methodological trap: variants
Do not count A, B, C, D variants as independent questions.
The official PDFs I inspected show mappings like “A variant question 1, B variant question 6, C variant question 11, D variant question 1” for the same underlying item. (State Examination Center) If we count every variant separately, we will inflate the dataset and overstate statistical confidence.
The correct unit is:
underlying item, not printed variant occurrence.
Each item should store variant metadata:
item_id
exam_date
exam_type
group
subgroup
subject
language_section
variant_positions: {A: 1, B: 6, C: 11, D: 1}
question_text
choices
correct_answer
explanation
source_pdf
page_number
requires_image
requires_audio
requires_written_answer
5. Dataset schema
Use a strict schema from the beginning. I would use JSONL, one item per underlying question.
Example:
{
  "benchmark": "AzDIMBench",
  "source": "DİM official",
  "exam_date": "2026-06-07",
  "exam_type": "university_entrance_stage_2",
  "group": "I",
  "subgroup": "RK_or_RI_if_known",
  "subject": "mathematics",
  "grade_level": 9,
  "language_section": "az",
  "variant_map": {
    "A": 1,
    "B": 6,
    "C": 11,
    "D": 1
  },
  "question_type": "multiple_choice",
  "modality": "text",
  "question": "...",
  "choices": {
    "A": "...",
    "B": "...",
    "C": "...",
    "D": "...",
    "E": "..."
  },
  "answer": "D",
  "answer_text": "36",
  "explanation_available": true,
  "source_url": "...",
  "source_page": 1,
  "copyright_status": "official_public_but_not_relicensed"
}
For open-ended questions:
{
  "question_type": "codable_open",
  "answer_format": "integer_or_decimal",
  "answer": "42"
}
For written-response questions:
{
  "question_type": "written_open",
  "scoring": "rubric_required",
  "automatic_scoring": false
}
Written-response tasks should not be mixed with multiple-choice accuracy unless you have a human/expert rubric.
6. Evaluation design
I would run several controlled conditions.
Condition 1 — Native Azerbaijani, answer only
The model receives the original Azerbaijani question and answer options.
Prompt:
Sualı cavablandır. Yalnız doğru variantın hərfini yaz: A, B, C, D və ya E.
This tests practical exam-solving in Azerbaijani.
Condition 2 — Native Russian, answer only
Same for Russian-sector materials.
Prompt:
Ответь на вопрос. Напиши только букву правильного варианта: A, B, C, D или E.
This separates Azerbaijani-language weakness from general reasoning weakness.
Condition 3 — English translation control
Translate the question to English using a fixed, audited translation pipeline. This helps answer:
Did the model fail because it cannot reason, or because Azerbaijani is underrepresented?
But translation must be a separate condition, not the main score.
Condition 4 — Multimodal
For diagrams, geometry figures, maps, charts, chemistry structures, and picture-based foreign-language tasks, use the original PDF/page image with a vision-capable model.
Report text-only and vision-enabled separately.
Condition 5 — Robustness
Test whether scores change when:
	•	options are shuffled;
	•	prompt language changes;
	•	the model is asked for only the answer vs answer plus reasoning;
	•	OCR-normalized text is used vs page screenshot.
MMLU-Pro found prompt sensitivity to be a meaningful benchmark issue, so this is not cosmetic; it is part of scientific measurement. (arXiv)
7. Metrics
Do not report only overall accuracy.
Report:
Metric
Why it matters
Overall accuracy
Basic comparability.
Macro accuracy by subject
Prevents math-heavy or language-heavy imbalance.
Macro accuracy by group
I/II/III/IV measure different abilities.
Azerbaijani vs Russian delta
Measures language-specific performance.
Text-only vs multimodal delta
Measures vision dependence.
Closed MCQ vs codable open accuracy
Different answer formats.
Invalid answer rate
Models sometimes output explanations instead of choices.
Calibration
Ask confidence; compare confidence to correctness.
Exam-score equivalent
Convert to DİM-style points where possible.
Pass-threshold simulation
“Would this model qualify?” is intuitive, but should be secondary.
HELM is a good methodological precedent because it argues for multi-metric evaluation rather than accuracy-only leaderboards. (arXiv)
8. Model selection
Use three model families.
Frontier closed models GPT, Claude, Gemini, maybe Grok, depending on API access.
Open multilingual models Llama, Qwen, Mistral, Gemma, DeepSeek, Aya, Command-R, etc.
Azerbaijani-relevant models Include Azerbaijani-specific or Azerbaijani-supported models where possible. Some Azerbaijani foundation-model work is encoder-focused, so those models may not be directly comparable to generative LLMs unless adapted for multiple-choice classification. (arXiv)
For each model, record:
model_name
provider
version/date
temperature
top_p
max_tokens
prompt_template
API date
whether internet/search/tools disabled
This matters because API models change silently.
9. Contamination control
This is one of the paper’s most important sections.
The benchmark should have three splits:
Public historical split
Older DİM PDFs and answer keys. Useful, but possibly contaminated.
Recent public split
Exams released after a model’s known training cutoff or after the model version date. This is stronger, but still imperfect because API providers may update models.
Private / embargoed split
Best scientific evidence. Keep questions private; release metadata and aggregate results. Public release can include a validation set, while the test set remains hidden. This is similar in spirit to newer contamination-aware benchmark design. (arXiv)
To check contamination, run:
	•	exact web search for distinctive question strings;
	•	n-gram overlap against Common Crawl-derived indexes if available;
	•	ask models whether they recognize the item, but do not rely on self-report;
	•	compare performance on public vs fresh/private items.
10. Data extraction pipeline
The practical pipeline should be:
	1	Source inventory Crawl DİM pages by year, exam type, date, group, language, and file URL.
	2	PDF classification Label each file as:
	◦	full question booklet;
	◦	explanation PDF with question text;
	◦	answer-key-only PDF;
	◦	program/specification;
	◦	news article without usable items.
	3	Text extraction Use native PDF text when available. Use OCR only when necessary.
	4	Image extraction Extract diagrams, maps, graphs, tables, and page screenshots. Math-heavy PDFs often need image preservation.
	5	Question segmentation Split by item, not by page. Preserve variant mapping.
	6	Answer alignment Align each item to DİM’s answer key or explanation.
	7	Deduplication Merge A/B/C/D variants of the same item.
	8	Human verification Every item should be checked by at least one Azerbaijani/Russian speaker; STEM/math items need subject review.
	9	Gold release format Release clean JSONL plus source metadata. If copyright permission is not obtained, release code, metadata, hashes, and evaluation scripts, but not the full copyrighted question text.
11. Legal and ethical position
This is not a human-subjects study unless you collect student data. But it is a copyright and licensing issue.
DİM materials are official and public, but public availability does not automatically mean redistribution is allowed. The safest publication model is:
	•	cite DİM sources;
	•	store internal research copies;
	•	publish derived metadata and aggregate scores;
	•	ask DİM for permission before redistributing the question text/images;
	•	release a reproducible scraper that downloads from official URLs where legally acceptable;
	•	avoid unofficial test-prep sites unless every item is verified against DİM.
This matters because a benchmark paper can be scientifically strong while still being careful with copyrighted exam content.
12. Paper structure
I would write the paper like this:
	1	Introduction Azerbaijani is low-resource in LLM evaluation; national exams provide high-quality, expert-written, curriculum-grounded tasks.
	2	Exam system background Explain DİM, school-leaving exams, two-stage university admissions, I–V groups, Azerbaijani/Russian sections.
	3	Dataset construction Sources, inclusion criteria, extraction, deduplication, schema, validation.
	4	Benchmark design Native Azerbaijani, native Russian, translated English, text-only, multimodal, contamination-aware splits.
	5	Models evaluated Closed, open, multilingual, Azerbaijani-relevant.
	6	Results Overall and by subject/group/language/modality.
	7	Error analysis Math reasoning, Azerbaijani grammar, literature/history knowledge, diagrams, hallucinated formulas, option-order sensitivity.
	8	Contamination analysis Public vs fresh/private split.
	9	Limitations Copyright, OCR, incomplete public archive, written tasks, changing model versions.
	10	Release Dataset card, model cards, evaluation scripts, source inventory.
13. The main risks
The project can fail or become weak if we ignore these:
Risk
Consequence
Control
Counting variants as separate questions
Inflated dataset, false confidence
Deduplicate by underlying item.
OCR/math extraction errors
Wrong model scores
Human STEM validation.
Public-data contamination
Overestimated LLM ability
Fresh/private split.
Mixing MCQ and written tasks
Invalid aggregate metric
Separate scoring regimes.
Ignoring Russian section
Misses natural language-control experiment
Evaluate Azerbaijani and Russian separately.
Ignoring images
Penalizes or benefits models unfairly
Separate text-only and multimodal tracks.
Copyright uncertainty
Cannot release benchmark
Get DİM permission or release metadata/scripts only.
Prompt instability
Leaderboard noise
Use fixed prompts plus robustness tests.
Model version drift
Irreproducible results
Record model versions and API dates.
14. The cleanest contribution
The strongest contribution is not “we collected questions.” It is:
We introduce AzDIMBench, a contamination-aware benchmark derived from Azerbaijani state school-leaving and university entrance exams, covering Azerbaijani and Russian sections, I–IV specialty groups, multiple subjects, variants, and multimodal items; we evaluate modern LLMs under controlled native-language, translated, and multimodal settings.
That is a serious paper.
15. Bottom line
We should proceed, but in two tracks:
Track 1: Public benchmark paper Use official DİM PDFs, explanations, and answer keys. This is feasible now and enough for a credible first paper, especially if we are honest about coverage.
Track 2: DİM collaboration / private held-out benchmark Needed for the strongest version: all variants, all languages, all groups, exact booklets/images, and contamination-resistant evaluation.
My judgment: the project is scientifically worthwhile, feasible, and timely. The key is to treat it as a rigorous benchmark-construction and measurement project, not a casual scraping/evaluation exercise.
#USER:
Thank you. We shall proceed with Track 1: Public benchmark paper.



#GPT:

Excellent. Then we should treat Track 1 as a disciplined public-benchmark construction project, not just a scraping project.
Working title
AzDIMBench-Public: A Public Benchmark of Azerbaijani State Examination Questions for Evaluating Large Language Models
Use “Public” in the title/version name because this first paper will use official public materials only. That makes the scope honest and protects us from overclaiming.
1. Scope we should freeze now
For the first paper, the benchmark should include:
Component
Include in Track 1?
Decision
11-year school-leaving / first-stage admission exams
Yes
Core benchmark.
University entrance stage 2, Groups I–IV
Yes
Core benchmark.
Group V
No, except as context
DİM says V-group candidates do not take the second-stage exam and compete using first-stage results, so it is not a clean LLM exam benchmark. (State Examination Center)
Azerbaijani-sector questions
Yes
Core.
Russian-sector / Russian-language questions
Yes, when full public text is available
Must distinguish “Russian sector” from “Russian language/literature subject.”
Closed multiple-choice questions
Yes
Main automatic benchmark.
Codable open questions
Yes, separate metric
Automatically scorable if answer key is clear.
Written open-response questions
Store, but do not include in main accuracy
Requires rubric/human scoring.
Listening/audio tasks
Include as “printed transcript condition” only
Public PDFs often print the text/explanation, but the real exam modality may have been audio.
Diagrams, maps, figures
Include, but flag as multimodal
Evaluate text-only and vision-enabled models separately.
Unofficial prep-site materials
Exclude from main benchmark
Use only official DİM sources for Track 1.
DİM’s own description gives us the institutional backbone: university admission is centralized, held in two stages, the first stage overlaps with school-leaving exams for current graduates, and the first stage contains Azerbaijani/Russian language, foreign language, and mathematics with 85 tasks and 300 maximum points. The second stage is organized by specialty groups, with 90 tasks and 400 maximum points. (State Examination Center)
2. Confirmed public source base for v0
For v0, I would start with a 2026 official-source corpus because it is recent, structured, and already contains the main exam types.
Source block
Coverage
Status
15 March 2026 school-leaving exam
11-year school-leaving tasks, explanations, answer keys
DİM page links both the explanations and correct answers for closed/codable open tasks. (State Examination Center)
19 April 2026 admission/school-leaving exam
First-stage admission / school-leaving material
DİM page links explanations and correct answers. (State Examination Center)
24 May 2026 university entrance, Groups II–III
Stage-2 Groups II and III
DİM page links explanations for Groups II and III and the correct-answer file. (State Examination Center)
7 June 2026 university entrance, Groups I, IV, and III geography
Stage-2 Groups I and IV, plus III-group geography
DİM page links explanations for I group, IV group, III-group geography, and correct answers. (State Examination Center)
This is already enough for a strong first benchmark paper, provided we clearly say: this is an official public benchmark sample, not a complete archive of all Azerbaijani state exams.
3. What the raw PDFs actually contain
The official PDFs are usable for item-level extraction. For example, the 7 June 2026 Group I PDF contains the exam date, group, subject, variant mapping, question text, answer choices, topic, grade level, explanation, and correct answer. (State Examination Center)
That matters because our schema can be precise. A single item may appear at different positions in A/B/C/D variants; therefore we must deduplicate by underlying question, not by printed variant occurrence. The PDF explicitly shows this structure, for example one mathematics item mapped to A variant question 1, B variant question 6, C variant question 11, and D variant question 1. (State Examination Center)
The language variable is also real but must be handled carefully. The school-leaving PDF includes Russian-language material, including “Русский язык” tasks, while the stage-2 answer-key files include both Azerbaijani-section and Russian-sector markings in at least some places. (State Examination Center) The Group III explanation PDF also contains Russian-language questions and Russian literature/language content. (State Examination Center)
4. Core scientific claims for the paper
The paper should make only claims that Track 1 can support.
Strong claims we can make:
	1	Azerbaijani state exam materials can be converted into a structured LLM benchmark.
	2	Current LLMs can be evaluated across Azerbaijani, Russian, STEM, humanities, language, and multimodal exam items.
	3	Performance differs by subject, group, language, modality, and answer format.
	4	Public high-stakes exam materials reveal failure modes not captured by English-centric benchmarks.
	5	Public benchmarks require contamination analysis because the questions are online.
Claims we should not make yet:
	1	“We collected all Azerbaijani state exam questions.”
	2	“This measures uncontaminated reasoning.”
	3	“This fully represents Azerbaijani education.”
	4	“This proves model X can pass Azerbaijani university entrance exams.”
	5	“Azerbaijani and Russian versions are perfectly parallel.”
5. Dataset object model
Each record should represent one underlying item, not one variant occurrence.
{
  "item_id": "azdim_public_2026_stage2_group1_math_0001",
  "source_authority": "DİM",
  "source_type": "official_public_pdf",
  "exam_date": "2026-06-07",
  "exam_type": "university_entrance",
  "stage": 2,
  "grade_base": "11_year",
  "group": "I",
  "subgroup": "RK_or_RI_or_unknown",
  "subject": "mathematics",
  "topic": "Ədədi ardıcıllıqlar. Silsilələr",
  "grade_level_tag": "9",
  "sector": "az",
  "question_language": "az",
  "question_type": "multiple_choice",
  "original_modality": "text",
  "requires_image": false,
  "requires_audio": false,
  "requires_written_response": false,
  "variant_map": {
    "A": 1,
    "B": 6,
    "C": 11,
    "D": 1
  },
  "question_text": "...",
  "choices": {
    "A": "...",
    "B": "...",
    "C": "...",
    "D": "...",
    "E": "..."
  },
  "gold_answer_label": "D",
  "gold_answer_text": "36",
  "explanation_text": "...",
  "source_pdf_id": "dim_2026_06_07_group1_explanation",
  "source_page": 1,
  "source_line_or_bbox": null,
  "license_release_status": "internal_text_public_metadata_only"
}
For public release, we should separate:
raw_private/
  official PDFs downloaded for research use

data_public/
  source manifest
  item metadata
  hashes
  page references
  evaluation scripts
  optionally question text only if permission is secured

data_internal/
  full extracted question text
  full extracted explanations
  answer keys
6. Variables we must encode from day one
The benchmark will fail scientifically if these variables are added later. They should be present from the first annotation pass.
Variable
Values / examples
exam_type
school_leaving, admission_stage1, admission_stage2
stage
1, 2, not_applicable
group
I, II, III, IV, V_context_only
subgroup
I_RK, I_RI, III_DT, III_TC, unknown
sector
az_sector, ru_sector, unknown
question_language
az, ru, en, de, fr, etc.
subject
mathematics, physics, chemistry, biology, Azerbaijani language, Russian language, literature, history, geography, informatics, foreign language
question_type
MCQ, multi-select, codable open, written open
modality
text, diagram, map, graph, table, image, audio-transcript
answer_source
explanation PDF, answer-key PDF, both
dedup_status
canonical item, duplicate variant, uncertain
evaluation_track
main, open_numeric, multimodal, human_scored_excluded
release_status
public metadata, public text permitted, internal only
7. Evaluation tracks
We should not produce one single score. We should produce several controlled tracks.
Track A — Native Azerbaijani text
Input: Azerbaijani question text and answer options.
Prompt:
Sualı cavablandır. Yalnız doğru cavab variantının hərfini yaz: A, B, C, D və ya E.
Metric: exact option accuracy.
Track B — Native Russian text
Input: Russian-sector or Russian-language question text when publicly available.
Prompt:
Ответь на вопрос. Напиши только букву правильного варианта: A, B, C, D или E.
Metric: exact option accuracy.
Track C — English translation control
Input: human-reviewed English translation of the same item.
Purpose: separate language failure from reasoning failure.
Report this separately. Do not mix it into the main Azerbaijani benchmark score.
Track D — Multimodal PDF/page condition
Input: original page image or cropped question image.
Use this for geometry diagrams, maps, charts, chemistry diagrams, tables, and visual comprehension items.
Report separately:
text-only accuracy
vision-enabled accuracy
vision gain = vision accuracy - text-only accuracy
Track E — Robustness
For a subset of items:
original option order
shuffled option order
Azerbaijani prompt
English prompt
answer-only
answer-plus-explanation
This will show whether models are solving the question or exploiting option/order artifacts.
8. Metrics
Primary metrics:
overall accuracy
macro accuracy by subject
macro accuracy by group
macro accuracy by language
macro accuracy by modality
macro accuracy by question type
invalid-response rate
Secondary metrics:
DİM-style score approximation
pass-threshold simulation
confidence calibration
option-order sensitivity
translation gain/loss
vision gain/loss
For statistics:
95% bootstrap confidence intervals
paired model comparisons on the same item set
McNemar tests for paired binary correctness
clustered analysis by source exam and subject
The unit of analysis should remain the underlying item, not variant copies.
9. Model set
Use a deliberately mixed model panel.
Category
Examples
Frontier closed models
GPT, Claude, Gemini
Strong open multilingual models
Qwen, Llama, Mistral, Gemma, DeepSeek
Smaller open models
7B–14B class models
Azerbaijani-relevant models
Any Azerbaijani or Turkic-focused models that can support multiple-choice inference
Translation baselines
Azerbaijani → English → model; Russian → English → model
Random / heuristic baselines
Random choice; majority-option if useful
For every run, store:
model name
provider
exact version
API date
temperature
top_p
max_tokens
prompt template
whether tools/search were disabled
number of runs
raw output
parsed answer
latency
cost
Use temperature = 0 for the main benchmark.
10. Data pipeline
The pipeline should be reproducible.
Step 1: Build source manifest
Step 2: Download official PDFs
Step 3: Compute SHA256 hashes
Step 4: Extract native PDF text
Step 5: Extract page images / crops
Step 6: Segment into candidate items
Step 7: Parse variant mappings
Step 8: Parse choices and gold answers
Step 9: Align explanation PDF with answer-key PDF
Step 10: Human verification
Step 11: Export JSONL
Step 12: Run model evaluations
Step 13: Aggregate metrics
Step 14: Produce paper tables and figures
Minimum source manifest fields:
{
  "source_id": "dim_2026_06_07_group1_explanation",
  "authority": "DİM",
  "exam_date": "2026-06-07",
  "exam_type": "university_entrance_stage2",
  "group": "I",
  "document_type": "explanation_pdf",
  "public_page_citation": "...",
  "pdf_sha256": "...",
  "page_count": 30,
  "download_timestamp_utc": "...",
  "parser_version": "0.1.0",
  "manual_verification_status": "pending"
}
11. Human validation protocol
This must be serious.
Each item receives two passes:
Pass 1: extraction validation
Reviewer checks:
question text complete
answer choices complete
correct answer aligned
variant map correct
subject correct
language correct
image/diagram flag correct
open/written flag correct
Pass 2: scientific validation
Subject reviewer checks:
is the item answerable from extracted text?
does it require an omitted image/audio?
is the gold answer unambiguous?
should the item be in main benchmark or separate track?
Adjudication rule:
If two annotators disagree, mark item as "needs_adjudication".
Only adjudicated or agreement-verified items enter v1.0.
12. Contamination handling
Because the PDFs are public, the main paper must include a contamination section.
For each item:
search distinctive 8–15 word snippets
record whether exact question text is indexed online
record whether answer/explanation is indexed online
record PDF publication date
record model release/evaluation date
Then report:
performance on likely-indexed items
performance on not-found items
performance on recent items
performance by publication date
This does not solve contamination completely, but it makes the paper credible.
13. Legal/release strategy
For Track 1, assume the safest position:
Official public does not automatically mean freely redistributable.
Release:
source manifest
metadata
hashes
evaluation code
prompt templates
model outputs where allowed
aggregate results
item IDs and source page references
Do not release full question text/images publicly unless DİM permission is obtained.
The paper can still be fully reproducible by giving scripts that reconstruct the dataset from official public sources, subject to DİM’s terms and availability.
14. First paper structure
1. Introduction
2. Azerbaijani state exam system
3. Dataset construction
4. Source coverage and limitations
5. Item schema and annotation
6. Evaluation design
7. Models
8. Results
9. Error analysis
10. Contamination analysis
11. Limitations
12. Release and reproducibility
15. Concrete timeline
Week 1 — Source inventory and schema freeze
Deliverables:
source_manifest_v0.csv
schema_v0.json
annotation_guide_v0.md
paper_outline.md
Decision at end of week:
v0 scope fixed: which 2026 sources are included
Week 2 — Extraction prototype
Deliverables:
PDF downloader
hash generator
text extractor
first 50 manually verified items
image/page crop prototype
Decision at end of week:
is native PDF extraction good enough, or do we need heavier manual correction?
Week 3 — Full extraction
Deliverables:
all candidate items extracted
variant maps parsed
answer keys aligned
known-bad items flagged
Week 4 — Human verification
Deliverables:
verified_items_v0.jsonl
excluded_items_v0.jsonl
audit report
inter-annotator agreement
Week 5 — Model evaluation
Deliverables:
model_outputs/
parsed_answers.jsonl
metrics_by_model.csv
metrics_by_subject.csv
metrics_by_language.csv
metrics_by_modality.csv
Week 6 — Analysis and paper draft
Deliverables:
main result tables
error taxonomy
contamination analysis
paper draft v0
16. Minimum viable paper
The minimum publishable version should have:
official DİM-only source corpus
hundreds of verified items
deduplication by underlying item
at least 8–12 LLMs
Azerbaijani native evaluation
Russian-language/sector subset where available
subject-level and group-level metrics
text-only vs multimodal split
contamination discussion
public source manifest and code
clear copyright-aware release policy
17. Immediate next decision
The cleanest v0 is:
Use 2026 official DİM public materials only, covering 15 March, 19 April, 24 May, and 7 June releases; build the full pipeline and paper around that; expand to earlier years only after v0 is stable.
That gives us a rigorous, defensible first paper rather than a messy archive project.
