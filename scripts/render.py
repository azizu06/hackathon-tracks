"""Build the Markdown and export views from the same project-award rows."""
from collections import Counter, defaultdict
import csv
import json
import os
from pathlib import Path
import re
from textwrap import shorten
from urllib.parse import quote, urlencode, urlsplit

from catalog_display import display_prize_title, display_text, has_money, short_prize_title
from fetch import verified_link
from publish import HERE, OTHER_SPONSOR, dedup_project_rows, events, gallery_url
from sponsor_use import COVERAGE_DISCLOSURE, code_coverage_text, prize_coverage_text, use_coverage, use_heading


SITE_URL = "https://tracks.azizu.dev/"
ROOT_PAGES = ("SPONSORS.md", "HACKATHONS.md", "TOPICS.md")
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
    "Playable game": r"\b(?:games?|gameplay|pygame|godot|unreal.engine|roblox studio)\b",
    "Command line or SDK": r"\b(?:cli|command[ -]line|developer tool|sdk)\b",
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


def sponsor_link(sponsor, prefix=""):
    return f"[{md(sponsor)}]({prefix}by-sponsor/{slugify(sponsor)}.md)"


def edition_link(row, prefix="", anchor=False):
    target = f"{prefix}by-hackathon/{event_file(row)}"
    if anchor:
        target += f"#{project_anchor(row)}"
    return f"[{md(event_name(row))}]({target})"


def site_link(**params):
    return SITE_URL + "#browse?" + urlencode(params)


def site_sponsor_link(sponsor):
    return SITE_URL + "#sponsor=" + quote(sponsor, safe="")


def winner_count(rows):
    return len(dedup_project_rows(rows))


def hackathon_count(rows):
    return len({row["event_slug"] for row in rows})


def plural(count, word, many=None):
    return f"{count:,} {word if count == 1 else many or word + 's'}"


def leaderboard(groups, limit=10, prefix=""):
    named = [[row for row in entries if row["sponsor"] != OTHER_SPONSOR] for entries in groups.values()]
    winners = sorted((entries for entries in named if len(entries) > 1), key=lambda entries: (
        -len(entries), -entries[0]["event_prize_count"], entries[0]["project"].casefold(),
        entries[0]["event_slug"], entries[0]["url"],
    ))
    return data_table(
        ["Project", "Hackathon", "Sponsor prizes"],
        (
            (project_ref(row, prefix), edition_link(row, prefix), len(entries))
            for entries in winners[:limit] for row in entries[:1]
        ),
    )


def details(label, body):
    return ["<details>", f"<summary>{label}</summary>", "", *body, "", "</details>"]


def common_patterns(rows):
    projects = dedup_project_rows(rows)
    videos = sum(row["demo_video_count_listed"] > 0 for row in projects)
    return [
        "## What winners have in common", "",
        f"- **Most used tech:** {tally_text(common_tech(rows), 5)}",
        f"- **Project areas:** {tally_text(occurrences(rows, AREA_PATTERNS), 3)}",
        f"- **Demo formats:** {tally_text(occurrences(rows, DEMO_PATTERNS, include_tags=True), 3)}",
        f"- **Demo videos:** {videos:,} of {len(projects):,} winners link one",
        "",
        "<sub>Counts use one entry per winning project. Areas and formats are matched from keywords "
        "in project descriptions and tech tags.</sub>",
    ]


def split_directory(rows):
    sponsors, editions = defaultdict(list), defaultdict(list)
    for row in rows:
        sponsors[row["sponsor"]].append(row)
        editions[row["event_slug"]].append(row)
    return sponsors, editions


def event_series(name):
    for series in ("Cal Hacks", "HackGT", "HackNYU", "HackPrinceton", "Knight Hacks", "PennApps", "SB Hacks", "YHack"):
        if name == series or name.startswith(series + " "):
            return series
    return name


def letter(name):
    initial = name[0].upper()
    return initial if "A" <= initial <= "Z" else "0-9"


def heading_anchor(text):
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text).strip().lower()
    return re.sub(r"[^\w\- ]", "", text).replace(" ", "-")


def jump_bar(labels):
    return "**Jump to:** " + " · ".join(f"[{label}](#{heading_anchor(label)})" for label in labels)


def breadcrumb(*parts):
    return " / ".join(parts)


