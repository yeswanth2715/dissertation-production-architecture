from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from common import latest_file, project_path, rel, write_text


FORBIDDEN_RENDER_TERMS = [
    "pre-survey",
    "when responses are supplied",
    "/learn",
    "artifact folder",
    "response-quality",
    "completion timestamp",
    "straightline",
    "low variation",
    "survey was weak",
    "ai-generated",
    "decorative artwork",
    "time taken",
    "duration",
]


def find_docx(project_dir: Path, explicit: str | None) -> Path:
    if explicit:
        path = Path(explicit)
        return path if path.is_absolute() else project_dir / path
    found = latest_file(project_dir / "outputs" if (project_dir / "outputs").exists() else project_dir, ["*.docx"])
    if found is None:
        raise FileNotFoundError("No DOCX found for render QA.")
    return found


def bundled_render_script() -> Path | None:
    root = Path.home() / ".codex" / "plugins" / "cache" / "openai-primary-runtime" / "documents"
    if not root.exists():
        return None
    matches = sorted(root.glob("*/skills/documents/render_docx.py"))
    return matches[-1] if matches else None


def run_bundled_renderer(docx: Path, outdir: Path) -> tuple[bool, str]:
    script = bundled_render_script()
    if script is None:
        return False, "bundled render_docx.py not found"
    proc = subprocess.run(
        [sys.executable, str(script), str(docx), "--output_dir", str(outdir), "--emit_pdf"],
        text=True,
        capture_output=True,
    )
    if proc.returncode == 0:
        return True, proc.stdout.strip()
    return False, (proc.stderr or proc.stdout).strip()


def run_word_render(docx: Path, outdir: Path) -> tuple[Path, int]:
    import win32com.client as win32  # type: ignore

    outdir.mkdir(parents=True, exist_ok=True)
    pdf = outdir / f"{docx.stem}.pdf"
    word = win32.DispatchEx("Word.Application")
    word.Visible = False
    document = None
    try:
        document = word.Documents.Open(str(docx))
        document.Fields.Update()
        for toc in document.TablesOfContents:
            toc.Update()
        pages = int(document.ComputeStatistics(2))
        document.ExportAsFixedFormat(str(pdf), 17)
    finally:
        if document is not None:
            document.Close(False)
        word.Quit()
    return pdf, pages


def rasterize_pdf(pdf: Path, outdir: Path) -> tuple[bool, str]:
    if shutil.which("pdftoppm") is None:
        return False, "pdftoppm not found"
    prefix = outdir / "page"
    proc = subprocess.run(["pdftoppm", "-png", "-r", "130", str(pdf), str(prefix)], text=True, capture_output=True)
    if proc.returncode == 0:
        return True, proc.stdout.strip()
    return False, (proc.stderr or proc.stdout).strip()


def page_nonblank_report(outdir: Path) -> dict[str, Any]:
    files = sorted(outdir.glob("page-*.png"))
    if not files:
        return {"png_pages": 0, "possible_blank": None, "min_nonwhite": None}
    try:
        from PIL import Image
    except Exception as exc:
        return {"png_pages": len(files), "possible_blank": None, "min_nonwhite": None, "error": str(exc)}

    values = []
    for file in files:
        image = Image.open(file).convert("L")
        nonwhite = sum(1 for px in image.getdata() if px < 245) / float(image.size[0] * image.size[1])
        values.append(nonwhite)
    return {
        "png_pages": len(files),
        "possible_blank": len([v for v in values if v < 0.002]),
        "min_nonwhite": min(values),
        "max_nonwhite": max(values),
    }


def pdf_text(pdf: Path, outdir: Path) -> tuple[str, str]:
    text_file = outdir / "rendered_text.txt"
    if shutil.which("pdftotext") is None:
        return "", "pdftotext not found"
    proc = subprocess.run(["pdftotext", str(pdf), str(text_file)], text=True, capture_output=True)
    if proc.returncode != 0:
        return "", (proc.stderr or proc.stdout).strip()
    try:
        return text_file.read_text(encoding="utf-8", errors="ignore"), ""
    except TypeError:
        return text_file.read_text(encoding="utf-8"), ""


