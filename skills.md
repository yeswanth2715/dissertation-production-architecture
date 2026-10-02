# Architecture Skills

This file records reusable dissertation-production behavior for the overall architecture. It is the process memory for the repository.

## Learning Rule

The architecture learns only when the user explicitly writes a `/learn` instruction.

Examples:

```text
/learn Always check professor feedback before regenerating affected outputs.
/learn Keep survey questionnaires in both DOCX and MD when approved.
```

Allowed `/learn` updates:

```text
- process rules
- QA rules
- model-routing heuristics
- output naming conventions
- reusable workflow improvements
- template adaptation practices
```

Before updating architecture memory, route every `/learn` instruction:

```powershell
python scripts/route_learn.py --instruction "/learn <instruction>"
```

Routing rule:

```text
- deterministic, repeatable, machine-checkable rules go to scripts/utils/config/
- human judgement, academic-process, writing, or model-routing rules stay in skills.md
- mixed rules are split between utility config and skills.md
```

Examples:

```text
- banned wording, word-count targets, survey question limits, folder gates -> utility config
- academic style, source synthesis, topic isolation, judgement quality -> skills.md
```


Forbidden `/learn` updates:

```text
- dissertation prose from a completed topic
- literature-review paragraphs
- findings from a topic
- copied source text
- student-specific private data
- reusable arguments that belong to one dissertation
```

## Utility Conversion Skill

When a learned rule can be checked deterministically, prefer converting it into reusable code/config rather than leaving it only as prose.

Machine-checkable rule types:

```text
- banned/meta wording scans
- word-count and section-target checks
- figure/table/caption counts
- survey question range checks
- Cronbach alpha and reliability thresholds
- folder and artifact-gate requirements
- final-output readiness gates
- deterministic file inventory and stale-output checks
- official/public dataset sourcing rules for technical coding projects
```

Required behavior:

```text
- keep reusable dissertation prose out of scripts and configs
- store checkable constants in scripts/utils/config/
- store reusable code in scripts/utils/
- keep human academic judgement and writing principles in skills.md
- update docs when a new utility changes the architecture workflow
```

## Final Artifact Read Gate Skill

Before generating a final dissertation or professor-facing output, inspect the existing project artifacts first.

Required behavior:

```text
- run project discovery
- run the artifact gate
- read/inspect current inputs, knowledge-base files, feedback, QA reports, existing outputs, datasets, scripts, and result files where present
- use the artifact-gate report to avoid generating from memory or ignoring existing files
- only then generate or regenerate the requested final output
```

Command:

```powershell
python scripts/artifact_gate.py --project <project> --stage final --write
```

The standard runner performs this automatically:

```powershell
python scripts/run_project.py --project <project> --stage final --qa fast
```

## Technical Coding Dataset Skill

When a project is technical, coding-based, experimental, model-training, simulation, dashboard, robotics, computer-vision, forecasting, NLP, or data-science focused, do not wait silently for the user to provide a dataset.

Required behavior:

```text
- identify whether the dissertation needs a dataset, benchmark, simulator, API export, or generated experimental logs
- prefer official, public, research-lab, government/open-data, paper-linked, competition, or well-documented benchmark datasets
- avoid unclear licence data, random uncited images, private data without permission, and AI-generated data presented as empirical evidence
- record dataset name, source URL, licence/access terms, relevance, sample size, selection/exclusion criteria, preprocessing, split, and limitations
- if dataset choice changes methodology, scope, runtime, cost, ethics, or download size, ask the user before committing
- if the user already provided a dataset, validate it first before suggesting replacement
- place technical code, dataset notes, and outputs in the project evidence/package structure required by the architecture
```

## Topic Isolation Skill

Every dissertation topic must start from a fresh knowledge base.

Reusable:

```text
- architecture policies
- QA workflow
- template handling
- guideline adaptation approach
- learned process instructions from /learn
```

Not reusable:

