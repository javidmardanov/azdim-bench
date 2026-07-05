"""Parse a model's raw output into an answer label A-E (or None)."""

import re

# a standalone letter A-E, possibly wrapped in punctuation: "C", "C)", "(C).",
# "**C**", "Cavab: C", "Ответ: C"
_STANDALONE = re.compile(r"(?<![A-Za-z])([A-E])(?![A-Za-z])")


def parse_answer(raw: str) -> str | None:
    if not raw:
        return None
    text = raw.strip()
    # strict: entire output is one letter (after stripping punctuation/markup)
    bare = re.sub(r"[\s*_.()\[\]\"'`:]+", "", text)
    if len(bare) == 1 and bare in "ABCDE":
        return bare
    # fallback 1: letter on the last non-empty line
    last = text.splitlines()[-1].strip()
    m = _STANDALONE.findall(last)
    if len(set(m)) == 1:
        return m[0]
    # fallback 2: unique standalone letter anywhere in the output
    m = _STANDALONE.findall(text)
    if len(set(m)) == 1:
        return m[0]
    return None
