"""Build the Markdown and export views from the same project-award rows."""
from collections import Counter, defaultdict
import csv
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

from publish import HERE, dedup_project_rows, events, gallery_url


LIST_FIELDS = (
    "built_with", "sponsor_tech", "event_prizes", "source_urls", "demo_video_urls",
)
INT_FIELDS = (
    "year", "team_size", "event_prize_count", "source_link_count_listed",
    "demo_video_count_listed", "http_status",
)
AREA_PATTERNS = {
    "Accessibility and assistive tools": r"accessib|disabilit|assistive|(?:blind|deaf|low.vision)\b",
    "Health and care": r"\b(?:health|healthcare|clinic\w*|patients?|medical|therapy|caregivers?)\b",
    "Education and learning": r"\b(?:learners?|education|educational|teaching|tutors?|students?|classroom)\b",
    "Finance and commerce": r"\b(?:financ\w*|fintech|banking|invest\w*|shopping|payments?|budget\w*)\b",
    "Climate and environment": r"\b(?:climate|sustainab\w*|carbon|recycl\w*|pollution|wildfires?|environmental)\b",
    "Developer tools": r"\b(?:develop(?:er|ers)|codebase|debugg\w*|github repositor\w*|software development)\b",
    "Safety and emergency response": r"\b(?:rescue|disaster\w*|emergenc\w*|public safety|first responders?)\b",
    "Security and privacy": r"\b(?:cybersecurity|privacy|malware|fraud|phishing|security)\b",
    "Games and entertainment": r"\b(?:games?|gaming|entertainment|music|storytell\w*)\b",
}
DEMO_PATTERNS = {
    "Web app or dashboard": r"\b(?:web[ -]?(?:app|site)|browser|dashboard|next\.js|nextjs|reactjs|svelte)\b",
    "Voice or conversational interface": r"\b(?:voice|speech|chatbot|voicebot|text.to.speech)\b",
    "Hardware or robotics": r"\b(?:robot\w*|rover|arduino|raspberry[ -]pi|esp32|jetson|wearable)\b",
    "Mobile app": r"\b(?:mobile app|android|swiftui|react[ -]native|flutter|ios)\b",
    "AR, VR or spatial": r"\b(?:augmented reality|virtual reality|webxr|arkit|webvr|meta[ -]quest|spectacles)\b",
    "Game": r"\b(?:games?|gameplay|pygame|godot|unreal.engine|roblox studio)\b",
    "CLI or developer tool": r"\b(?:cli|command[ -]line|developer tool|sdk)\b",
}


def slugify(label):
    return re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")


def md(value):
    return (
        " ".join(str(value).split()).replace("&", "&amp;")
        .replace("[", "&#91;").replace("]", "&#93;").replace("|", "&#124;")
        .replace("<", "&lt;").replace(">", "&gt;").replace("`", "&#96;")
    )


def event_name(row):
    return f'{row["hackathon"]} {row["year"]}'


def event_file(row):
    return slugify(event_name(row)) + ".md"


def project_anchor(row):
    return "project-" + urlsplit(row["url"]).path.rsplit("/", 1)[-1]


def project_ref(row, prefix=""):
    return f'[{md(row["project"])}]({prefix}by-hackathon/{event_file(row)}#{project_anchor(row)})'


def pairs(rows):
    grouped = defaultdict(list)
    for row in rows:
        grouped[(row["event_slug"], row["url"])].append(row)
    return grouped


def common_tech(rows):
    counts = Counter()
    labels = {}
    for row in dedup_project_rows(rows):
        tags = {tag.casefold(): tag for tag in row["built_with"]}
        counts.update(tags.keys())
        for key, label in tags.items():
            labels.setdefault(key, label)
    return [(labels[key], count) for key, count in ranked(counts)]


def ranked(counts):
    return sorted(counts.items(), key=lambda item: (-item[1], item[0].casefold()))


def tally_text(items, limit=6):
    return ", ".join(f"{md(k)} ({n})" for k, n in items[:limit]) or "None listed"


