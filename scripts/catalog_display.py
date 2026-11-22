"""Shared display rules for the Markdown directory and the static site."""
import re
from html import unescape


_CURRENCY = r"(?:US\$|CA\$|AU\$|[$€£¥₹])"
_AMOUNT = r"\d+(?:[,.]\d+)*(?:\s*[KMB](?=\b|cash|credits))?"
_CODES = r"USD|CAD|EUR|GBP|AUD|JPY|INR"
_MONEY = re.compile(
    rf"{_CURRENCY}\s*{_AMOUNT}(?:\s+(?:in )?(?:cash|credits|value))?"
    rf"|\b(?:{_CODES})\s*{_AMOUNT}"
    rf"|\b{_AMOUNT}\s*{_CURRENCY}"
    rf"|\b{_AMOUNT}\s*(?:{_CODES}|dollars?|euros?|in cash|cash|credits)\b",
    re.I,
)


def _without_monetary_asides(title):
    start = None
    depth = 0
    previous = 0
    parts = []
    for index, char in enumerate(title):
        if char == "(":
            if depth == 0:
                start = index
            depth += 1
        elif char == ")" and depth:
            depth -= 1
            if depth == 0:
                parts.append(title[previous:start])
                aside = title[start:index + 1]
                if not _MONEY.search(aside):
                    parts.append(aside)
                previous = index + 1
    if depth and _MONEY.search(title[start:]):
        parts.append(title[previous:start])
    else:
        parts.append(title[previous:])
    return "".join(parts)


def has_money(text):
    return bool(_MONEY.search(unescape(text)))


def display_text(text):
    """Drop monetary asides and amounts from viewer-facing prose."""
    if not has_money(text):
        return text
    text = _without_monetary_asides(unescape(text))
    text = _MONEY.sub("", text)
    return " ".join(text.split()).replace(" .", ".").replace(" ,", ",").strip(" :-–—+,/")


def display_prize_title(title):
    """Remove money from a display label while preserving the original export value."""
    if not has_money(title):
        return title
    title = _without_monetary_asides(unescape(title))
    title, *extras = re.split(r"\s+\+\s+", title)
    title = " + ".join([title, *(part for part in extras if not _MONEY.match(part.strip()))])
    title = _MONEY.sub("", title)
    return " ".join(title.split()).strip(" :-–—+,/") or "Prize"


def short_prize_title(title, sponsor):
    title = display_prize_title(title)
    if sponsor:
        title = re.sub(r"^\[[^\]]+\]\s*", "", title)
        title = re.sub(r"^MLH\s*[:\-–]\s*", "", title, flags=re.I)
        for separator in (": ", " - ", " – "):
            prefix = sponsor + separator
            if title.casefold().startswith(prefix.casefold()):
                title = title[len(prefix):]
    trimmed = re.sub(r"\s*\([^()]*\)$", "", title)
    return (trimmed if len(trimmed) >= 8 else title) or "Prize"
