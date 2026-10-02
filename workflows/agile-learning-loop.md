# Agile Learning Loop

The workflow is iterative, but the reusable architecture only learns when `/learn` is used.

## Normal Topic Loop

```text
1. Run project discovery.
2. Add topic input.
3. Update topic knowledge base.
4. Generate the pre-survey dissertation package when survey or mixed-methods work is expected: Introduction, Chapter One, Chapter Two, and Chapter Three - Methodology.
5. Generate survey questionnaire only after pre-survey package approval.
6. Assign the questionnaire manually to project participants outside the repo.
7. Add returned survey results to the same topic project.
8. Identify stale outputs.
9. Generate approved remaining outputs.
10. Run Fast QA.
11. Collect professor feedback.
12. Update the same topic knowledge base.
13. Regenerate affected outputs.
```

This loop improves the current dissertation only.

## /learn Architecture Loop

```text
1. User gives /learn instruction.
2. Confirm it is a reusable process rule.
3. Reject if it contains topic content or source prose.
4. Update root-level skills.md.
5. Apply the learned process to future work.
```

## Stale Output Logic

Examples:

```text
Methodology changes:
- regenerate Chapter Three
- update dissertation.docx
- update viva/methodology notes if present
- rerun methodology QA

Professor feedback changes:
- update professor-feedback.md
- update affected knowledge-base files
- regenerate only affected outputs

Referencing guideline changes:
- update citation rules
- rerun citation QA
- regenerate bibliography/list of illustrations if needed
```
