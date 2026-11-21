#!/usr/bin/env python3
"""Verify the curated entries against cached Devpost evidence and render the index."""
import argparse
from collections import defaultdict
import csv
import json
from pathlib import Path
import re

from fetch import Fetcher, built_with, cache_path, gallery_winners, prize_label, structured_data


HERE = Path(__file__).resolve().parent


def load_tsv(name):
    with (HERE / name).open(newline="") as source:
        return list(csv.reader(source, delimiter="\t"))


EVENTS = {slug: (name, int(year)) for slug, name, year in load_tsv("events.tsv")}
PROJECTS = dict(load_tsv("projects.tsv"))
SPONSORS = dict(load_tsv("sponsors.tsv"))
FEATURED_URL = "https://devpost.com/software/backrooms-h4o783"
HYPHENATE = "[Hyphenate] The Hyphenated Enterprise: Autonomous Systems for Finance"
TECH = {
    "Anthropic": r"anthropic|claude",
    "Capital One": r"capital.one|nessie",
    "Databricks": r"databricks|^genie$|^delta-lake$",
    "ElevenLabs": r"eleven.?labs",
    "Encompass": r"arduino|esp32|^esp-now$|^u-blox$|lidar|arkit|^arcore$|^ar-foundation$",
    "Fetch.ai": r"fetch[. -]?ai|^fetch$|agentverse|asi[.:-]?one|uagents?|^fet$",
    "Figma": r"figma",
    "Full Sail": r"meta-quest|webxr|three\.js",
    "GoDaddy Registry": r"godaddy|^\.tech$",
    "Google": r"gemini|gemma|google.cloud|vertex.ai",
    "Hugging Face": r"hugging.?face|^qwen",
    "MongoDB": r"mongo|atlas",
    "NVIDIA": r"nvidia|jetson|tensorrt|^cuda$|^dgx",
    "OpenAI": r"openai|^gpt[-0-9]|^chatgpt$|^whisper$",
    "Roblox": r"roblox|^luau$",
    "Snap": r"spectacle|spectecle|lens.?studio|^snap|^snapar$",
    "Solana": r"solana|^anchor$|^solders$",
    "Tiger Data": r"tiger.data|timescale",
    "Vultr": r"vultr",
}


def gallery_url(event):
    return f"https://{event}.devpost.com/project-gallery"


def read_page(cache, receipts, url):
    record = receipts.get(url, {})
    path = cache_path(cache, url)
    if record.get("status") != 200 or not path.exists():
        raise ValueError(f"Missing HTTP 200 evidence for {url}")
    return path.read_text(encoding="utf-8", errors="replace")


def sponsor_for(prize):
    for sponsor, pattern in SPONSORS.items():
        if re.search(pattern, prize, re.I):
            return sponsor
    return None


def index_rows(cache, receipts):
    awards = defaultdict(list)
    hyphenate_track_present = False
    for event in EVENTS:
        html = read_page(cache, receipts, gallery_url(event))
        if event == "cal-hacks-13-0":
            hyphenate_track_present = any(item["prize"] == HYPHENATE for item in gallery_winners(html))
        for item in gallery_winners(html):
            sponsor = sponsor_for(item["prize"])
            if sponsor and item["url"] in PROJECTS:
                awards[item["url"]].append((event, sponsor, item["prize"], "Devpost Winner label"))
    if FEATURED_URL in PROJECTS and not any(
        sponsor == "Hyphenate" for _, sponsor, _, _ in awards[FEATURED_URL]
    ):
        if not hyphenate_track_present:
            raise ValueError("The Cal Hacks gallery no longer confirms the Hyphenate track name")
        awards[FEATURED_URL].append(
            ("cal-hacks-13-0", "Hyphenate", HYPHENATE, "Sponsor-reported prize")
        )

    rows = []
    seen = set()
    for url, summary in PROJECTS.items():
        html = read_page(cache, receipts, url)
        project = structured_data(html, "software-json-ld")
        if project.get("url") != url or not awards[url]:
            raise ValueError(f"Missing project or eligible award evidence for {url}")
        tags = built_with(html)
        for event, sponsor, prize, evidence in awards[url]:
            key = (url, event, prize)
            if key in seen:
                continue
            seen.add(key)
            if f"https://{event}.devpost.com/" not in {
                source.get("url") for source in project.get("subjectOf", [])
            }:
                raise ValueError(f"Project does not list event {event}: {url}")
            if evidence == "Devpost Winner label" and prize not in {
                prize_label(award) for award in project.get("award", [])
            }:
                raise ValueError(f"Project and gallery disagree for {url}: {prize}")
            name, year = EVENTS[event]
            rows.append({
                "project": project["name"].strip(),
                "hackathon": name,
                "year": year,
                "sponsor": sponsor,
                "prize": prize,
                "description": summary,
                "sponsor_tech": [tag for tag in tags if re.search(
                    TECH.get(sponsor, re.escape(sponsor)), tag, re.I
                )],
                "url": url,
                "gallery_url": gallery_url(event),
                "award_evidence": evidence,
                "fetched_on": receipts[url]["fetched_at"][:10],
                "http_status": receipts[url]["status"],
            })
    return sorted(rows, key=lambda r: (r["sponsor"].casefold(), -r["year"], r["project"].casefold()))


