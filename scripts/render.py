"""Build the Markdown and export views from the same project-award rows."""
from collections import Counter, defaultdict
import csv
import json
from pathlib import Path
import re
from textwrap import shorten
from urllib.parse import urlsplit

from fetch import verified_link
from publish import HERE, OTHER_SPONSOR, dedup_project_rows, events, gallery_url


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
        .replace("*", "&#42;").replace("_", "&#95;").replace("~", "&#126;")
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


def compact(value, width):
    normalized = " ".join(value.split())
    if not normalized:
        return "—"
    shortened = shorten(normalized, width, placeholder="…")
    return md(normalized[:width - 1] + "…" if shortened == "…" else shortened)


def award_title(row):
    # The exact Devpost label is preserved in the exports and project details.
    title = row["prize"]
    sponsor = row["sponsor"]
    bracket, closing, rest = title.partition("] ")
    if closing and bracket.startswith("[") and bracket[1:] in {sponsor, "MLH"}:
        return rest
    if sponsor == OTHER_SPONSOR and closing and bracket.startswith("["):
        return rest
    for separator in (": ", " - "):
        if title.casefold().startswith(sponsor.casefold() + separator):
            return title[len(sponsor + separator):]
    return title


def sponsor_link(sponsor, prefix=""):
    return f"[{md(sponsor)}]({prefix}by-sponsor/{slugify(sponsor)}.md)"


def edition_link(row, prefix=""):
    return f"[{md(event_name(row))}]({prefix}by-hackathon/{event_file(row)})"


def award_table(rows, event_view):
    records = []
    for row in rows:
        project = f'[{md(row["project"])}]({row["url"]})'
        if row["source_urls"]:
            project += f' · [code]({row["source_urls"][0]})'
        if row["demo_video_urls"]:
            project += f' · [demo]({row["demo_video_urls"][0]})'
        details = f"#{project_anchor(row)}" if event_view else (
            f"../by-hackathon/{event_file(row)}#{project_anchor(row)}"
        )
        group = sponsor_link(row["sponsor"], "../") if event_view else edition_link(row, "../")
        label = compact(award_title(row), 90)
        if row["award_evidence"] == "Sponsor-reported prize":
            label += " (sponsor-reported)"
        tech = list(dict.fromkeys(row["sponsor_tech"] + row["built_with"]))
        records.append((
            project, f"{group} · {label} · [details]({details})",
            compact(row["description"], 110), ", ".join(md(tag) for tag in tech[:3]) or "—",
        ))
    return data_table(
        ["Project", "Sponsor prize" if event_view else "Edition and prize", "What it built", "Tech"],
        records,
    )


def leaderboard(groups, limit=10, prefix=""):
    named = [[row for row in entries if row["sponsor"] != OTHER_SPONSOR] for entries in groups.values()]
    winners = sorted((entries for entries in named if len(entries) > 1), key=lambda entries: (
        -len(entries), -entries[0]["event_prize_count"], entries[0]["project"].casefold(),
        entries[0]["event_slug"], entries[0]["url"],
    ))
    return data_table(
        ["Project", "Edition", "Tracks"],
        (
            (project_ref(row, prefix), edition_link(row, prefix), len(entries))
            for entries in winners[:limit] for row in entries[:1]
        ),
    )


def details(label, body):
    return ["<details>", f"<summary>{label}</summary>", "", *body, "", "</details>"]


def common_patterns(rows):
    projects = len(dedup_project_rows(rows))
    return [
        "## What winners have in common", "",
        f"- **Most listed tech** {tally_text(common_tech(rows), 3)}",
        f"- **Common project areas** {tally_text(occurrences(rows, AREA_PATTERNS), 3)}",
        f"- **Common demo formats** {tally_text(occurrences(rows, DEMO_PATTERNS, include_tags=True), 3)}",
        f"- **Projects with a listed demo video** {sum(r['demo_video_count_listed'] > 0 for r in dedup_project_rows(rows))} of {projects}",
        "",
        "Counts use one project per edition. Areas and demo formats come from keywords in project descriptions and tech tags.",
    ]


def split_directory(rows):
    sponsors, editions = defaultdict(list), defaultdict(list)
    for row in rows:
        sponsors[row["sponsor"]].append(row)
        editions[row["event_slug"]].append(row)
    return sponsors, editions


