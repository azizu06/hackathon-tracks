# Publish Hackathon Tracks on GitHub Pages

The site runs from static files with no runtime dependencies. GitHub Pages supports branch publishing from the root or `/docs`. Publish `site/` from `main` using a GitHub Actions artifact.

## Build and preview locally

From the repository root, run:

```sh
python3 site/build.py
python3 -m http.server 8000 --bind 127.0.0.1
```

Open `http://127.0.0.1:8000/site/`. You can also open `site/index.html` directly. The generated `catalog.js` is bundled with the page, so local search and filters work from a file URL. Devpost images and outbound links still need a network connection.

The build reads `winners/winners.json` and refreshes both `site/catalog.js` and the counts in `site/README_HERO.md`. Run it after updating the winners index.

## Publish from a workflow on main

1. In GitHub's Pages settings, choose **GitHub Actions** as the source once publication is approved.
2. Start from GitHub's static Pages workflow template and have its build job check out `main` and run the commands below. The entry point and all runtime assets should sit at the artifact root.
3. Point the template's `upload-pages-artifact` step at `${{ runner.temp }}/tracks-pages`. Keep the template's deploy job, environment and permissions.
4. Open the reported Pages URL and its `#sponsors` and `#picker` routes. Replace `LIVE_SITE_URL` in the proposed README block with the verified URL. Use `docs/tracks-banner.png` for the repository's social preview.

```sh
python3 site/build.py
mkdir -p "$RUNNER_TEMP/tracks-pages"
cp site/index.html site/style.css site/app.js site/catalog.js site/favicon.png "$RUNNER_TEMP/tracks-pages/"
```

## Publish from main /docs instead

If you use branch publishing, build the catalog from the repository root and copy the five runtime files above into `docs/`. Place an empty `.nojekyll` file alongside them. Keep the banner and preview where they are, then choose **Deploy from a branch**, **main**, **/docs**. Repeat the copy whenever the app or catalog changes.

[GitHub Pages publishing source and workflow documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)
