"""Validate the published claim and evidence for each sponsor use note."""
import csv
from functools import lru_cache
from html import unescape
import json
from pathlib import Path
import re
from urllib.parse import parse_qs, unquote, urlsplit


MISSING_INTEGRATION = "Sponsor use not stated on Devpost"
BUILT_WITH = "devpost:built_with"
CODE = "code"
VIDEO = "demo_video"
AWARD = "award"
INFERRED_PREFIX = "inferred:"
INFERRED_FROM = {
    "devpost:what_it_does": "write-up",
    "devpost:how_we_built": "write-up",
    "devpost:other_sections": "write-up",
    "devpost:gallery_caption": "write-up",
    BUILT_WITH: "write-up",
    VIDEO: "demo",
    "github:readme": "README",
}
DEPENDENCY_NOTE = "Lists "
CODE_QUOTE = re.compile(r"(?P<path>[^:]+):(?P<line>[1-9][0-9]*) (?P<text>.+)")
TIMED_QUOTE = re.compile(r"(?P<time>[0-9]{2}:[0-5][0-9]:[0-5][0-9]) (?P<text>.+)")
PINNED_CODE_URL = re.compile(
    r"(https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)/blob/[a-f0-9]{40}/([^#]+)#L([1-9][0-9]*)"
)
DEPENDENCY_PATH = re.compile(
    r"(?:^|/)(?:package\.json|requirements[^/]*\.txt|pyproject\.toml|go\.mod|Cargo\.toml|"
    r"Pipfile|Gemfile|composer\.json|pubspec\.yaml|pom\.xml|build\.gradle(?:\.kts)?|"
    r"Package\.swift|[^/]+\.csproj)$", re.I,
)
USE_EVIDENCE = {
    "devpost:how_we_built": "Devpost project write-up",
    "devpost:what_it_does": "Devpost project write-up",
    BUILT_WITH: "Devpost Built With",
    "github:readme": "GitHub README",
    "devpost:other_sections": "Devpost project write-up",
    "devpost:gallery_caption": "Devpost gallery caption",
    "devpost:project_link": "Devpost project link",
    CODE: "GitHub source code",
    VIDEO: "Demo video captions",
    AWARD: "Devpost prize title",
}
USE_UNAVAILABLE = "Integration detail unavailable"
DEPENDENCY_EVIDENCE = "GitHub dependency manifest"
ALIAS_FILE = Path(__file__).with_name("sponsor-aliases.tsv")
USE_FILE = Path(__file__).with_name("sponsor-uses.tsv")
AWARD_FILE = Path(__file__).with_name("award-framing.tsv")
INFERRED_FILE = Path(__file__).with_name("inferred-uses.tsv")
INFERRED_CACHE = Path(__file__).with_name("inferred-evidence.tsv")
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


def award_note(sponsor, prize):
    return f"Won “{prize}” from {sponsor}. The write-up gives no details on how the team used the sponsor’s tech."


def project_link_note(sponsor, quote):
    if sponsor == ".Tech Domains" and re.fullmatch(r"(?:[a-z0-9-]+\.)+tech", quote):
        return f"The team links to {quote} as its .tech project site."
    if sponsor == "Defang" and re.fullmatch(r"(?:[a-z0-9-]+\.)+defang\.dev", quote):
        return "The team links to a Defang-hosted project endpoint."
    if sponsor == "Hex" and quote == "app.hex.tech":
        return "The team links to its project work on Hex."
    if sponsor == "Figma":
        route = re.fullmatch(r"www\.figma\.com/(design|file|make|proto|slides)/", quote)
        if route:
            resource = {"design": "design file", "file": "file", "make": "Make project",
                        "proto": "prototype", "slides": "slide deck"}[route[1]]
            return f"The team links to its Figma {resource}."
    return None


def source_label(source, note):
    if base := inference_source(source):
        return f"Inferred from {USE_EVIDENCE[base]}"
    if source == CODE and note.startswith(DEPENDENCY_NOTE):
        return DEPENDENCY_EVIDENCE
    return USE_EVIDENCE.get(source, USE_UNAVAILABLE)


def use_coverage(row):
    source = row.get("use_source")
    if inference_source(source):
        return "inferred"
    if source == AWARD:
        return "award-framed"
    if source == BUILT_WITH or row.get("summary_evidence") == DEPENDENCY_EVIDENCE:
        return "grounded-light"
    return "full" if source else "not stated"


def inference_source(source):
    if source and source.startswith(INFERRED_PREFIX):
        base = source.removeprefix(INFERRED_PREFIX)
        if base in INFERRED_FROM:
            return base
    return None


def prize_key(row):
    return row["event_slug"], row["url"], row["prize"]


