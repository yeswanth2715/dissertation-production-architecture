# Guideline Adaptation Policy

The architecture must adapt when new university, course, supervisor, or referencing guidelines are provided.

## Separation Of Concerns

Guidelines define rules:

```text
- word count
- submission expectations
- chapter structure
- referencing style
- academic ethics
- assessment criteria
```

Templates define output shape:

```text
- title page layout
- page order
- heading styles
- declaration page
- table of contents position
- placeholder pages
```

## Adaptation Steps

```text
1. Add or reference the new guideline/template source.
2. Extract concrete rules.
3. Compare against current extracted rules.
4. Update relevant policy files only when process behavior changes.
5. Mark affected outputs stale.
6. Regenerate affected outputs after user approval.
7. Record the decision in the project feedback or decision log.
```

## Priority Order

```text
1. Academic integrity and plagiarism rules
2. University dissertation guide
3. Referencing guide
4. Dissertation template
5. Topic-specific professor instructions
6. User-approved special instructions
7. Model and token optimization
8. Style preferences
```

## Control Folder

`/control` is intentionally gitignored. It is not part of the durable architecture.

Use `/control` only for:

```text
- local runtime switches
- private notes
- temporary active-run state
- non-shareable settings
```
