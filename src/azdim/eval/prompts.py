"""Fixed evaluation prompts. Frozen for v0 — do not edit between runs."""

# Track A: native Azerbaijani, answer letter only
INSTR_AZ = ("Sualı cavablandır. Yalnız doğru cavab variantının hərfini yaz: "
            "A, B, C, D və ya E.")

# Track B: native Russian, answer letter only
INSTR_RU = ("Ответь на вопрос. Напиши только букву правильного варианта: "
            "A, B, C, D или E.")

INSTR_BY_LANG = {"az": INSTR_AZ, "ru": INSTR_RU}


def format_mcq(item: dict) -> str:
    """Render one MCQ item as the user prompt for its native language."""
    instr = INSTR_BY_LANG.get(item["question_language"], INSTR_AZ)
    lines = [instr, "", item["question_text"].strip(), ""]
    for letter in "ABCDE":
        choice = (item.get("choices") or {}).get(letter)
        if choice is not None and str(choice).strip():
            lines.append(f"{letter}) {choice}")
    return "\n".join(lines)