def inferred_note(product, feature, source):
    return f"Likely used {product} for {feature} (inferred from the {INFERRED_FROM[source]})."


def validate_inferred_use(row, base):
    note = row["sponsor_integration"]
    quote = row["use_quote"]
    url = row["use_evidence_url"]
    suffix = re.escape(f" (inferred from the {INFERRED_FROM[base]}).")
    phrase = r"\S(?:[^\n]*\S)?"
    if row.get("inferred") is not True or not re.fullmatch(rf"Likely used {phrase} for {phrase}{suffix}", note):
        raise ValueError("Inferred use requires inferred=true and the source-specific note wording")
    if row["sponsor"] == "Other" or row["summary_evidence"] != source_label(row["use_source"], note):
        raise ValueError("Invalid inferred sponsor or summary evidence")
    if base.startswith("devpost:"):
        linked = url == row["url"]
    elif base == VIDEO:
        linked = url in row["demo_video_urls"] and urlsplit(url).hostname in {"www.youtube.com", "vimeo.com"}
    else:
        linked = url in row["source_urls"] and url.startswith("https://github.com/")
    if not linked:
        raise ValueError("Inference must cite its project page, linked README or linked demo")
    if not quote or quote != " ".join(quote.split()) or len(quote) > 200:
        raise ValueError("Inferred quote must contain 1–200 characters of verbatim source text")
    if not any(quote in excerpt for excerpt in load_inferred_cache().get((url, base), [])):
        raise ValueError("Inferred quote is absent from the cited source cache")


def validate_code_quote(row, quote, evidence_url):
    locator = CODE_QUOTE.fullmatch(quote)
    origin = PINNED_CODE_URL.fullmatch(evidence_url or "")
    if not locator or not origin:
        raise ValueError("Code requires a path:line quote and a commit-pinned GitHub URL")
    repo, encoded_path, line = origin.groups()
    path = locator["path"]
    if repo not in row["source_urls"] or unquote(encoded_path) != path or locator["line"] != line:
        raise ValueError("Code quote does not match its linked repository, path or line")
    if path.startswith("/") or any(part in {"", ".", ".."} for part in path.split("/")):
        raise ValueError("Invalid quoted code path")
    if row["summary_evidence"] == DEPENDENCY_EVIDENCE:
        if not DEPENDENCY_PATH.search(path):
            raise ValueError("Dependency-only claim must point to a dependency manifest")
        match = re.fullmatch(r"Lists (.+) as a dependency\.", row["sponsor_integration"])
        if not match or match[1].casefold() not in locator["text"].casefold():
            raise ValueError("Dependency-only claim must name the listed dependency")
    elif DEPENDENCY_PATH.search(path):
        raise ValueError("Dependency manifest alone cannot support a full use note")
    return locator["text"], path


def validate_use(row):
    sponsor = row["sponsor"]
    source, quote = row["use_source"], row["use_quote"]
    evidence_url = row.get("use_evidence_url")
    note = row["sponsor_integration"]
    if base := inference_source(source):
        validate_inferred_use(row, base)
        return
    if "inferred" in row:
        raise ValueError("Only inferred sources can carry the inferred flag")
    if note == MISSING_INTEGRATION:
        if any(value is not None for value in (source, quote, evidence_url)) or row["summary_evidence"] != USE_UNAVAILABLE:
            raise ValueError("Placeholder has conflicting use evidence")
        return
    if source not in USE_EVIDENCE or row["summary_evidence"] != source_label(source, note):
        raise ValueError("Missing or invalid use source")
    if source == AWARD:
        if sponsor == "Other" or evidence_url or quote != row["prize"] or note != award_note(sponsor, quote):
            raise ValueError("Award framing must repeat the exact verified prize")
        return
    if not quote or len(quote) > 200 or quote != " ".join(quote.split()):
        raise ValueError("Use quote must contain 1–200 characters of source text")
    excerpt = quote
    if source == CODE:
        text, path = validate_code_quote(row, quote, evidence_url)
        excerpt = f"{path} {text}".replace("_", " ")
    elif source == VIDEO:
        timed = TIMED_QUOTE.fullmatch(quote)
        if not timed or evidence_url not in row["demo_video_urls"]:
            raise ValueError("Video requires a timestamped quote from a linked demo")
        if urlsplit(evidence_url).hostname not in {"www.youtube.com", "vimeo.com"}:
            raise ValueError("Video source must be a YouTube or Vimeo demo")
        excerpt = timed["text"]
    elif evidence_url:
        raise ValueError("Unexpected evidence URL")
    if sponsor == "Other" or not alias_pattern(sponsor).search(excerpt):
        raise ValueError("Use quote does not name the sponsor or a product")
    if not alias_pattern(sponsor).search(note):
        raise ValueError("Use note does not name the sponsor or a product")
    if source == BUILT_WITH:
        expected = built_with_note(quote)
        if quote not in row["built_with"] or note.casefold() != expected.casefold():
            raise ValueError("Built With claim must repeat a matching Devpost tag")
    elif not note.endswith(".") or note.endswith(" ."):
        raise ValueError("Full use note must be a sentence")
    if source == CODE:
        return
    if source == "devpost:project_link":
        if note != project_link_note(sponsor, quote):
            raise ValueError("Project-link note must describe the linked sponsor resource")
        return
    missing = ungrounded_words(note, excerpt, sponsor)
    if missing:
        raise ValueError(f"Use note has words absent from its quote: {', '.join(missing)}")


