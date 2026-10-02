# Repository Map

## Durable Architecture

```text
architecture/
```

Stores reusable policies, learning behavior, routing rules, output contracts, and QA strategy.

Key policy files include model routing, performance optimisation, QA, originality, output contracts, benchmark targets, and thesis figure visual style.

`architecture/learning-routing-policy.md` defines whether a `/learn` instruction stays in `skills.md` or becomes a machine-enforced utility rule.

`architecture/runtime-execution-policy.md` defines the nontechnical execution path, preflight checks, and fallback behavior for sandbox/tool issues.

## Source Rules

```text
guidelines/
```

Stores extracted rules and pointers to university/reference documents.

## Output Shells

```text
templates/
```

Stores template interpretations and reusable shells for future DOCX/MD artifacts.

## Repeatable Workflows

```text
workflows/
```

Stores the step-by-step operating model for sprinting, generating, reviewing, and learning.


## Automation Scripts

```text
scripts/
```

Stores deterministic project runners and checks for file discovery, survey analysis, Fast QA, Render QA, and DOCX template assembly. Scripts must not contain reusable dissertation prose.

```text
scripts/utils/
```

Stores shared deterministic utilities and machine-readable config for repeated checks such as banned wording, word-count targets, survey rules, learning routing, and artifact-gate requirements.

Technical coding project dataset rules are stored in `scripts/utils/config/technical_dataset_rules.json`.

## Local Architecture Cache

```text
architecture/cache/
```

Stores local machine-readable caches for extracted guideline/template/QA rules. Cache data is ignored by Git by default except for the README.

## Topic Work

```text
projects/
```

Stores one isolated dissertation topic per folder. Use `projects/_template/` to start a new topic.

## Local Runtime State

```text
control/
```

Gitignored. Not a durable architecture location.
