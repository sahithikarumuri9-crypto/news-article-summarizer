"""Small reusable text utilities."""
import re


def clean_text(text: str) -> str:
    """Normalize whitespace without changing the article's wording."""
    if not isinstance(text, str):
        return ""
    text = text.replace("\x00", " ")
    return re.sub(r"\s+", " ", text).strip()


def word_count(text: str) -> int:
    """Count whitespace-separated words."""
    return len(clean_text(text).split())


def compression_percent(original: str, summary: str) -> float:
    """Return percentage reduction in word count."""
    original_count = word_count(original)
    if original_count == 0:
        return 0.0
    reduction = (1 - word_count(summary) / original_count) * 100
    return round(max(0.0, reduction), 1)
