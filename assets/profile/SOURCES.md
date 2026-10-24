# Profile graphic sources

This README follows the byte theme of the owner's portfolio `DinoPreloader`: a carbon canvas (#080808), warm white pixels (#EEECE6), a running T-Rex, compact monospace context, numbered project rows, technology icons, and a dated activity snapshot. The portfolio files remain unchanged. `jeushdev.me` is a future domain, shown as coming soon.

## Header and icons

- `tools/build_profile.py` reuses the body and two running poses from `portfolio-ver1/src/components/DinoPreloader.tsx`. It generates `hero.svg` and `hero-mobile.svg`; the README selects the compact header at viewport widths up to 600px.
- The header uses two-frame CSS animation and a `prefers-reduced-motion` static fallback. This implementation is present in the SVG; published GitHub image-proxy and animation behavior has not been accepted or verified.
- Outlined lettering comes from [Press Start 2P](https://github.com/google/fonts/tree/main/ofl/pressstart2p) and [Geist Mono](https://github.com/google/fonts/tree/main/ofl/geistmono), from the official Google Fonts repository under the SIL Open Font License. Source fonts are cached locally, not bundled; header display needs no font download.
- Nine technology icons are stored locally. React, Next.js, TypeScript, Python, Django, PostgreSQL, Supabase, and Docker come from [skill-icons](https://github.com/tandpfun/skill-icons), under the MIT license retained in `icons/LICENSE-skill-icons.txt`. The n8n path comes from [Simple Icons](https://github.com/simple-icons/simple-icons/blob/develop/icons/n8n.svg), distributed under CC0, and is placed on a matching icon background.
- Core context, project table, contribution boundaries, numbered headings, and contact links are native Markdown or supported HTML. The artwork uses self-contained SVGs. It does not use runtime third-party statistics-card services.

## Activity data

`tools/update_stats.py` reads the public GitHub profile and owned repositories through REST, plus the account's public contribution-calendar HTML. `stats.json` records the source URLs, timestamp, metrics, scope, and daily calendar levels. Calendar totals follow account visibility settings; repository and star metrics cover public repositories only.

The saved snapshot at `2026-10-24T10:28:48+08:00` contains **1,087 contributions in the last year, 13 public repositories, 13 followers, and 1 star on public repositories**. These are dated observed values, not permanent claims. `activity.svg` and `activity-mobile.svg` display the snapshot and date, with muted green activity levels (#1B2421, #46564C, #7A9282, #B4C7BB, #EEECE6). Their text uses a generic monospace family. The updater also refreshes the README's activity alt text with the exact values and date.

`.github/workflows/profile-stats.yml` is prepared locally to refresh daily at 19:35 UTC and on manual dispatch, then commit changed snapshot files and README alt text. Publication, the first remote run, and scheduled execution remain unverified. Reading visible data locally does not establish remote workflow acceptance.

## Rebuild and preview

From the repository root:

```text
python tools/build_profile.py --cache FONT_CACHE_DIRECTORY
python tools/update_stats.py
node tools/render_profile.cjs --preview-dir PREVIEW_DIRECTORY
```

The header generator requires `fonttools` and downloads missing fonts from Google Fonts. The statistics updater uses Python's standard library and requires network access; `GITHUB_TOKEN` is optional for its REST calls. Preview mode requires Node, `playwright`, Microsoft Edge available through Playwright's `msedge` channel, a `github-markdown.css` file in the preview directory, and access to GitHub's Markdown API. Pillow and Sharp are not required.

Local evidence is saved at `C:/Users/jeush/Documents/Codex/2026-10-24/jeushdev-readme-preview/`: `github-rendered.html`, `index.html`, `checks.json`, and four screenshots covering 1280px desktop and 390px mobile in light and dark schemes. All four cases record 11 decoded images, the expected desktop/mobile hero and activity sources, no horizontal overflow, and no page errors.

`github-rendered.html` is the GitHub Markdown API response after its rendering and sanitization; the screenshots apply a local GitHub-style stylesheet to it. These are local approximations, not published profile captures or verification of GitHub's production image proxy, animation, or scheduled workflow. The checks inventory links without proving destination health.
