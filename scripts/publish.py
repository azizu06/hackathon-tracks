#!/usr/bin/env python3
"""Reconcile cached Devpost evidence and render the sponsor-track directory."""
import argparse
from collections import defaultdict
import csv
import json
from pathlib import Path
import re

from evidence import clean, overview_tracks, project_details
from fetch import Fetcher, cache_path, gallery_winners, prize_label, verified_link
from sponsor_use import BUILT_WITH, MISSING_INTEGRATION, USE_EVIDENCE, USE_UNAVAILABLE, load_uses, validate_use


HERE = Path(__file__).resolve().parent
OTHER_SPONSOR = "Other"
FEATURED_URL = "https://devpost.com/software/backrooms-h4o783"
FEATURED_EVENT = "cal-hacks-13-0"
FEATURED_PRIZE = "[Hyphenate] The Hyphenated Enterprise: Autonomous Systems for Finance"


def load_tsv(name):
    with (HERE / name).open(encoding="utf-8", newline="") as source:
        return list(csv.reader(source, delimiter="\t"))


def events():
    return {slug: (name, int(year)) for slug, name, year in load_tsv("events.tsv")}


def gallery_url(event):
    return f"https://{event}.devpost.com/project-gallery"


def event_url(event):
    return f"https://{event}.devpost.com/"


def read_page(cache, receipts, url):
    record = receipts.get(url, {})
    path = cache_path(cache, url)
    if record.get("status") != 200 or not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def candidate_awards(cache, receipts):
    classified_tracks = load_tsv("tracks.tsv")
    classifications = {(event, prize): sponsor for event, prize, sponsor in classified_tracks}
    if len(classifications) != len(classified_tracks):
        raise ValueError("tracks.tsv contains a duplicate edition and prize label")
    candidates = defaultdict(list)
    missing = defaultdict(list)
    for event in events():
        page = read_page(cache, receipts, gallery_url(event))
        if not page:
            missing[event].append("Gallery unavailable")
            continue
        seen = set()
        items = gallery_winners(page)
        labels = {item["prize"] for item in items}
        if not items:
            missing[event].append("Gallery returned HTTP 200 with no published Winner labels")
        for item in items:
            key = (item["url"], item["prize"])
            if key in seen:
                continue
            seen.add(key)
            sponsor = classifications.get((event, item["prize"]))
            if sponsor is None:
                missing[event].append(f"Unclassified track label: {item['prize']}")
            if sponsor not in (None, "-"):
                candidates[event].append((item["url"], item["prize"], sponsor, "Devpost Winner label"))
        if event == FEATURED_EVENT and FEATURED_PRIZE in labels:
            if not any(u == FEATURED_URL and p == FEATURED_PRIZE for u, p, _, _ in candidates[event]):
                candidates[event].append((FEATURED_URL, FEATURED_PRIZE, "Hyphenate", "Sponsor-reported prize"))
    return candidates, missing


def event_prizes(data, event):
    submissions = data.get("subjectOf", [])
    source = next(
        (source for source in submissions if source.get("url") == event_url(event)), None
    )
    if source is None or sum(entry.get("name") == source.get("name") for entry in submissions) > 1:
        return None
    return {
        prize_label(award) for award in data.get("award", [])
        if prize_label(award) and (
            len(submissions) == 1 or award.rpartition(" — ")[2] == source.get("name")
        )
    }


