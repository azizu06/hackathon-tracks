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

from catalog_display import has_money
from evidence import project_details
from fetch import cache_path
from publish import validate_cached_inference
from sponsor_use import (
    AWARD, CODE, COVERAGE_DISCLOSURE, VIDEO, check_cached_use, code_coverage_text, inference_source,
    load_award_tracks, load_inferred_uses, load_prize_kinds, load_uses, prize_coverage, prize_coverage_text, prize_key,
    track_key, use_heading, validate_prize_kind, validate_use,
)
from render import (
    INT_FIELDS, LIST_FIELDS, ROOT_PAGES, SITE_URL, event_file, heading_anchor, render, slugify, update_readme,
)


def decode_csv(row, nullable):
    return {
        key: json.loads(value) if key in LIST_FIELDS
        else json.loads(value) if key == "inferred"
        else int(value) if key in INT_FIELDS and value
        else None if key in nullable and not value
        else value
        for key, value in row.items()
        if key != "inferred" or value
    }


def anchors(path):
    text = path.read_text(encoding="utf-8")
    names = set(re.findall(r'<a name="([^"]+)"></a>', text))
    names.update(heading_anchor(html.unescape(title)) for title in re.findall(r"^#{1,6} (.+)$", text, re.M))
    return names


DISPLAY_FIELDS = (
    "project", "hackathon", "sponsor", "description", "sponsor_integration", "summary",
    "required_tech", "built_with", "sponsor_tech",
)


def check_display_money(value, context):
    if isinstance(value, dict):
        for key, item in value.items():
            check_display_money(item, f"{context}/{key}")
    elif isinstance(value, list):
        for item in value:
            check_display_money(item, context)
    elif isinstance(value, str) and has_money(value):
        raise AssertionError(f"Monetary amount in displayed text: {context}")


def verify_site(site, rows):
    index = (site / "index.html").read_text(encoding="utf-8")
    check_display_money(index, site / "index.html")
    for name in ("app.js", "style.css"):
        path = site / name
        check_display_money(path.read_text(encoding="utf-8"), path)
    hero = index.partition('<section class="hero"')[2].partition("</section>")[0]
    coverage = [
        f"<p><!-- BEGIN {name} -->{html.escape(text)}<!-- END {name} --></p>"
        for name, text in (
            ("coverage disclosure", COVERAGE_DISCLOSURE),
            ("prize coverage", prize_coverage_text(rows)),
            ("code coverage", code_coverage_text(rows)),
        )
    ]
    assert re.search(r"\s*".join(map(re.escape, coverage)), hero), (
        "Site hero disclosure or coverage counts are stale. Run python3 site/build.py."
    )
    path = site / "catalog.js"
    data = path.read_text(encoding="utf-8")
    prefix, suffix = "window.TRACKS_CATALOG = ", ";\n"
    assert data.startswith(prefix) and data.endswith(suffix), "Unexpected site catalog format"
    catalog = json.loads(data.removeprefix(prefix).removesuffix(suffix))
    check_display_money(catalog, path)
    expected = set()
    for row in rows:
        sponsor = "" if row["sponsor"] == "Other" else row["sponsor"]
        heading = use_heading(row, sponsor, f"Award from {sponsor}")
        note = " ".join(row["sponsor_integration"].split())
        expected.add((row["event_slug"], row["url"], sponsor, heading, note))
    actual = {(card["editionId"], card["devpost"], note["sponsor"], note["heading"], note["note"])
              for card in catalog for note in card["integrations"]}
    assert actual == expected, "Site catalog sponsor notes or headings differ from the export"