def topic_groups(rows):
    """Map each project-area and demo-format page to the prize rows of its matching projects."""
    groups = {}
    for kind, patterns, include_tags in (
        ("area", AREA_PATTERNS, False), ("format", DEMO_PATTERNS, True),
    ):
        for category, pattern in patterns.items():
            matched = set()
            for row in dedup_project_rows(rows):
                corpus = row["description"] + (" " + " ".join(row["built_with"]) if include_tags else "")
                if re.search(pattern, corpus, re.I):
                    matched.add((row["event_slug"], row["url"]))
            groups[category] = (kind, [row for row in rows if (row["event_slug"], row["url"]) in matched])
    return groups


def top_sponsors(rows, limit=3, prefix=""):
    counts = Counter()
    for (event, url), entries in pairs(rows).items():
        counts.update({row["sponsor"] for row in entries if row["sponsor"] != OTHER_SPONSOR})
    return ", ".join(sponsor_link(name, prefix) for name, _ in ranked(counts)[:limit]) or "—"


# Project entries on sponsor, hackathon and topic pages


def short_prize(row):
    return short_prize_title(row["prize"], row["sponsor"])


def prize_text(row):
    label = compact(short_prize(row), 100)
    if row["award_evidence"] == "Sponsor-reported prize":
        label += " (sponsor-reported)"
    return f"**{label}**"


def integration_note(row):
    coverage = use_coverage(row)
    sponsor = row["sponsor"] if row["sponsor"] != OTHER_SPONSOR else ""
    label = use_heading(row, sponsor, "Award")
    if coverage == "theme":
        return f'**{md(label)}** · {md(display_text(row["sponsor_integration"]))}'
    note = f'**{md(label)}:** {md(display_text(row["sponsor_integration"]))}'
    if coverage == "inferred":
        note += f' [Evidence]({row["use_evidence_url"]})'
    return note


def entry_links(entries, details_url=None):
    row = entries[0]
    parts = []
    parts.append(f'[Code]({row["source_urls"][0]})' if row["source_urls"] else "No public code found")
    if row["demo_video_urls"]:
        parts.append(f'[Demo video]({row["demo_video_urls"][0]})')
    if details_url:
        parts.append(f"[Details]({details_url})")
    sponsor_tech = [tag for item in entries for tag in item["sponsor_tech"]]
    tech = list(dict.fromkeys(sponsor_tech + row["built_with"]))[:4]
    if tech:
        parts.append("Built with " + ", ".join(md(tag) for tag in tech))
    return " · ".join(parts)


def entry_details(entries):
    row = entries[0]
    body = [
        f'- **Team size:** {row["team_size"] or "Not listed"}',
        f'- **Built with:** {", ".join(map(md, row["built_with"])) or "No tags listed"}',
        f'- **Code:** {publish_links(row["source_urls"], row["source_link_count_listed"], "Source")}',
        f'- **Demo video:** {publish_links(row["demo_video_urls"], row["demo_video_count_listed"], "Video")}',
        f'- **All prizes at this hackathon ({row["event_prize_count"]}):** '
        + " · ".join(md(display_prize_title(label)) for label in row["event_prizes"]),
    ]
    for item in entries:
        value = item["prize_value"]
        detail = f" Prize: {md(value)}" if value and value != item["prize"] and not has_money(value) else ""
        body.append(f"- {integration_note(item)}{detail}")
    body.append(f'- **Checked on Devpost:** {row["fetched_on"]}')
    return details("Team, all prizes and sponsor notes", body)


def project_entry(entries, context, level=3):
    """One project at one hackathon. context is sponsor, event or topic."""
    row = entries[0]
    lines = []
    if context == "event":
        lines += [f'<a name="{project_anchor(row)}"></a>', ""]
    lines += [f'{"#" * level} [{md(row["project"])}]({row["url"]})', ""]
    awards = [f'{sponsor_link(item["sponsor"], "../")} · {prize_text(item)}' for item in entries]
    if context == "sponsor":
        prize_line = edition_link(row, "../", anchor=True) + " · " + " · ".join(prize_text(item) for item in entries)
    elif context == "topic":
        prize_line = "<br>".join([edition_link(row, "../", anchor=True), *awards])
    else:
        prize_line = "<br>".join(awards)
    lines += [prize_line, "", compact(display_text(row["description"]), 220), ""]
    if context == "sponsor":
        lines += [integration_note(row), ""]
    links = entry_links(entries)
    if links:
        lines += [links, ""]
    if context == "event":
        lines += [*entry_details(entries), ""]
    return lines