```text
- research claims
- source summaries specific to a topic
- citations selected for a topic
- methodology justification written for a topic
- data, findings, analysis, and discussion
```

## Source-Based Writing Skill

Generated academic writing must be synthesis-based.

Required behavior:

```text
- map every material claim to a source, finding, or explicit project assumption
- avoid close paraphrasing of source sentences
- use direct quotations rarely
- cite direct quotations with page numbers where available
- write in an academic, impersonal voice
- maintain Harvard-style citation and bibliography consistency
```

## Heading Skill

Subheadings must be context-based and numbered according to their parent chapter.

Examples:

```text
1.1 Strategic Context of Agile Adoption
1.2 Delivery Constraints in Remote Software Teams
2.1 Critical Success Factors in Agile Implementation
3.1 Research Philosophy and Design Rationale
4.1.1 Survey Response Profile
4.2.1 Interpretation of Delivery Performance Findings
4.3.1 Comparison With Prior Literature
```

Generic subheadings should be rejected during QA unless they are required by the university template.

## Output Approval Skill

Do not create final dissertation content artifacts until the user approves the output request.

Architecture artifacts, skeletons, policies, and templates may be created when requested. Topic-specific dissertation content requires explicit approval.


## Survey Questionnaire Design Skill

When a project needs a survey questionnaire DOCX, handle existing and new questionnaires differently.

Required behavior:

```text
- if the project already includes a survey questionnaire, do not disturb, rewrite, or renumber it unless the user explicitly asks for questionnaire improvement
- validate the existing survey against the topic, methodology, research questions, variables, and university guideline before using it in the dissertation
- if generating a survey questionnaire from scratch, create a strong, focused instrument with ideally 15 to 25 questions
- include consent, screening/profile questions, core construct questions, outcome/performance questions, enabling/barrier questions, and 1 to 3 open-ended questions where suitable
- avoid bloated surveys; every question must support a research question, variable, hypothesis/proposition, or analysis need
- design Likert questions so they can be analysed cleanly using descriptive statistics, reliability checks, and cautious correlation/regression only when the sample and scale quality support it
- design survey constructs before writing questions, with 3 to 5 aligned Likert items per important construct where reliability will be tested
- avoid mixing different constructs inside one scale; keep wording consistent, specific, non-leading, and not double-barrelled
- use a consistent response scale direction and clearly mark any reverse-coded items so reliability calculations are valid
- where possible, pilot the survey before distribution and revise weak, confusing, or overlapping items before collecting final responses
- target Cronbach alpha of 0.70 or above for multi-item constructs, but never hide, inflate, or rewrite collected results to claim stronger reliability than the data supports
- if an already collected survey has weak reliability, report it honestly, shift the analysis toward item-level/descriptive interpretation, and state the limitation clearly
- remind the user before creating a new survey questionnaire that 15 to 25 well-designed questions is the target range unless the university guideline or supervisor asks otherwise
- keep the survey DOCX independent per project and do not reuse another project's survey wording unless the user explicitly approves adaptation
```

## Template Preservation Skill

For final dissertation DOCX output, do not recreate the document from scratch when an approved university template is available.

Required behavior:

```text
- keep the original template file untouched in templates/source/
- duplicate the approved template into the topic output folder
- insert and align dissertation content inside the duplicated file
- preserve the template page order, title page, declarations, TOC position, heading styles, page breaks, and formatting conventions
- replace only approved placeholder/content areas
- run Fast QA before final delivery and Render QA when final DOCX layout approval is required
```

Default output path:

```text
projects/<topic>/outputs/dissertation.docx
```

## Manual Front-Matter Completion Skill

Personal front-matter fields are not treated as academic-content defects unless the user explicitly asks for final front-matter completion.

Manual completion items include:

```text
- Master title
- student name
- year
- acknowledgement personalisation
- declaration signature/name/date fields
- dotted placeholder lines intended for manual form completion
```

Required behavior:

