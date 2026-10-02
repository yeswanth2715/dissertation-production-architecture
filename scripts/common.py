from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
PROJECTS_DIR = REPO_ROOT / "projects"


def word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?", text))


def project_path(project: str | Path) -> Path:
    candidate = Path(project)
    if candidate.exists():
        return candidate.resolve()

    direct = PROJECTS_DIR / str(project)
    if direct.exists():
        return direct.resolve()

    matches = [p for p in PROJECTS_DIR.iterdir() if p.is_dir() and p.name.lower() == str(project).lower()]
    if matches:
        return matches[0].resolve()

    raise FileNotFoundError(f"Project not found: {project}")


def latest_file(root: Path, patterns: list[str]) -> Path | None:
    files: list[Path] = []
    for pattern in patterns:
        files.extend(root.rglob(pattern))
    files = [p for p in files if p.is_file() and not p.name.startswith("~$")]
    if not files:
        return None
    return max(files, key=lambda p: p.stat().st_mtime)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8-sig")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if value == "":
        return ""
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    if value.lower() in {"null", "none"}:
        return None
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def load_manifest(project_dir: Path) -> dict[str, Any]:
    path = project_dir / "project.yaml"
    if not path.exists():
        return {}

    try:
        import yaml  # type: ignore

        data = yaml.safe_load(read_text(path))
        return data or {}
    except Exception:
        pass

    data: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, data)]
    for raw in read_text(path).splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()
        if ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        while stack and indent <= stack[-1][0]:
            stack.pop()
        current = stack[-1][1]
        if value.strip() == "":
            node: dict[str, Any] = {}
            current[key.strip()] = node
            stack.append((indent, node))
        else:
            current[key.strip()] = parse_scalar(value)
    return data


def dump_json(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False, default=str)


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)
