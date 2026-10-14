from __future__ import annotations

import re


def _remove_all_occurrences(text: str, attack: str) -> tuple[str, bool]:
    if not attack:
        return text, False
    pattern = re.compile(re.escape(attack), re.IGNORECASE)
    if not pattern.search(text):
        return text, False
    clean = pattern.sub(" ", text)
    clean = re.sub(r"[ \t]+\n", "\n", clean)
    clean = re.sub(r"\n[ \t]+", "\n", clean)
    clean = re.sub(r"\n{3,}", "\n\n", clean)
    return clean.strip(), True


def _insert_attack(text: str, attack: str, position: str) -> str:
    position = (position or "end").lower()
    if position == "start":
        return attack + "\n" + text
    if position == "middle":
        index = len(text) // 2
        right = text.find(" ", index)
        left = text.rfind(" ", 0, index)
        choices = [i for i in (left, right) if i >= 0]
        if choices:
            index = min(choices, key=lambda i: abs(i - index))
        return text[:index] + "\n" + attack + "\n" + text[index:]
    return text + "\n" + attack


def build_clean_poison_pair(
    context: str,
    attack: str,
    position: str = "end",
) -> tuple[str, str, bool]:
    """Return (clean_text, poisoned_text, found_in_source_context).

    All occurrences of an embedded payload are removed from the negative example.
    If the source row contains only clean context plus injection metadata, construct
    the positive by inserting the attack at its declared position. Assertions here
    protect downstream training from silently receiving identical or mislabeled text.
    """
    if not isinstance(context, str) or not context.strip():
        raise ValueError("context must be non-empty text")
    if not isinstance(attack, str) or not attack.strip():
        raise ValueError("attack must be non-empty text")

    context = context.strip()
    attack = attack.strip()
    clean, found = _remove_all_occurrences(context, attack)
    if found:
        poisoned = context
    else:
        clean = context
        poisoned = _insert_attack(context, attack, position)

    if attack.casefold() not in poisoned.casefold():
        raise ValueError("positive example does not contain the attack payload")
    if attack.casefold() in clean.casefold():
        raise ValueError("negative example still contains the attack payload")
    if not clean.strip() or not poisoned.strip():
        raise ValueError("clean and poisoned examples must both be non-empty")
    return clean, poisoned, found
