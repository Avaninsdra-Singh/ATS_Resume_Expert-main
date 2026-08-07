import re
from typing import Iterable


def normalize_text(text):
    cleaned = re.sub(r"[^a-z0-9\s]", " ", text.lower())
    return re.sub(r"\s+", " ", cleaned).strip()


def stem_word(word):
    return re.sub(r"(?:s|es|ed|ing)$", "", word.lower()) if len(word) > 4 else word.lower()


def match_with_synonyms(required, actual_text):
    normalized_text = normalize_text(actual_text)
    actual_tokens = normalized_text.split()
    actual_stems = {stem_word(token) for token in actual_tokens}

    matched = []
    for phrase in required:
        normalized_phrase = normalize_text(phrase)
        if not normalized_phrase:
            continue

        if normalized_phrase in normalized_text:
            matched.append(phrase)
            continue

        phrase_tokens = normalized_phrase.split()
        if all(stem_word(token) in actual_stems for token in phrase_tokens):
            matched.append(phrase)
            continue

    return matched
