# Rebuild the winners index

Run from the repo root with Python 3.9 or later and curl on your PATH. No packages, API keys, or logins are needed.

```sh
python3 scripts/fetch.py curated
python3 scripts/publish.py
```

The fetcher requests public Devpost pages serially, at most once per second, and saves the HTML and timestamped status receipts in `.devpost-cache/`. Keep the cache local. The first run takes several minutes. Repeat runs reuse cached responses. For a fresh fetch, pass the same new `--cache` directory to both commands. Use `--retry-failed` to retry failed requests in an existing cache.

The publisher checks each project's HTTP 200 receipt, event, and exact prize label against the cached gallery and project page. It handles Backrooms as a sponsor-reported prize, with the public track name checked against the Cal Hacks gallery. It reads technology tags from the Built With section. It then renders both Markdown views, CSV, and JSON from the same award rows. If a source is missing or awards disagree, review the evidence before publishing an updated index.

## Add projects

1. Put one public Devpost hackathon slug per line in a text file. Run `python3 scripts/fetch.py galleries events.txt` and inspect `.devpost-cache/galleries.json`.
2. Put the Devpost project URLs you want to inspect in a text file. Run `python3 scripts/fetch.py projects urls.txt` and read the cached pages. Select sponsor-backed awards with clear project descriptions.
3. Update [events.tsv](events.tsv) with the slug, event name, and year. Add the canonical URL and a one-sentence description to [projects.tsv](projects.tsv). [sponsors.tsv](sponsors.tsv) maps known winner labels to sponsor names, and [patterns.tsv](patterns.tsv) holds the notes based on the included projects.
4. Rebuild and review the diff. Use `python3 scripts/publish.py --output <new-directory>` to render a separate snapshot for comparison.

Run one fetch command at a time to keep the shared Devpost request rate within one request per second.
