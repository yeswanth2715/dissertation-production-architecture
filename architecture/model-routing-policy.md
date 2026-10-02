# Model Routing Policy

The model router selects the smallest capable model for the task. Accuracy is optimized first; cost and latency are optimized after the quality target is met.

## Routing Tiers

### Tier 1: Fast / Low Cost

Use for deterministic, repetitive, or low-risk tasks:

```text
- classify input documents
- extract headings and sections
- summarize small document chunks
- generate checklists
- detect missing fields
- format citations from complete metadata
- identify stale outputs after a knowledge-base change
```

### Tier 2: Balanced

Use for normal dissertation operations:

```text
- create chapter outlines
- update knowledge-base notes
- summarize professor feedback
- draft supervisor progress updates
- create survey questionnaire drafts
- rewrite short sections for clarity
```

### Tier 3: High Reasoning

Use when correctness, synthesis, or academic judgment matters:

```text
- research gap analysis
- literature synthesis across many sources
- methodology selection and justification
- rejected-methods rationale
- findings-to-analysis mapping
- discussion that connects primary and secondary research
- final rubric review
- originality-risk review
```

## Token Reduction Rules

```text
1. Use extraction tools before model calls where possible.
2. Send only relevant knowledge-base sections to the model.
3. Summarize large source files once and reuse the summary.
4. Do not send the full dissertation for a local chapter task.
5. Regenerate only stale outputs.
6. Prefer short, structured outputs for internal artifacts.
7. Track model, reason, input size, output size, and result quality.
```

## Usage Log

Each substantial generation should record:

```text
date
topic project
task
selected model tier
reason for selection
inputs used
outputs produced
quality result
follow-up required
```

Concrete model names should remain configurable because model availability and pricing change over time.



## Automation Routing Gate

Before any model writing or benchmark judgement, run deterministic project checks where applicable:

```powershell
python scripts/scan_project.py --project <project> --write
python scripts/analyse_survey.py --project <project> --write
python scripts/fast_qa.py --project <project> --stage final --write
```

Use the model only after these scripts have produced compact, inspectable evidence. This prevents the model from guessing project state, survey numbers, file names, word counts, or heading defects.

## Default Reasoning Effort

```text
- deterministic scripts: no model
- simple classification, extraction, checklist generation: low reasoning
- ordinary summaries, short section drafting, project notes: medium reasoning
- literature synthesis, methodology defence, findings-to-discussion mapping, benchmark judgement: high reasoning
```

Do not use high reasoning merely because an output is long. Use high reasoning only where judgement, synthesis, or academic risk justifies the extra cost and latency.