SPONSOR_TERMS = {
    "Amazon Web Services": r"\baws\b|amazon[ .-]web[ .-]services|dynamodb|\bbedrock\b|\bsagemaker\b|amazon[ .-](?:s3|transcribe)|aws[ .-]lambda",
    "Anthropic": r"anthropic|claude",
    "Capital One": r"capital[ .-]one|\bnessie\b",
    "Cognition": r"\bdevin\b",
    "DAIN Labs": r"\bdain\b",
    "Databricks": r"databricks|\bgenie\b|delta[- ]lake",
    "Elastic": r"\belasticsearch\b",
    "ElevenLabs": r"eleven[ .-]?labs",
    "Fetch.ai": r"fetch[. -]?ai|agentverse|asi[.:-]?one|uagents?",
    "FREE-WILi": r"free[ .-]?wili",
    "GoDaddy Registry": r"godaddy|\.tech\b",
    "Google": r"gemini|gemma|google[ .-](?:cloud|adk|maps)|vertex[ .-]ai|firebase|\bgcp\b",
    "HashiCorp": r"terraform|hashicorp",
    "Hugging Face": r"hugging[ .-]?face",
    "MathWorks": r"\bmatlab\b|\bsimulink\b",
    "Meta": r"\bmeta\b|\bllama[- .0-9]|muse spark|tribe v2",
    "Microsoft": r"\bazure\b|visual[ .-]studio|\bvs[ .-]?code\b|\bgit(?:hub)?[ .-]copilot\b",
    "MongoDB": r"mongo(?:db)?|\batlas\b",
    "NVIDIA": r"nvidia|jetson|tensorrt|\bcuda\b|\bdgx\b|\bnemotron\b",
    "OpenAI": r"openai|\bgpt[- .0-9]|chatgpt|\bwhisper\b|\bcodex\b",
    "QNX": r"\bqnx\b|\bqos\b",
    "Ripple": r"\bxrpl\b|\bxrp[ .-]ledger\b",
    "Snap": r"spectacles?|lens[ .-]?studio|\bsnap(?:ar)?\b",
    "Solana": r"solana|\banchor\b|\bsolders\b",
    "Spacetime": r"\bspacetimedb\b",
    "Tiger Data": r"tiger[ .-]data|timescale",
    "Zetic": r"\bzetic(?:ai)?\b|\bmelange\b",
}


def sentence(value):
    return value.strip().rstrip(".!?") + "."


def evidence_sentences(text, max_words=30):
    for part in re.split(r"(?<=[.!?])\s+(?=[A-Z])", text):
        part = re.sub(r"^We\b", "The team", part.strip().lstrip("-• "))
        part = re.sub(r"^Our\b", "The", part)
        part = re.sub(r"\b(?:our|us)\b", lambda match: "the" if match[0] == "our" else "the team", part)
        if not (7 <= len(part.split()) <= max_words) or re.search(r"[\x00-\x1f<>{}`]|\b(?:we|our|us|my|I)\b", part, re.I):
            continue
        yield sentence(part)


def sponsor_pattern(sponsor):
    names = sponsor.split(" / ")
    terms = [rf"(?<!\w){re.escape(name)}(?!\w)" for name in names]
    terms.extend(SPONSOR_TERMS[name] for name in names if name in SPONSOR_TERMS)
    return re.compile("|".join(terms), re.I)


def describe(project, sponsor, curated):
    pattern = sponsor_pattern(sponsor)
    tags = [tag for tag in project.built_with if sponsor != OTHER_SPONSOR and pattern.search(tag)]
    features = [
        s for heading, text in project.story if re.search(r"what (?:it|this|we)|features|overview", heading)
        for s in evidence_sentences(text)
    ]
    feature = features[0] if features else ""
    caption = " ".join(re.split(r"(?<=[.!?])\s+(?=[A-Z])", project.tagline)[:2])
    if curated:
        description = sentence(curated)
    elif caption and 6 <= len(caption.split()) <= 35 and not re.search(r"\b(?:I|we|our|my)\b", caption, re.I):
        description = sentence(caption)
    elif feature:
        description = feature
    elif project.story and any(evidence_sentences(project.story[0][1])):
        description = next(evidence_sentences(project.story[0][1]))
    elif caption and len(caption.split()) <= 35:
        description = f'The team describes the project as “{caption.rstrip(".!?")}”.'
    else:
        description = "The Devpost entry has no usable short project description."
    return description, tags


REQUIRED_PRODUCTS = {
    "best use of gemini": "Gemini API",
    "best use of gemma": "Gemma",
    "best use of nessie": "Capital One Nessie API",
    "best usage of nessie": "Capital One Nessie API",
    "best use of mongodb atlas": "MongoDB Atlas",
    "best use of snowflake": "Snowflake API",
    "best use of godaddy": "GoDaddy Registry domain",
    "best .tech domain": ".tech domain",
    "best use of .tech": ".tech domain",
    "best domain name from godaddy": "GoDaddy Registry domain",
    "best domain from .tech": ".tech domain",
    "best use of elevenlabs": "ElevenLabs",
    "best use of presage": "Presage",
    "best use of solana": "Solana",
    "best use of vultr": "Vultr",
    "best use of tiger data": "Tiger Data",
    "best use of jetson nano": "NVIDIA Jetson Nano",
    "best use of claude agent sdk": "Claude Agent SDK",
    "best use of claude": "Claude",
    "best use of figma": "Figma",
    "best use of github": "GitHub",
    "best ai application built with cloudflare": "Cloudflare",
    "using redis beyond caching": "Redis",
    "best use of sonic": "Cartesia Sonic",
    "best use of fetch.ai": "Fetch.ai",
    "best use of asi:one": "ASI:One",
    "best deployment of agentverse": "Agentverse",
    "claude for public benefit": "Claude",
    "databricks geo-insight challenge": "Databricks",
    "best use of open source ai": "Open-source AI",
    "build with poke": "Poke",
    "best creation with heygen": "HeyGen Avatar API",
    "best hack using a vision language model": "A vision-language model",
    "best project built on solana": "Solana",
    "best mobile experience built with expo": "Expo",
    "create an embedded system with qnx": "QNX OS",
    "best use of snap lens studio": "Lens Studio",
    "best use of factory droid sdk": "Factory Droid SDK",
}


