# Project Discovery

Run this before generating any topic-specific output.

## Available Inputs

```text
- dissertation topic/title:
- university/supervisor instructions:
- papers/articles:
- datasets:
- survey/interview material:
- source images/figures:
- professor feedback:
```

## Missing Inputs

```text
-
```

## Research Design Type

Choose one:

```text
survey-only
mixed-methods
secondary/case-study
conceptual
unknown
```

## Methodology Status

```text
not started / draft / approved / revised after feedback
```

## Pre-Survey Package Status

```text
not started / Introduction drafted / Chapter One drafted / Chapter Two drafted / Chapter Three drafted / approved for questionnaire
```

## Survey Questionnaire Status

```text
not required / blocked until pre-survey package / ready to generate / generated / assigned manually / results returned
```

## Required Outputs

```text
- dissertation.docx
- professor-feedback.docx/md
- survey-questionnaire.docx/md, if survey is required
```

## Next Action

```text
-
```

## Automation Command

Refresh this discovery file in a copied project folder with:

```powershell
python scripts/scan_project.py --project <topic-slug> --write
```