def occurrences(rows, patterns, include_tags=False):
    counts = Counter()
    for row in dedup_project_rows(rows):
        corpus = row["description"]
        if include_tags:
            corpus += " " + " ".join(row["built_with"])
        for category, pattern in patterns.items():
            if re.search(pattern, corpus, re.I):
                counts[category] += 1
    return ranked(counts)


def data_table(headings, records):
    header = "| " + " | ".join(headings) + " |"
    divider = "| " + " | ".join("---" for _ in headings) + " |"
    return [header, divider, *("| " + " | ".join(map(str, record)) + " |" for record in records)]


def award_table(rows, event_view):
    records = []
    for row in rows:
        sponsor = row["sponsor"]
        if event_view:
            project = f'[{md(row["project"])}](#{project_anchor(row)})'
            group = f'[{md(sponsor)}](../by-sponsor/{slugify(sponsor)}.md)'
        else:
            project = project_ref(row, "../")
            group = f'[{md(event_name(row))}](../by-hackathon/{event_file(row)})'
        label = md(row["prize"])
        if row["award_evidence"] == "Sponsor-reported prize":
            label += " (sponsor-reported)"
        prize_value = row["prize_value"]
        if prize_value == row["prize"]:
            prize_value = "See track label"
        records.append((
            project, group, label, md(prize_value or "—"), md(row["sponsor_integration"]),
            row["event_prize_count"],
        ))
    return data_table(
        ["Project", "Sponsor" if event_view else "Hackathon", "Winning track", "Listed prize", "Sponsor integration or project detail", "Event prizes"],
        records,
    )


def leaderboard(groups, limit=None, prefix="", include_event_prizes=False):
    winners = sorted(groups.values(), key=lambda entries: (
        -len(entries), -entries[0]["event_prize_count"], entries[0]["project"].casefold(),
        entries[0]["event_slug"], entries[0]["url"],
    ))
    winners = [
        entries for entries in winners
        if len(entries) > 1 or (include_event_prizes and entries[0]["event_prize_count"] > 1)
    ][:limit]
    if not winners:
        return ["This group has no projects with multiple qualifying prize labels at one edition."]
    return data_table(
        ["Project", "Hackathon", "Sponsor tracks", "All event prizes", "Sponsors"],
        (
            (project_ref(row, prefix), md(event_name(row)), len(entries), row["event_prize_count"],
             ", ".join(md(sponsor) for sponsor in sorted({item["sponsor"] for item in entries}, key=str.casefold)))
            for entries in winners for row in entries[:1]
        ),
    )


def write_lines(path, lines):
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def publish_links(urls, listed, label):
    if not urls:
        return "Listed on Devpost. HTTP 200 unverified." if listed else "None listed in recognized formats."
    result = [f"[{label} {i}]({url})" for i, url in enumerate(urls, 1)]
    if listed > len(urls):
        result.append(f"{listed - len(urls)} additional listed links without HTTP 200 receipts")
    return " · ".join(result)


def render_event(path, rows):
    row = rows[0]
    rules = f' · [Official prize rules]({row["rules_url"]})' if row["rules_url"] else ""
    groups = pairs(rows)
    intro = [
        f"# {event_name(row)}", "",
        f'[Devpost gallery]({row["gallery_url"]}){rules} · [Winners index](../README.md)', "",
        f"{len(groups)} projects and {len(rows)} sponsor-track awards.", "",
        "## Sponsor awards", "",
        *award_table(rows, event_view=True), "", "## Project details",
    ]
    for entries in sorted(groups.values(), key=lambda values: (
        values[0]["project"].casefold(), values[0]["url"]
    )):
        row = entries[0]
        source = publish_links(row["source_urls"], row["source_link_count_listed"], "Source")
        demo = publish_links(row["demo_video_urls"], row["demo_video_count_listed"], "Video")
        intro.extend([
            "", f'<a name="{project_anchor(row)}"></a>', "",
            f'### [{md(row["project"])}]({row["url"]})', "",
            md(row["description"]), "",
            f'- **Team size** {row["team_size"] or "Unlisted"}',
            f'- **Built With** {", ".join(map(md, row["built_with"])) or "No tags listed"}',
            f"- **Code** {source}", f"- **Demo video** {demo}",
            f'- **All event prizes ({row["event_prize_count"]})** '
            + " · ".join(md(label) for label in row["event_prizes"]),
            f'- **Devpost checked** {row["fetched_on"]} UTC',
        ])
        for item in entries:
            note = ""
            if item["summary_evidence"] == "Project write-up without a specific integration":
                note = " Devpost gives no specific sponsor integration detail."
            intro.append(f'- **{md(item["sponsor"])}** {md(item["sponsor_integration"])}{note}')
    write_lines(path, intro)


