"""Download official DIM PDFs listed in manifest/sources.json.

Writes PDFs to data/raw_pdfs/<source_id>.pdf and a run report to
manifest/downloads.json with HTTP status, SHA256, and page count per source.
"""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import httpx
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "manifest" / "sources.json"
REPORT = ROOT / "manifest" / "downloads.json"
RAW_DIR = ROOT / "data" / "raw_pdfs"


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def page_count_of(path: Path) -> int | None:
    try:
        return len(PdfReader(path).pages)
    except Exception:
        return None


def download_all(include_out_of_scope: bool = True) -> list[dict]:
    sources = json.loads(MANIFEST.read_text())["sources"]
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    results = []
    with httpx.Client(timeout=60, follow_redirects=True) as client:
        for src in sources:
            if not include_out_of_scope and not src["in_scope"]:
                continue
            dest = RAW_DIR / f"{src['source_id']}.pdf"
            rec = {"source_id": src["source_id"], "url": src["url"]}
            if dest.exists():
                rec["status"] = "cached"
            else:
                try:
                    resp = client.get(src["url"])
                    rec["http_status"] = resp.status_code
                    if resp.status_code == 200 and resp.content[:4] == b"%PDF":
                        dest.write_bytes(resp.content)
                        rec["status"] = "downloaded"
                    else:
                        rec["status"] = "failed"
                except httpx.HTTPError as e:
                    rec["status"] = "failed"
                    rec["error"] = str(e)
            if dest.exists():
                rec["sha256"] = sha256_of(dest)
                rec["bytes"] = dest.stat().st_size
                rec["page_count"] = page_count_of(dest)
            results.append(rec)
            print(f"{rec['status']:>10}  {src['source_id']}"
                  f"  pages={rec.get('page_count', '-')}")
    report = {
        "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
        "results": results,
    }
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    return results


if __name__ == "__main__":
    results = download_all()
    ok = sum(r["status"] in ("downloaded", "cached") for r in results)
    print(f"\n{ok}/{len(results)} sources on disk; report: {REPORT}")