def verify(root, readme=None, source_cache=None, devpost_cache=None, github_cache=None):
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
    prize_kinds = load_prize_kinds()
    uses = load_uses()
    inferred_uses = load_inferred_uses()
    for row in rows:
        key = prize_key(row)
        for field in DISPLAY_FIELDS:
            check_display_money(row[field], f"{key}/{field}")
        check_display_money(row["use_quote"], f"{key}/use_quote")
        assert key not in seen, f"Duplicate project prize {key}"
        seen.add(key)
        assert row["event_prize_count"] == len(set(row["event_prizes"])), key
        assert row["prize"] in row["event_prizes"], key
        try:
            curated = uses.get((row["url"], row["sponsor"]))
            validate_prize_kind(row, prize_kinds, curated)
            validate_use(row, curated)
            source = row["use_source"]
            inferred = inference_source(source)
            if (source == AWARD or inferred) and track_key(row) not in award_tracks:
                raise ValueError("Award framing requires a reviewed prize in scripts/award-framing.tsv")
            if inferred:
                fields = ("sponsor_integration", "use_source", "use_quote", "use_evidence_url")
                if tuple(row[field] for field in fields) != inferred_uses.pop(key, None):
                    raise ValueError("Inference does not match the reviewed prize evidence")
                project = None
                if devpost_cache is not None and inferred.startswith("devpost:"):
                    page = cache_path(devpost_cache, row["url"]).read_text(encoding="utf-8", errors="replace")
                    project = project_details(page)
                validate_cached_inference(
                    row, project=project, github_cache=github_cache, source_cache=source_cache,
                )
            if source_cache is not None and source in {CODE, VIDEO} and not check_cached_use(
                source_cache, source, row["use_quote"], row["use_evidence_url"],
            ):
                raise ValueError("Use quote is absent from the cited code or caption")
        except (KeyError, OSError, ValueError) as error:
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

    assert not inferred_uses, f"Reviewed inferences missing from the export: {sorted(inferred_uses)}"
    assert set(prize_kinds) == {track_key(row) for row in rows}, "Prize kind ledger and exports cover different tracks"
    coverage = prize_coverage(rows)
    assert set(coverage) == {"shown", "listed", "inferred", "theme", "gap"}
    assert coverage["theme"] == sum(row["prize_kind"] == "theme" for row in rows)
    assert sum(coverage.values()) == len(rows), "The five prize coverage buckets must cover every row"
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

    pages = list(root.rglob("*.md"))
    project_root = Path(__file__).resolve().parent.parent
    if readme:
        pages += [readme.parent / name for name in ("README.md", *ROOT_PAGES)]
        pages += [path for path in (readme.parent / "docs/coverage.md", readme.parent / "INFERENCE_REPORT.md")
                  if path.is_file()]
    for path in pages:
        check_display_money(path.read_text(encoding="utf-8"), path)
    if root.resolve() == project_root / "winners":
        verify_site(project_root / "site", rows)

    with tempfile.TemporaryDirectory(prefix="hackathon-index-") as directory:
        replay = Path(directory)
        render(replay, rows, receipts)
        file_set = {p.relative_to(root) for p in root.rglob("*") if p.is_file()}
        assert file_set == {p.relative_to(replay) for p in replay.rglob("*") if p.is_file()}
        for relative_path in file_set:
            assert (root / relative_path).read_bytes() == (replay / relative_path).read_bytes(), relative_path
        if readme:
            preview = replay / "root-readme.md"
            readme_bytes = readme.read_bytes()
            assert readme_bytes.split(b"\n\n", 2)[1:2] == [b"<!-- BEGIN prize coverage -->"], (
                "README coverage disclosure must appear directly below the title"
            )
            preview.write_bytes(readme_bytes)
            update_readme(preview, rows)
            assert readme_bytes == preview.read_bytes(), "Root README disclosure, counts, indexes or badges are stale"
            for name in ROOT_PAGES:
                assert (readme.parent / name).read_bytes() == (replay / name).read_bytes(), f"{name} is stale"
    if readme:
        coverage = readme.parent / "docs" / "coverage.md"
        lines = coverage.read_text(encoding="utf-8").splitlines()
        assert prize_coverage_text(rows) in lines and code_coverage_text(rows) in lines, "Coverage report counts are stale"
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
    parser.add_argument("--cache", type=Path, help="Check inference excerpts against cached Devpost pages")
    parser.add_argument("--github-cache", type=Path, help="Check inference excerpts against cached GitHub READMEs")
    args = parser.parse_args()
    verify(args.output, args.readme, args.source_cache, args.cache, args.github_cache)
