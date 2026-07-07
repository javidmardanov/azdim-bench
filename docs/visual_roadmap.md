# AzDIM-Bench — Visual & Results-Communication Roadmap

Ideas for what to build next, visually and in how we communicate scientific
results. Each item carries implementation notes, data dependencies, and a
priority (P0 = before public release, P1 = v1.x, P2 = ambitious/later).
The governing aesthetic is already codified: *The Examination Paper* —
Newsreader + IBM Plex Mono, paper/ink/carmine, answer-bubble motif,
one message per visual, direct labels over legends. Everything below must
pass the test: **would removing it make the page clearer?** If unsure, cut.

---

## 1. The design system, codified (P0)

Before adding more visuals, freeze the «почерк» so every future chart —
site, paper, slides, social — is recognizably ours.

- **Deliverable**: `site/style-tokens.css` (CSS custom properties only) +
  `docs/design_system.md` (one page: palette hexes, type scale, chart rules).
- **Chart rules to write down**: axis text 10px mono; hairline grid `#d8d3c8`
  at 10-point intervals only; no y-axis when rows are labeled; carmine =
  "the thing we're pointing at", ink = context, never more than one accent;
  CI always drawn, never footnoted; numbers right-aligned in mono;
  dumbbells > grouped bars for paired comparisons; slopegraphs > side-by-side
  bars for before/after.
- **Matplotlib twin**: `paper/azdim.mplstyle` mirroring the tokens
  (font.family: IBM Plex Mono/Newsreader, axes.edgecolor, figure.facecolor
  `#f7f5f0`, carmine cycle). Every paper figure inherits it → the paper and
  the site look like siblings. ~30 lines, one-time cost.

## 2. Item Explorer — "show me a real question" (P0)

The single most persuasive artifact for scientists *and* the public:
browse actual exam items with model answers side by side.

- **What**: a `/explorer.html` page (same static stack): filter by subject /
  language / year / difficulty; each item card shows question (KaTeX-rendered
  math), choices, DİM's official answer + explanation (collapsible), and a
  bubble-row of which panel models got it right (filled bubble = correct —
  the motif does real work here).
- **Implementation**: `site_data.py` gains an `--explorer` mode exporting
  `site/items.js` (eval-pool items + per-model correctness bitmap, ~1–2 MB
  gzipped — acceptable; lazy-load per subject if not). KaTeX from CDN,
  render on card open only (perf). No server needed.
- **Care**: this page IS the dataset browser reviewers will poke at — link
  each card to its source PDF page (`source_id` + page anchor) for instant
  provenance. Difficulty = fraction of panel models correct (free, no IRT
  needed at first).
- **Effort**: ~1 day. **Data**: already on disk.

## 3. Difficulty map / "which questions beat everyone" (P0-P1)

- **What**: a strip/beeswarm of all eval items on a 0→14 "models correct"
  axis, colored by subject; hover reveals the item; click jumps to Explorer.
  The right tail (0–2 models correct) is the "hall of pain" — feature the
  3–5 hardest items verbatim on the main page as pull-quotes. Nothing
  communicates benchmark difficulty like *reading* an item that beat GPT-5.5.
- **Implementation**: per-item correctness matrix already computable from
  `results/raw/*.jsonl`; add `hardest_items` to `data.js`; SVG beeswarm
  (~80 lines JS, simple x-jitter layout). The pull-quote cards reuse
  Explorer card markup.
- **Upgrade path (P2)**: 2-PL IRT (py-irt or a 40-line EM loop) for
  difficulty/discrimination per item → enables adaptive subset design and a
  "300-item mini-AzDIM" with near-identical rankings (huge for hobbyists).

## 4. Subject × model heat matrix (P1)

- **What**: the dense-information view for experts: rows = 14 subjects,
  cols = models, cell = accuracy, color = 3-step ramp (paper → ink at low,
  carmine only for <40% "failure" cells). Mono numerals in cells; no
  colorbar (direct reading).
