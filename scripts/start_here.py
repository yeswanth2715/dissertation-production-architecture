from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from common import PROJECTS_DIR, REPO_ROOT, project_path


TASKS = {
    "1": ("discover", "Read project folder and show what exists."),
    "2": ("pre-survey", "Prepare project before survey questionnaire work."),
    "3": ("survey-analysis", "Analyse returned survey results."),
    "4": ("final", "Run final artifact gate, configured builders, and QA."),
}


def choose_project() -> str:
    projects = sorted([p for p in PROJECTS_DIR.iterdir() if p.is_dir() and p.name != "_template"], key=lambda p: p.name.lower())
    if not projects:
        print("No project folders found under projects/. Create one from projects/_template/ first.")
        sys.exit(1)
    print("Available projects:")
    for index, path in enumerate(projects, start=1):
        print(f"{index}. {path.name}")
    selected = input("Choose project number: ").strip()
    try:
        return str(projects[int(selected) - 1])
    except Exception:
        print("Invalid selection.")
        sys.exit(1)


def choose_task() -> str:
    print("What do you want to do?")
    for number, (task, description) in TASKS.items():
        print(f"{number}. {task} - {description}")
    selected = input("Choose task number: ").strip()
    if selected not in TASKS:
        print("Invalid selection.")
        sys.exit(1)
    return TASKS[selected][0]


def run_step(args: list[str]) -> int:
    print("", flush=True)
    print("Running: " + " ".join(args), flush=True)
    proc = subprocess.run(args, cwd=REPO_ROOT, text=True)
    return proc.returncode


def main() -> None:
    parser = argparse.ArgumentParser(description="Simple nontechnical dissertation architecture entrypoint.")
    parser.add_argument("--project", help="Project folder name or path. Omit for interactive selection.")
    parser.add_argument("--task", choices=["discover", "pre-survey", "survey-analysis", "final"], help="What to run. Omit for interactive selection.")
    parser.add_argument("--render", action="store_true", help="Use render QA for final outputs when available.")
    parser.add_argument("--execute-builders", action="store_true", help="Run configured project builder scripts.")
    args = parser.parse_args()

    project = args.project or choose_project()
    task = args.task or choose_task()
    root = project_path(project)

    preflight_code = run_step([sys.executable, "scripts/preflight.py", "--project", str(root), "--write"])
    if preflight_code != 0:
        print("Preflight found a blocking problem. Check qa/preflight-report.md if it was written.")
        sys.exit(preflight_code)

    qa_mode = "render" if args.render else "fast"
    command = [sys.executable, "scripts/run_project.py", "--project", str(root), "--stage", task, "--qa", qa_mode]
    if args.execute_builders or task == "final":
        command.append("--execute-builders")
    code = run_step(command)
    if code == 0:
        print("")
        print("Done. Check the project qa/ folder for reports and outputs/ for generated documents.")
    sys.exit(code)


if __name__ == "__main__":
    main()
