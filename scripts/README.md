# Rebuild the winners index

Run from the repo root with Python 3.9 or later and curl 7.84 or later.

```sh
python3 scripts/fetch.py all
python3 scripts/publish.py --result result.md
python3 scripts/verify.py
```

The fetcher reads public Devpost galleries, event prize descriptions and project pages. It checks recognized source and demo URLs with HTTP HEAD. It uses one request start per second or slower, reads robots.txt for each host, and backs off on HTTP 403 and 429. Run one fetch command at a time. The first run can take tens of minutes. The next run reuses the pages and receipts in `.devpost-cache/`. Keep that raw cache local. Follow a host's cooldown before using `--retry-failed` for an existing cache. Use a new `--cache` directory to capture fresh evidence for a previously missing page.

The build joins each sponsor award to its exact gallery label and requires the same Devpost project to confirm the prize and edition. Backrooms uses a separately attributed sponsor report with the track label confirmed in the Cal Hacks gallery. The result report identifies gaps where public sources differ or are unavailable. The generated [HTTP receipts](../winners/fetch-receipts.jsonl) cover every linked external URL in the winners directory. A status check on a video link cannot establish playback.

The link checker follows recognized same-host redirects and records the HTTP 200 destination used in the directory. The site catalog can be refreshed locally with `python3 site/build.py` after a rebuild.

The JSON and CSV share one row per project, edition and sponsor prize. The five list fields are JSON arrays in both formats. `event_prizes` includes general event prizes and each recorded sponsor award for that project. `prize_value` preserves prize wording stated in the track label, including placement and scope. Summaries draw on edited project notes, Devpost captions and implementation details. `summary_evidence` records the level of support for the sponsor integration. Team information is limited to the member count.

## Reproduce or add coverage

- Rebuild twice from one cache with `python3 scripts/publish.py --output <directory>` and compare the output trees. For a public checkout without the cache, `python3 scripts/verify.py` rebuilds the Markdown, CSV and receipt manifest offline from the committed snapshot and compares bytes.
- Add an edition and year to [events.tsv](events.tsv). Use `python3 scripts/fetch.py galleries slugs.txt` to inspect its winner labels in `.devpost-cache/galleries.json`. [gallery-probes.txt](gallery-probes.txt) records the alternate slugs investigated for the coverage report.
- Add each exact gallery label to [tracks.tsv](tracks.tsv). The columns are event slug, Devpost label and sponsor. Use `-` for event or unattributed prizes. Use the event prize description when the label does not explicitly name the sponsor.
- Run the three commands above. Inspect unresolved evidence. Use [projects.tsv](projects.tsv) for edited project descriptions and [summaries.tsv](summaries.tsv) for edited explanations of specific sponsor integrations.