def year_sections(rows, context):
    """Project entries grouped under one heading per year, newest first."""
    lines = []
    for year in sorted({row["year"] for row in rows}, reverse=True):
        lines += [f"## {year} winners", ""]
        for entries in sorted_projects([row for row in rows if row["year"] == year]):
            lines += project_entry(entries, context)
    return lines


def year_labels(rows):
    return [f"{year} winners" for year in sorted({row["year"] for row in rows}, reverse=True)]


def track_heading(sponsor):
    return "Other prizes" if sponsor == OTHER_SPONSOR else f"{sponsor} winners"


def sorted_projects(rows, newest_first=True):
    return sorted(pairs(rows).values(), key=lambda entries: (
        -entries[0]["year"] if newest_first else 0, -len(entries),
        entries[0]["project"].casefold(), entries[0]["event_slug"], entries[0]["url"],
    ))


# Root index pages


def sponsor_rows(name, entries, prefix):
    return (sponsor_link(name, prefix), f"{winner_count(entries):,}", f"{hackathon_count(entries):,}")


def sponsors_page(sponsors):
    named = {name: entries for name, entries in sponsors.items() if name != OTHER_SPONSOR}
    by_size = sorted(named.items(), key=lambda item: (-winner_count(item[1]), -len(item[1]), item[0].casefold()))
    groups = defaultdict(list)
    for name in sorted(named, key=str.casefold):
        groups[letter(name)].append(name)
    order = sorted(groups, key=lambda key: (key != "0-9", key))
    headings = ["Sponsor", "Winning projects", "Hackathons"]
    lines = [
        breadcrumb("[Hackathon Tracks](README.md)", "Sponsors"), "",
        "# Sponsors", "",
        f"{len(named):,} sponsors awarded prizes at the hackathons in this index. Open one to see every "
        "winning project and what it built. Sponsor-use notes appear where the Devpost write-up says how the "
        "team used the tech. Code is linked where public.", "",
        jump_bar(["Most awarded", *order]), "",
        "## Most awarded", "",
        *data_table(headings, (sponsor_rows(name, entries, "winners/") for name, entries in by_size[:20])), "",
    ]
    for key in order:
        lines += [
            f"## {key}", "",
            *data_table(headings, (sponsor_rows(name, named[name], "winners/") for name in groups[key])), "",
            "[Back to top](#sponsors)", "",
        ]
    if OTHER_SPONSOR in sponsors:
        lines += [
            "## Prizes without a sponsor", "",
            f"{sponsor_link(OTHER_SPONSOR, 'winners/')} lists {plural(len(sponsors[OTHER_SPONSOR]), 'prize')} "
            "credited to an individual or to no sponsoring organization.",
        ]
    return lines


def hackathons_page(rows, editions):
    groups = defaultdict(list)
    for entries in editions.values():
        groups[letter(event_series(entries[0]["hackathon"]))].append(entries)
    order = sorted(groups)
    series = {event_series(entries[0]["hackathon"]) for entries in editions.values()}
    lines = [
        breadcrumb("[Hackathon Tracks](README.md)", "Hackathons"), "",
        "# Hackathons", "",
        f"{len(editions)} editions of {len(series)} hackathons. Open one to see every sponsor track it "
        "offered and the projects that won them.", "",
        jump_bar([*order, "Projects that won the most tracks"]), "",
    ]
    for key in order:
        ordered = sorted(groups[key], key=lambda entries: (
            event_series(entries[0]["hackathon"]).casefold(), -entries[0]["year"], entries[0]["hackathon"].casefold(),
        ))
        lines += [
            f"## {key}", "",
            *data_table(["Hackathon", "Year", "Winning projects", "Sponsors"], (
                (
                    f'[{md(entries[0]["hackathon"])}](winners/by-hackathon/{event_file(entries[0])})',
                    entries[0]["year"], f"{winner_count(entries):,}",
                    len({row["sponsor"] for row in entries} - {OTHER_SPONSOR}),
                )
                for entries in ordered
            )), "",
            "[Back to top](#hackathons)", "",
        ]
    lines += [
        "## Projects that won the most tracks", "",
        "Projects that won the most sponsor prizes at a single hackathon.", "",
        *leaderboard(pairs(rows), prefix="winners/"), "",
        "[Back to top](#hackathons)",
    ]
    return lines


