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


def guess_title(text):
    """Use the first non-empty line as a title if it looks like a headline."""
    first_line = next((l.strip() for l in (text or "").splitlines() if l.strip()), "")
    word_count = len(first_line.split())
    looks_like_headline = 3 <= word_count <= 20 and len(first_line) <= 150 \
        and not first_line.endswith((".", "!", "?"))
    return first_line if looks_like_headline else ""


def tidy_summary(text):
    """Remove spaces the tokenizer leaves before punctuation (e.g. '4.7% .' -> '4.7%.')."""
    import re
    text = re.sub(r"\s+([.,;:!?%)])", r"\1", text)
    return re.sub(r"([(])\s+", r"\1", text)


def split_headline(raw_text: str):
    """Split pasted text into (headline, body). Call on RAW text, before clean_text()."""
    if not isinstance(raw_text, str):
        return "", ""
    lines = raw_text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    for index, line in enumerate(lines):
        if not line.strip():
            continue
        candidate = clean_text(line)
        body = "\n".join(lines[index + 1:])
        looks_like_headline = (
            3 <= len(candidate.split()) <= 25
            and len(candidate) <= 200
            and not candidate.endswith(".")
            and len(clean_text(body)) > 0
        )
        return (candidate, body) if looks_like_headline else ("", raw_text)
    return "", raw_text


def title_from_summary(summary: str, max_words: int = 14) -> str:
    """Fallback title: the first sentence of the generated summary, shortened."""
    summary = clean_text(summary)
    if not summary:
        return ""
    first_sentence = re.split(r"(?<=[.!?])\s+", summary)[0].rstrip(" .!?;:,")
    words = first_sentence.split()
    if len(words) > max_words:
        first_sentence = " ".join(words[:max_words]).rstrip(" ,;:-") + "..."
    return first_sentence


def tidy_summary(text: str) -> str:
    """Remove spaces the tokenizer can leave before punctuation ('4.7% .' -> '4.7%.')."""
    text = clean_text(text)
    text = re.sub(r"\s+([.,;:!?%)])", r"\1", text)
    return re.sub(r"([(])\s+", r"\1", text)
