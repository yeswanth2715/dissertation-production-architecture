"""Validate claim provenance. Passage existence does not prove semantic support."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from common import artifact_path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_evidence(root: Path, output: Path | None = None) -> dict[str, Any]:
    checks = []
    def add(ok: bool, name: str, detail: str) -> None:
        checks.append({"status": "pass" if ok else "fail", "check": name, "detail": detail})

    try:
        ledger = json.loads((root / "knowledge-base/evidence-ledger.json").read_text())
        sources = ledger["sources"]
        claims = ledger["claims"]
        if not isinstance(sources, list) or not isinstance(claims, list) or not claims:
            raise ValueError("sources and nonempty claims must be lists")
        indexed = {}
        for source in sources:
            sid = source["id"]
            if sid in indexed:
                raise ValueError(f"Duplicate source: {sid}")
            path = artifact_path(root, source["path"])
            add(path.is_file() and sha256(path) == source["sha256"], f"source:{sid}", "source content hash must match")
            indexed[sid] = source
        seen = set()
        for claim in claims:
            cid = claim["id"]
            if cid in seen:
                raise ValueError(f"Duplicate claim: {cid}")
            seen.add(cid)
            add(bool(claim.get("text")) and bool(claim.get("section")), f"claim:{cid}", "claim text and output section required")
            if claim.get("kind") == "assumption":
                add(claim.get("disclosed") is True, f"assumption:{cid}", "assumptions must be disclosed")
                continue
            source = indexed.get(claim.get("source_id"))
            add(source is not None, f"provenance:{cid}", "registered source required")
            if source:
                path = artifact_path(root, source["path"])
                passage = claim.get("passage", "")
                # Ledger points to extracted UTF-8 text, not opaque binary originals.
                text = path.read_text(encoding="utf-8")
                add(bool(passage) and passage in text and bool(claim.get("locator")), f"passage:{cid}", "exact passage and page/section locator required")
            add(claim.get("support_review") == "verified", f"support:{cid}", "support must be reviewed against source")
        if output is not None:
            review = ledger.get("output_review", {})
            add(output.is_file() and review.get("sha256") == sha256(output), "output binding", "review must match current output hash")
            add(review.get("claims_complete") is True and bool(review.get("reviewer")), "claim coverage", "reviewer must attest material-claim coverage")
    except (OSError, ValueError, KeyError, TypeError, UnicodeError, AttributeError) as exc:
        add(False, "evidence ledger", str(exc))
    return {"status": "fail" if any(c["status"] == "fail" for c in checks) else "pass", "checks": checks}