def render_sponsor(path, sponsor, rows, all_groups):
    projects = len(dedup_project_rows(rows))
    tracks = {(row["event_slug"], row["prize"]): row for row in rows}
    groups = {key: all_groups[key] for key in pairs(rows)}
    intro = [
        f"# {sponsor}", "", "[Winners index](../README.md)", "",
        f"{projects} projects across {len({r['event_slug'] for r in rows})} editions, with {len(rows)} sponsor award rows.",
        "", "## Tracks and required technology", "",
        *data_table(
            ["Edition", "Devpost track name", "Required tech or brief", "Source"],
            (
                (f"[{md(event_name(row))}](../by-hackathon/{event_file(row)})", md(row["prize"]),
                 md(row["required_tech"] or "No specific requirement captured"),
                 f'[{row["requirement_source"] or "Event prize rules"}]({row["rules_url"]})'
                 if row["rules_url"] else f'[Devpost gallery]({row["gallery_url"]})')
                for row in sorted(tracks.values(), key=lambda r: (-r["year"], r["event_slug"], r["prize"].casefold()))
            ),
        ),
        "", "## What winners have in common", "",
        f"- **Top Built With tags** {tally_text(common_tech(rows))}",
        f"- **Problem areas** {tally_text(occurrences(rows, AREA_PATTERNS))}",
        f"- **Demo types** {tally_text(occurrences(rows, DEMO_PATTERNS, include_tags=True))}",
        f"- **Projects with a listed demo video** {sum(r['demo_video_count_listed'] > 0 for r in dedup_project_rows(rows))} of {projects}",
        "",
        "Counts use one project per edition. Problem areas and demo types reflect keywords in project descriptions and stack tags. A project can appear in multiple categories.",
        "", "## Multi-track winners", "",
        *leaderboard(groups, prefix="../", include_event_prizes=True),
        "", "## Sponsor awards", "", *award_table(rows, event_view=False),
    ]
    write_lines(path, intro)


