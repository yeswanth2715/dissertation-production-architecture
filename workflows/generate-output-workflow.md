# Generate Output Workflow

Use this workflow after the user approves creation of a topic-specific output.

For nontechnical use, start with:

```powershell
python scripts/start_here.py --project <project> --task final
```

The entrypoint runs preflight, artifact gate, project runner, and QA without requiring the user to understand sandbox/runtime details.

## Steps

```text
1. Run runtime preflight.
2. Run project discovery before generation.
3. Run the artifact gate so existing project artifacts are inspected before final output generation.
4. Identify what exists in the topic project and what is missing.
5. Classify research design: survey-only, mixed-methods, secondary/case-study, or conceptual.
6. If technical/coding-based, identify whether an official/public dataset, benchmark, simulator, API export, or experiment log is needed.
7. Confirm requested output type.
8. Load applicable guidelines and template rules.
9. Load only relevant knowledge-base files.
10. Select model tier using architecture/model-routing-policy.md.
11. Enforce the pre-survey package gate for survey-related outputs.
12. Apply `architecture/visual-style-policy.md` to diagrams, charts, and figure replacements.
13. Generate draft output.
14. Run Fast QA.
15. Update feedback or stale-output register.
16. If final DOCX is requested, run Render QA only when `project.yaml`, the active stage, or the user request marks final layout QA as required.
17. Deliver output and record generation notes.
```

## Pre-Survey Package Gate

The survey questionnaire must not be generated before the dissertation has been drafted and approved up to and including Chapter Three - Methodology, following the BSBI/UCA guide and template.

Required before questionnaire generation:

```text
- Introduction
- Chapter One - Literature Review I
- Chapter Two - Literature Review II
- Chapter Three - Methodology
- research aim, objectives, and research questions
- methodology direction, sampling, ethics, and analysis plan
```

```text
Survey-only project:
- the pre-survey package defines the topic, literature basis, survey design, sampling, ethics, and analysis plan
- questionnaire is generated after pre-survey package approval
- survey results are manually collected outside the repo
- returned results drive findings, analysis, and discussion

Mixed-methods project:
- the pre-survey package defines survey plus any interview, case-study, or secondary-data component
- survey questionnaire is generated only for the survey component
- returned survey results are combined with other evidence in Chapter Four

Secondary/case-study project:
- no questionnaire unless the approved pre-survey package later adds primary survey data

Conceptual project:
- no questionnaire unless the approved pre-survey package later adds empirical data collection
```

## Technical Coding Dataset Gate

For technical/coding-based projects, the architecture should not wait silently for the user to provide data.

Required behavior:

```text
- inspect whether the project already contains a dataset, code, logs, outputs, or technical evidence
- if no dataset exists, identify suitable official/public datasets or benchmarks
- ask before using a dataset when the choice affects methodology, scope, runtime, cost, ethics, or download size
- record dataset source, licence/access terms, selection criteria, preprocessing, split, and limitations
- use actual experiment/code outputs only; do not invent technical results
```

## Output Naming

```text
dissertation.docx
professor-feedback.md
professor-feedback.docx
survey-questionnaire.md
survey-questionnaire.docx
```

## Regeneration Rule

Do not regenerate every output by default. Regenerate only files affected by the knowledge-base or guideline change.


## Optimized Runner Path

Use the deterministic runner before model writing or final judgement:

```powershell
python scripts/run_project.py --project <project> --stage discover --qa none
python scripts/run_project.py --project <project> --stage survey-analysis --qa fast
python scripts/run_project.py --project <project> --stage final --qa fast
```

For explicit artifact inspection:

```powershell
python scripts/artifact_gate.py --project <project> --stage final --write
```

Use render QA only for final professor/submission documents:

```powershell
python scripts/run_project.py --project <project> --stage final --qa render --execute-builders
```

The runner does not provide reusable dissertation prose. It supplies project discovery, survey analysis, QA reports, and optional execution of project-specific builders listed in `project.yaml`.