def topic_table(groups, kind):
    return data_table(["Type", "Winning projects", "Top sponsors"], (
        (f"[{md(name)}](winners/by-topic/{slugify(name)}.md)", f"{winner_count(entries):,}",
         top_sponsors(entries, 3, "winners/"))
        for name, (group_kind, entries) in sorted(groups.items(), key=lambda item: (-winner_count(item[1][1]), item[0]))
        if group_kind == kind and entries
    ))


def topics_page(rows):
    groups = topic_groups(rows)
    tech_rows = defaultdict(list)
    for entries in pairs(rows).values():
        for tag in {tag.casefold() for tag in entries[0]["built_with"]}:
            tech_rows[tag].extend(entries)
    top_tech = common_tech(rows)[:40]
    tech_blocks = []
    for start in range(0, len(top_tech), 10):
        block = top_tech[start:start + 10]
        title = "Top 10" if start == 0 else f"{start + 1} to {start + len(block)}"
        tech_blocks += [f"### {title}", "", *data_table(["Tech", "Winning projects", "Top sponsors"], (
            (f"[{md(label)}]({site_link(tech=label.casefold())})", f"{count:,}",
             top_sponsors(tech_rows[label.casefold()], 3, "winners/"))
            for label, count in block
        )), ""]
    return [
        breadcrumb("[Hackathon Tracks](README.md)", "Tech and project types"), "",
        "# Tech and project types", "",
        "Find winners by what they were about, how they were demoed, or what they were built with. "
        "Areas and formats are matched from keywords in project descriptions and tech tags, "
        "so a project can appear under more than one.", "",
        jump_bar(["Project areas", "Demo formats", "Most used tech"]), "",
        "## Project areas", "", *topic_table(groups, "area"), "",
        "## Demo formats", "", *topic_table(groups, "format"), "",
        "## Most used tech", "",
        "Each tech opens the site with that filter applied.", "",
        *tech_blocks,
        "[Back to top](#tech-and-project-types)",
    ]


def root_pages(rows):
    sponsors, editions = split_directory(rows)
    return {
        "SPONSORS.md": sponsors_page(sponsors),
        "HACKATHONS.md": hackathons_page(rows, editions),
        "TOPICS.md": topics_page(rows),
    }


def browse_section(rows, sponsors, editions):
    named = {name: entries for name, entries in sponsors.items() if name != OTHER_SPONSOR}
    projects = winner_count(rows)
    return [
        "## Browse", "",
        *data_table(["Start with", "What you get"], [
            ("**[By sponsor](SPONSORS.md)**",
             f"{len(named):,} sponsors, A to Z. See what won and the evidence for each sponsor note."),
            ("**[By hackathon](HACKATHONS.md)**",
             f"{len(editions)} editions, with sponsor tracks and their winners."),
            ("**[By tech or project type](TOPICS.md)**",
             "Health, finance, hardware, voice and more, plus the most used tech."),
            (f"**[Search the site]({SITE_URL})**",
             f"Filter all {projects:,} winners by sponsor, hackathon, year and tech."),
        ]),
    ]


def directory_sections(sponsors):
    named = {name: entries for name, entries in sponsors.items() if name != OTHER_SPONSOR}
    top = sorted(named.items(), key=lambda item: (-winner_count(item[1]), -len(item[1]), item[0].casefold()))[:12]
    return [
        "## Top sponsors", "",
        *data_table(["Sponsor", "Winning projects", "Hackathons"], (
            sponsor_rows(name, entries, "winners/") for name, entries in top
        )), "",
        f"[See all {len(named):,} sponsors](SPONSORS.md)",
    ]


def update_readme(path, rows):
    sponsors, editions = split_directory(rows)
    badges = [
        ("Winning projects", winner_count(rows), "6D4FA3"),
        ("Hackathon editions", len(editions), "356A8A"),
        ("Sponsors", len(sponsors.keys() - {OTHER_SPONSOR}), "377662"),
        ("Sponsor prizes", len(rows), "90613D"),
    ]
    lines = path.read_text(encoding="utf-8")
    for name, section in (
        ("prize coverage", [COVERAGE_DISCLOSURE, "", prize_coverage_text(rows), "", code_coverage_text(rows)]),
        ("browse", browse_section(rows, sponsors, editions)),
        ("coverage", [" ".join(
            f"![{count:,} {label.lower()}](https://img.shields.io/badge/{label.replace(' ', '%20')}-{count:,}-{color})"
            for label, count, color in badges
        )]),
        ("directory", directory_sections(sponsors)),
    ):
        start, end = f"<!-- BEGIN {name} -->", f"<!-- END {name} -->"
        before, rest = lines.split(start, 1)
        _, after = rest.split(end, 1)
        lines = before + start + "\n\n" + "\n".join(section) + "\n\n" + end + after
    path.write_text(lines, encoding="utf-8")
    for name, page in root_pages(rows).items():
        write_lines(path.parent / name, page)