- **Why**: the leaderboard hides that e.g. literature-AZ is uniformly hard
  while history saturates. One glance answers "is this a language benchmark
  or a knowledge benchmark?" (answer: both, by subject).
- **Implementation**: `acc_by_subject` already in metrics; render as HTML
  table with CSS backgrounds (no SVG needed — tables are the honest
  container for matrices). ~60 lines.

## 5. Human anchors — the government-grade layer (P1, high impact)

Raw accuracy means nothing to a ministry. Anchor everything to human reality:

- **Admission-threshold overlays**: on the 700-point table, draw the official
  müsabiqə şərti lines (e.g. 200 general / 250 for Group-I CS-math-physics,
  from the annual DİM competition-conditions booklet — cite year). One line
  of CSS border on the table, enormous interpretive value: "every frontier
  model qualifies for every program; Llama-8B qualifies for none."
- **Percentile anchoring**: DİM publishes annual statistical reports with
  score distributions (dim.gov.az → statistika; PDFs with per-band counts).
  Parse one year's distribution (deterministic, pdftotext — same trick as
  etalons) → "GPT-5.5's simulated 6xx places in the top N% of 2025
  applicants." Show as a small distribution curve with model dots on it.
  **This is the headline figure for the government audience.**
- **Care**: label simulation caveats on the figure itself (written tasks
  extrapolated), not in a footnote nobody reads.
- **Effort**: 0.5 day for thresholds; 1–2 days for percentile parsing.

## 6. Model report cards — the shareable unit (P1)

- **What**: one generated card per model, styled as a DİM exam certificate
  (attestat aesthetics: ornamental hairline border, mono serial number =
  run hash, bubble-row of subjects, big 700-score, "qualifies for: …" line).
  Downloadable PNG/SVG; doubles as the og-image for social sharing.
- **Implementation**: one HTML template + `site_data`; render to PNG at
  build time with `playwright screenshot` (already have playwright MCP;
  in CI use `npx playwright screenshot`). og:image meta per model page
  anchor. ~1 day.
- **Why**: hobbyists will run their model, get a certificate, and post it.
  That's the growth loop for community submissions.

## 7. Calibration & behavior plots (P1 — the "serious scientist" section)

- **Confidence calibration**: re-run a 200-item subset asking for a 0–100
  confidence on the answer line; reliability diagram (10 bins, mono dots,
  diagonal hairline). Cost ≈ $2. Claim unlocked: "models are (mis)calibrated
  on low-resource exam content."
- **Invalid-rate vs accuracy scatter**: already-collected data; small
  scatter, one dot per model, quadrant labels ("obedient & right",
  "chatty & right", "obedient & wrong"…). Cheap, memorable.
- **Reasoning-length vs correctness**: tokens-out per item vs P(correct),
  per model tier — do models "think longer" on items they get wrong?
  (Usually yes — nice negative-space finding.) Data already in raw files.
- **Option-position bias**: distribution of gold labels vs distribution of
  model picks (A–E) — five paired mono bars; detects position bias and
  doubles as a dataset-balance audit. Data on disk; ~40 lines.

## 8. Contamination communication (P1)

The 2025-vs-2026 dumbbell exists; upgrade the argument:

- **Slopegraph small-multiples**: one mini-slope per model (2025→2026),
  sorted by slope; models whose accuracy *drops* on fresh items are
  contamination suspects; flat slopes are the defensible ones. Add a
  bootstrap CI band per slope — a slope inside its CI is a non-finding,
  and saying so builds credibility.
- **Per-sitting granularity**: x = exam date (7 sittings), y = accuracy;
  one hairline per model, carmine for the frontier. If a specific sitting
  (e.g. 13 Jul 2025) is anomalously easy for one model family — that's the
  most contamination-suggestive plot we can draw from public data.
- **Implementation**: `acc_by_year` exists; per-sitting needs a 10-line
  metrics extension (`acc_by_exam_date`).

## 9. Az/En bilingual site (P1 for gov/public release)

