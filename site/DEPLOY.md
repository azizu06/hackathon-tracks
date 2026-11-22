[Hackathon Tracks](../README.md) / Site build and deploy

# Site build and deploy

The site at [tracks.azizu.dev](https://tracks.azizu.dev/) is five static files with no dependencies: `index.html`, `style.css`, `app.js`, `catalog.js` and `favicon.png`.

## Preview locally

From the repository root:

```sh
python3 site/build.py
python3 -m http.server 8000 --bind 127.0.0.1 --directory site
```

Open `http://127.0.0.1:8000/`. `build.py` reads `winners/winners.json` and writes `site/catalog.js`, so run it after rebuilding the index.

## Deploy

Every push to `main` runs [the Pages workflow](../.github/workflows/pages.yml). It rebuilds `catalog.js`, copies the five files into a Pages artifact and deploys it to the custom domain.

## Links into the site

The site reads its state from the URL, so any view can be linked:

| Link | Opens |
| --- | --- |
| `#browse?sponsor=google&tech=python` | Winners filtered by sponsor and tech. Also accepts `event`, `year`, `q` and `sort` |
| `#sponsor=Google` | One sponsor's winners and what they have in common |
| `#sponsors`, `#hackathons`, `#champions`, `#picker` | The other tabs |
