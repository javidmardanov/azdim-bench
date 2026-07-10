"""Deterministic per-item bounding boxes for the verification tool.

We never captured coordinates during extraction, but the DİM PDFs have a clean
text layer — so we locate each item on its page by matching the plain-language
tokens of its question stem against the page's word coordinates
(`pdftotext -bbox`). Math-heavy stems with few plain words simply return no box
(graceful: better a missing box than a wrong one).

Coordinates are returned as fractions of page width/height so the caller can
overlay them on any rendering of the page regardless of scale.
"""

import re
import subprocess
from functools import lru_cache
from xml.etree import ElementTree as ET

# Azerbaijani-aware lowercasing: the dotted/dotless I pair and the special
# letters must fold without Unicode decomposition (NFKD shreds ğ/ç/ə into
# base + combining mark, which then splits the token).
_AZ = str.maketrans({"İ": "i", "I": "ı", "Ə": "ə", "Ç": "ç",
                     "Ş": "ş", "Ğ": "ğ", "Ö": "ö", "Ü": "ü"})


def _norm(s: str) -> str:
    s = re.sub(r"\\[a-zA-Z]+", " ", s)      # strip LaTeX commands
    s = re.sub(r"[${}^_\\~]", " ", s)       # strip LaTeX punctuation
    s = s.translate(_AZ).lower()
    return re.sub(r"[^\w\s]", " ", s, flags=re.UNICODE)


def _stem(text: str, k: int = 10) -> list[str]:
    return [t for t in _norm(text).split() if len(t) >= 4][:k]


@lru_cache(maxsize=256)
def _page_words(pdf_path: str, page: int):
    """Return (words, page_w, page_h). words: [(norm_text, x0, y0, x1, y1)]."""
    xml = subprocess.run(
        ["pdftotext", "-bbox", "-f", str(page), "-l", str(page), pdf_path, "-"],
        capture_output=True, text=True).stdout
    xml = re.sub(r'xmlns="[^"]+"', "", xml, count=1)
    pg = ET.fromstring(xml).find(".//page")
    if pg is None:
        return [], 0.0, 0.0
    pw, ph = float(pg.get("width")), float(pg.get("height"))
    words = []
    for w in pg.findall(".//word"):
        t = _norm(w.text or "").strip()
        if t:
            words.append((t, float(w.get("xMin")), float(w.get("yMin")),
                          float(w.get("xMax")), float(w.get("yMax"))))
    return words, pw, ph


def _match(words, question_text):
    """Best contiguous run of the stem tokens in the page word stream."""
    toks = _stem(question_text)
    if len(toks) < 3:
        return None
    wt = [w[0] for w in words]
    best = None
    for i in range(len(wt)):
        j, hits, idxs = i, 0, []
        for t in toks:
            for dj in range(8):            # tolerate small gaps (math between words)
                if j + dj < len(wt) and wt[j + dj] == t:
                    idxs.append(j + dj)
                    j = j + dj + 1
                    hits += 1
                    break
        if best is None or hits > best[0]:
            best = (hits, idxs)
    hits, idxs = best
    if hits < max(3, len(toks) - 3):
        return None
    xs = [words[m][1] for m in idxs] + [words[m][3] for m in idxs]
    ys = [words[m][2] for m in idxs] + [words[m][4] for m in idxs]
    return min(xs), min(ys), max(xs), max(ys)


def item_box(pdf_path: str, page: int, question_text: str, pad: float = 4.0):
    """Fractional (x, y, w, h) box for an item, or None if not confidently located."""
    words, pw, ph = _page_words(pdf_path, page)
    if not words or pw == 0:
        return None
    m = _match(words, question_text)
    if not m:
        return None
    x0, y0, x1, y1 = m
    x0 = max(0.0, x0 - pad) / pw
    y0 = max(0.0, y0 - pad) / ph
    x1 = min(pw, x1 + pad) / pw
    y1 = min(ph, y1 + pad) / ph
    return (x0, y0, x1 - x0, y1 - y0)
