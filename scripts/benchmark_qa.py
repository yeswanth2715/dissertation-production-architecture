from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

from common import dump_json, project_path, read_text, write_text

DIMENSIONS = [
    ("Knowledge and context", 75),
    ("Literature synthesis and criticality", 80),
    ("Methodology and research design", 75),
    ("Findings, analysis, and discussion", 80),
    ("Professional academic execution", 75),
    ("Compliance, originality, and referencing", 0),
]


def check(project: str | Path, stage: str = "final") -> dict[str, Any]:
    root = project_path(project)
    scorecard = root / "qa" / "benchmark-scorecard.md"
    checks: list[dict[str, str]] = []
    scores: dict[str, float | None] = {}
    if not scorecard.exists():
        checks.append({"status": "fail", "check": "benchmark scorecard", "detail": "qa/benchmark-scorecard.md is missing"})
    else:
        text = read_text(scorecard)
        for name, minimum in DIMENSIONS:
            row = next((line for line in text.splitlines() if line.startswith("| " + name + " |")), "")
            cells = [cell.strip() for cell in row.strip().strip("|").split("|")] if row else []
            current = cells[2] if len(cells) > 2 else ""
            match = re.search(r"\b([0-9]{2}(?:\.[0-9]+)?)\b", current)
            value = float(match.group(1)) if match else None
            scores[name] = value
            if name == "Compliance, originality, and referencing":
                passed = "pass" in current.lower() and "fail" not in current.lower()
                checks.append({"status": "pass" if passed else "fail", "check": name, "detail": current or "compliance result missing"})
            elif value is None:
                checks.append({"status": "fail", "check": name, "detail": "numeric current estimate is missing"})
            else:
                checks.append({"status": "pass" if value >= minimum else "fail", "check": name, "detail": f"{value:g}; required minimum {minimum}"})
        weighted = re.search(r"(?im)^\s*(?:weighted score|overall score)\s*:\s*([0-9]{2}(?:\.[0-9]+)?)", text)
        if weighted:
            value = float(weighted.group(1))
            checks.append({"status": "pass" if 80 <= value <= 89.99 else "fail", "check": "weighted benchmark", "detail": f"{value:g}; target 80-89"})
        else:
            checks.append({"status": "fail", "check": "weighted benchmark", "detail": "weighted score is missing"})
        for field in ["Evidence", "Action needed"]:
            checks.append({"status": "pass" if field.lower() in text.lower() else "fail", "check": f"scorecard field:{field}", "detail": "present" if field.lower() in text.lower() else "missing"})
    fast_report = root / "qa" / "fast-qa-report.md"
    if stage == "final" and fast_report.exists():
        text = read_text(fast_report)
        word_count = re.search(
            r"(?im)\|\s*(?:warn|pass|fail)\s*\|\s*body word count\s*\|\s*([0-9,]+) words; target ([0-9,]+); pre-humaniser range ([0-9,]+)-([0-9,]+)",
            text,
        )
        if word_count:
            actual, target, minimum, maximum = (int(value.replace(",", "")) for value in word_count.groups())
            in_range = minimum <= actual <= maximum
            checks.append({"status": "pass" if in_range else "fail", "check": "word-count benchmark", "detail": f"{actual} words; required pre-humaniser range {minimum}-{maximum} for target {target}"})
        else:
            checks.append({"status": "fail", "check": "word-count benchmark", "detail": "fast QA report does not contain a parseable body word-count result"})
        section_target_report = root / "qa" / "section-target-qa-report.md"
        if section_target_report.exists():
            section_text = read_text(section_target_report)
            section_passed = re.search(r"(?im)^Status:\s*PASS\s*$", section_text) is not None
            checks.append({"status": "pass" if section_passed else "fail", "check": "section word-count benchmark", "detail": "section-level 85%-92% gate passed" if section_passed else "section-level 85%-92% gate failed"})
        else:
            checks.append({"status": "fail", "check": "section word-count benchmark", "detail": "qa/section-target-qa-report.md is missing"})
        match = re.search(r"(?im)^-\s*Fail:\s*(\d+)", text)
        if match:
            failures = int(match.group(1))
            checks.append({"status": "pass" if failures == 0 else "fail", "check": "Fast QA prerequisite", "detail": f"{failures} Fast QA failure(s)"})
    failed = [item for item in checks if item["status"] == "fail"]
    return {"project": root.name, "stage": stage, "status": "fail" if failed else "pass", "scores": scores, "checks": checks, "summary": {"pass": len(checks) - len(failed), "fail": len(failed)}}


def markdown(report: dict[str, Any]) -> str:
    lines = ["# Deterministic Benchmark QA Report", "", f"Project: {report['project']}", f"Stage: {report['stage']}", f"Status: {report['status']}", "", "## Scores", ""]
    lines += [f"- {name}: {value if value is not None else 'missing'}" for name, value in report["scores"].items()]
    lines += ["", "## Checks", "", "| Status | Check | Detail |", "| --- | --- | --- |"]
    lines += [f"| {item['status']} | {item['check']} | {item['detail'].replace('|', '\\|')} |" for item in report["checks"]]
    lines += ["", "The benchmark is an internal quality gate, not a guaranteed university mark."]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic Level 7 benchmark QA.")
    parser.add_argument("--project", required=True)
    parser.add_argument("--stage", default="final")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = check(args.project, args.stage)
    if args.write:
        write_text(project_path(args.project) / "qa" / "benchmark-qa-report.md", markdown(report))
    print(dump_json(report) if args.json else markdown(report))
    if report["status"] == "fail":
        sys.exit(1)


if __name__ == "__main__":
    main()