def write_lines(path, lines):
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def publish_links(urls, listed, label):
    if not urls:
        if label == "Source":
            return "No public code found"
        return "Listed on Devpost but not verified." if listed else "None listed."
    return " · ".join(f"[{label} {i}]({url})" for i, url in enumerate(urls, 1))


def page_header(crumb, title, stats, extra=()):
    return [
        breadcrumb("[Hackathon Tracks](../../README.md)", *crumb), "",
        f"# {title}", "",
        " · ".join([stats, *extra]), "",
    ]


def render_event(path, rows):
    row = rows[0]
    groups = pairs(rows)
    sponsors = defaultdict(list)
    for item in rows:
        sponsors[item["sponsor"]].append(item)
    links = [f'[Devpost gallery]({row["gallery_url"]})']
    if row["rules_url"]:
        links.append(f'[Prize rules]({row["rules_url"]})')
    named = sponsors.keys() - {OTHER_SPONSOR}
    ordered = sorted(sponsors.items(), key=lambda item: (item[0] == OTHER_SPONSOR, item[0].casefold()))
    projects = sorted_projects(rows, newest_first=False)
    several = [entries for entries in projects if len(entries) > 1]
    single = [entries for entries in projects if len(entries) == 1]
    jumps = ["What winners have in common", "Sponsor tracks"]
    jumps += ["Won several sponsor prizes"] if several else []
    jumps += ["Winners by sponsor track"]
    lines = [
        *page_header(
            ["[Hackathons](../../HACKATHONS.md)", md(event_name(row))], md(event_name(row)),
            f"**{plural(len(groups), 'winning project')}** · {plural(len(named), 'sponsor')} · "
            f"{plural(len(rows), 'sponsor prize')}", links,
        ),
        jump_bar(jumps), "",
        *common_patterns(rows), "",
        "## Sponsor tracks", "",
        "Pick a track to jump to its winners on this page.", "",
        *data_table(["Sponsor", "Winners", "Track"], (
            (sponsor_link(name, "../"), winner_count(entries),
             f'[{compact("; ".join(dict.fromkeys(short_prize(item) for item in entries)), 120)}]'
             f'(#{heading_anchor(track_heading(name))})')
            for name, entries in ordered
        )), "",
    ]
    if several:
        lines += [
            "## Won several sponsor prizes", "",
            "These projects won more than one prize here. Each one is listed once.", "",
        ]
        for entries in several:
            lines += project_entry(entries, "event")
    lines += ["## Winners by sponsor track", ""]
    for name, entries in ordered:
        lines += [f"### {md(track_heading(name))}", ""]
        tracks = "; ".join(dict.fromkeys(md(short_prize(item)) for item in entries))
        lines += [f"**Track:** {tracks} · [All {md(name)} winners](../by-sponsor/{slugify(name)}.md)"
                  if name != OTHER_SPONSOR else f"**Prizes:** {tracks}", ""]
        repeat = [group for group in several if any(item["sponsor"] == name for item in group)]
        if repeat:
            lines += ["Also won this track: " + ", ".join(
                f'[{md(group[0]["project"])}](#{project_anchor(group[0])})' for group in repeat
            ) + " (listed above)", ""]
        for group in single:
            if group[0]["sponsor"] == name:
                lines += project_entry(group, "event", level=4)
    lines += ["[Back to top](#" + heading_anchor(event_name(row)) + ")"]
    write_lines(path, lines)