def slugify(label):
    return re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")


def md(value):
    return value.replace("[", "&#91;").replace("]", "&#93;").replace("|", "&#124;").replace("<", "&lt;")


def table(rows, event_view):
    column = "Sponsor" if event_view else "Hackathon"
    lines = [
        f"| Project | {column} | Devpost track label | What it does | Relevant Built With tags | Fetched (UTC) |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        group = row["sponsor"] if event_view else f'{row["hackathon"]} {row["year"]}'
        group_folder = "by-sponsor" if event_view else "by-hackathon"
        project = f'[{md(row["project"])}]({row["url"]})'
        prize = md(row["prize"])
        if row["award_evidence"] == "Sponsor-reported prize":
            prize += " (sponsor-reported prize)"
        tech = ", ".join(md(tag) for tag in row["sponsor_tech"]) or "No matching tag listed"
        lines.append(
            f'| {project} | [{group}](../{group_folder}/{slugify(group)}.md) | {prize} | '
            f'{md(row["description"])} | {tech} | {row["fetched_on"]} |'
        )
    return "\n".join(lines) + "\n"


def render(output, rows):
    output.mkdir(parents=True, exist_ok=True)
    (output / "winners.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n")
    with (output / "winners.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0], lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({**row, "sponsor_tech": json.dumps(row["sponsor_tech"], ensure_ascii=False)})

    sponsors = defaultdict(list)
    events = defaultdict(list)
    for row in rows:
        sponsors[row["sponsor"]].append(row)
        events[f'{row["hackathon"]} {row["year"]}'].append(row)
    notes = dict(load_tsv("patterns.tsv"))
    description = [
        "# Winners index",
        "",
        f"Browse {len({r['url'] for r in rows})} projects across {len(events)} hackathon editions. "
        f"The index has {len(rows)} awards across {len(sponsors)} sponsors.",
        "",
        "[CSV](winners.csv) · [JSON](winners.json) · [Track-first method](../README.md)",
        "",
        "Each row is one project and prize. Sponsor pages summarize patterns in the examples listed there. "
        "The Built With column shows relevant tags from the project page. A missing tag means the page lacks a matching entry in that section. "
        "For product and theme challenges, the column can include hardware, models, or other implementation tech relevant to the track.",
        "",
        "Devpost marks the awards in the index as winners, with one sponsor-reported prize for Backrooms. "
        "Its Devpost page supplies the project details and the Cal Hacks gallery supplies the Hyphenate track name.",
    ]
    for view, groups, heading in [
        ("by-sponsor", sponsors, "By sponsor"),
        ("by-hackathon", events, "By hackathon"),
    ]:
        folder = output / view
        folder.mkdir(exist_ok=True)
        description.extend(["", f"## {heading}", ""])
        for group, entries in sorted(groups.items(), key=lambda item: item[0].casefold()):
            filename = slugify(group) + ".md"
            award_word = "award" if len(entries) == 1 else "awards"
            description.append(f"- [{group}]({view}/{filename}) ({len(entries)} {award_word})")
            intro = f'[Devpost gallery]({entries[0]["gallery_url"]})' if view == "by-hackathon" else notes[group]
            (folder / filename).write_text(
                f"# {group}\n\n{intro}\n\n[All winners](../README.md)\n\n"
                + table(entries, event_view=view == "by-hackathon")
            )
    (output / "README.md").write_text("\n".join(description) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=Path(".devpost-cache"))
    parser.add_argument("--output", type=Path, default=HERE.parent / "winners")
    args = parser.parse_args()
    rows = index_rows(args.cache, Fetcher(args.cache, retry_failed=False).receipts)
    render(args.output, rows)
    print(f"Published {len(rows)} verified index rows to {args.output}")


if __name__ == "__main__":
    main()
