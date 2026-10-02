# Dissertation Topic Template

Copy this folder to start a new topic:

```text
projects/<topic-slug>/
```

Each topic must have a fresh knowledge base. Do not copy research claims, literature review prose, findings, or discussion from another topic.

## Folder Roles

```text
inputs/          raw topic-specific source files
knowledge-base/  structured source of truth
feedback/        professor and reviewer feedback
qa/              fast QA and final QA records
outputs/         generated topic artifacts
```

Before a final dissertation output is treated as ready, complete `qa/benchmark-scorecard.md`.


## Project Manifest

Each project should fill `project.yaml` before generation. This lets the runner identify method type, survey files, word-count target, template source, QA mode, and optional project-specific builder scripts without relying on chat memory.

Fast path:

```powershell
python scripts/run_project.py --project <topic-slug> --stage final --qa fast
```

Final layout path:

```powershell
python scripts/run_project.py --project <topic-slug> --stage final --qa render --execute-builders
```
