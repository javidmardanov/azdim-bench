"""Parse a model's raw output into an answer label A-E (or None)."""

import re

# a standalone letter A-E, possibly wrapped in punctuation: "C", "C)", "(C).",
# "**C**", "Cavab: C", "Ответ: C"
_STANDALONE = re.compile(r"(?<![A-Za-z])([A-E])(?![A-Za-z])")
# explicit final-answer marker in AZ / RU / EN
_MARKER = re.compile(
    r"(?:cavab|ответ|answer)\s*[:\-–]?\s*\**\s*([A-E])(?![A-Za-z])",
    re.IGNORECASE)


def parse_answer(raw: str) -> str | None:
    if not raw:
        return None
    text = raw.strip()
    # preferred: last explicit "Cavab: X" / "Ответ: X" marker
    markers = _MARKER.findall(text)
    if markers:
        return markers[-1]
    # strict: entire output is one letter (after stripping punctuation/markup)
    bare = re.sub(r"[\s*_.()\[\]\"'`:]+", "", text)
    if len(bare) == 1 and bare in "ABCDE":
        return bare
    # fallback 1: letter on the first non-empty line (models often lead with
    # "C) ..."), then the last line ("Cavab: C")
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    for line in (lines[0], lines[-1]):
        m = _STANDALONE.findall(line)
        if len(set(m)) == 1:
            return m[0]
    # fallback 2: unique standalone letter anywhere in the output
    m = _STANDALONE.findall(text)
    if len(set(m)) == 1:
        return m[0]
    return None
