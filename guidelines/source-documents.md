# Source Documents

The architecture expects local source files such as:

```text
guidelines/source/<dissertation-guide>.pdf
guidelines/source/<referencing-guide>.pdf
templates/source/<dissertation-template>.docx
```

## Document Roles

`guidelines/source/<dissertation-guide>.pdf`

```text
Role: guideline source
Purpose: dissertation structure, word limits, submission expectations, academic writing rules, marking expectations, and embedded template sample
```

`guidelines/source/<referencing-guide>.pdf`

```text
Role: referencing guideline source
Purpose: UCA Harvard citation, bibliography, image referencing, and list-of-illustrations rules
```

`templates/source/<dissertation-template>.docx`

```text
Role: template source
Purpose: output shell, title page fields, section order, declaration page, and placeholder headings
```

## Rule

Do not overwrite source documents without approval. Files under `guidelines/source/` and `templates/source/` are local-only by default and should not be committed to GitHub. Extracted rules and reusable interpretations belong in `guidelines/`, `templates/`, and `architecture/`.
