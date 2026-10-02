from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


UTILS_DIR = Path(__file__).resolve().parent
CONFIG_DIR = UTILS_DIR / "config"
REPO_ROOT = UTILS_DIR.parents[1]


def load_json_config(name: str, default: Any) -> Any:
    path = CONFIG_DIR / name
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def load_banned_terms() -> list[str]:
    data = load_json_config("banned_terms.json", {})
    terms: set[str] = set()
    if isinstance(data, dict):
        for values in data.values():
            if isinstance(values, list):
                terms.update(str(value).lower() for value in values)
    return sorted(terms)


def route_learn_instruction(instruction: str) -> dict[str, Any]:
    rules = load_json_config("learn_routing_rules.json", {})
    text = instruction.lower().replace("/learn", " ").strip()
    utility_routes = rules.get("utility_config_routes", {}) if isinstance(rules, dict) else {}
    skills_keywords = rules.get("skills_md_keywords", []) if isinstance(rules, dict) else []

    utility_matches: dict[str, list[str]] = {}
    def keyword_matches(keyword: str) -> bool:
        keyword = str(keyword).lower()
        if re.fullmatch(r"[a-z0-9_-]+", keyword):
            return re.search(rf"\b{re.escape(keyword)}\b", text) is not None
        return keyword in text

    for target, keywords in utility_routes.items():
        hits = [keyword for keyword in keywords if keyword_matches(keyword)]
        if hits:
            utility_matches[target] = hits

    skills_hits = [keyword for keyword in skills_keywords if keyword_matches(keyword)]

    if utility_matches and skills_hits:
        destination = rules.get("split_destination", "skills.md + scripts/utils/config")
        reason = "Instruction contains both machine-checkable rule language and human judgement/process language."
    elif utility_matches:
        destination = "scripts/utils/config"
        reason = "Instruction is deterministic or machine-checkable and should be enforced by utility code/config."
    else:
        destination = rules.get("default_destination", "skills.md")
        reason = "Instruction is process, judgement, writing, or architecture memory rather than a deterministic check."

    return {
        "instruction": instruction,
        "destination": destination,
        "reason": reason,
        "utility_config_matches": utility_matches,
        "skills_md_matches": skills_hits,
    }
