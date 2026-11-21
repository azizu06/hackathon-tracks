#!/usr/bin/env python3
"""Check the saved directory against its exports, Markdown rows and HTTP receipts."""
import argparse
from collections import Counter
import csv
import json
from itertools import takewhile
from pathlib import Path
import re
import tempfile

from render import INT_FIELDS, LIST_FIELDS, event_file, project_anchor, render, slugify, update_readme


def decode_csv(row, nullable):
    return {
        key: json.loads(value) if key in LIST_FIELDS
        else int(value) if key in INT_FIELDS and value
        else None if key in nullable and not value
        else value
        for key, value in row.items()
    }


def read_awards(path):
    award_lines = path.read_text(encoding="utf-8").split("## Sponsor awards\n", 1)[1]
    return list(takewhile(lambda line: line.startswith("|"), award_lines.strip().splitlines()))[2:]


def verify(root, readme=None):
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
    for row in rows:
        key = (row["event_slug"], row["url"], row["prize"])
        assert key not in seen, f"Duplicate project prize {key}"
        seen.add(key)
        assert row["event_prize_count"] == len(set(row["event_prizes"])), key
        assert row["prize"] in row["event_prizes"], key
        assert set(row["sponsor_tech"]) <= set(row["built_with"]), key
        assert row["team_size"] is None or (isinstance(row["team_size"], int) and row["team_size"] > 0), key
        assert row["http_status"] == 200, key
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

    for folder in ("by-hackathon", "by-sponsor"):
        actual = {p for p in (root / folder).glob("*.md")}
        expected = {p for p in counted if p.parent.name == folder}
        assert actual == expected, f"Unexpected {folder} files: {actual ^ expected}"
        for path in actual:
            lines = read_awards(path)
            assert len(lines) == counted[path] and all(l.startswith("| [") for l in lines), path

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
    valid_anchors = {event_file(row) + "#" + project_anchor(row) for row in rows}
    valid_anchors.update(f"README.md#{name}" for name in ("leaderboard", "sponsor-index", "hackathon-index"))
    checked_links = 0
    for path in root.rglob("*.md"):
        for destination in re.findall(r"\]\(([^ )]+)\)", path.read_text(encoding="utf-8")):
            if destination.startswith("https://"):
                assert receipts[destination]["status"] == 200, destination
            else:
                file_name, _, anchor = destination.partition("#")
                target = (path.parent / file_name) if file_name else path
                assert target.is_file(), (path, destination)
                if anchor:
                    assert target.name + "#" + anchor in valid_anchors, (path, destination)
            checked_links += 1
    print(f"Verified {len(rows):,} CSV, JSON and Markdown award rows, "
          f"{len(receipts):,} HTTP 200 receipts and {checked_links:,} Markdown links. "
          "Offline replay is byte-identical.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("winners"))
    parser.add_argument("--readme", type=Path, help="Check the generated sections in the root README")
    args = parser.parse_args()
    verify(args.output, args.readme)
