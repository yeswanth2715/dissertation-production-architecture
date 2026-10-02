# Performance Optimization Policy

This repository optimizes dissertation delivery by separating deterministic work from academic judgement.

## Target Runtime Bands

```text
3-5 minutes:
- project already has approved knowledge base
- survey results or other primary evidence already exists
- project.yaml is complete
- only deterministic assembly and Fast QA are required

5-10 minutes:
- professor-review draft
- minor content revision
- survey analysis plus Fast QA

15-30 minutes:
- final DOCX with render QA
- figure/accessibility checks
- Word/PDF/page-image validation
```

Full research, literature synthesis, new writing, source verification, and render QA should not be expected to complete in 3-5 minutes.

## Deterministic First Rule

Use scripts before model reasoning for:

```text
- project file inventory
- document structure detection
- word counts
- survey result checks
- reliability/correlation/regression calculations
- heading and numbering scans
- placeholder scans
- internal wording scans
- DOCX package checks
- accessibility and render checks
```

The model should be used only for:

```text
- topic-specific academic writing
- literature synthesis
- research gap judgement
- methodology justification
- findings-to-discussion interpretation
- professor feedback interpretation
- final benchmark judgement
```

## Standard Commands

Optional local token-reduction bootstrap:

```powershell
rtk init -g --codex
```

Use this once per local machine/Codex profile when the `rtk` CLI is installed. This is a local runtime setup command for reducing repeated context and token use; it must not be included in professor-facing dissertation content, project appendices, or submitted artefacts.

RTK/Codex integration rule:

```powershell
Get-Command rtk -ErrorAction SilentlyContinue
rtk --version
codex doctor
codex app-server --listen ws://127.0.0.1:4500
codex agents --remote ws://127.0.0.1:4500
```

Use `rtk init -g --codex` only after the `rtk` executable is available on PATH. After configuration, future Codex sessions should read the global Codex instruction file and prefix shell commands with `rtk`. If RTK is unavailable in the active shell, continue with Codex CLI, deterministic project scripts, and bounded Codex agent work where appropriate. Keep auth tokens, bearer-token environment variables, remote addresses, app-server settings, and generated runtime configuration outside git and outside submitted dissertation artefacts.

```powershell
python scripts/scan_project.py --project <project> --write
python scripts/analyse_survey.py --project <project> --write
python scripts/fast_qa.py --project <project> --stage final --write
python scripts/render_qa.py --project <project> --write
```

One-command pipeline:

```powershell
python scripts/run_project.py --project <project> --stage final --qa fast
```

Run configured project builders only when `project.yaml` explicitly lists them:

```powershell
python scripts/run_project.py --project <project> --stage final --qa render --execute-builders
```

## Anti-Hallucination Rules

```text
- project.yaml declares the stage, method, output target, survey files, and builder scripts
- knowledge-base files remain the source of truth
- survey numbers are copied from script output, not estimated by the model
- claims must map to citation-claim-map.md, primary results, or explicit assumptions
- final outputs are regenerated only from affected inputs
- unsupported claims are removed or marked as assumptions before DOCX generation
```

## Permission Strategy

Local permissions are not part of the dissertation architecture and should not be committed with project content.

Recommended low-friction mode:

```toml
sandbox_mode = "workspace-write"
approval_policy = "never"
```

Full-control mode:

```toml
sandbox_mode = "danger-full-access"
approval_policy = "never"
```

Use full-control mode only on a trusted local machine and trusted repository. Keep private runtime settings in `/control/`, which is gitignored.

## Cache Strategy

Stable extracted rules can be cached locally under `architecture/cache/`, but cache files should not contain private student, university, or supervisor content unless they remain untracked.
