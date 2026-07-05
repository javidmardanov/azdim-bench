"""Render downloaded PDFs to per-page PNGs for vision-LLM extraction.

Usage:
    uv run python -m azdim.render <source_id> [<source_id> ...]
    uv run python -m azdim.render --all-izah

Pages land in data/pages/<source_id>/page-NN.png (gitignored, reproducible).
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "manifest" / "sources.json"
RAW_DIR = ROOT / "data" / "raw_pdfs"
PAGES_DIR = ROOT / "data" / "pages"

DPI = 200


def render(source_id: str) -> list[Path]:
    pdf = RAW_DIR / f"{source_id}.pdf"
    if not pdf.exists():
        raise FileNotFoundError(f"{pdf} not downloaded; run azdim.download first")
    out_dir = PAGES_DIR / source_id
    out_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["pdftoppm", "-png", "-r", str(DPI), str(pdf), str(out_dir / "page")],
        check=True,
    )
    pages = sorted(out_dir.glob("page-*.png"))
    print(f"{source_id}: {len(pages)} pages -> {out_dir}")
    return pages


def izah_source_ids() -> list[str]:
    sources = json.loads(MANIFEST.read_text())["sources"]
    return [s["source_id"] for s in sources
            if s["doc_type"] == "izah" and s["in_scope"]]


if __name__ == "__main__":
    args = sys.argv[1:]
    ids = izah_source_ids() if args == ["--all-izah"] else args
    if not ids:
        sys.exit("usage: python -m azdim.render <source_id>... | --all-izah")
    for sid in ids:
        render(sid)
