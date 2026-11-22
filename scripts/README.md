[Hackathon Tracks](../README.md) / Rebuild the index

# Rebuild the winners index

Run from the repo root with Python 3.9 or later and curl 7.84 or later.

```sh
python3 scripts/fetch.py all
python3 scripts/publish.py --readme README.md --result docs/coverage.md
python3 site/build.py
python3 scripts/verify.py --readme README.md
```

The fetcher reads public Devpost galleries, event prize descriptions and project pages. It checks recognized source and demo URLs with HTTP HEAD. It uses one request start per second or slower, reads robots.txt for each host, and backs off on HTTP 403 and 429. Run one fetch command at a time. The first run can take tens of minutes. The next run reuses the pages and receipts in `.devpost-cache/`. Keep that raw cache local. Follow a host's cooldown before using `--retry-failed` for an existing cache. Use a new `--cache` directory to capture fresh evidence for a previously missing page.

The build joins each sponsor award to its exact gallery label and requires the same Devpost project to confirm the prize and edition. Backrooms uses a separately attributed sponsor report with the track label confirmed in the Cal Hacks gallery. The [coverage report](../docs/coverage.md) identifies gaps where public sources differ or are unavailable. The generated [HTTP receipts](../winners/fetch-receipts.jsonl) cover every linked external URL in the winners directory. A status check on a video link cannot establish playback.

The link checker follows recognized same-host redirects and records the HTTP 200 destination used in the directory. `site/build.py` packages `winners/winners.json` for the [site](https://tracks.azizu.dev/); pushing to `main` deploys it.

The JSON and CSV share one row per project, edition and sponsor prize. The five list fields are JSON arrays in both formats. `event_prizes` includes general event prizes and each recorded sponsor award for that project. `prize_value` preserves prize wording stated in the track label, including placement and scope. `use_source` identifies where the sponsor note comes from and `use_quote` stores the supporting text with whitespace normalized. Full notes describe documented use. Light notes name a matching product from a Built With tag or dependency manifest. Award notes reproduce the exact prize label. Team information is limited to the member count.

## Reproduce or add coverage

- Rebuild twice from one cache with `python3 scripts/publish.py --output <directory>` and compare the output trees. `--readme README.md` also rewrites the README's generated sections and the root `SPONSORS.md`, `HACKATHONS.md` and `TOPICS.md` pages. In a checkout without the cache, `python3 scripts/verify.py --readme README.md` reproduces the exports, every generated page and the README sections offline, compares bytes and checks every relative link and anchor.
- Add an edition and year to [events.tsv](events.tsv). Use `python3 scripts/fetch.py galleries slugs.txt` to inspect its winner labels in `.devpost-cache/galleries.json`. [gallery-probes.txt](gallery-probes.txt) records the alternate slugs investigated for the coverage report.
- Add each exact gallery label to [tracks.tsv](tracks.tsv). The columns are event slug, Devpost label and sponsor. Use `Other` for prizes attributed to an individual instead of a sponsoring organization. Use `-` to exclude general event prizes and unattributed labels. Use the event prize description when the label does not explicitly name the sponsor.
- Run the commands above. Inspect unresolved evidence. Use [projects.tsv](projects.tsv) for edited project descriptions and [summary-descriptions.tsv](summary-descriptions.tsv) for sponsor-specific descriptions. Record each grounded claim in [sponsor-uses.tsv](sponsor-uses.tsv) as project URL, sponsor, note, source and exact quote of up to 200 characters. Devpost sources include `devpost:how_we_built`, `devpost:what_it_does`, `devpost:other_sections`, `devpost:gallery_caption` and `devpost:built_with`. Add product aliases to [sponsor-aliases.tsv](sponsor-aliases.tsv) under their sponsor.
- Use `devpost:project_link` with the exact hostname for a linked .tech site, Defang endpoint or Hex project. For a Figma resource, quote the host and resource type, such as `www.figma.com/design/`. Use `github:readme` for a linked README. Keep README files in `.github-cache/<owner>/<repo>.md` and pass `--github-cache .github-cache` to `publish.py` to check the quotes.
- Use `code` with a quote formatted as `path:line excerpt` and a sixth column containing its commit-pinned GitHub line URL. Use `demo_video` with `HH:MM:SS excerpt` and the verified Devpost demo URL in the sixth column. Pass `--source-cache` to publish or verify to check those excerpts directly. That directory holds source files under `repos/<owner>/<repo>/files/`, the pinned SHA in the adjacent `tree.json` and WebVTT files under `captions/`.
- Use [award-framing.tsv](award-framing.tsv) for categories, access prizes and other tracks where the award alone supports the note. Record the edition slug, exact prize title, sponsor and eligibility rationale. Use [code-matches.tsv](code-matches.tsv) for independently recovered repositories. Record the Devpost URL, public repository URL, HTTP 200 check time in UTC and the match evidence.
