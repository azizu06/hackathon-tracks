"""Package the current winners index for static hosting and offline browsing."""

import json
import re
from pathlib import Path
from urllib.parse import urlsplit

SITE = Path(__file__).resolve().parent
ROOT = SITE.parent


def field(row, *keys):
    return next((row[key] for key in keys if row.get(key)), None)


def label(value):
    if isinstance(value, dict):
        value = field(value, "name", "title", "label")
    return " ".join(value.split()) if isinstance(value, str) else ""


def items(value):
    return value if isinstance(value, list) else [value]


def web_url(value):
    if isinstance(value, dict):
        value = field(value, "url", "href", "link", "src")
    if not isinstance(value, str):
        return ""
    value = value.strip()
    try:
        parsed = urlsplit(value)
        if parsed.scheme in {"https", "http"} and parsed.hostname:
            return value
    except ValueError:
        pass
    return ""


def first_url(*values, host=None):
    for value in values:
        for entry in items(value):
            url = web_url(entry)
            hostname = urlsplit(url).hostname
            if url and (not host or hostname == host or hostname.endswith("." + host)):
                return url
    return ""


def short_title(title, sponsor):
    """Drop a sponsor or MLH prefix and a trailing prize-value aside from a Devpost label."""
    text = " ".join(title.split())
    if sponsor:
        text = re.sub(r"^\[[^\]]+\]\s*", "", text)
        text = re.sub(r"^MLH\s*[:\-–]\s*", "", text)
        for separator in (": ", " - ", " – "):
            if text.casefold().startswith(sponsor.casefold() + separator):
                text = text[len(sponsor + separator):]
    trimmed = re.sub(r"\s*\([^()]*\)$", "", text)
    return trimmed if len(trimmed) >= 8 else text


def award_rows(row, sponsors):
    prize = label(field(row, "prize", "prize_name", "award", "award_title"))
    for sponsor in sponsors or [""]:
        if prize:
            yield (sponsor, prize)

    for entry in items(field(row, "all_prizes", "all_prizes_won", "all_awards", "event_prizes", "prizes_won", "prizes", "awards")):
        if isinstance(entry, dict):
            title = label(field(entry, "prize", "prize_name", "award", "name", "title", "label"))
            sponsor = label(field(entry, "sponsor", "sponsor_name", "organization"))
        else:
            title = label(entry)
            sponsor = ""
        if title:
            yield (sponsor, title)


def catalog(source):
    if isinstance(source, dict):
        source = field(source, "projects", "winners", "entries", "data") or []
    if not isinstance(source, list):
        raise ValueError("Expected a winners array or an object containing one.")

    projects = {}
    for row in source:
        if not isinstance(row, dict):
            continue
        name = label(field(row, "project", "project_name", "project_title", "name", "title"))
        if not name:
            continue
        event = label(field(row, "hackathon", "event", "hackathon_name", "event_name"))
        year = str(field(row, "year", "hackathon_year", "event_year") or "")
        year = year if len(year) == 4 and year.isascii() and year.isdigit() else ""
        links = row.get("links") if isinstance(row.get("links"), dict) else {}
        devpost = first_url(field(row, "devpost_url", "devpost", "project_url", "url"), links.get("devpost"), host="devpost.com")
        key = urlsplit(devpost).path.rstrip("/").casefold() if devpost else (name.casefold(), event.casefold(), year)
        summary = label(field(row, "description", "project_summary", "summary", "tagline", "short_description"))
        github = first_url(field(row, "github_url", "github", "github_links", "repository_url", "source_url", "source_urls", "source_links"), links.get("github"), host="github.com")
        demo = first_url(field(row, "demo_url", "demo", "demo_links", "demo_video_urls", "video_url", "video_link", "live_url"), links.get("demo"))
        image = first_url(field(row, "image_url", "thumbnail_url", "thumbnail", "project_image_url", "cover_image_url", "devpost_image_url", "image", "images"))
        if image and urlsplit(image).scheme != "https":
            image = ""
        team = field(row, "team_size", "team_count", "member_count")
        if isinstance(team, str) and team.isascii() and team.isdigit():
            team = int(team)
        sponsors = [label(value) for value in items(field(row, "sponsor", "sponsors", "sponsor_name"))]
        sponsors = [sponsor for sponsor in sponsors if sponsor and sponsor.casefold() != "other"]
        tech = [label(value) for key_name in ("built_with", "tech", "technologies", "tech_stack", "sponsor_tech") for value in items(row.get(key_name))]
        project = projects.setdefault(key, {
            "name": name, "event": event, "year": year, "devpost": devpost,
            "sponsors": {}, "tech": {}, "awards": {},
        })
        for key_name, value in {"github": github, "demo": demo, "image": image, "team": team, "event": event, "year": year}.items():
            if value and not project.get(key_name):
                project[key_name] = value
        if len(summary) > len(project.get("summary", "")):
            project["summary"] = summary
        for sponsor in sponsors:
            project["sponsors"].setdefault(sponsor.casefold(), sponsor)
        for tag in filter(None, tech):
            project["tech"].setdefault(tag.casefold(), tag)
        for sponsor, title in award_rows(row, sponsors):
            if sponsor:
                project["sponsors"].setdefault(sponsor.casefold(), sponsor)
            award_key = title.casefold()
            if sponsor or award_key not in project["awards"]:
                project["awards"][award_key] = {"sponsor": sponsor, "title": short_title(title, sponsor)}

    for project in projects.values():
        for key_name in ("sponsors", "tech", "awards"):
            project[key_name] = list(project[key_name].values())
    return list(projects.values())


def main():
    source = json.loads((ROOT / "winners/winners.json").read_text(encoding="utf-8"))
    projects = catalog(source)
    if not projects:
        raise SystemExit("No projects found in winners/winners.json.")
    data = json.dumps(projects, ensure_ascii=True, separators=(",", ":"))
    (SITE / "catalog.js").write_text(f"window.TRACKS_CATALOG = {data};\n", encoding="utf-8")
    sponsors = {sponsor.casefold() for project in projects for sponsor in project["sponsors"]}
    editions = {(project["event"].casefold(), project["year"]) for project in projects if project["event"]}
    print(f"{len(projects)} projects · {len(sponsors)} sponsors · {len(editions)} hackathon editions")


if __name__ == "__main__":
    main()
