"""Fixed evaluation prompts. Frozen for v0 — do not edit between runs.

Main condition (v0): the model may reason visibly, but must end with a
single final-answer line. This follows MMLU-Pro/AGIEval practice and avoids
conflating instruction compliance with ability (bare-letter prompts make
compliant models answer math blind while non-compliant ones reason anyway).
"""

# Track A: native Azerbaijani
INSTR_AZ = ("Sualı həll et. İstəsən qısa izah verə bilərsən, amma cavabının "
            "SON sətri mütləq bu formatda olmalıdır:\n"
            "Cavab: <hərf>\n"
            "burada <hərf> A, B, C, D və ya E-dir.")

# Track B: native Russian
INSTR_RU = ("Реши задачу. Можешь кратко объяснить решение, но ПОСЛЕДНЯЯ "
            "строка твоего ответа должна иметь строго такой формат:\n"
            "Ответ: <буква>\n"
            "где <буква> — A, B, C, D или E.")

# Track F: foreign-language exam sections (EN/DE/FR items); meta-instruction
# in English, the items themselves stay in their language
INSTR_EN = ("Solve the task. You may explain briefly, but the LAST line of "
            "your answer must have exactly this format:\n"
            "Answer: <letter>\n"
            "where <letter> is A, B, C, D or E.")

INSTR_BY_LANG = {"az": INSTR_AZ, "ru": INSTR_RU,
                 "en": INSTR_EN, "de": INSTR_EN, "fr": INSTR_EN}


def format_mcq(item: dict) -> str:
    """Render one MCQ item as the user prompt for its native language."""
    instr = INSTR_BY_LANG.get(item["language"], INSTR_AZ)
    lines = [instr, "", item["question_text"].strip(), ""]
    for letter in "ABCDE":
        choice = (item.get("choices") or {}).get(letter)
        if choice is not None and str(choice).strip():
            lines.append(f"{letter}) {choice}")
    return "\n".join(lines)