```text
- flag these items as manual completion notes, not major dissertation risks
- do not rewrite or invent personal details
- do not block distinction benchmark validation only because these fields are blank
- check them only during final submission-readiness QA or when the user asks
```

## Model Routing Execution Skill

For dissertation project work, choose the smallest capable model tier for each task after the accuracy requirement is clear.

Required behavior:

```text
- use deterministic tools for file listing, OCR, word counts, heading scans, table/image counts, and survey value counts
- use a fast/low-cost model tier for extraction, classification, checklist generation, stale-output detection, and citation formatting from complete metadata
- use a balanced model tier for project summaries, professor-feedback summaries, knowledge-base updates, and ordinary drafting
- use a high-reasoning model tier only for literature synthesis, methodology justification, findings-to-discussion mapping, originality review, and final benchmark judgement
- record the selected tier and reason in the project QA/model usage log
- regenerate only affected outputs instead of resending or rewriting the full dissertation
```

## Strict Guideline And Artifact Validation Skill

Do not call any dissertation output final, high-distinction, professor-ready, or submission-ready until each required artifact has been validated one by one against the active guideline, template, professor feedback, and benchmark rules.

Required behavior:

```text
- validate each artifact separately: dissertation DOCX, professor-feedback artifact, survey questionnaire, QA checklist, benchmark scorecard, citation audit, and knowledge-base files
- verify every major output claim against the knowledge base, source file, survey data, cited source, or explicit project assumption
- do not invent or assume missing guideline rules
- run a chapter-level and total word-count check against the active university guideline before calling a dissertation final-ready
- if the dissertation is materially below the required word-count target or chapter allocation, mark it as underdeveloped and not final-ready
- do not use high-distinction naming or wording unless benchmark, word-count, structure, citation, feedback, and originality checks all pass
- report validation gaps clearly before generating or delivering the final DOCX
- use deterministic tools for counts, file checks, table checks, and dataset checks before using model judgement
```

## MSc Examiner And Final-Submission Audit Skill

When the user invokes `/learn` with a dissertation-review or final-submission audit rule, apply the following reusable review protocol to every future dissertation review:

```text
- act as a strict MSc examiner and final-submission auditor
- check title, research questions and objectives for alignment
- check consistency across the abstract, literature, methodology, findings, discussion and conclusion
- verify survey-to-results traceability
- verify all numbers, statistics, tables and figures against the underlying evidence
- check Cronbach alpha calculation, interpretation and limitations
- distinguish country claims from the evidence actually collected
- detect unsupported claims, causal language and overgeneralisation
- check citation-bibliography consistency and source quality
- check terminology, tense and unnecessary repetition
- check ethics, formatting and unresolved placeholders
- trace every recommendation back to evidence
- aggressively scan for AI, meta and drafting instructions, including phrases such as
  "high-distinction", "high-quality dissertation", "final dissertation should",
  "fieldwork should", "should be added", "Level 7", and wording about how the
  dissertation ought to be written
- do not invent issues; report only evidence-backed defects
- exclude internal test, pilot, validation and placeholder responses from survey analysis before calculating themes, percentages or reliability
- scan both paragraphs and table cells for examiner/meta/drafting language before delivery; zero matches are required
- verify that findings chapter labels match the research method; do not use experimental or technical-evaluation terminology for survey-only studies
- verify table and figure captions in the order they appear in the body, not only in the list of tables or figures
- when a survey result uses question-specific valid denominators, state that denominator explicitly in the dissertation

```

For each genuine issue, report:

```text
- location
- original wording
- why it is problematic
- exact replacement
- severity: Critical, Major or Minor
```

Finish every such audit with:

```text
- estimated grade
- submission-readiness verdict
- remaining evidence or QA limitations
```

This rule is an internal review protocol and must never be copied into professor-facing dissertation content.


## Final Academic Wording Review Skill

When the user invokes `/learn` with a final wording-review instruction, apply this reusable protocol to future dissertation polishing:

