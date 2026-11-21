# Hackathon Tracks site delivery

Built a mobile-first static catalog with instant search, sponsor/hackathon/year/tech filters, sorting, project cards, sponsor pages, a multi-track champions view, and a track picker that ranks matching winners and tallies their most listed tech. The theme defaults to the system setting and supports persistent light and dark overrides.

## Open locally

Open [index.html](index.html) from the filesystem, or run `python3 -m http.server 8000 --bind 127.0.0.1` from the repository root and visit `http://127.0.0.1:8000/site/`. Refresh the catalog and proposed README counts with `python3 site/build.py` after an index update.

## Files and images

- `site/index.html`, `site/style.css`, `site/app.js`, `site/favicon.png` — the site.
- `site/build.py`, `site/catalog.js` — the data packager and bundled catalog.
- [Proposed README hero](README_HERO.md) and [Pages instructions](DEPLOY.md).
- [1280×640 README banner and social preview](../docs/tracks-banner.png) and [README site screenshot](../docs/tracks-preview.webp).
- [390px light catalog](qa/390-browse-light.png), [390px dark track picker](qa/390-picker-dark.png), [1280px light catalog](qa/1280-browse-light.png), and [1280px dark track picker](qa/1280-picker-dark.png).

## Verified

- A headless Chromium session passed at 390px and 1280px. Checked search by project, summary and tech, each filter and combined filters, clearing, zero results, sorting, pagination, sponsor pages and direct links, champions, the track picker and its matching-tech tally, keyboard skip and checkbox controls, theme persistence and system changes. No horizontal page overflow or console errors in the tested flows. The catalog also fit at 320px.
- Direct file navigation supported search. A synthetic enriched fixture exercised same-sponsor multi-track wins, optional team size, source and demo links, additional event prizes, and rendering a remote image URL with an intercepted response.
- Representative text and control border colors measured at least 6.86:1 and 3.54:1, respectively, against their checked backgrounds.

## Data and publication

The final local build used 187 award rows and rendered 178 projects, 27 sponsors and 16 hackathon editions. That snapshot supplied no thumbnail, GitHub or demo URLs. Cards render those fields when a later index supplies them. Rebuild after the parallel data enrichment lands to refresh site data and counts.

Pages publishing and the README's live URL are pending. All deliverables are local.
