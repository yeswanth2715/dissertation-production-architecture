from __future__ import annotations

import argparse

from common import project_path, write_text
from utils.runtime import markdown, preflight


def main() -> None:
    parser = argparse.ArgumentParser(description="Run nontechnical runtime preflight checks.")
    parser.add_argument("--project", help="Project folder name or path.")
    parser.add_argument("--write", action="store_true", help="Write qa/preflight-report.md when a project is supplied.")
    args = parser.parse_args()

    root = project_path(args.project) if args.project else None
    report = preflight(root)
    if args.write and root is not None:
        write_text(root / "qa" / "preflight-report.md", markdown(report))
    print(markdown(report))


if __name__ == "__main__":
    main()
