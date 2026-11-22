"""Extract public project and track fields from the Devpost page templates."""
from dataclasses import dataclass
from html import unescape
from html.parser import HTMLParser
import re
from urllib.parse import parse_qs, urlsplit

from fetch import built_with, structured_data


def clean(value):
    return " ".join(value.split())


def html_text(value):
    return clean(unescape(re.sub(r"<[^>]+>", " ", value)))


class PageLinks(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.links = []
        self.anchor = None
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        if tag in ("a", "iframe", "video"):
            url = attr.get("href" if tag == "a" else "src")
            if url:
                if tag == "a":
                    self.anchor = (url, [])
                else:
                    self.links.append((tag, url, ""))

    def handle_data(self, data):
        if self.anchor:
            self.anchor[1].append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self.anchor:
            url, label = self.anchor
            self.links.append((tag, url, clean("".join(label))))
            self.anchor = None


@dataclass
class Project:
    name: str
    data: dict
    tagline: str
    built_with: list
    team_size: int
    story: list
    writeup_text: str
    source_links: list
    demo_links: list


def app_links(html):
    start = re.search(r'<div class="app-links section"[^>]*>', html)
    if not start:
        return ""
    return html[start.end():].partition("</div>")[0]


def normalized_link(url):
    if url.startswith("//"):
        url = "https:" + url
    try:
        parts = urlsplit(url)
    except ValueError:
        return None, None
    host = parts.hostname
    if parts.scheme not in ("http", "https") or parts.netloc != host:
        return None, None
    path = parts.path.rstrip("/")
    if host in ("github.com", "www.github.com", "gitlab.com", "bitbucket.org", "codeberg.org"):
        host = "github.com" if host == "www.github.com" else host
        segments = path.split("/")
        if len(segments) >= 3 and all(re.fullmatch(r"[\w.-]+", s, re.ASCII) for s in segments[1:3]):
            if any(s in (".", "..") for s in segments[1:3]):
                return None, None
            repo = path.split("/-/")[0] if host == "gitlab.com" else "/".join(segments[:3])
            return "source", f"https://{host}{repo.removesuffix('.git')}"
    if host in ("www.youtube.com", "youtube.com", "m.youtube.com", "youtu.be", "www.youtube-nocookie.com"):
        video = parse_qs(parts.query).get("v", [""])[0] if path == "/watch" else path.split("/")[-1]
        if re.fullmatch(r"[\w-]{11}", video, re.ASCII):
            return "demo", f"https://www.youtube.com/watch?v={video}"
    if host in ("vimeo.com", "player.vimeo.com", "www.vimeo.com") and path.split("/")[-1].isdigit():
        return "demo", f"https://vimeo.com/{path.split('/')[-1]}"
    if host in ("www.loom.com", "loom.com") and re.fullmatch(r"/(?:share|embed)/[a-f0-9]{32}", path):
        return "demo", f"https://www.loom.com/share/{path.split('/')[-1]}"
    return None, None


def project_details(html):
    data = structured_data(html, "software-json-ld")
    if not data.get("name"):
        raise ValueError("Missing Devpost project metadata")
    team = re.search(r'<section id="app-team"[^>]*>(.*?)</section>', html, re.S)
    aliases = set()
    authors = data.get("author", [])
    if isinstance(authors, dict):
        authors = [authors]
    for author in authors:
        alias = author.get("name", "")
        if len(alias) > 2:
            aliases.add(alias)
    if team:
        aliases.update(
            html_text(name) for name in re.findall(
                r'<a class="user-profile-link"[^>]*>([^<]+)</a>', team[1]
            ) if len(html_text(name)) > 2
        )
    team_count = team[1].count('class="software-team-member"') if team else len(authors)
    left = html.partition('id="app-details-left"')[2].partition('id="app-details-right"')[0]
    story_html = re.split(r'id="built-with"|class="app-links section"', left, maxsplit=1)[0]
    paragraphs = []
    heading = ""
    for tag, body in re.findall(r"<(h[1-6]|p|li)(?:\s[^>]*)?>(.*?)</\1>", story_html, re.S):
        value = html_text(body)
        if tag.startswith("h"):
            heading = value.casefold()
        elif len(value.split()) >= 5:
            safe = public_text(value, aliases)
            if safe:
                paragraphs.append((heading, safe))
    source_links = set()
    demo_links = set()
    for _, urls, _ in PageLinks(app_links(left)).links:
        for url in re.split(r",\s+(?=https?://)", urls):
            kind, link = normalized_link(url)
            if kind == "demo":
                demo_links.add(link)
            if kind == "source":
                source_links.add(link)
    story_sources = set()
    for tag, url, label in PageLinks(story_html).links:
        kind, link = normalized_link(url)
        if kind == "demo" and (tag == "iframe" or re.search(r"(?i)demo|pitch|walkthrough|video", label)):
            demo_links.add(link)
        if kind == "source" and re.search(r"(?i)source code|github|repo(?:sitory)?|our code", label):
            story_sources.add(link)
    if not source_links:
        for url in re.findall(r"\bgit clone\s+(https?://[^\s<>]+)", story_html):
            kind, link = normalized_link(url)
            if kind == "source" and urlsplit(link).path.split("/")[1] != "your-repo":
                story_sources.add(link)
        source_links = story_sources
    name = clean(data["name"])
    return Project(
        name, data, public_text(data.get("description", ""), aliases),
        [tag for tag in built_with(html) if public_text(tag, aliases)],
        team_count or None, paragraphs, html_text(story_html), sorted(source_links), sorted(demo_links),
    )


def public_text(value, aliases):
    value = clean(value)
    if re.search(r"(?i)\b[\w.+-]+@[\w.-]+\.[a-z]{2,}|\b(?:https?://|www\.)", value):
        return ""
    if re.search(r"(?i)\b(?:team members?|credits|special thanks|supervised by|created by)\s*:", value):
        return ""
    if any(re.search(r"(?<!\w)" + re.escape(name) + r"(?!\w)", value, re.I) for name in aliases):
        return ""
    return value


def overview_tracks(html):
    records = {}
    chunks = re.split(r'<div class="[^"]*\bprize" id="prize_\d+">', html.partition('id="prizes"')[2])
    for chunk in chunks[1:]:
        title = re.search(r'<div class="prize-title">.*?<div>(.*?)</div>', chunk, re.S)
        if not title:
            continue
        content = chunk.partition('<div class="prize-content">')[2]
        body = content.partition("</h6>")[0].partition("</article>")[0]
        source = [html_text(p) for p in re.findall(r"<(?:p|li)(?:\s[^>]*)?>(.*?)</(?:p|li)>", body, re.S)]
        records[html_text(title[1])] = source
    return records