def sponsor_index(sponsors, prefix=""):
    named = {sponsor: len(rows) for sponsor, rows in sponsors.items() if sponsor != OTHER_SPONSOR}
    top = ranked(named)[:40]
    halfway = (len(top) + 1) // 2
    cells = [f"{sponsor_link(name, prefix)} ({count})" for name, count in top]
    columns = [
        (cell, cells[index + halfway] if index + halfway < len(cells) else "")
        for index, cell in enumerate(cells[:halfway])
    ]
    alphabet = defaultdict(list)
    for name in sorted(named, key=str.casefold):
        initial = name[0].upper()
        alphabet[initial if "A" <= initial <= "Z" else "0-9 / symbols"].append(
            f"{sponsor_link(name, prefix)} ({named[name]})"
        )
    return [
        "## Sponsor index", "",
        "Most-awarded sponsors in this directory. Counts show prize rows.", "",
        *data_table(["Sponsor (rows)", "Sponsor (rows)"], columns), "",
        *details(f"All {len(named):,} sponsors A-Z", [
            f"- **{letter}** " + " · ".join(links) for letter, links in alphabet.items()
        ]),
        *(
            ["", f"{sponsor_link(OTHER_SPONSOR, prefix)} · {len(sponsors[OTHER_SPONSOR])} prize rows without a sponsoring organization."]
            if OTHER_SPONSOR in sponsors else []
        ),
    ]


def event_series(name):
    for series in ("Cal Hacks", "HackGT", "HackNYU", "HackPrinceton", "Knight Hacks", "PennApps", "SB Hacks", "YHack"):
        if name == series or name.startswith(series + " "):
            return series
    return name


def edition_index(editions, prefix=""):
    series = defaultdict(list)
    for rows in editions.values():
        series[event_series(rows[0]["hackathon"])].append(rows)
    records = [
        (md(name), " · ".join(
            f"{edition_link(rows[0], prefix)} ({len(rows)})"
            for rows in sorted(groups, key=lambda rows: (-rows[0]["year"], rows[0]["hackathon"].casefold()))
        ))
        for name, groups in sorted(series.items(), key=lambda item: item[0].casefold())
    ]
    return [
        "## Hackathon index", "",
        *details(f"Browse {len(editions)} editions across {len(series)} event series", [
            "Pick an edition to see its winning projects and sponsors. Counts show prize rows.", "",
            *data_table(["Event series", "Editions (rows)"], records),
        ]),
    ]


def directory_sections(rows, sponsors, editions, prefix=""):
    return [
        "## Leaderboard", "",
        "The ten projects that won the most sponsor tracks at one edition. "
        "Ties use total event prizes, then project name.", "",
        *leaderboard(pairs(rows), prefix=prefix), "",
        *sponsor_index(sponsors, prefix), "",
        *edition_index(editions, prefix),
    ]


def update_readme(path, rows):
    sponsors, editions = split_directory(rows)
    badges = [
        ("Projects", len({row["url"] for row in rows}), "6D4FA3"),
        ("Hackathon editions", len(editions), "356A8A"),
        ("Sponsors", len(sponsors.keys() - {OTHER_SPONSOR}), "377662"),
        ("Prize rows", len(rows), "90613D"),
    ]
    lines = path.read_text(encoding="utf-8")
    for name, section in (
        ("coverage", [" ".join(
            f"![{count:,} {label.lower()}](https://img.shields.io/badge/{label.replace(' ', '%20')}-{count:,}-{color})"
            for label, count, color in badges
        )]),
        ("directory", directory_sections(rows, sponsors, editions, "winners/")),
    ):
        start, end = f"<!-- BEGIN {name} -->", f"<!-- END {name} -->"
        before, rest = lines.split(start, 1)
        _, after = rest.split(end, 1)
        lines = before + start + "\n\n" + "\n".join(section) + "\n\n" + end + after
    path.write_text(lines, encoding="utf-8")


def write_lines(path, lines):
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def publish_links(urls, listed, label):
    if not urls:
        return "Listed on Devpost. HTTP 200 unverified." if listed else "None listed in recognized formats."
    return " · ".join(f"[{label} {i}]({url})" for i, url in enumerate(urls, 1))


def render_event(path, rows):
    row = rows[0]
    rules = f' · [Official prize rules]({row["rules_url"]})' if row["rules_url"] else ""
    groups = pairs(rows)
    intro = [
        f"# {md(event_name(row))}", "",
        f"**{len(groups):,} projects · {len({r['sponsor'] for r in rows} - {OTHER_SPONSOR})} sponsors · {len(rows):,} prize rows**", "",
        f'[Winners index](../README.md) · [Devpost gallery]({row["gallery_url"]}){rules}', "",
        *common_patterns(rows), "",
        "## Sponsor awards", "",
        *award_table(rows, event_view=True), "", "## Project details",
    ]
    for entries in sorted(groups.values(), key=lambda values: (
        values[0]["project"].casefold(), values[0]["url"]
    )):
        row = entries[0]
        source = publish_links(row["source_urls"], row["source_link_count_listed"], "Source")
        demo = publish_links(row["demo_video_urls"], row["demo_video_count_listed"], "Video")
        project_details = [
            md(row["description"]), "",
            f'- **Team size** {row["team_size"] or "Unlisted"}',
            f'- **Built With** {", ".join(map(md, row["built_with"])) or "No tags listed"}',
            f"- **Code** {source}", f"- **Demo video** {demo}",
            f'- **All event prizes ({row["event_prize_count"]})** '
            + " · ".join(md(label) for label in row["event_prizes"]),
            f'- **Devpost checked** {row["fetched_on"]} UTC',
        ]
        for item in entries:
            project_details.append(
                f'- **{md(item["sponsor"])} · {md(item["prize"])}** {md(item["sponsor_integration"])}'
                + (f' Listed prize: {md(item["prize_value"])}' if item["prize_value"] and item["prize_value"] != item["prize"] else "")
            )
        intro.extend([
            "", f'<a name="{project_anchor(row)}"></a>', "",
            *details(md(row["project"]), project_details),
        ])
    write_lines(path, intro)


