from __future__ import annotations

import argparse

from common import dump_json
from utils.rules import route_learn_instruction


def markdown(report: dict) -> str:
    lines = [
        "# Learn Routing Decision",
        "",
        f"Instruction: `{report['instruction']}`",
        "",
        f"Destination: `{report['destination']}`",
        "",
        f"Reason: {report['reason']}",
        "",
        "## Utility Config Matches",
        "",
    ]
    if report["utility_config_matches"]:
        for target, hits in report["utility_config_matches"].items():
            lines.append(f"- `{target}`: {', '.join(hits)}")
    else:
        lines.append("- none")
    lines.extend(["", "## Skills.md Matches", ""])
    if report["skills_md_matches"]:
        for hit in report["skills_md_matches"]:
            lines.append(f"- {hit}")
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Route a /learn instruction to skills.md or utility config/code.")
    parser.add_argument("--instruction", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = route_learn_instruction(args.instruction)
    print(dump_json(report) if args.json else markdown(report))


if __name__ == "__main__":
    main()
