from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

from common import rel
from utils.rules import load_json_config


REPO_ROOT = Path(__file__).resolve().parents[2]


def _check_import(module_name: str) -> tuple[bool, str]:
    try:
        __import__(module_name)
        return True, "available"
    except Exception as exc:
        return False, str(exc)


def _write_access(path: Path) -> tuple[bool, str]:
    try:
        path.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("w", delete=False, dir=path, encoding="utf-8") as handle:
            handle.write("ok")
            temp_path = Path(handle.name)
        temp_path.unlink(missing_ok=True)
        return True, "write access confirmed"
    except Exception as exc:
        return False, str(exc)


def _compile_scripts_available() -> tuple[bool, str]:
    scripts_dir = REPO_ROOT / "scripts"
    required = [
        "run_project.py",
        "scan_project.py",
        "artifact_gate.py",
        "fast_qa.py",
        "analyse_survey.py",
        "render_qa.py",
        "route_learn.py",
    ]
    missing = [name for name in required if not (scripts_dir / name).exists()]
    if missing:
        return False, "missing: " + ", ".join(missing)
    return True, "required scripts present"


def preflight(project_root: Path | None = None) -> dict[str, Any]:
    rules = load_json_config("runtime_rules.json", {})
    checks: list[dict[str, str]] = []

    checks.append({"status": "pass", "check": "python_available", "detail": sys.version.split()[0]})

    ok, detail = _write_access(REPO_ROOT)
    checks.append({"status": "pass" if ok else "fail", "check": "repo_write_access", "detail": detail})

    if project_root is not None:
        checks.append(
            {
                "status": "pass" if project_root.exists() else "fail",
                "check": "project_exists",
                "detail": rel(project_root) if project_root.exists() else str(project_root),
            }
        )

    ok, detail = _compile_scripts_available()
    checks.append({"status": "pass" if ok else "fail", "check": "scripts_compile", "detail": detail})

    rtk = shutil.which("rtk")
    checks.append({"status": "pass" if rtk else "warn", "check": "rtk_available", "detail": rtk or "optional; direct Python fallback will be used"})

    soffice = shutil.which("soffice")
    checks.append({"status": "pass" if soffice else "warn", "check": "soffice_available", "detail": soffice or "optional; render QA will use structural fallback"})

    for module, check_name in [("docx", "python_docx_available"), ("openpyxl", "openpyxl_available")]:
        ok, detail = _check_import(module)
        checks.append({"status": "pass" if ok else "warn", "check": check_name, "detail": detail})

    failures = [item for item in checks if item["status"] == "fail"]
    warnings = [item for item in checks if item["status"] == "warn"]
    return {
        "status": "fail" if failures else ("warn" if warnings else "pass"),
        "policy": rules.get("command_policy", {}),
        "checks": checks,
        "summary": {"pass": len(checks) - len(warnings) - len(failures), "warn": len(warnings), "fail": len(failures)},
    }


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Runtime Preflight Report",
        "",
        f"Status: `{report['status']}`",
        "",
        "This report is for nontechnical usability. Warnings usually mean the architecture will use a fallback.",
        "",
        "## Checks",
        "",
        "| Status | Check | Detail |",
        "| --- | --- | --- |",
    ]
    for check in report["checks"]:
        lines.append(f"| {check['status']} | {check['check']} | {check['detail'].replace('|', '\\|')} |")
    lines.extend(["", "## Runtime Policy", "", "```json", json.dumps(report.get("policy", {}), indent=2), "```", ""])
    return "\n".join(lines)