def render_sponsor(path, sponsor, rows):
    tracks = {(row["event_slug"], row["prize"]): row for row in rows}
    notes = (
        ["Prizes credited to an individual or with no identified sponsoring organization.", ""]
        if sponsor == OTHER_SPONSOR else []
    )
    extra = [] if sponsor == OTHER_SPONSOR else [f"[Filter on the site]({site_sponsor_link(sponsor)})"]
    lines = [
        *page_header(
            ["[Sponsors](../../SPONSORS.md)", md(sponsor)], md(sponsor),
            f"**{plural(winner_count(rows), 'winning project')}** · {plural(hackathon_count(rows), 'hackathon')} · "
            f"{plural(len(rows), 'prize')}", extra,
        ),
        *notes,
        jump_bar(["What winners have in common", *year_labels(rows), "Track names and requirements"]), "",
        *common_patterns(rows), "",
        *year_sections(rows, "sponsor"),
        "## Track names and requirements", "",
        *details("Show track names, required tech and rule sources", data_table(
            ["Hackathon", "Track name", "Required tech or brief", "Source"],
            (
                (edition_link(row, "../"), md(display_prize_title(row["prize"])),
                 md(display_text(row["required_tech"] or "No specific requirement captured")),
                 f'[{row["requirement_source"] or "Event prize rules"}]({row["rules_url"]})'
                 if row["rules_url"] else f'[Devpost gallery]({row["gallery_url"]})')
                for row in sorted(tracks.values(), key=lambda r: (-r["year"], r["event_slug"], r["prize"].casefold()))
            ),
        )), "",
        "[Back to top](#" + heading_anchor(sponsor) + ")",
    ]
    write_lines(path, lines)


def render_topic(path, name, kind, rows):
    note = (
        "Matched from keywords in the project description." if kind == "area"
        else "Matched from keywords in the project description and its tech tags."
    )
    lines = [
        *page_header(
            ["[Tech and project types](../../TOPICS.md)", md(name)], md(name),
            f"**{plural(winner_count(rows), 'winning project')}** · {plural(hackathon_count(rows), 'hackathon')}",
        ),
        note, "",
        jump_bar(["What winners have in common", *year_labels(rows)]), "",
        *common_patterns(rows), "",
        *year_sections(rows, "topic"),
        "[Back to top](#" + heading_anchor(name) + ")",
    ]
    write_lines(path, lines)


FIELDS = [
    ("project", "Project name on Devpost"),
    ("hackathon, year, event_slug", "Hackathon edition name, year and Devpost subdomain"),
    ("sponsor", "Organization that awarded the prize. `Other` when the prize names no organization"),
    ("prize", "Raw prize label from the Devpost gallery. Displayed titles omit monetary amounts"),
    ("prize_kind, prize_kind_basis, prize_kind_rules_url", "Theme or tech classification, its rationale, and the cached rules URL where available"),
    ("prize_value", "Raw placement or value stated in the label, or null"),
    ("description", "What the project does, from its Devpost page"),
    ("sponsor_integration", "Documented sponsor use, a listed product, a labeled inference, or award context"),
    ("use_source, use_quote", "Source type and supporting excerpt. Award framing cites the display prize title or preserves the source of a supplemental note"),
    ("use_evidence_url", "Cited page for inferences, commit-pinned code line, or linked demo"),
    ("inferred", "`true` for labeled inferences. Absent in other JSON rows and blank in CSV"),
    ("summary, summary_evidence", "Description plus integration note, and how well the source supports it"),
    ("sponsor_tech", "Built With tags that belong to the sponsor"),
    ("built_with", "All Built With tags on Devpost"),
    ("team_size", "Number of team members, or null"),
    ("event_prizes, event_prize_count", "Every prize the project won at that hackathon"),
    ("required_tech, requirement_source", "Tech or brief the track required, and where that came from"),
    ("source_urls, demo_video_urls", "Code and demo video links that returned HTTP 200"),
    ("code_match_evidence", "How a repository found outside Devpost was matched to the project, or null"),
    ("source_link_count_listed, demo_video_count_listed", "How many code and video links Devpost listed"),
    ("url, gallery_url, rules_url", "Devpost project page, winners gallery and prize rules"),
    ("award_evidence", "`Devpost Winner label`, or `Sponsor-reported prize` for a prize confirmed by the sponsor"),
    ("fetched_on, http_status", "Date the project page was read and its HTTP status"),
]