def render_sponsor(path, sponsor, rows):
    projects = len(dedup_project_rows(rows))
    tracks = {(row["event_slug"], row["prize"]): row for row in rows}
    notes = (
        ["Prizes credited to an individual or with no identified sponsoring organization.", ""]
        if sponsor == OTHER_SPONSOR else []
    )
    write_lines(path, [
        f"# {md(sponsor)}", "",
        f"**{projects:,} projects · {len({r['event_slug'] for r in rows})} editions · {len(rows):,} prize rows**", "",
        "[Winners index](../README.md)", "", *notes,
        *common_patterns(rows), "",
        "## Sponsor awards", "",
        *award_table(rows, event_view=False), "",
        *details("Track labels, requirements and rules", data_table(
            ["Edition", "Devpost track name", "Required tech or brief", "Source"],
            (
                (edition_link(row, "../"), md(row["prize"]),
                 md(row["required_tech"] or "No specific requirement captured"),
                 f'[{row["requirement_source"] or "Event prize rules"}]({row["rules_url"]})'
                 if row["rules_url"] else f'[Devpost gallery]({row["gallery_url"]})')
                for row in sorted(tracks.values(), key=lambda r: (-r["year"], r["event_slug"], r["prize"].casefold()))
            ),
        )),
    ])


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
    sponsors, editions = split_directory(rows)
    write_lines(output / "README.md", [
        "# Sponsor-track hackathon winners", "",
        f"**{len({r['url'] for r in rows}):,} projects · {len(editions)} editions · "
        f"{len(sponsors.keys() - {OTHER_SPONSOR})} sponsors · {len(rows):,} prize rows**", "",
        "[Leaderboard](#leaderboard) · [Sponsors](#sponsor-index) · [Hackathons](#hackathon-index) · [Track-first guide](../README.md)", "",
        "[CSV](winners.csv) · [JSON](winners.json) · [HTTP receipts](fetch-receipts.jsonl) · [Coverage report](../result.md)", "",
        "Each row records one project and one prize. Open a row's details on its edition page to see the full tech stack, links and all listed event prizes. "
        "Backrooms includes a separately attributed sponsor-reported prize.", "",
        *common_patterns(rows), "",
        *directory_sections(rows, sponsors, editions),
    ])
    for sponsor, entries in sponsors.items():
        path = output / "by-sponsor" / (slugify(sponsor) + ".md")
        path.parent.mkdir(exist_ok=True)
        render_sponsor(path, sponsor, entries)
    for entries in editions.values():
        path = output / "by-hackathon" / event_file(entries[0])
        path.parent.mkdir(exist_ok=True)
        render_event(path, entries)


def report(path, rows, candidates, missing, links, receipts, commit):
    event_groups = defaultdict(list)
    sponsor_groups = defaultdict(list)
    for row in rows:
        event_groups[row["event_slug"]].append(row)
        sponsor_groups[row["sponsor"]].append(row)
    covered_projects = len({r["url"] for r in rows})
    unique_projects = dedup_project_rows(rows)
    verified_links = {
        kind: {url for url in urls if verified_link(url, receipts)}
        for kind, urls in links.items()
    }
    lines = [
        "# Sponsor-track directory build report", "",
        f"Indexed **{covered_projects:,} distinct projects**, **{len(event_groups)} editions**, "
        f"**{len(sponsor_groups.keys() - {OTHER_SPONSOR})} sponsors** and **{len(rows):,} prize rows**.",
        "",
        f"{sum(len(value) for value in candidates.values()):,} candidate award rows were found in the audited galleries. "
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
        "- Sponsor names come from the exact track label or its event prize description. Individual-sponsored awards use the Other bucket. "
        "General event awards remain visible in project prize lists.",
        "- HackMIT 2017 lists Cryptonite and Portfolio Risk Analysis & Data Visualization under `Sponsor Prize - Best FinTech Related Prize`. "
        "The public prize entry supplies no sponsor identity, so those two awards fall outside the named-sponsor index.",
        "- Prize values come from the track label. Multiple placements, team totals, and service credits stay in the source wording.",
        "",
    ])
    for kind, urls in sorted(links.items()):
        status_counts = Counter(
            "redirect landed on HTTP 200" if url in verified_links[kind] and receipts[url]["status"] != 200
            else str(receipts.get(url, {}).get("status") or receipts.get(url, {}).get("reason") or "unverified")
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
