# Evidence and Execution Harness

Final runs block failed artifact and evidence prerequisites before executing builders. Final QA cannot be disabled. The manifest's `qa.render_required_for_final` setting overrides fast QA. A missing render engine blocks required final verification while leaving generated content available for repair.

## Explicit artifacts

Set `survey.results` explicitly; arbitrary newest CSV/XLSX files are never treated as responses. Dissertation QA uses `outputs.dissertation`, defaulting to `outputs/dissertation.docx`. CLI paths and configured builder paths must resolve inside the current project. Missing configured builders fail; builders have a configurable `generation.timeout_seconds` (default 300).

These path checks prevent accidental cross-project selection. They do not sandbox Python builder code: use trusted builders and the host execution sandbox.

## Evidence ledger

Before final generation, create `knowledge-base/evidence-ledger.json` from actual inspected evidence. Use extracted UTF-8 source text, preserving page/section locators. Keep the original source and extraction alongside one another. Hash the extracted text; never fabricate passages or verification statuses.

```json
{
  "sources": [
    {"id": "S1", "path": "inputs/extracted/study.txt", "sha256": "ACTUAL_SHA256"}
  ],
  "claims": [
    {
      "id": "C001",
      "kind": "source",
      "text": "A material claim in the chapter",
      "section": "2.1",
      "source_id": "S1",
      "passage": "Exact supporting text from the extracted source",
      "locator": "page 12, paragraph 3",
      "support_review": "verified"
    }
  ],
  "output_review": {
    "sha256": "ACTUAL_OUTPUT_SHA256",
    "claims_complete": true,
    "reviewer": "Identifiable reviewer or review run"
  }
}
```

Explicit assumptions use `kind: assumption` and `disclosed: true`; they must appear as assumptions in the output. Empirical claims point to saved calculation results or experiment evidence. Verify citation metadata against the original publication before recording it.

After generation, review every material output claim and bind `output_review` to the exact output hash. Rerun QA with builders disabled after recording the review. A builder changing output invalidates the prior review. Compute hashes with `sha256sum <file>` or `hashlib.sha256`.

The ledger verifies provenance, exact passage existence, source freshness, and review binding. It does not automatically prove semantic support, discover every uncatalogued output claim, authenticate reviewer identity, or verify external bibliographic metadata. These still require academic review. A passing benchmark scorecard also remains a recorded assessment, not an independently established grade.

## Survey analysis

Without a codebook, produce item descriptions only. Never infer constructs from column count. A `knowledge-base/survey-codebook.json` may contain:

```json
{"constructs": [{"code": "A", "name": "Project-defined construct", "items": [1, 2, 3], "reverse_items": [2]}]}
```

Items are one-based indexes into detected Likert columns. Codebook analysis currently requires all columns after `survey.metadata_cols` to be valid five-point Likert items; move free-text/profile fields before that boundary or supply a dedicated Likert export. Mixed invalid columns block positional codebook analysis so indexes cannot silently shift. Invalid/rejected columns remain visible in item-only diagnostics.

Reverse items use `6 - response`. Construct scores require complete responses for their items. Item agreement percentages use valid item responses and display their denominator. Exclusions and duplicate handling must be documented and performed on a reviewed analysis input; the harness does not silently delete collected responses.

## Validation

Install dependencies from `scripts/requirements.txt`, then run:

```sh
python -m unittest discover -s scripts/tests -v
```

Regression fixtures cover wrong-artifact selection, cross-project paths, failed gates, missing builders, timeouts, invented passages, stale hashes, invalid codebooks, reverse coding, and missing-data denominators.
