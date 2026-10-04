from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Any

from analyse_survey import analyse, markdown as survey_markdown, qa_markdown
from common import artifact_path, dissertation_path, dump_json, latest_file, load_manifest, project_path, rel, write_text
from fast_qa import markdown as fast_qa_markdown, qa as run_fast_qa
from benchmark_qa import check as run_benchmark_qa, markdown as benchmark_qa_markdown
from render_qa import markdown as render_qa_markdown, render_qa
from scan_project import discovery_markdown, scan
from utils.artifact_gate import gate as run_artifact_gate, markdown as artifact_gate_markdown
from utils.evidence import check_evidence, sha256
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
        path = artifact_path(root, value.strip())
        if not path.is_file() or path.suffix != ".py":
            raise ValueError(f"Configured builder missing or not Python: {path}")
        scripts.append(path)
    return scripts


def run_script(script: Path, root: Path, timeout: int = 300) -> dict[str, Any]:
    try:
        proc = subprocess.run([sys.executable, str(script)], cwd=root, text=True, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"script": rel(script), "returncode": 124, "status": "fail", "stderr": f"Builder timed out after {timeout}s"}
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
    return False


def run_pipeline(project: str | Path, stage: str, qa_mode: str, execute_builders: bool) -> dict[str, Any]:
    root = project_path(project)
    manifest = load_manifest(root)
    log: dict[str, Any] = {"project": root.name, "stage": stage, "qa_mode": qa_mode, "steps": [], "readiness": "not validated"}

    def finish() -> dict[str, Any]:
        failed = any(s.get("status") == "fail" or s.get("returncode", 0) != 0 for s in log["steps"])
        log["status"] = "fail" if failed else "pass"
        if root.name != "_template":
            write_text(root / "qa/run-log.md", dump_json(log))
        return log

    if stage == "final" and qa_mode == "none":
        log["steps"].append({"name": "final prerequisites", "status": "fail", "reason": "Final runs require QA"})
        return finish()
    if stage == "final" and manifest.get("qa", {}).get("render_required_for_final", False):
        qa_mode = "render"
        log["qa_mode"] = qa_mode

    preflight = run_preflight(root)
    if root.name == "_template":
        log["steps"].append({"name": "preflight", "status": preflight["status"], "output": "not written for _template"})
    else:
        write_text(root / "qa" / "preflight-report.md", preflight_markdown(preflight))
        log["steps"].append({"name": "preflight", "status": preflight["status"], "summary": preflight["summary"], "output": rel(root / "qa" / "preflight-report.md")})
    if preflight["summary"]["fail"]:
        return finish()

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

    if artifact_gate["status"] == "fail":
        return finish()
    if stage == "final":
        evidence = check_evidence(root)
        log["steps"].append({"name": "evidence prerequisites", **evidence})
        if evidence["status"] == "fail":
            return finish()
    survey_required = manifest.get("method", {}).get("type") in {"survey", "survey-only", "mixed-methods"} or manifest.get("method", {}).get("survey_required", False)
    if stage == "survey-analysis" or (stage == "final" and survey_required):
        if not survey_results_available(root, manifest):
            log["steps"].append({"name": "survey prerequisites", "status": "fail", "reason": "Explicit survey.results file required"})
            return finish()

    if stage in {"survey-analysis", "final"} and survey_results_available(root, manifest):
        try:
            survey = analyse(root)
        except (ValueError, OSError, KeyError) as exc:
            log["steps"].append({"name": "analyse_survey", "status": "fail", "reason": str(exc)})
            return finish()
        write_text(root / "knowledge-base" / "results-analysis.md", survey_markdown(survey))
        write_text(root / "qa" / "survey-results-check.md", qa_markdown(survey))
        log["steps"].append({"name": "analyse_survey", "status": "pass", "rows": survey["rows"], "likert_columns": survey["likert_columns"]})
    elif stage in {"survey-analysis", "final"}:
        log["steps"].append({"name": "analyse_survey", "status": "skip", "reason": "no survey result file found"})

    if stage == "final":
        try:
            scripts = configured_scripts(root, manifest)
        except ValueError as exc:
            log["steps"].append({"name": "builder configuration", "status": "fail", "reason": str(exc)})
            return finish()
        if execute_builders and scripts:
            for script in scripts:
                result = run_script(script, root, timeout=int(manifest.get("generation", {}).get("timeout_seconds", 300)))
                log["steps"].append({"name": "builder", **result})
                if result["returncode"] != 0:
                    return finish()
        elif scripts:
            log["steps"].append({"name": "builder", "status": "skip", "reason": "configured but --execute-builders was not set"})
        else:
            log["steps"].append({"name": "builder", "status": "skip", "reason": "no generation.builder configured in project.yaml"})

    if qa_mode in {"fast", "render"}:
        try:
            fast = run_fast_qa(root, stage="final" if stage == "final" else "draft")
        except Exception as exc:
            log["steps"].append({"name": "fast_qa", "status": "fail", "reason": str(exc)})
            return finish()
        write_text(root / "qa" / "fast-qa-report.md", fast_qa_markdown(fast))
        log["steps"].append({"name": "fast_qa", "status": "pass" if fast["summary"]["fail"] == 0 else "fail", "summary": fast["summary"]})
        if stage == "final":
            output = dissertation_path(root)
            evidence = check_evidence(root, output)
            log["steps"].append({"name": "output evidence", **evidence})
            if output.is_file():
                log["output_sha256"] = sha256(output)
            benchmark = run_benchmark_qa(root, stage="final")
            write_text(root / "qa" / "benchmark-qa-report.md", benchmark_qa_markdown(benchmark))
            log["steps"].append({"name": "benchmark_qa", "status": benchmark["status"], "summary": benchmark["summary"]})

    if qa_mode == "render":
        try:
            rendered = render_qa(root)
        except Exception as exc:
            log["steps"].append({"name": "render_qa", "status": "fail", "reason": f"Required render verification unavailable: {exc}"})
            return finish()
        write_text(root / "qa" / "render-qa-report.md", render_qa_markdown(rendered))
        log["steps"].append({"name": "render_qa", "status": rendered["status"], "page_images": rendered["page_images"]})

    if stage == "final" and not any(s.get("status") == "fail" for s in log["steps"]):
        log["readiness"] = "automated checks passed; academic and visual review still required"
    return finish()


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