def requirement(label, description):
    value = label.casefold()
    for phrase, product in REQUIRED_PRODUCTS.items():
        if phrase.casefold() in value:
            return product, "Track label"
    use_of = re.search(r"(?i)\bBest (?:creative )?use of\s+(.+)", label)
    if use_of:
        product = re.split(r"\s*(?:\(|\|\|| - MLH| by MLH| Winner$)", use_of[1], maxsplit=1)[0].strip()
        if product and len(product) <= 75 and not re.search(r"(?i)^AI$|^data hack$|^open.source", product):
            return product, "Track label"
    for paragraph in description:
        for part in re.split(r"(?<=[.!?])\s+|\s+[–•]\s+", paragraph):
            if 12 < len(part) < 165 and re.search(
                r"(?i)^(?:best use of|build (?:your|an?|the)|use (?:the |at least )|"
                r"(?:the |your )?projects? must|must use|must include|hard requirements)", part
            ) and not re.search(r"(?i)https?://|@|\b[\w.-]+\.com\b", part):
                return sentence(part), "Devpost prize description"
    return None, None


def stated_value(label):
    parts = label.split(" || ", maxsplit=2)
    if len(parts) == 3:
        return parts[2]
    if "$" in label or re.search(r"\b\d[\d,.]*\s*(?:USD|CAD|EUR)\b", label):
        details = re.search(r"\(([^()]*\$[^()]*)\)\s*$", label)
        return details[1] if details else label
    details = re.search(r"\(([^()]*(?:per team member|per person|gift card|credits|swag|x4)[^()]*)\)\s*$", label, re.I)
    return details[1] if details else None


def verified(links, receipts):
    return sorted({target for link in links if (target := verified_link(link, receipts))})


def dedup_project_rows(rows):
    return list({(row["event_slug"], row["url"]): row for row in rows}.values())


def cached_readme_has_quote(cache, links, quote):
    for link in links:
        if not link.startswith("https://github.com/"):
            continue
        repo = link.removeprefix("https://github.com/")
        readme = cache / f"{repo}.md"
        if readme.is_file() and quote in clean(readme.read_text(encoding="utf-8", errors="replace")):
            return True
    return False


