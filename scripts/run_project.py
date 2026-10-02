from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Any

from analyse_survey import analyse, markdown as survey_markdown, qa_markdown
from common import dump_json, latest_file, load_manifest, project_path, rel, write_text
from fast_qa import markdown as fast_qa_markdown, qa as run_fast_qa
from benchmark_qa import check as run_benchmark_qa, markdown as benchmark_qa_markdown
from render_qa import markdown as render_qa_markdown, render_qa
from scan_project import discovery_markdown, scan
from utils.artifact_gate import gate as run_artifact_gate, markdown as artifact_gate_markdown
from utils.runtime import markdown as preflight_markdown, preflight as run_preflight


def configured_scripts(root: Path, manifest: dict[str, Any]) -> list[Path]:
    generation = manifest.get("generation", {}) if isinstance(manifest.get("generation"), dict) else {}
    values = []
    for key in ["builder", "post_build", "cleanup"]:
        value = generation.get(key)
        if value:
            values.extend(str(value).split(","))
    scripts = []
    for value in values:
        path = Path(value.strip())
        if not path.is_absolute():
            path = root / path
        if path.exists():
            scripts.append(path)
    return scripts


def run_script(script: Path, root: Path) -> dict[str, Any]:
    proc = subprocess.run([sys.executable, str(script)], cwd=root, text=True, capture_output=True)
    return {
        "script": rel(script),
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip()[-3000:],
        "stderr": proc.stderr.strip()[-3000:],
    }


def survey_results_available(root: Path, manifest: dict[str, Any]) -> bool:
    configured = manifest.get("survey", {}).get("results") if isinstance(manifest.get("survey"), dict) else None
    if configured:
        path = Path(str(configured))
        if not path.is_absolute():
            path = root / path
        return path.exists()
    return latest_file(root, ["*.xlsx", "*.csv", "*.tsv"]) is not None


def run_pipeline(project: str | Path, stage: str, qa_mode: str, execute_builders: bool) -> dict[str, Any]:
    root = project_path(project)
    manifest = load_manifest(root)
    log: dict[str, Any] = {"project": root.name, "stage": stage, "qa_mode": qa_mode, "steps": []}

    preflight = run_preflight(root)
    if root.name == "_template":
        log["steps"].append({"name": "preflight", "status": preflight["status"], "output": "not written for _template"})
    else:
        write_text(root / "qa" / "preflight-report.md", preflight_markdown(preflight))
        log["steps"].append({"name": "preflight", "status": preflight["status"], "summary": preflight["summary"], "output": rel(root / "qa" / "preflight-report.md")})
    if preflight["summary"]["fail"]:
        write_text(root / "qa" / "run-log.md", dump_json(log))
        return log

    discovery = scan(root)
    if root.name == "_template":
        log["steps"].append({"name": "scan_project", "status": "pass", "output": "not written for _template"})
    else:
        write_text(root / "project-discovery.md", discovery_markdown(discovery))
        log["steps"].append({"name": "scan_project", "status": "pass", "output": rel(root / "project-discovery.md")})

    artifact_gate = run_artifact_gate(root, stage)
    if root.name == "_template":
        log["steps"].append({"name": "artifact_gate", "status": artifact_gate["status"], "output": "not written for _template"})
    else:
        write_text(root / "qa" / "artifact-gate-report.md", artifact_gate_markdown(artifact_gate))
        log["steps"].append(
            {
                "name": "artifact_gate",
                "status": artifact_gate["status"],
                "artifacts": artifact_gate["summary"]["artifacts"],
                "output": rel(root / "qa" / "artifact-gate-report.md"),
            }
        )

    if stage in {"survey-analysis", "final"} and survey_results_available(root, manifest):
        survey = analyse(root)
        write_text(root / "knowledge-base" / "results-analysis.md", survey_markdown(survey))
        write_text(root / "qa" / "survey-results-check.md", qa_markdown(survey))
        log["steps"].append({"name": "analyse_survey", "status": "pass", "rows": survey["rows"], "likert_columns": survey["likert_columns"]})
    elif stage in {"survey-analysis", "final"}:
        log["steps"].append({"name": "analyse_survey", "status": "skip", "reason": "no survey result file found"})

    if stage == "final":
        scripts = configured_scripts(root, manifest)
        if execute_builders and scripts:
            for script in scripts:
                result = run_script(script, root)
                log["steps"].append({"name": "builder", **result})
                if result["returncode"] != 0:
                    break
        elif scripts:
            log["steps"].append({"name": "builder", "status": "skip", "reason": "configured but --execute-builders was not set"})
        else:
            log["steps"].append({"name": "builder", "status": "skip", "reason": "no generation.builder configured in project.yaml"})

    if qa_mode in {"fast", "render"}:
        fast = run_fast_qa(root, stage="final" if stage == "final" else "draft")
        write_text(root / "qa" / "fast-qa-report.md", fast_qa_markdown(fast))
        log["steps"].append({"name": "fast_qa", "status": "pass" if fast["summary"]["fail"] == 0 else "fail", "summary": fast["summary"]})
        if stage == "final":
            benchmark = run_benchmark_qa(root, stage="final")
            write_text(root / "qa" / "benchmark-qa-report.md", benchmark_qa_markdown(benchmark))
            log["steps"].append({"name": "benchmark_qa", "status": benchmark["status"], "summary": benchmark["summary"]})

    if qa_mode == "render":
        rendered = render_qa(root)
        write_text(root / "qa" / "render-qa-report.md", render_qa_markdown(rendered))
        log["steps"].append({"name": "render_qa", "status": rendered["status"], "page_images": rendered["page_images"]})

    write_text(root / "qa" / "run-log.md", dump_json(log))
    return log


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the deterministic dissertation project pipeline.")
    parser.add_argument("--project", required=True)
    parser.add_argument("--stage", default="discover", choices=["discover", "pre-survey", "survey-analysis", "final"])
    parser.add_argument("--qa", default="fast", choices=["none", "fast", "render"])
    parser.add_argument(
        "--execute-builders",
        action="store_true",
        help="Run project-specific builder scripts listed in project.yaml. Keep off for dry deterministic discovery/QA.",
    )
    args = parser.parse_args()

    log = run_pipeline(args.project, args.stage, args.qa, args.execute_builders)
    print(dump_json(log))
    failed = [step for step in log["steps"] if step.get("status") == "fail" or step.get("returncode", 0) != 0]
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
