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

The JSON and CSV share one row per project, edition and sponsor prize. The five list fields are JSON arrays in both formats. `event_prizes` includes general event prizes and each recorded sponsor award for that project. `prize_value` preserves prize wording stated in the track label, including placement and scope. Summaries draw on edited project notes, Devpost write-ups and linked GitHub READMEs. `use_source` identifies the source field and `use_quote` stores the supporting text with whitespace normalized. Full notes describe documented use. Built With notes name the product listed on Devpost. Team information is limited to the member count.

## Reproduce or add coverage

- Rebuild twice from one cache with `python3 scripts/publish.py --output <directory>` and compare the output trees. `--readme README.md` also rewrites the README's generated sections and the root `SPONSORS.md`, `HACKATHONS.md` and `TOPICS.md` pages. In a checkout without the cache, `python3 scripts/verify.py --readme README.md` reproduces the exports, every generated page and the README sections offline, compares bytes and checks every relative link and anchor.
- Add an edition and year to [events.tsv](events.tsv). Use `python3 scripts/fetch.py galleries slugs.txt` to inspect its winner labels in `.devpost-cache/galleries.json`. [gallery-probes.txt](gallery-probes.txt) records the alternate slugs investigated for the coverage report.
- Add each exact gallery label to [tracks.tsv](tracks.tsv). The columns are event slug, Devpost label and sponsor. Use `Other` for prizes attributed to an individual instead of a sponsoring organization. Use `-` to exclude general event prizes and unattributed labels. Use the event prize description when the label does not explicitly name the sponsor.
- Run the commands above. Inspect unresolved evidence. Use [projects.tsv](projects.tsv) for edited project descriptions and [summary-descriptions.tsv](summary-descriptions.tsv) for sponsor-specific descriptions. Record each grounded claim in [sponsor-uses.tsv](sponsor-uses.tsv) as project URL, sponsor, note, source and exact quote of up to 200 characters. Use `devpost:how_we_built` for narrative about implementation, `devpost:what_it_does` for functionality, including an explicit project caption, `devpost:built_with` for product tags and `github:readme` for README evidence. Add product aliases to [sponsor-aliases.tsv](sponsor-aliases.tsv) under their sponsor. Keep downloaded GitHub READMEs in `.github-cache/<owner>/<repo>.md`. Pass `--github-cache .github-cache` to `publish.py` to check GitHub quotes against those files. The publish and verify scripts check source fields, Built With tags and claim vocabulary. The publish step checks Devpost excerpts against the cached project text.