def index_rows(cache, receipts, *, validate_quotes=True, github_cache=None):
    rows = []
    event_info = events()
    descriptions = dict(load_tsv("projects.tsv"))
    overrides = {(url, sponsor): summary for url, sponsor, summary in load_tsv("summary-descriptions.tsv")}
    uses = load_uses()
    candidates, missing = candidate_awards(cache, receipts)
    parsed = {}
    observed_links = defaultdict(set)
    for event, awards in candidates.items():
        name, year = event_info[event]
        gallery = gallery_url(event)
        overview = event_url(event)
        track_details = overview_tracks(read_page(cache, receipts, overview))
        gallery_labels = defaultdict(set)
        for item in gallery_winners(read_page(cache, receipts, gallery)):
            gallery_labels[item["url"]].add(item["prize"])
        for url, prize, sponsor, evidence in awards:
            if url not in parsed:
                html = read_page(cache, receipts, url)
                if html:
                    try:
                        parsed[url] = project_details(html)
                    except ValueError:
                        parsed[url] = None
                else:
                    parsed[url] = None
            project = parsed[url]
            if project is None:
                receipt = receipts.get(url, {})
                status = receipt.get("status")
                if status == 200:
                    reason = "HTTP 200 without project metadata"
                elif status:
                    reason = f"HTTP {status}"
                else:
                    reason = receipt.get("reason") or "No HTTP 200 project receipt"
                missing[event].append(f"{reason}: {url} ({prize})")
                continue
            if project.data.get("url") != url:
                missing[event].append(f"Canonical project mismatch: {url} ({prize})")
                continue
            labels = event_prizes(project.data, event)
            if labels is None or (evidence == "Devpost Winner label" and prize not in labels):
                missing[event].append(f"Project and gallery award disagree: {url} ({prize})")
                continue
            prizes_at_event = sorted(labels | gallery_labels[url] | ({FEATURED_PRIZE} if event == FEATURED_EVENT and url == FEATURED_URL else set()), key=str.casefold)
            if gallery_labels[url] - labels:
                missing[event].append(f"Gallery lists additional Winner labels for {url}")
            before, tags = describe(project, sponsor, overrides.get((url, sponsor), descriptions.get(url)))
            use, source, quote = uses.get((url, sponsor), (MISSING_INTEGRATION, None, None))
            if source == BUILT_WITH and quote in project.built_with and quote not in tags:
                tags.append(quote)
            rules = track_details.get(clean(prize), [])
            needed, requirement_source = requirement(prize, rules)
            observed_links["source"].update(project.source_links)
            observed_links["demo"].update(project.demo_links)
            rows.append({
                "project": project.name, "hackathon": name, "year": year, "event_slug": event,
                "sponsor": sponsor, "prize": prize, "prize_value": stated_value(prize),
                "description": before, "sponsor_integration": use, "summary": f"{before} {use}",
                "summary_evidence": USE_EVIDENCE.get(source, USE_UNAVAILABLE),
                "use_source": source, "use_quote": quote, "sponsor_tech": tags,
                "built_with": project.built_with, "team_size": project.team_size,
                "event_prize_count": len(prizes_at_event), "event_prizes": prizes_at_event,
                "required_tech": needed, "requirement_source": requirement_source,
                "source_urls": verified(project.source_links, receipts),
                "demo_video_urls": verified(project.demo_links, receipts),
                "source_link_count_listed": len(project.source_links),
                "demo_video_count_listed": len(project.demo_links),
                "url": url, "gallery_url": gallery, "rules_url": overview if track_details else None,
                "award_evidence": evidence, "fetched_on": receipts[url]["fetched_at"][:10],
                "http_status": receipts[url]["status"],
            })
    for row in rows:
        project = parsed[row["url"]]
        try:
            validate_use(row)
            source, quote = row["use_source"], row["use_quote"]
            if validate_quotes and source and source.startswith("devpost:") and source != BUILT_WITH:
                if quote not in project.writeup_text and quote not in project.tagline:
                    raise ValueError("Use quote is absent from the cached Devpost write-up")
            if github_cache is not None and source == "github:readme":
                links = set(project.source_links) | set(row["source_urls"])
                if not cached_readme_has_quote(github_cache, links, quote):
                    raise ValueError("Use quote is absent from the cached linked GitHub READMEs")
        except ValueError as error:
            raise ValueError(f"{row['url']} ({row['sponsor']}): {error}") from error
    rows.sort(key=lambda row: (
        row["sponsor"].casefold(), -row["year"], row["event_slug"],
        row["project"].casefold(), row["url"], row["prize"].casefold(),
    ))
    return rows, candidates, {event: sorted(set(issues)) for event, issues in missing.items()}, observed_links


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=Path(".devpost-cache"))
    parser.add_argument("--github-cache", type=Path, help="Verify README excerpts against a local cache")
    parser.add_argument("--output", type=Path, default=HERE.parent / "winners")
    parser.add_argument("--readme", type=Path, help="Refresh the generated sections in the root README")
    parser.add_argument("--result", type=Path)
    parser.add_argument("--commit", default="")
    parser.add_argument("--list-links", action="store_true")
    args = parser.parse_args()
    fetcher = Fetcher(args.cache, retry_failed=False)
    rows, candidates, missing, links = index_rows(
        args.cache, fetcher.receipts, validate_quotes=not args.list_links, github_cache=args.github_cache,
    )
    if args.list_links:
        for link in sorted(links["source"] | links["demo"]):
            print(link)
        return
    if not rows:
        parser.error("No award rows have both a matching gallery and project receipt")
    from render import render, report, update_readme
    render(args.output, rows, fetcher.receipts)
    if args.readme:
        update_readme(args.readme, rows)
    if args.result:
        report(args.result, rows, candidates, missing, links, fetcher.receipts, args.commit)
    print(f"Rendered {len(rows)} award rows across {len(dedup_project_rows(rows))} project editions")
    if missing:
        print(f"Coverage flags in {len(missing)} editions. Use --result to write the evidence report.")


if __name__ == "__main__":
    main()