def data_guide(rows, sponsors, editions):
    reported = sum(row["award_evidence"] == "Sponsor-reported prize" for row in rows)
    return [
        breadcrumb("[Hackathon Tracks](../README.md)", "Data"), "",
        "# Winners data", "",
        f"Every sponsor prize in this index as one row: {len(rows):,} prizes won by "
        f"{winner_count(rows):,} projects at {len(editions)} hackathon editions "
        f"from {len(sponsors.keys() - {OTHER_SPONSOR}):,} sponsors.", "",
        "## Files", "",
        *data_table(["File", "What it holds"], [
            ("[winners.json](winners.json)", "One object per project and sponsor prize. Best for scripts and AI agents."),
            ("[winners.csv](winners.csv)", "The same rows. List fields hold JSON arrays."),
            ("[fetch-receipts.jsonl](fetch-receipts.jsonl)", "HTTP status and fetch time for every linked URL."),
            ("[Coverage report](../docs/coverage.md)", "Which galleries were read, known gaps and link checks."),
        ]), "",
        "Readable pages: [sponsors](../SPONSORS.md), [hackathons](../HACKATHONS.md) and "
        "[tech and project types](../TOPICS.md).", "",
        "## Fields", "",
        *data_table(["Field", "Meaning"], ((", ".join(f"`{name}`" for name in names.split(", ")), meaning)
                                           for names, meaning in FIELDS)), "",
        "## Notes", "",
        "- A project that won several sponsor prizes at one hackathon has one row per prize.",
        f"- `sponsor` is `Other` for {plural(len(sponsors.get(OTHER_SPONSOR, [])), 'prize')} credited to an "
        "individual or to no organization. Sponsor counts leave it out.",
        f"- {plural(reported, 'prize')} came from a sponsor report instead of a Devpost Winner label; "
        "`award_evidence` marks it.",
        "- Rebuild instructions are in [scripts/README.md](../scripts/README.md).",
    ]


def render(output, rows, receipts):
    output.mkdir(parents=True, exist_ok=True)
    with (output / "winners.json").open("w", encoding="utf-8") as stream:
        stream.write(json.dumps(rows, ensure_ascii=False, indent=2) + "\n")
    with (output / "winners.csv").open("w", newline="", encoding="utf-8") as stream:
        fields = [key for key in rows[0] if key != "inferred"]
        if any("inferred" in row for row in rows):
            fields.append("inferred")
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            encoded = {key: json.dumps(row[key], ensure_ascii=False) for key in LIST_FIELDS}
            if "inferred" in row:
                encoded["inferred"] = json.dumps(row["inferred"])
            writer.writerow({**row, **encoded})

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
    write_lines(output / "README.md", data_guide(rows, sponsors, editions))
    for sponsor, entries in sponsors.items():
        path = output / "by-sponsor" / (slugify(sponsor) + ".md")
        path.parent.mkdir(exist_ok=True)
        render_sponsor(path, sponsor, entries)
    for entries in editions.values():
        path = output / "by-hackathon" / event_file(entries[0])
        path.parent.mkdir(exist_ok=True)
        render_event(path, entries)
    for name, (kind, entries) in topic_groups(rows).items():
        if not entries:
            continue
        path = output / "by-topic" / (slugify(name) + ".md")
        path.parent.mkdir(exist_ok=True)
        render_topic(path, name, kind, entries)


