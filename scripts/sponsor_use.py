"""Validate the published claim and evidence for each sponsor use note."""
import csv
from functools import lru_cache
from pathlib import Path
import re


MISSING_INTEGRATION = "Sponsor use not stated on Devpost"
BUILT_WITH = "devpost:built_with"
USE_EVIDENCE = {
    "devpost:how_we_built": "Devpost project write-up",
    "devpost:what_it_does": "Devpost project write-up",
    BUILT_WITH: "Devpost Built With",
    "github:readme": "GitHub README",
}
USE_UNAVAILABLE = "Integration detail unavailable"
ALIAS_FILE = Path(__file__).with_name("sponsor-aliases.tsv")
USE_FILE = Path(__file__).with_name("sponsor-uses.tsv")
FRAMING_WORDS = frozenset("""
    a an and are as at be been built by for from had has have in is it its of on or our that the
    their them these they this those to used use uses using via was we were which who with project team
    listed devpost through
""".split())


def words(text):
    return re.findall(r"[^\W_]+(?:#|\+\+)?", text.casefold())


@lru_cache(maxsize=1)
def sponsor_aliases():
    aliases = {}
    with ALIAS_FILE.open(encoding="utf-8", newline="") as stream:
        for sponsor, *products in csv.reader(stream, delimiter="\t"):
            if sponsor in aliases or not products or not all(products):
                raise ValueError(f"Invalid alias row for {sponsor}")
            aliases[sponsor] = products
    return aliases


@lru_cache(maxsize=None)
def search_terms(sponsor):
    names = sponsor.split(" / ")
    return tuple(dict.fromkeys(
        term for name in [sponsor, *names]
        for term in [name, *sponsor_aliases().get(name, [])]
    ))


@lru_cache(maxsize=None)
def alias_pattern(sponsor):
    terms = sorted(search_terms(sponsor), key=len, reverse=True)
    patterns = []
    for term in terms:
        pieces = words(term)
        if not pieces:
            continue
        prefix = r"\." if term.startswith(".") else r"(?<!\w)"
        segment = r"[\s.\-_:&]*".join(map(re.escape, pieces))
        patterns.append(rf"{prefix}{segment}(?!\w)")
    return re.compile("|".join(patterns), re.I)


def normalize_products(text, sponsor):
    return alias_pattern(sponsor).sub(lambda hit: "".join(words(hit[0])), text)


def word_forms(word):
    forms = {word}
    for ending in ("s", "es", "ed", "ing"):
        if word.endswith(ending) and len(word) > len(ending) + 2:
            base = word.removesuffix(ending)
            forms.update((base, base + "e"))
    if word.endswith(("ies", "ied")) and len(word) >= 5:
        forms.add(word[:-3] + "y")
    return forms


def claim_words(text, sponsor):
    text = re.sub(r"['’]s\b", "", text, flags=re.I)
    return words(normalize_products(text, sponsor))


def ungrounded_words(note, quote, sponsor):
    """Check content words against evidence, with inflections and product spellings."""
    evidence = set().union(*(word_forms(word) for word in claim_words(quote, sponsor)))
    claim = set(claim_words(note, sponsor)) - FRAMING_WORDS
    return sorted(word for word in claim if not (word_forms(word) & evidence))


def built_with_note(product):
    return f"Built with {product} (listed on Devpost)"


def validate_use(row):
    sponsor = row["sponsor"]
    source, quote = row["use_source"], row["use_quote"]
    note = row["sponsor_integration"]
    if note == MISSING_INTEGRATION:
        if source is not None or quote is not None or row["summary_evidence"] != USE_UNAVAILABLE:
            raise ValueError("Placeholder has conflicting use evidence")
        return
    if source not in USE_EVIDENCE or row["summary_evidence"] != USE_EVIDENCE[source]:
        raise ValueError("Missing or invalid use source")
    if not quote or len(quote) > 200 or quote != " ".join(quote.split()):
        raise ValueError("Use quote must contain 1–200 characters of source text")
    if sponsor == "Other" or not alias_pattern(sponsor).search(quote):
        raise ValueError("Use quote does not name the sponsor or a product")
    if not alias_pattern(sponsor).search(note):
        raise ValueError("Use note does not name the sponsor or a product")
    if source == BUILT_WITH:
        expected = built_with_note(quote)
        if quote not in row["built_with"] or note.casefold() != expected.casefold():
            raise ValueError("Built With claim must repeat a matching Devpost tag")
    elif not note.endswith(".") or note.endswith(" ."):
        raise ValueError("Full use note must be a sentence")
    missing = ungrounded_words(note, quote, sponsor)
    if missing:
        raise ValueError(f"Use note has words absent from its quote: {', '.join(missing)}")


def load_uses():
    notes = {}
    with USE_FILE.open(encoding="utf-8", newline="") as stream:
        for url, sponsor, note, source, quote in csv.reader(stream, delimiter="\t"):
            key = url, sponsor
            if key in notes:
                raise ValueError(f"Duplicate sponsor use: {key}")
            notes[key] = note, source, quote
    return notes
