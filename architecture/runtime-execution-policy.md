# Runtime Execution Policy

The architecture must be usable by nontechnical users. Users should not need to understand sandbox failures, RTK helper errors, PowerShell syntax, LibreOffice availability, or Python import details.

## User-Facing Rule

Expose simple commands:

```powershell
python scripts/start_here.py
```

or:

```powershell
python scripts/start_here.py --project <project> --task final
```

The scripts handle preflight, artifact inspection, runner execution, and fallback reporting internally.

## Internal Runtime Rules

```text
- Run preflight before project execution.
- Prefer direct Python scripts as the stable baseline.
- Use RTK only when detected and stable.
- If RTK/helper setup fails, fallback to direct Python.
- Do not rely on chained shell commands.
- Keep writes inside the repository/project folder.
- Treat missing LibreOffice/soffice as a render-QA limitation, not a content-generation blocker.
- Convert scary terminal failures into qa/preflight-report.md or qa/run-log.md explanations where possible.
```

## Preflight

Run:

```powershell
python scripts/preflight.py --project <project> --write
```

Checks:

```text
- Python availability
- repository write access
- project folder exists
- required scripts exist
- RTK availability
- LibreOffice/soffice availability
- python-docx availability
- openpyxl availability
```

Warnings should trigger fallbacks. Only blocking failures should stop the workflow.