```text
- improve only academic wording, grammar, clarity, consistency and flow
- do not change the research design, methodology, results, citations, data values, research questions, argument meaning, or evidence boundary
- remove meta, examiner-facing, process-facing, and "student dissertation" wording from professor-facing content
- replace broad terms such as "validates" with precise evidence-based wording such as "supports", "provides evidence for", "indicates", or "is consistent with" where the evidence does not prove full validation
- remove repetition and overclaims while preserving the existing contribution
- keep writing natural, MSc-level and topic-specific, avoiding generic AI-style phrasing
- check methodology and results consistency before delivery, especially where methodology mentions centreline, candidate, simulation, survey, or physical evaluation that may not have been measured
- run a final consistency check across research questions, findings, discussion and conclusion after wording edits
- do not add new claims, fabricated evidence, new citations, new experiments or new results during wording polish
```

This rule improves professor-facing academic polish only; it must not be copied into dissertation prose.

## Pre-Humaniser Word Count Buffer Skill

When preparing any dissertation DOCX that may later be humanised or manually expanded, do not write exactly to the maximum or ideal word count during AI drafting.

Required behavior:

- Use a pre-humaniser target buffer of approximately 85% to 92% of the section's ideal or maximum word count unless the active university guideline requires a strict minimum.
- Example: if an abstract target is 200 words, draft around 165 to 180 words before humanising.
- Example: if a literature-review section target is 2,000 words, draft around 1,700 to 1,850 words before humanising.
- After humanising or manual editing, run a fresh word-count check at chapter and section level.
- Do not make sections so short that they become shallow, underdeveloped, or below the guideline expectation.
- If there is a conflict between the buffer and a required minimum word count, the guideline wins.

## Source-Based Figure Replacement Skill

For any dissertation DOCX, audit images and figures before final delivery.

Required behavior:

- Reject low-quality, irrelevant, decorative, or AI-generated images unless the user explicitly approves them for a non-submission draft.
- Prefer publicly sourced, academically relevant figures, article-style visuals, institutional/public report charts, or self-created charts based directly on the project's survey/data.
- Every external image or figure must have a credible source note, citation, and license/usage check where needed.
- For high-distinction work, figures must support the argument, methodology, conceptual framework, or findings; they should not be used as decoration.
- When survey data exists, prioritise original charts generated from the validated dataset over generic web images.
- Keep figure numbering and captions consistent with the chapter numbering and Harvard/source requirements.
- Apply `architecture/visual-style-policy.md` to generated diagrams, charts, conceptual frameworks, and figure replacements.
- Use a publication-quality academic style: white or very light neutral background, deep academic navy, muted blue-grey, restrained research blue, muted teal only for emphasis, thin borders, precise arrows, flat vector geometry, and modern academic sans-serif labels.
- Avoid saturated colours, AI-style gradients, glowing effects, 3D/isometric corporate visuals, cartoon illustrations, stock-image aesthetics, photorealistic people, decorative blobs, robots, and futuristic AI imagery.
- Do not treat generated visuals as empirical evidence; evidence figures must be source-backed or data-derived.



## Chapter-Level Figure Coverage Skill

When building or revising dissertation DOCX outputs, plan figures chapter by chapter rather than adding visuals only at the end.

Required behavior:

- Add figures only when they improve evidence, explanation, methodology, analysis, comparison, or interpretation.
- Prefer 1 to 2 meaningful figures in the Introduction where they establish the problem, scope, or core evidence context.
- Prefer 1 to 3 meaningful figures across literature chapters where they synthesise frameworks, compare concepts, or clarify the evidence gap.
- Include methodology figures where they make the research design, data flow, sampling, constructs, or analysis route reproducible.
- For final survey or empirical chapters, prioritise original result charts generated from validated project data.
- Avoid decorative images, generic stock visuals, AI-looking illustrations, and images that are not discussed in the surrounding prose.
- Every figure must have chapter-correct numbering, an informative caption, a source note, and explicit discussion in the text.
- Figure density should support high-distinction readability without crowding the dissertation or reducing analytical depth.
- Keep all professor-facing figure text free from internal process wording such as project numbers, `/learn`, QA, model choices, and artifact-folder language.
## Local Token-Reduction CLI Bootstrap Skill