def a11y_audit(docx: Path) -> dict[str, Any] | None:
    root = Path.home() / ".codex" / "plugins" / "cache" / "openai-primary-runtime" / "documents"
    matches = sorted(root.glob("*/skills/documents/scripts/a11y_audit.py")) if root.exists() else []
    if not matches:
        return None
    proc = subprocess.run([sys.executable, str(matches[-1]), str(docx)], text=True, capture_output=True)
    return {"returncode": proc.returncode, "output": (proc.stdout or proc.stderr).strip()}


def render_qa(project: str | Path, docx: str | None = None) -> dict[str, Any]:
    root = project_path(project)
    docx_path = find_docx(root, docx)
    outdir = root / ".codex_work" / "render_qa"
    outdir.mkdir(parents=True, exist_ok=True)

    bundled_ok, bundled_message = run_bundled_renderer(docx_path, outdir)
    render_engine = "bundled"
    pdf = outdir / f"{docx_path.stem}.pdf"
    pages = None
    if not bundled_ok or not pdf.exists():
        render_engine = "word-com"
        pdf, pages = run_word_render(docx_path, outdir)

    raster_ok, raster_message = rasterize_pdf(pdf, outdir)
    text, text_error = pdf_text(pdf, outdir)
    heading_issue = bool(re.search(r"(?m)^\d+\.\d+[ \t]+\d+\.\d+[ \t]+[A-Za-z]", text))
    bad_terms = [term for term in FORBIDDEN_RENDER_TERMS if term in text.lower()]
    pages_report = page_nonblank_report(outdir)
    audit = a11y_audit(docx_path)

    status = "pass"
    if heading_issue or bad_terms or pages_report.get("possible_blank") not in {0, None}:
        status = "fail"

    return {
        "project": root.name,
        "docx": rel(docx_path),
        "render_engine": render_engine,
        "bundled_renderer_ok": bundled_ok,
        "bundled_renderer_message": bundled_message[:1000],
        "pdf": rel(pdf),
        "word_page_count": pages,
        "raster_ok": raster_ok,
        "raster_message": raster_message[:1000],
        "page_images": pages_report,
        "pdf_text_error": text_error,
        "heading_duplicate_numbering_issue": heading_issue,
        "forbidden_render_terms": bad_terms,
        "a11y_audit": audit,
        "status": status,
    }


def markdown(report: dict[str, Any]) -> str:
    return (
        "# Render QA Report\n\n"
        f"Project: `{report['project']}`\n\n"
        f"DOCX: `{report['docx']}`\n\n"
        f"Status: `{report['status']}`\n\n"
        f"Render engine: `{report['render_engine']}`\n\n"
        f"PDF: `{report['pdf']}`\n\n"
        f"Word page count: `{report['word_page_count']}`\n\n"
        f"Raster OK: `{report['raster_ok']}`\n\n"
        f"Page images: `{report['page_images']}`\n\n"
        f"Duplicate heading numbering issue: `{report['heading_duplicate_numbering_issue']}`\n\n"
        f"Forbidden rendered terms: `{report['forbidden_render_terms']}`\n\n"
        f"Accessibility audit: `{report['a11y_audit']}`\n\n"
        "Rendered PNG/PDF files are internal QA intermediates and should not be delivered unless explicitly requested.\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run render QA for a final dissertation DOCX.")
    parser.add_argument("--project", required=True)
    parser.add_argument("--docx")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    report = render_qa(args.project, args.docx)
    if args.write:
        write_text(project_path(args.project) / "qa" / "render-qa-report.md", markdown(report))
    print(markdown(report))
    if report["status"] == "fail":
        sys.exit(1)


if __name__ == "__main__":
    main()