- **What**: full Azerbaijani version. Not machine-translated boilerplate —
  the exam terminology already lives in the data (DİM's own vocabulary).
  Toggle in the header (`AZ | EN`), persisted in localStorage,
  `lang`-attribute switch.
- **Implementation**: extract copy strings into `site/i18n.js`
  (two dicts); charts stay language-neutral (mono labels already read as
  "international scientific"). Findings section needs real translation —
  Javid reviews. ~1 day of engineering + translation pass.
- **Why**: the government/public audience reads Azerbaijani; showing up in
  their language *in their exam's own typographic voice* is the statement.

## 10. Community leaderboard mechanics (P1-P2)

- **Submission flow**: hobbyist runs `run_azdim.py` → gets
  `azdim_out__<model>.jsonl` → opens a PR adding it to `submissions/`.
  CI (GitHub Action) validates schema + recomputes metrics from raw outputs
  (we re-parse; we never trust submitted `correct` flags) + regenerates
  `data.js` → merge = on the leaderboard, tagged `community` (hollow bubble
  vs our filled bubble — motif again).
- **Anti-gaming honesty**: publish that gold answers ship with the dataset
  (inherent to open benchmarks); community tier is "on your honor," the
  maintained tier is ours; the 2026+ rolling fresh split (below) is the
  audit mechanism.
- **Rolling fresh split (P2, the long game)**: DİM publishes new sittings
  every year on a public calendar. Automate: manifest watcher → new izah →
  extraction → verification queue → `fresh-2027` split nobody can have
  trained on. AzDIM becomes a *renewable* benchmark — very few benchmarks
  can claim this structurally.

## 11. Paper figures (P0 for submission)

All figures generated by `paper/figures.py` from the same JSONs the site
reads (single source of truth), using `azdim.mplstyle`:

1. **Fig 1 — pipeline**: export the site's node canvas: open site,
   `rsvg-convert -f pdf` on the inline SVG (or headless chrome
   `--print-to-pdf` of a figure-only page). Vector, identical to site.
2. **Fig 2 — dataset composition**: horizontal stacked bar by subject ×
   item-type; counts in mono. No pie charts, ever.
3. **Fig 3 — main results**: dot + CI-whisker plot (leaderboard as figure),
   AZ track; random baseline as dashed hairline at 20%.
4. **Fig 4 — language gap**: the dumbbell, verbatim from site.
5. **Fig 5 — 700-point simulation**: table (booktabs) + threshold rules;
   floor/central as paired columns.
6. **Fig 6 — format experiment**: two dots and an arrow. Resist the urge
   to add more. The caption does the work.
7. **Appendix**: QC agreement table; per-subject heat matrix; hardest items
   verbatim with per-model bubble rows (LaTeX `\newcommand{\bub}` circle).

## 12. Smaller site polish (P2, batched)

- Scroll-linked bubble TOC fills as sections complete (already state-aware;
  add a fill animation on section completion — 10 lines CSS).
- `<details>` methodology notes under each chart ("what would make this
  wrong?") — pre-empting reviewer questions builds trust.
- Print stylesheet: the site already looks like a paper; make ⌘P produce a
  clean 6-page PDF brief (hide toc/toggles, `break-inside:avoid` on charts).
  This *is* the government one-pager, free.
- Permalink states for leaderboard sort/track (`#track=B&sort=invalid`).
- `prefers-reduced-motion` guard on reveals; `prefers-color-scheme: dark`
  variant = ink paper inverted (the bigmoment band already proves it works).
- OpenGraph/Twitter meta + generated og-image (report card of the leader).

---

## Sequencing recommendation

| Wave | Items | Rationale |
|---|---|---|
| Before public link | 1, 2, 3, 11 | provenance-browsable + design frozen = scientist-proof |
| Release week | 5, 6, 9 | government + shareability + Azerbaijani audience |
| v1.x | 4, 7, 8, 10 | depth for experts, community growth |
| Long game | 3-IRT, 10-rolling-split | renewable benchmark, mini-AzDIM |

The through-line: every visual answers one question a specific audience
actually has, uses data we already log, and wears the same clothes.
