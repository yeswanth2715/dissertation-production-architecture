from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from common import dump_json, latest_file, load_manifest, project_path, rel, write_text


STANDARD_17_CONSTRUCTS = [
    {"code": "LR", "name": "Legacy readiness", "items": [1, 2, 3]},
    {"code": "EM", "name": "Engineering-management capability", "items": [4, 5, 6]},
    {"code": "RG", "name": "Responsible AI governance", "items": [7, 8, 9, 10]},
    {"code": "CV", "name": "Cost and value management", "items": [11, 12, 13]},
    {"code": "IF", "name": "Integration feasibility", "items": [14, 15, 16, 17]},
]


def likert_value(value: Any) -> float:
    if pd.isna(value):
        return np.nan
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value) if 1 <= float(value) <= 5 and float(value).is_integer() else np.nan
    match = re.match(r"^\s*([1-5])(?:\s|$|[-:.)])", str(value))
    return float(match.group(1)) if match else np.nan


def cronbach_alpha(frame: pd.DataFrame) -> float:
    clean = frame.dropna()
    k = clean.shape[1]
    if k <= 1 or clean.empty:
        return np.nan
    total_var = clean.sum(axis=1).var(ddof=1)
    if not total_var or math.isnan(total_var):
        return np.nan
    item_var = clean.var(axis=0, ddof=1).sum()
    return float((k / (k - 1)) * (1 - item_var / total_var))


def survey_questions(path: Path | None) -> list[str]:
    if path is None or not path.exists() or path.suffix.lower() != ".docx":
        return []
    try:
        from docx import Document
    except Exception:
        return []
    try:
        doc = Document(path)
    except Exception:
        return []
    texts = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    return [re.sub(r"^\d+\.\s*", "", text) for text in texts if re.match(r"^\d+\.", text)]


def resolve_results(project_dir: Path, explicit: str | None, manifest: dict[str, Any]) -> Path:
    if explicit:
        path = Path(explicit)
        if not path.is_absolute():
            path = project_dir / path
        return path
    configured = manifest.get("survey", {}).get("results") if isinstance(manifest.get("survey"), dict) else None
    if configured:
        path = Path(str(configured))
        if not path.is_absolute():
            path = project_dir / path
        return path
    found = latest_file(project_dir, ["*.xlsx", "*.csv", "*.tsv"])
    if found is None:
        raise FileNotFoundError("No survey result file found. Provide --results or set survey.results in project.yaml.")
    return found


def resolve_questionnaire(project_dir: Path, explicit: str | None, manifest: dict[str, Any]) -> Path | None:
    if explicit:
        path = Path(explicit)
        return path if path.is_absolute() else project_dir / path
    configured = manifest.get("survey", {}).get("questionnaire") if isinstance(manifest.get("survey"), dict) else None
    if configured:
        path = Path(str(configured))
        return path if path.is_absolute() else project_dir / path
    outputs = project_dir / "outputs"
    search_roots = [outputs, project_dir] if outputs.exists() else [project_dir]
    pattern_groups = [
        ["*Questionnaire*.docx", "*questionnaire*.docx"],
        ["*Survey_Questionnaire*.docx", "*survey_questionnaire*.docx"],
        ["*Survey*.docx", "*survey*.docx"],
    ]
    for base in search_roots:
        for patterns in pattern_groups:
            found = latest_file(base, patterns)
            if found and "dissertation" not in found.name.lower():
                return found
    return None


