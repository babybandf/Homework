# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A 7th-grade geometry problem-solving assistant that produces per-problem directories containing matplotlib-drawn PNG figures, Markdown solutions, and interactive bilingual HTML pages. Each problem lives under `math/NNN/`.

## Core Constraint Documents (read these first)

- **`AGENT.MD`** — Hard MUST/MUST NOT constraints. Defines knowledge scope (7th grade only — no trig, no Pythagorean theorem, prefer similar triangles/congruence/auxiliary constructions), tech stack (matplotlib PNG, TailwindCSS + MathJax 3, template-first), required output files, and completion criteria. This document takes precedence over all others.
- **`checker.md`** — Self-check checklist and the mandatory report template that must be pasted verbatim at task completion. Every item must be PASS or FAIL; "all passed" summaries are prohibited.
- **`problem_solve_steps.md`** — Implementation workflow from parsing → solving → drawing → writing → HTML generation → verification. Contains file naming conventions.
- **`geometry_drawing_guide.md`** — Matplotlib G-standards: all visual elements (right-angle markers, angle arcs, tick marks, label offsets) must be normalized by `L_ref = compute_visual_scale(ax)`, never hardcoded absolute values. Mandates `LayoutAuditor` usage: create auditor → `set_active_auditor(auditor)` → draw → `set_active_auditor(None)` → `check()` must return empty list before saving.
- **`webpage_guide.md`** — Interactive HTML specifications: step cards, hint system, keyboard navigation, i18n, progress indicator.

## Starting a New Problem (NNN)

```bash
mkdir -p math/NNN
cp templates/_template.html               math/NNN/NNN.html
cp templates/_template_solution.md        math/NNN/NNN_solution.md
cp templates/_template_geometry_figures.py math/NNN/geometry_figures.py
```

Then fill in `{{...}}` / `TODO:` placeholders. **Never** write these files from scratch — all existing scaffolding (bilingual switcher, progress bar, keyboard nav, hint framework, font loading, utility functions) must be preserved.

## Required Output Files per Problem

| File | Purpose |
|---|---|
| `NNN_solution.md` | Markdown solution with pure-text formulas (no `$...$`) |
| `NNN.html` | Interactive page with `data-i18n`, step cards, hints, summary |
| `geometry_figures.py` | Must run `python geometry_figures.py` without errors |
| `step*.png` | At least one per key step; each classification case gets its own figure |

## Key Technical Rules

- **Formulas in Markdown**: Pure text only — `(1/2)`, `S△ABC`, `²`. No `$...$` or `$$...$$`.
- **Chinese font**: Load from `font/STHeiti Medium.ttc` via absolute path in matplotlib scripts.
- **Figure labels**: Use English to avoid font rendering issues. Labels must not overlap lines, right-angle markers, or other labels. Use `LayoutAuditor` with real bbox collision detection.
- **Step isolation**: Each `step*.png` highlights only the current step's geometry; prior context uses `alpha ≤ 0.35`.
- **HTML**: Include `langZh`/`langEn` toggle, `i18n` dictionary with `zh` and `en` keys, every visible element with `data-i18n` attribute, keyboard nav (`←`/`→`), progress indicator, ≥2 expandable hints per key step, and a final summary page.
- **CDN stack**: TailwindCSS, MathJax 3, optionally JSXGraph 1.8.0.
- **Method constraint**: Solutions must use 7th-grade methods (similar triangles, congruence, auxiliary lines like midline extension, cut-and-paste, three-in-one line). If higher-level knowledge is referenced, it must be translated into 7th-grade accessible equivalents.

## Task Completion

Every task must end by pasting the self-check report template from `checker.md` with every item marked PASS or FAIL. If any item is FAIL, fix and re-run the full checklist. The task is only complete when the report shows all PASS with `[结论] YES / YES`.

## Viewing Results

```bash
cd math/NNN
python -m http.server 8080
# Open http://localhost:8080/NNN.html
```

Run `python geometry_figures.py` to regenerate all PNG figures.