def render(output, rows, receipts):
    output.mkdir(parents=True, exist_ok=True)
    with (output / "winners.json").open("w", encoding="utf-8") as stream:
        stream.write(json.dumps(rows, ensure_ascii=False, indent=2) + "\n")
    with (output / "winners.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0], lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({**row, **{key: json.dumps(row[key], ensure_ascii=False) for key in LIST_FIELDS}})

    urls = set()
    for row in rows:
        urls.update(x for x in (row["url"], row["gallery_url"], row["rules_url"]) if x)
        urls.update(row["source_urls"])
        urls.update(row["demo_video_urls"])
    write_lines(output / "fetch-receipts.jsonl", [
        json.dumps({key: receipts[url][key] for key in ("url", "status", "fetched_at")}, ensure_ascii=False)
        for url in sorted(urls)
    ])
    by_sponsor, by_edition = defaultdict(list), defaultdict(list)
    for row in rows:
        by_sponsor[row["sponsor"]].append(row)
        by_edition[row["event_slug"]].append(row)
    groups = pairs(rows)
    intro = [
        "# Sponsor-track hackathon winners", "",
        f"**{len({r['url'] for r in rows}):,} projects · {len(by_edition)} editions · "
        f"{len(by_sponsor)} sponsors · {len(rows):,} sponsor prize rows**", "",
        "[CSV](winners.csv) · [JSON](winners.json) · [HTTP receipts](fetch-receipts.jsonl) · [Track-first method](../README.md) · [Coverage report](../result.md)",
        "",
        "One row records one project and one sponsor prize. Event pages show the complete Devpost Built With tags, team size, verified links and all listed prizes for that project at that edition. "
        "A sponsor row links to the implementation detail and Devpost evidence. Backrooms includes a separately attributed sponsor-reported prize.",
        "", "## Most sponsor tracks won at one event", "",
        *leaderboard(groups, 20),
        "", "## Most-awarded sponsors", "",
        *data_table(["Sponsor", "Award rows", "Projects"], [
            (f"[{md(sponsor)}](by-sponsor/{slugify(sponsor)}.md)", count, len(dedup_project_rows(by_sponsor[sponsor])))
            for sponsor, count in ranked({key: len(entries) for key, entries in by_sponsor.items()})[:15]
        ]),
        "", "## Most common Built With tags", "",
        *data_table(["Tag", "Projects per edition"], common_tech(rows)[:20]),
        "", "## Find a sponsor", "",
    ]
    for sponsor, entries in sorted(by_sponsor.items(), key=lambda item: item[0].casefold()):
        path = output / "by-sponsor" / (slugify(sponsor) + ".md")
        path.parent.mkdir(exist_ok=True)
        render_sponsor(path, sponsor, entries, groups)
        intro.append(f"- [{md(sponsor)}](by-sponsor/{path.name}) · {len(entries)} awards")
    intro.extend(["", "## Browse by hackathon edition", ""])
    for event, entries in sorted(by_edition.items(), key=lambda item: (-item[1][0]["year"], event_name(item[1][0]).casefold())):
        path = output / "by-hackathon" / event_file(entries[0])
        path.parent.mkdir(exist_ok=True)
        render_event(path, entries)
        intro.append(f"- [{md(event_name(entries[0]))}](by-hackathon/{path.name}) · {len(entries)} awards")
    write_lines(output / "README.md", intro)


def report(path, rows, candidates, missing, links, receipts, commit):
    event_groups = defaultdict(list)
    sponsor_groups = defaultdict(list)
    for row in rows:
        event_groups[row["event_slug"]].append(row)
        sponsor_groups[row["sponsor"]].append(row)
    covered_projects = len({r["url"] for r in rows})
    unique_projects = dedup_project_rows(rows)
    verified_links = {kind: {url for url in urls if receipts.get(url, {}).get("status") == 200} for kind, urls in links.items()}
    lines = [
        "# Sponsor-track directory build report", "",
        f"Indexed **{covered_projects:,} distinct projects**, **{len(event_groups)} editions**, "
        f"**{len(sponsor_groups)} sponsors** and **{len(rows):,} sponsor prize rows**.",
        "",
        f"{sum(len(value) for value in candidates.values()):,} candidate sponsor award rows were found in the audited galleries. "
        "The candidate total includes Backrooms, whose Hyphenate prize was sponsor-reported. "
        "Each indexed Devpost Winner label was confirmed on both the gallery and its project page.",
        "",
        "## Editions", "",
        *data_table(["Edition", "Projects", "Indexed prize rows", "Candidate prize rows", "Coverage notes"], [
            (f"[{md(name)} {year}](winners/by-hackathon/{event_file(event_groups[slug][0])})" if event_groups[slug] else f"{md(name)} {year}",
             len(dedup_project_rows(event_groups[slug])), len(event_groups[slug]), len(candidates.get(slug, [])),
             len(missing.get(slug, [])))
            for slug, (name, year) in sorted(events().items(), key=lambda item: (item[1][0].casefold(), -item[1][1]))
        ]),
        "", "## Sponsors", "",
        *data_table(["Sponsor", "Projects", "Prize rows"], [
            (f"[{md(sponsor)}](winners/by-sponsor/{slugify(sponsor)}.md)",
             len(dedup_project_rows(entries)), len(entries))
            for sponsor, entries in sorted(sponsor_groups.items(), key=lambda item: item[0].casefold())
        ]),
        "", "## Three sample rows", "",
    ]
    for slug, sponsor in [("farsight-t4qyli", "NVIDIA"), ("crisislens-rlebdw", "Databricks"), ("backrooms-h4o783", "Hyphenate")]:
        row = next((r for r in rows if r["url"].endswith("/" + slug) and r["sponsor"] == sponsor), None)
        if not row:
            continue
        prize_count = row["event_prize_count"]
        prize_word = "label" if prize_count == 1 else "labels"
        lines.extend([
            f'### [{md(row["project"])}]({row["url"]})', "",
            f'**{md(event_name(row))} · {md(sponsor)} · {md(row["prize"])}**', "",
            md(row["summary"]), "",
            f'- Team size {row["team_size"] or "unlisted"}. {prize_count} event prize {prize_word}.',
            f'- Built With {", ".join(map(md, row["built_with"])) or "unlisted"}.',
            f'- Event prizes {" · ".join(map(md, row["event_prizes"]))}.',
            f'- Code {publish_links(row["source_urls"], row["source_link_count_listed"], "Source")}',
            f'- Video {publish_links(row["demo_video_urls"], row["demo_video_count_listed"], "Video")}',
            f'- Evidence {row["award_evidence"]}. Integration evidence {row["summary_evidence"]}.',
            "",
        ])
    lines.extend(["## Skipped gallery URLs", ""])
    for slug in sorted(set((HERE / "gallery-probes.txt").read_text().splitlines()) - set(events())):
        url = gallery_url(slug)
        status = receipts.get(url, {}).get("status")
        detail = f"HTTP {status}" if status else "No successful response"
        if status in (403, 429):
            detail += ", request backoff applied"
        if status == 200:
            detail += " with zero public Devpost Winner labels"
        lines.append(f"- `{url}` returned {detail}.")
    lines.extend([
        "", "The 2024 HackMIT organizer used Ballot and the 2026 organizer used its Plume gallery. "
        "The Devpost probes for HackMIT 2024–2026 did not expose winner records for this dataset. "
        "HackMIT 2013 and 2016–2019 supplied Devpost Winner records. "
        "Hacklytics 2025 was indexed from the working `hacklytics2025` gallery after the hyphenated URL returned 410.",
        "", "## Coverage and link limits", "",
        f"- Built With tags are available for {sum(bool(r['built_with']) for r in unique_projects):,} of {len(unique_projects):,} project editions.",
        f"- Team counts are available for {sum(r['team_size'] is not None for r in unique_projects):,} project editions.",
        f"- Summary evidence by award row: {tally_text(ranked(Counter(r['summary_evidence'] for r in rows)))}.",
        f"- Source code links verified HTTP 200 for {len(verified_links['source'])} of {len(links['source'])} unique recognized links.",
        f"- Demo video links verified HTTP 200 for {len(verified_links['demo'])} of {len(links['demo'])} unique recognized links.",
        "- The export only links to recognized public code and video URLs with HTTP 200 receipts. A video page status does not verify playback.",
        "- Project summaries use edited notes, Devpost project captions and short evidence sentences. "
        "When the project supplies only a stack tag or omits an integration description, the row labels that evidence.",
        "- Sponsor names come from the exact track label or its event prize description. "
        "General event awards remain visible in project prize lists.",
        "- The HackMIT 2017 label `Sponsor Prize - Best FinTech Related Prize` has no sponsor identity in its public prize entry.",
        "- Prize values come from the track label. Multiple placements, team totals, and service credits stay in the source wording.",
        "",
    ])
    for kind, urls in sorted(links.items()):
        status_counts = Counter(
            str(receipts.get(url, {}).get("status") or receipts.get(url, {}).get("reason") or "unverified")
            for url in urls
        )
        lines.append(f"- {kind.capitalize()} link check results by status: {tally_text(ranked(status_counts))}.")
    if missing:
        lines.extend(["", "### Unresolved project and gallery evidence", ""])
        for slug, issues in sorted(missing.items()):
            lines.extend([f"#### {slug}", "", *[f"- {md(issue)}" for issue in issues], ""])
    lines.extend([
        "", "## Local commits", "",
        f"- {commit}" if commit else "- Directory changes are awaiting their local commit.",
    ])
    write_lines(path, lines)
