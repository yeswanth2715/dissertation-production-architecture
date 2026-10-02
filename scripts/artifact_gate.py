from __future__ import annotations

import argparse

from common import project_path, write_text
from utils.artifact_gate import gate, markdown, to_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect all project artifacts before final output generation.")
    parser.add_argument("--project", required=True)
    parser.add_argument("--stage", default="final")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = project_path(args.project)
    report = gate(root, args.stage)
    if args.write:
        write_text(root / "qa" / "artifact-gate-report.md", markdown(report))
    print(to_json(report) if args.json else markdown(report))


if __name__ == "__main__":
    main()