def caption_words(path):
    """Yield timestamped words, removing the repeated lines in rolling VTT cues."""
    previous = []
    for block in re.split(r"\n\s*\n", path.read_text(encoding="utf-8-sig")):
        cue = re.search(r"^(\d{2}:\d{2}:\d{2})\.\d+ --> [^\n]+\n(.+)", block, re.M | re.S)
        if not cue:
            continue
        timestamp, text = cue.groups()
        current = unescape(re.sub(r"<[^>]*>", "", text)).split()
        overlap = next(
            (n for n in range(min(len(current), len(previous)), 0, -1) if previous[-n:] == current[:n]),
            0,
        )
        yield from ((timestamp, word) for word in current[overlap:])
        previous = current


def caption_paths(cache, url):
    parts = urlsplit(url)
    video = parse_qs(parts.query).get("v", [""])[0] if parts.hostname == "www.youtube.com" else parts.path.strip("/")
    return (cache / "captions").glob(f"{video}.*.vtt")


def check_cached_use(cache, source, quote, url):
    if source == CODE:
        repo, _, _ = PINNED_CODE_URL.fullmatch(url).groups()
        locator = CODE_QUOTE.fullmatch(quote)
        root = cache / "repos" / repo.removeprefix("https://github.com/")
        path = root / "files" / locator["path"]
        stamp = root / "tree.json"
        if not path.is_file() or not stamp.is_file():
            return False
        if json.loads(stamp.read_text(encoding="utf-8"))["sha"] != urlsplit(url).path.split("/")[4]:
            return False
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        index = int(locator["line"]) - 1
        return index < len(lines) and locator["text"] in " ".join(lines[index].split())
    match = TIMED_QUOTE.fullmatch(quote)
    expected = match["text"].split()
    for path in caption_paths(cache, url):
        tokens = list(caption_words(path))
        words_only = [word for _, word in tokens]
        for i, (timestamp, word) in enumerate(tokens):
            if timestamp == match["time"] and word == expected[0] and words_only[i:i + len(expected)] == expected:
                return True
    return False


@lru_cache(maxsize=1)
def load_inferred_cache():
    excerpts = {}
    with INFERRED_CACHE.open(encoding="utf-8", newline="") as stream:
        for url, source, passage in csv.reader(stream, delimiter="\t"):
            if source not in INFERRED_FROM or not passage or passage != " ".join(passage.split()):
                raise ValueError(f"Invalid inferred evidence for {url}")
            excerpts.setdefault((url, source), []).append(passage)
    return excerpts


def load_inferred_uses():
    uses = {}
    with INFERRED_FILE.open(encoding="utf-8", newline="") as stream:
        for event, url, prize, product, feature, source, quote, location in csv.reader(stream, delimiter="\t"):
            key = event, url, prize
            if key in uses or not product or not feature or source not in INFERRED_FROM:
                raise ValueError(f"Invalid or duplicate inferred use: {key}")
            uses[key] = inferred_note(product, feature, source), INFERRED_PREFIX + source, quote, location
    return uses


def load_uses():
    notes = {}
    with USE_FILE.open(encoding="utf-8", newline="") as stream:
        for url, sponsor, note, source, quote, *location in csv.reader(stream, delimiter="\t"):
            key = url, sponsor
            if key in notes or len(location) > 1:
                raise ValueError(f"Invalid or duplicate sponsor use: {key}")
            notes[key] = note, source, quote, (location[0] if location else None)
    return notes


def load_award_tracks():
    tracks = set()
    with AWARD_FILE.open(encoding="utf-8", newline="") as stream:
        for event, prize, sponsor, rationale in csv.reader(stream, delimiter="\t"):
            key = event, prize, sponsor
            if key in tracks or not rationale.strip() or sponsor == "Other":
                raise ValueError(f"Invalid or duplicate award framing: {key}")
            tracks.add(key)
    return tracks
