#!/usr/bin/env python3
"""Cache public Devpost pages and extract winner and project evidence."""
import argparse
from datetime import datetime, timezone
from html import unescape
import json
from pathlib import Path
import re
import subprocess
import time
from urllib.parse import urlsplit


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


class Fetcher:
    def __init__(self, cache, retry_failed):
        self.cache = cache
        cache.mkdir(parents=True, exist_ok=True)
        self.log = cache / "fetches.jsonl"
        self.receipts = {}
        if self.log.exists():
            for line in self.log.read_text().splitlines():
                record = json.loads(line)
                self.receipts[record["url"]] = record
        self.retry_failed = retry_failed
        self.last_request = 0

    def get(self, url):
        parts = urlsplit(url)
        if parts.scheme != "https" or not (
            parts.hostname and (parts.hostname == "devpost.com" or parts.hostname.endswith(".devpost.com"))
        ):
            raise ValueError(f"Expected a public HTTPS Devpost URL: {url}")
        path = cache_path(self.cache, url)
        previous = self.receipts.get(url)
        if previous and previous["status"] == 200 and path.exists():
            return path.read_text(encoding="utf-8", errors="replace")
        if previous and previous["status"] != 200 and not self.retry_failed:
            return ""
        time.sleep(max(0, 1 - (time.monotonic() - self.last_request)))
        self.last_request = time.monotonic()
        record = {"url": url, "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
        response = subprocess.run(
            ["curl", "--disable", "--silent", "--show-error", "--max-time", "18",
             "--write-out", "\n%{http_code}", url],
            capture_output=True,
            check=False,
        )
        body, _, status = response.stdout.rpartition(b"\n")
        record["status"] = int(status) or None
        if response.returncode:
            record["curl_exit"] = response.returncode
        if response.returncode and record["status"] == 200:
            record["status"] = None
        if record["status"] == 200:
            path.write_bytes(body)
        with self.log.open("a") as log:
            log.write(json.dumps(record) + "\n")
        self.receipts[url] = record
        print(record["status"], url, flush=True)
        return body.decode("utf-8", errors="replace") if record["status"] == 200 else ""


def cache_path(cache, url):
    parts = urlsplit(url)
    return cache / (parts.hostname + parts.path.replace("/", "_") + ".html")


def structured_data(html, element_id):
    script = re.search(rf'<script[^>]*id="{element_id}"[^>]*>(.*?)</script>', html, re.S)
    return json.loads(script[1]) if script else {}


def prize_label(award):
    if not award.startswith("Winner, "):
        return ""
    return award.removeprefix("Winner, ").rpartition(" \u2014 ")[0].strip()


def gallery_winners(html):
    event = structured_data(html, "challenge-winners-json-ld")
    winners = []
    for project in event.get("itemListElement", []):
        for award in project.get("award", []):
            label = prize_label(award)
            if label:
                winners.append({"name": project["name"], "url": project["url"], "prize": label})
    return winners


def built_with(html):
    section = re.search(r'<div id="built-with"[^>]*>(.*?)</div>', html, re.S)
    if not section:
        return []
    return [
        unescape(re.sub(r"<[^>]+>", "", item)).strip()
        for item in re.findall(r'<span class="cp-tag[^"]*">(.*?)</span>', section[1], re.S)
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["galleries", "projects", "curated"])
    parser.add_argument("input", type=Path, nargs="?", help="Optional file of gallery slugs or project URLs, one per line")
    parser.add_argument("--cache", type=Path, default=Path(".devpost-cache"))
    parser.add_argument("--retry-failed", action="store_true")
    args = parser.parse_args()
    fetcher = Fetcher(args.cache, args.retry_failed)
    if args.mode == "curated":
        from publish import EVENTS, PROJECTS

        for event in EVENTS:
            fetcher.get(f"https://{event}.devpost.com/project-gallery")
        for url in sorted(PROJECTS):
            fetcher.get(url)
        return
    if args.input is None:
        parser.error("galleries and projects need an input file")
    galleries = {}
    for entry in args.input.read_text().splitlines():
        entry = entry.strip()
        if not entry or entry.startswith("#"):
            continue
        if args.mode == "galleries":
            html = fetcher.get(f"https://{entry}.devpost.com/project-gallery")
            galleries[entry] = gallery_winners(html)
            write_json(args.cache / "galleries.json", galleries)
        else:
            fetcher.get(entry)


if __name__ == "__main__":
    main()
