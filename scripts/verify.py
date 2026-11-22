#!/usr/bin/env python3
"""Check the saved directory against its exports, Markdown rows and HTTP receipts."""
import argparse
import html
from collections import Counter
import csv
import json
from pathlib import Path
import re
import tempfile

from sponsor_use import AWARD, CODE, VIDEO, check_cached_use, load_award_tracks, validate_use
from render import (
    INT_FIELDS, LIST_FIELDS, ROOT_PAGES, SITE_URL, event_file, heading_anchor, render, slugify, update_readme,
)


def decode_csv(row, nullable):
    return {
        key: json.loads(value) if key in LIST_FIELDS
        else int(value) if key in INT_FIELDS and value
        else None if key in nullable and not value
        else value
        for key, value in row.items()
    }


def anchors(path):
    text = path.read_text(encoding="utf-8")
    names = set(re.findall(r'<a name="([^"]+)"></a>', text))
    names.update(heading_anchor(html.unescape(title)) for title in re.findall(r"^#{1,6} (.+)$", text, re.M))
    return names


def verify(root, readme=None, source_cache=None):
    rows = json.loads((root / "winners.json").read_text(encoding="utf-8"))
    receipts = {
        record["url"]: record
        for record in map(json.loads, (root / "fetch-receipts.jsonl").read_text(encoding="utf-8").splitlines())
    }
    nullable = {key for row in rows for key, value in row.items() if value is None}
    with (root / "winners.csv").open(encoding="utf-8", newline="") as stream:
        assert rows == [decode_csv(row, nullable) for row in csv.DictReader(stream)], "CSV and JSON differ"
    seen = set()
    counted = Counter()
    award_tracks = load_award_tracks()
    for row in rows:
        key = (row["event_slug"], row["url"], row["prize"])
        assert key not in seen, f"Duplicate project prize {key}"
        seen.add(key)
        assert row["event_prize_count"] == len(set(row["event_prizes"])), key
        assert row["prize"] in row["event_prizes"], key
        try:
            validate_use(row)
            source = row["use_source"]
            if source == AWARD and (row["event_slug"], row["prize"], row["sponsor"]) not in award_tracks:
                raise ValueError("Award framing requires a reviewed prize in scripts/award-framing.tsv")
            if source_cache is not None and source in {CODE, VIDEO} and not check_cached_use(
                source_cache, source, row["use_quote"], row["use_evidence_url"],
            ):
                raise ValueError("Use quote is absent from the cited code or caption")
        except (KeyError, ValueError) as error:
            raise AssertionError(f"{key}: {error}") from error
        assert set(row["sponsor_tech"]) <= set(row["built_with"]), key
        assert row["team_size"] is None or (isinstance(row["team_size"], int) and row["team_size"] > 0), key
        assert row["http_status"] == 200, key
        if row.get("code_match_evidence") is not None:
            evidence = row["code_match_evidence"]
            assert evidence and evidence == " ".join(evidence.split()), key
            assert any(url.startswith("https://github.com/") for url in row["source_urls"]), key
        assert row["fetched_on"] == receipts[row["url"]]["fetched_at"][:10], key
        for url in [
            row["url"], row["gallery_url"], row["rules_url"], *row["source_urls"], *row["demo_video_urls"]
        ]:
            assert url is None or receipts[url]["status"] == 200, key
        for path in (
            root / "by-hackathon" / event_file(row),
            root / "by-sponsor" / (slugify(row["sponsor"]) + ".md"),
        ):
            counted[path] += 1

    projects = {}
    for row in rows:
        projects.setdefault(root / "by-hackathon" / event_file(row), set()).add(row["url"])
        projects.setdefault(root / "by-sponsor" / (slugify(row["sponsor"]) + ".md"), set()).add((row["event_slug"], row["url"]))
    for folder in ("by-hackathon", "by-sponsor"):
        actual = {p for p in (root / folder).glob("*.md")}
        expected = {p for p in counted if p.parent.name == folder}
        assert actual == expected, f"Unexpected {folder} files: {actual ^ expected}"
        for path in actual:
            text = path.read_text(encoding="utf-8")
            entries = len(re.findall(r'^<a name="project-', text, re.M)) if folder == "by-hackathon" else len(
                re.findall(r"^### \[", text, re.M)
            )
            assert entries == len(projects[path]), (path, entries, len(projects[path]))

    with tempfile.TemporaryDirectory(prefix="hackathon-index-") as directory:
        replay = Path(directory)
        render(replay, rows, receipts)
        file_set = {p.relative_to(root) for p in root.rglob("*") if p.is_file()}
        assert file_set == {p.relative_to(replay) for p in replay.rglob("*") if p.is_file()}
        for relative_path in file_set:
            assert (root / relative_path).read_bytes() == (replay / relative_path).read_bytes(), relative_path
        if readme:
            preview = replay / "root-readme.md"
            preview.write_bytes(readme.read_bytes())
            update_readme(preview, rows)
            assert readme.read_bytes() == preview.read_bytes(), "Root README indexes or badges are stale"
            for name in ROOT_PAGES:
                assert (readme.parent / name).read_bytes() == (replay / name).read_bytes(), f"{name} is stale"
    pages = list(root.rglob("*.md"))
    if readme:
        pages += [readme.parent / name for name in ("README.md", *ROOT_PAGES)]
        coverage = readme.parent / "docs" / "coverage.md"
        if coverage.is_file():
            pages.append(coverage)
    checked_links = 0
    anchor_cache = {}
    for path in pages:
        external_checked = path.is_relative_to(root) or path.name in ROOT_PAGES
        for destination in re.findall(r"\]\(([^ )]+)\)", path.read_text(encoding="utf-8")):
            if destination.startswith(("https://", "http://")):
                if external_checked and not destination.startswith(SITE_URL):
                    assert receipts[destination]["status"] == 200, destination
            else:
                file_name, _, anchor = destination.partition("#")
                target = (path.parent / file_name).resolve() if file_name else path.resolve()
                assert target.is_file(), (path, destination)
                if anchor:
                    if target not in anchor_cache:
                        anchor_cache[target] = anchors(target)
                    assert anchor in anchor_cache[target], (path, destination)
            checked_links += 1
    print(f"Verified {len(rows):,} CSV, JSON and Markdown award rows, "
          f"{len(receipts):,} HTTP 200 receipts and {checked_links:,} Markdown links. "
          "Offline replay is byte-identical.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("winners"))
    parser.add_argument("--readme", type=Path, help="Check the generated sections in the root README")
    parser.add_argument("--source-cache", type=Path, help="Verify excerpts against cached code and demo captions")
    args = parser.parse_args()
    verify(args.output, args.readme, args.source_cache)
