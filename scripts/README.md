# Dissertation Automation Scripts

These scripts handle deterministic workflow steps so the model spends fewer tokens on file access, counting, survey maths, and repeated QA.

## Standard Commands

Nontechnical entrypoint:

```powershell
python scripts/start_here.py
```

Direct noninteractive use:

```powershell
python scripts/start_here.py --project <project> --task discover
python scripts/start_here.py --project <project> --task final
```

Optional one-time local token-reduction setup when the `rtk` CLI is installed:

```powershell
rtk init -g --codex
```

This is a runtime bootstrap command for Codex CLI, not a per-project dissertation command. Keep generated global settings outside submitted project outputs.

If RTK is not installed, keep using the deterministic scripts and the Codex CLI/app-server path:

```powershell
codex doctor
codex app-server --listen ws://127.0.0.1:4500
codex agents --remote ws://127.0.0.1:4500
```

Only use remote agent sessions for bounded, project-isolated tasks. Do not use scripts or agent setup files to store dissertation prose, private tokens, or project-specific writing style.

```powershell
python scripts/preflight.py --project <project> --write
python scripts/scan_project.py --project <project> --write
python scripts/artifact_gate.py --project <project> --stage final --write
python scripts/analyse_survey.py --project <project> --write
python scripts/fast_qa.py --project <project> --stage final --write
python scripts/render_qa.py --project <project> --write
```

Route a new `/learn` instruction before updating memory:

```powershell
python scripts/route_learn.py --instruction "/learn <instruction>"
```

Run a whole deterministic pipeline:

```powershell
python scripts/run_project.py --project <project> --stage final --qa fast
```

Run configured project builder scripts plus final render QA:

```powershell
python scripts/run_project.py --project <project> --stage final --qa render --execute-builders
```

## Script Roles

```text
common.py                    shared path, manifest, word-count helpers
preflight.py                 nontechnical runtime/environment check
start_here.py                simple interactive/nontechnical entrypoint
artifact_gate.py             inspect existing project artifacts before final output generation
route_learn.py               classify /learn updates into skills.md or utility config
scan_project.py              compact project inventory and discovery update
analyse_survey.py            deterministic survey statistics and QA notes
fast_qa.py                   structure/content checks without render cost
render_qa.py                 Word/PDF/page-image final DOCX checks
build_docx_from_template.py  duplicate a template and optionally append project-specific Markdown
run_project.py               pipeline wrapper for common stages
```

Scripts should not contain reusable dissertation prose. They provide structure, calculations, validation, and assembly only.

## Utility Layer

```text
scripts/utils/
```

Contains reusable code and config for repeated deterministic rules:

```text
rules.py                         loads machine-readable architecture rules
artifact_gate.py                 shared artifact inspection functions
config/banned_terms.json         professor-facing/internal wording blocks
config/wordcount_targets.json    section-level pre-humaniser targets
config/survey_rules.json         survey design and reliability thresholds
config/artifact_requirements.json final-output artifact gate rules
config/learn_routing_rules.json  /learn routing rules
```

Human academic judgement stays in `skills.md`. Machine-checkable rules belong in `scripts/utils/config/`.
