# Learning Routing Policy

The architecture learns only from explicit `/learn` instructions.

## Routing Decision

Every `/learn` instruction must be classified before it is stored.

```text
Deterministic, repeatable, machine-checkable rule -> scripts/utils/config/
Human judgement, academic-process, writing, or routing rule -> skills.md
Mixed rule -> split: utility config for the checkable part, skills.md for the judgement part
```

## Utility Candidates

Route to `scripts/utils/config/` when the instruction concerns:

```text
- banned/meta wording
- word-count targets
- section-count targets
- survey question limits
- reliability thresholds
- folder/artifact requirements
- final-output gates
- deterministic QA checks
- figure/table count rules
```

## Skills Candidates

Keep in `skills.md` when the instruction concerns:

```text
- academic judgement
- source synthesis
- writing style independence
- topic isolation
- professor-facing content principles
- model-routing judgement
- interpretation quality
- originality and evidence boundaries
```

## Tooling

Use the routing utility before updating architecture memory:

```powershell
python scripts/route_learn.py --instruction "/learn <instruction>"
```

The utility returns the recommended destination and matched rule families.

## Final Output Gate

Before generating a final output, the architecture must inspect existing project artifacts and write an artifact-gate report:

```powershell
python scripts/artifact_gate.py --project <project> --stage final --write
```

The project runner performs this gate automatically:

```powershell
python scripts/run_project.py --project <project> --stage final --qa fast
```

This gate does not replace academic judgement. It ensures the model does not generate from memory while ignoring existing inputs, feedback, knowledge-base files, QA reports, outputs, datasets, or scripts.