When the `rtk` CLI is installed, initialise the local/global Codex context once with:

```powershell
rtk init -g --codex
```

Required behavior:

```text
- treat this as local runtime setup, not a professor-facing dissertation step
- do not run it repeatedly for every project unless the Codex/RTK profile changes
- keep any generated global configuration private and out of submitted project outputs
- feature-detect RTK first with `Get-Command rtk -ErrorAction SilentlyContinue` or `rtk --version`
- if RTK is unavailable, do not claim it was used; use Codex CLI/app-server and deterministic scripts as the fallback path
- after RTK is configured and visible to the current shell, prefix shell commands with `rtk` to reduce command-output tokens
- verify Codex readiness with `codex doctor` before relying on agent workflows
- use Codex agents only for bounded, project-isolated tasks where parallel work reduces time without mixing project writing styles
- continue using deterministic project scripts for scan, survey analysis, Fast QA and render QA
```

## Professor-Facing Content Separation Skill

Professor-facing dissertation and protocol outputs must not expose repository, agent, or internal workflow language.

Required behavior:

- Keep internal labels such as `Project 1`, `Project 2`, `Project 5`, `/learn`, `QA`, `artifact folder`, `pre-evaluation stage`, `fallback`, and model/tool decisions out of the dissertation body, figure text, captions, protocol body, and appendices unless the university template explicitly requires them.
- Do not place architecture rules, process notes, or assistant reasoning inside academic figures. Figures should show academic flows, frameworks, architectures, datasets, methods, results, or conceptual relationships.
- Avoid professor-facing wording such as "this will be done later", "I did this", "the agent decided", "survey was weak", or "replaces a survey". Use neutral academic phrasing such as "the study evaluates", "the methodology applies", "the evidence comprises", or "the results section reports validated outputs".
- Store internal process decisions in `knowledge-base/`, `qa/`, `project-discovery.md`, or local work logs only.
- Before delivery, scan DOCX and MD outputs for internal workflow language and clean any matches from professor-facing content.


## Survey Results Disclosure Skill

For dissertation survey projects, keep raw survey diagnostics separate from professor-facing dissertation prose.

Required behavior:

- Preserve the raw survey export unchanged and run deterministic QA before writing findings.
- Report academically relevant aggregate evidence in the dissertation: sample size, eligibility, missingness/exclusions where applicable, item distributions, reliability, construct means, and defensible relationships.
- Keep platform/export timing details, low-level response-quality flags, tool notes, and internal QA wording inside project `qa/` or work logs unless they materially change the usable analytical sample or the user explicitly asks to include them.
- Do not fabricate, delete, or alter survey values to hide a problem. If a data issue changes exclusions, validity, reliability, or interpretation, disclose it in academically appropriate limitation language.
- Use neutral limitation wording in final dissertations, such as cross-sectional design, self-reported perceptions, purposive sampling, and absence of technical telemetry.


## Deterministic Runner First Skill

For dissertation projects, use the deterministic runner and QA scripts before asking the model to infer project state or judge final readiness.

Required behavior:

```text
- run `scripts/scan_project.py --write` at the start of a project or when files change
- run `scripts/analyse_survey.py --write` before writing survey findings from returned results
- run `scripts/fast_qa.py --write` before final-readiness or benchmark claims
- run `scripts/render_qa.py --write` only for final DOCX layout acceptance or when explicitly requested
- do not estimate file names, survey numbers, word counts, table counts, image counts, or heading defects when scripts can verify them
- do not use high-reasoning model effort for deterministic checks
- keep scripts free of reusable dissertation prose so project writing style remains topic-specific
```