def report(path, rows, candidates, missing, links, receipts, commit):
    event_groups = defaultdict(list)
    sponsor_groups = defaultdict(list)
    for row in rows:
        event_groups[row["event_slug"]].append(row)
        sponsor_groups[row["sponsor"]].append(row)
    unique_projects = dedup_project_rows(rows)
    verified_links = {
        kind: {url for url in urls if verified_link(url, receipts)}
        for kind, urls in links.items()
    }
    base = Path(os.path.relpath(HERE.parent, path.resolve().parent)).as_posix() + "/"
    base = "" if base == "./" else base
    lines = [
        breadcrumb(f"[Hackathon Tracks]({base}README.md)", "Coverage report"), "",
        "# Coverage report", "",
        "How this index was built, which hackathon galleries it covers and where public sources fall short.", "",
        f"Indexed **{len(unique_projects):,} winning projects**, **{len(event_groups)} editions**, "
        f"**{len(sponsor_groups.keys() - {OTHER_SPONSOR})} sponsors** and **{len(rows):,} prize rows**.",
        "",
        f"{sum(len(value) for value in candidates.values()):,} candidate award rows were found in the audited galleries. "
        "The candidate total includes one prize confirmed by its sponsor instead of a Devpost Winner label. "
        "Each indexed Devpost Winner label was confirmed on both the gallery and its project page.",
        "",
        "## Editions", "",
        *data_table(["Edition", "Projects", "Indexed prize rows", "Candidate prize rows", "Coverage notes"], [
            (f"[{md(name)} {year}]({base}winners/by-hackathon/{event_file(event_groups[slug][0])})" if event_groups[slug] else f"{md(name)} {year}",
             len(dedup_project_rows(event_groups[slug])), len(event_groups[slug]), len(candidates.get(slug, [])),
             len(missing.get(slug, [])))
            for slug, (name, year) in sorted(events().items(), key=lambda item: (item[1][0].casefold(), -item[1][1]))
        ]),
        "", "## Sponsors", "",
        *data_table(["Sponsor", "Projects", "Prize rows"], [
            (f"[{md(sponsor)}]({base}winners/by-sponsor/{slugify(sponsor)}.md)",
             len(dedup_project_rows(entries)), len(entries))
            for sponsor, entries in sorted(sponsor_groups.items(), key=lambda item: item[0].casefold())
        ]),
        "", "## Three sample rows", "",
        "The first row for each of the three projects that won the most sponsor prizes at one hackathon.", "",
    ]
    named = [[row for row in entries if row["sponsor"] != OTHER_SPONSOR] for entries in pairs(rows).values()]
    samples = sorted((entries for entries in named if entries), key=lambda entries: (
        -len(entries), -entries[0]["event_prize_count"], entries[0]["project"].casefold(), entries[0]["url"],
    ))[:3]
    for entries in samples:
        row = entries[0]
        sponsor = row["sponsor"]
        prize_count = row["event_prize_count"]
        prize_word = "label" if prize_count == 1 else "labels"
        lines.extend([
            f'### [{md(row["project"])}]({row["url"]})', "",
            f'**{md(event_name(row))} · {md(sponsor)} · {md(display_prize_title(row["prize"]))}**', "",
            md(display_text(row["summary"])), "",
            f'- Team size {row["team_size"] or "unlisted"}. {prize_count} event prize {prize_word}.',
            f'- Built With {", ".join(map(md, row["built_with"])) or "unlisted"}.',
            f'- Event prizes {" · ".join(md(display_prize_title(label)) for label in row["event_prizes"])}.',
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
        prize_coverage_text(rows), "",
        code_coverage_text(rows), "",
        f"- Built With tags are available for {sum(bool(r['built_with']) for r in unique_projects):,} of {len(unique_projects):,} project editions.",
        f"- Team counts are available for {sum(r['team_size'] is not None for r in unique_projects):,} project editions.",
        f"- Summary evidence by award row: {tally_text(ranked(Counter(r['summary_evidence'] for r in rows)))}.",
        f"- Source code links verified HTTP 200 for {len(verified_links['source'])} of {len(links['source'])} unique recognized links.",
        f"- The {len(event_groups)} editions use {len({r['hackathon'] for r in rows})} display names. "
        f"The Markdown hackathon index groups them into {len({event_series(r['hackathon']) for r in rows})} event series.",
        f"- Demo video links verified HTTP 200 for {len(verified_links['demo'])} of {len(links['demo'])} unique recognized links.",
        "- The export only links to recognized public code and video URLs with HTTP 200 receipts. A video page status does not verify playback.",
        "- Documented roles cite a Devpost write-up, GitHub README, source code or demo captions. "
        "Technology listed only includes Devpost listings, code imports and dependency manifests. "
        "Inferred notes connect a documented feature to a sponsor product in the prize criteria. "
        "Theme prizes count once, even when they also show a listing, import or resource link. "
        "The no-use-found count covers tech prizes with an award-only note, no note or a resource link alone.",
        "- Sponsor names come from the exact track label or its event prize description. Individual-sponsored awards use the Other bucket. "
        "General event awards remain visible in project prize lists.",
        "- HackMIT 2017 lists Cryptonite and Portfolio Risk Analysis & Data Visualization under `Sponsor Prize - Best FinTech Related Prize`. "
        "The public prize entry supplies no sponsor identity, so those two awards fall outside the named-sponsor index.",
        "- Prize values come from the track label. Multiple placements, team totals, and service credits stay in the source wording.",
        "- Devpost credits the HackPrinceton Fall 2026 Best Physical AI Hack prize to an individual and names no sponsoring "
        "organization, so its three winners appear under Other with their exact labels.",
        "- University labs, foundations and student organizations stay as sponsors where the official award text credits them, "
        "for example Penn Labs for the PennApps Best Beginner Hack prize.",
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
    write_lines(path, lines)
