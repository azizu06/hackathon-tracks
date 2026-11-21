#!/usr/bin/env python3
"""Cache public Devpost pages and extract winner and project evidence."""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import fcntl
from html import unescape
from itertools import zip_longest
import json
from pathlib import Path
import re
import subprocess
import time
from urllib.parse import quote, urlsplit
from urllib.robotparser import RobotFileParser


USER_AGENT = "HackathonTracks"
LINK_HOSTS = frozenset({
    "github.com", "gitlab.com", "bitbucket.org", "codeberg.org",
    "www.youtube.com", "vimeo.com", "www.loom.com",
})


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
        self.last_request = time.monotonic()
        self.robots = {}
        self.backoff = {}
        for record in self.receipts.values():
            if "retry_after" in record:
                key = self.backoff_key(record["url"], record["status"])
                self.backoff[key] = max(self.backoff.get(key, 0), record["retry_after"])

    @staticmethod
    def backoff_key(url, status):
        host = urlsplit(url).hostname
        if status == 429 and (host == "devpost.com" or host.endswith(".devpost.com")):
            return "devpost.com"
        return host

    def allowed(self, url):
        host = urlsplit(url).netloc
        if host not in self.robots:
            robots_url = f"https://{host}/robots.txt"
            rules = RobotFileParser(robots_url)
            body = self.get(robots_url)
            status = self.receipts.get(robots_url, {}).get("status")
            if status == 200:
                rules.parse(body.splitlines())
            elif status in (404, 410):
                rules.allow_all = True
            self.robots[host] = rules
        rules = self.robots[host]
        rate = rules.request_rate(USER_AGENT)
        spacing = rate.seconds / rate.requests if rate and rate.requests else 0
        return rules.can_fetch(USER_AGENT, url), max(1, spacing, rules.crawl_delay(USER_AGENT) or 0)

    def record(self, record):
        with self.log.open("a", encoding="utf-8") as log:
            log.write(json.dumps(record) + "\n")
        self.receipts[record["url"]] = record

    def get(self, url):
        parts = urlsplit(url)
        devpost = parts.hostname and (
            parts.hostname == "devpost.com" or parts.hostname.endswith(".devpost.com")
        )
        if parts.scheme != "https" or parts.netloc != parts.hostname or not (
            devpost or parts.hostname in LINK_HOSTS
        ):
            raise ValueError("Expected a public HTTPS source URL")
        path = cache_path(self.cache, url)
        previous = self.receipts.get(url)
        head_only = not devpost and parts.path != "/robots.txt"
        if previous and previous["status"] == 200 and (path.exists() or head_only):
            return "" if head_only else path.read_text(encoding="utf-8", errors="replace")
        if previous and previous["status"] != 200 and (
            previous["status"] in (404, 410) or not self.retry_failed
        ):
            return ""
        now = time.time()
        limited = self.backoff.get(parts.hostname, 0) > now or (
            devpost and self.backoff.get("devpost.com", 0) > now
        )
        record = {"url": url, "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
        if limited:
            if not previous:
                self.record({**record, "status": None, "reason": "host backoff"})
            return ""
        delay = 1
        if parts.path != "/robots.txt":
            allowed, delay = self.allowed(url)
            if not allowed:
                if not previous:
                    self.record({**record, "status": None, "reason": "robots exclusion or unavailable policy"})
                return ""
        time.sleep(max(0, delay - (time.monotonic() - self.last_request)))
        self.last_request = time.monotonic()
        record["fetched_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        response = subprocess.run(
            ["curl", "--disable", "--silent", "--show-error", "--max-time", "18",
             "--user-agent", USER_AGENT, "--write-out", "\n%{http_code}\n%header{retry-after}",
             *(["--head"] if head_only else []), "--", url],
            capture_output=True,
            check=False,
        )
        body, status, retry_after = response.stdout.rsplit(b"\n", 2)
        record["status"] = int(status) or None
        if record["status"] in (403, 429):
            now = time.time()
            resume = now + (300 if record["status"] == 429 else 600)
            try:
                header = retry_after.decode().strip()
                retry = now + int(header) if header.isdigit() else parsedate_to_datetime(header).timestamp()
                resume = max(resume, retry)
            except ValueError:
                pass
            record["retry_after"] = resume
            self.backoff[self.backoff_key(url, record["status"])] = resume
        if response.returncode:
            record["curl_exit"] = response.returncode
        if response.returncode and record["status"] == 200:
            record["status"] = None
        if record["status"] == 200 and not head_only:
            path.write_bytes(body)
        self.record(record)
        print(record["status"], url, flush=True)
        return body.decode("utf-8", errors="replace") if record["status"] == 200 else ""


def cache_path(cache, url):
    parts = urlsplit(url)
    suffix = "_" + quote(parts.query, safe="") if parts.query else ""
    return cache / (parts.hostname + parts.path.replace("/", "_") + suffix + ".html")


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
    parser.add_argument("mode", choices=["all", "galleries", "projects", "curated", "pages"])
    parser.add_argument("input", type=Path, nargs="?", help="Optional file of gallery slugs or project URLs, one per line")
    parser.add_argument("--cache", type=Path, default=Path(".devpost-cache"))
    parser.add_argument("--retry-failed", action="store_true")
    args = parser.parse_args()
    if args.mode not in ("all", "curated") and args.input is None:
        parser.error(f"{args.mode} needs an input file")
    args.cache.mkdir(parents=True, exist_ok=True)
    with (args.cache / "fetch.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        run(args)


def run(args):
    fetcher = Fetcher(args.cache, args.retry_failed)
    if args.mode in ("all", "curated"):
        from publish import HERE, candidate_awards, event_url, events, gallery_url, index_rows, load_tsv

        for slug in sorted(set(events()) | set((HERE / "gallery-probes.txt").read_text().splitlines())):
            fetcher.get(gallery_url(slug))
        for slug in events():
            if fetcher.receipts.get(gallery_url(slug), {}).get("status") == 200:
                fetcher.get(event_url(slug))
        candidates, _ = candidate_awards(args.cache, fetcher.receipts)
        urls = {url for awards in candidates.values() for url, _, _, _ in awards}
        if args.mode == "curated":
            urls.intersection_update(url for url, _ in load_tsv("projects.tsv"))
        for url in sorted(urls):
            fetcher.get(url)
        if args.mode == "all":
            _, _, _, links = index_rows(args.cache, fetcher.receipts)
            hosts = defaultdict(list)
            for url in sorted(links["source"] | links["demo"]):
                hosts[urlsplit(url).hostname].append(url)
            for batch in zip_longest(*hosts.values()):
                for url in batch:
                    if url:
                        fetcher.get(url)
        return
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