def read_results(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix == ".tsv":
        return pd.read_csv(path, sep="\t")
    raise ValueError(f"Unsupported survey result format: {path.suffix}")


def detect_likert_columns(df: pd.DataFrame, metadata_cols: int) -> tuple[list[str], pd.DataFrame]:
    candidates = list(df.columns[metadata_cols:])
    likert_cols: list[str] = []
    parsed: dict[str, pd.Series] = {}
    for col in candidates:
        series = df[col].map(likert_value)
        nonmissing = df[col].notna().sum()
        valid = series.notna().sum()
        if nonmissing > 0 and valid == nonmissing:
            likert_cols.append(str(col))
            parsed[str(col)] = series
    return likert_cols, pd.DataFrame(parsed)


def load_constructs(project_dir: Path, likert_count: int) -> list[dict[str, Any]]:
    codebook = project_dir / "knowledge-base" / "survey-codebook.json"
    if codebook.exists():
        data = json.loads(codebook.read_text(encoding="utf-8"))
        constructs = data.get("constructs", [])
        if constructs:
            return constructs
    if likert_count == 17:
        return STANDARD_17_CONSTRUCTS
    if likert_count and likert_count % 5 == 0:
        group = likert_count // 5
        return [
            {"code": f"C{i}", "name": f"Construct {i}", "items": list(range((i - 1) * group + 1, i * group + 1))}
            for i in range(1, 6)
        ]
    return []


def analyse(project: str | Path, results: str | None = None, questionnaire: str | None = None, metadata_cols: int = 6) -> dict[str, Any]:
    root = project_path(project)
    manifest = load_manifest(root)
    results_path = resolve_results(root, results, manifest)
    questionnaire_path = resolve_questionnaire(root, questionnaire, manifest)
    df = read_results(results_path)
    survey_cols = list(df.columns[metadata_cols:])
    questions = survey_questions(questionnaire_path)
    likert_cols, likert = detect_likert_columns(df, metadata_cols)

    constructs = load_constructs(root, len(likert_cols))
    construct_rows = []
    scores: dict[str, pd.Series] = {}
    for construct in constructs:
        indexes = [int(i) - 1 for i in construct.get("items", [])]
        cols = [likert_cols[i] for i in indexes if 0 <= i < len(likert_cols)]
        if not cols:
            continue
        frame = likert[cols]
        score = frame.mean(axis=1)
        scores[str(construct["code"])] = score
        construct_rows.append(
            {
                "code": construct["code"],
                "name": construct.get("name", construct["code"]),
                "items": len(cols),
                "alpha": cronbach_alpha(frame),
                "mean": float(score.mean()),
                "sd": float(score.std(ddof=1)),
            }
        )

    score_frame = pd.DataFrame(scores)
    correlations = []
    if "IF" in score_frame.columns:
        for code in [c for c in score_frame.columns if c != "IF"]:
            corr = score_frame[[code, "IF"]].corr().iloc[0, 1]
            correlations.append({"code": code, "with": "IF", "pearson_r": float(corr)})

    regression = None
    if "IF" in score_frame.columns and len(score_frame.columns) > 2:
        try:
            import statsmodels.api as sm

            predictors = [c for c in score_frame.columns if c != "IF"]
            x = sm.add_constant(score_frame[predictors])
            model = sm.OLS(score_frame["IF"], x).fit()
            regression = {
                "outcome": "IF",
                "predictors": predictors,
                "r_squared": float(model.rsquared),
                "adjusted_r_squared": float(model.rsquared_adj),
                "f_pvalue": float(model.f_pvalue),
                "coefficients": {
                    code: {
                        "coef": float(model.params[code]),
                        "p": float(model.pvalues[code]),
                    }
                    for code in predictors
                },
            }
        except Exception as exc:
            regression = {"error": str(exc)}

    duplicate_id_count = None
    id_col = next((c for c in df.columns if str(c).strip().lower() == "id"), None)
    if id_col is not None:
        duplicate_id_count = int(df[id_col].duplicated().sum())

    item_rows = []
    for index, col in enumerate(likert_cols, start=1):
        series = likert[col]
        counts = series.value_counts().reindex([1, 2, 3, 4, 5], fill_value=0)
        item_rows.append(
            {
                "item": index,
                "column": col,
                "mean": float(series.mean()),
                "sd": float(series.std(ddof=1)),
                "agree_count": int(counts.loc[4] + counts.loc[5]),
                "agree_pct": float((counts.loc[4] + counts.loc[5]) / len(df) * 100),
            }
        )

    return {
        "project": root.name,
        "results_file": rel(results_path),
        "questionnaire_file": rel(questionnaire_path) if questionnaire_path else None,
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "survey_columns": len(survey_cols),
        "questionnaire_questions": len(questions),
        "survey_question_count_match": bool(questions and len(questions) == len(survey_cols)),
        "missing_survey_cells": int(df[survey_cols].isna().sum().sum()) if survey_cols else 0,
        "duplicate_respondent_ids": duplicate_id_count,
        "exact_duplicate_rows": int(df.duplicated().sum()),
        "likert_columns": len(likert_cols),
        "invalid_likert_cells": int(likert.isna().sum().sum()),
        "item_summary": item_rows,
        "construct_summary": construct_rows,
        "correlations": correlations,
        "regression": regression,
    }


def markdown(result: dict[str, Any]) -> str:
    lines = [
        "# Survey Results Analysis",
        "",
        f"Project: `{result['project']}`",
        f"Results file: `{result['results_file']}`",
        f"Questionnaire file: `{result['questionnaire_file']}`",
        "",
        "## Dataset Check",
        "",
        f"- Rows: {result['rows']}",
        f"- Columns: {result['columns']}",
        f"- Survey result columns: {result['survey_columns']}",
        f"- Questionnaire questions detected: {result['questionnaire_questions']}",
        f"- Question count match: {result['survey_question_count_match']}",
        f"- Missing survey cells: {result['missing_survey_cells']}",
        f"- Duplicate respondent IDs: {result['duplicate_respondent_ids']}",
        f"- Exact duplicate rows: {result['exact_duplicate_rows']}",
        f"- Likert columns detected: {result['likert_columns']}",
        f"- Invalid Likert cells: {result['invalid_likert_cells']}",
        "",
    ]
    if result["construct_summary"]:
        lines.extend(["## Construct Summary", ""])
        for row in result["construct_summary"]:
            alpha = row["alpha"]
            alpha_text = "n/a" if math.isnan(alpha) else f"{alpha:.3f}"
            lines.append(
                f"- {row['code']} {row['name']}: items {row['items']}, alpha {alpha_text}, "
                f"mean {row['mean']:.2f}, SD {row['sd']:.2f}."
            )
        lines.append("")
    if result["correlations"]:
        lines.extend(["## Correlations", ""])
        for row in result["correlations"]:
            lines.append(f"- {row['code']} with {row['with']}: Pearson r {row['pearson_r']:.3f}.")
        lines.append("")
    if result["regression"]:
        lines.extend(["## Regression", ""])
        regression = result["regression"]
        if "error" in regression:
            lines.append(f"- Regression not completed: {regression['error']}")
        else:
            lines.append(
                f"- Outcome: {regression['outcome']}; adjusted R-squared {regression['adjusted_r_squared']:.3f}."
            )
            for code, stats in regression["coefficients"].items():
                lines.append(f"- {code}: coefficient {stats['coef']:.3f}, p {stats['p']:.3f}.")
        lines.append("")
    lines.extend(
        [
            "## Item Means",
            "",
            "| Item | Mean | SD | Agree % | Column |",
            "| --- | ---: | ---: | ---: | --- |",
        ]
    )
    for row in result["item_summary"]:
        lines.append(f"| {row['item']} | {row['mean']:.2f} | {row['sd']:.2f} | {row['agree_pct']:.1f}% | {row['column']} |")
    lines.append("")
    return "\n".join(lines)


def qa_markdown(result: dict[str, Any]) -> str:
    return (
        "# Survey Results Check\n\n"
        f"- Results file: `{result['results_file']}`\n"
        f"- Rows: {result['rows']}\n"
        f"- Survey result columns: {result['survey_columns']}\n"
        f"- Questionnaire questions detected: {result['questionnaire_questions']}\n"
        f"- Question count match: {result['survey_question_count_match']}\n"
        f"- Missing survey cells: {result['missing_survey_cells']}\n"
        f"- Duplicate respondent IDs: {result['duplicate_respondent_ids']}\n"
        f"- Exact duplicate rows: {result['exact_duplicate_rows']}\n"
        f"- Likert columns detected: {result['likert_columns']}\n"
        f"- Invalid Likert cells: {result['invalid_likert_cells']}\n\n"
        "Professor-facing dissertation prose should use aggregate results only and should not expose internal survey diagnostics unless they affect validity, exclusions, reliability, or interpretation.\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyse a survey export deterministically.")
    parser.add_argument("--project", required=True)
    parser.add_argument("--results")
    parser.add_argument("--questionnaire")
    parser.add_argument("--metadata-cols", type=int, default=6)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--write", action="store_true", help="Write knowledge-base/results-analysis.md and qa/survey-results-check.md.")
    args = parser.parse_args()

    result = analyse(args.project, args.results, args.questionnaire, args.metadata_cols)
    root = project_path(args.project)
    if args.write:
        write_text(root / "knowledge-base" / "results-analysis.md", markdown(result))
        write_text(root / "qa" / "survey-results-check.md", qa_markdown(result))
    print(dump_json(result) if args.json else markdown(result))


if __name__ == "__main__":
    main()
