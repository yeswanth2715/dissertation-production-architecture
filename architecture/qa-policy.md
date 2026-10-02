# QA Policy

The repository uses two QA modes: Fast QA for iteration and Render QA for final delivery, manifest-required finalization, or explicit user request.

Benchmark scoring is handled separately in `architecture/benchmark-policy.md`. QA checks whether requirements pass; benchmarks estimate whether the work is reaching the target grade band.

## Fast QA

Fast QA is the default for drafts and intermediate outputs.

Checks:

```text
- required sections exist
- BSBI/UCA chapter order is followed
- word-count targets are respected
- headings and subheadings are numbered correctly
- subheadings are context-based
- Chapter Four contains 4.1 Findings, 4.2 Analysis, and 4.3 Discussion
- citations have matching bibliography entries
- bibliography entries are alphabetized
- Harvard citation style is consistent
- figures have captions and source references
- figures follow `architecture/visual-style-policy.md`
- no AI-generated dissertation images are used
- professor feedback has been addressed
- placeholders are not left in final-facing outputs
- originality-risk issues are flagged
- project discovery has been completed before generation
- survey questionnaire was not generated before pre-survey package approval
- Introduction, Chapter One, Chapter Two, and Chapter Three exist before survey-questionnaire generation
- returned survey results exist before survey-based findings are generated
```

## Render QA

Render QA is slower and should be reserved for:

```text
- final dissertation DOCX
- final professor-facing DOCX
- final survey questionnaire DOCX
- files where layout correctness is the acceptance criterion
- manifest-required or explicitly requested visual inspection
```

Render QA checks:

```text
- page breaks
- title page layout
- table of contents placement
- heading hierarchy
- image placement
- figure captions
- figure readability at page width
- table formatting
- text clipping or overlap
- page numbering
- final submission readability
```

## QA Escalation

Use Fast QA until the output is content-stable. Escalate to Render QA only when the active stage, project manifest, or user request requires final layout evidence, or when a layout defect is suspected.

Before final DOCX generation, complete the topic project's `qa/benchmark-scorecard.md`.


## Runner-First QA

Fast QA should run through `scripts/fast_qa.py` before any final-readiness claim.

```powershell
python scripts/fast_qa.py --project <project> --stage final --write
```

Render QA should run only when final DOCX layout acceptance is needed:

```powershell
python scripts/render_qa.py --project <project> --write
```

If the local image viewer is blocked, render QA may use Microsoft Word PDF export, text extraction, page-image generation, nonblank-page checks, accessibility audit, and package-level checks as the fallback evidence chain.
