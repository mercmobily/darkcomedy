# What is better than the old WordPress site

## Running it

* **No WordPress.** Nothing to update, patch or pay for. The old site ran WordPress plus 12 plugins (Septera theme,
  Contact Form 7, Content Views, Shortcodes Ultimate, Smush, Wordfence, Yoast SEO, WP Super Cache, BackWPup,
  Simple History, TablePress, a slider), each one a security risk if left un-updated.
* **No lost logins.** The old site depended on one person’s WordPress account. The new site is a folder of plain
  files: anyone with the repository can change it.
* **Free hosting** on GitHub Pages, with a working HTTPS certificate. The old address showed a security warning.
* **One folder per festival**, all built the same way (`festivals/2026-wodc7/` …). Next year is a copy of this year’s folder.
* **Instructions for next year** in `AGENTS.md`, written so an AI assistant (or a person) can do the yearly update.
* **Preview before publishing** with one command (`python3 build.py --serve`). Publishing is automatic when the
  change is pushed to GitHub.
* **QR codes that never change.** `print/qr-vote` points at `/vote/` and `print/qr-donate` at `/donate/`.
  When the voting form or donation page changes, only `site.json` changes; printed material stays valid.
* **A full backup** of the old site, including every original image (see [old-site-check.md](old-site-check.md)).

## The archive

| Festival | Old site | New site |
| --- | --- | --- |
| WoDC 1 (2018) | Archive page: trailer only (films on separate posts) | 10 films, trailer, logo |
| WoDC 2 (2019) | Archive page: short excerpts | 13 films with their quotes |
| WoDC 3 (2020) | Films; winners as two pictures, on a separate post | 15 films, winners and 30 audience comments as text, award badges on the films |
| WoDC 4 (2022) | Archive page listed 10 of the 14 films | All 14 films |
| WoDC 5 (2024) | Trailer only | 14 films with stills and quotes, screenings, printed programme |
| WoDC 6 (2025) | Nothing (a PDF on the voting page) | 14 films with stills, screenings, trailer, banner, printed programme |
| WoDC 7 (2026) | – | Home page, programme, voting page |

* The printed programmes are now **real web pages**: readable on a phone, searchable, and found by Google. The PDFs are still there to download.
* Every film is written the same way: “Country / length”, credits written out, a quote where there was one.
* Previous / next links between festivals.

## Visitors

* **Built for phones first**, and checked at phone width.
* **Screenings and ticket links on the home page**, not on a separate “The Tour” page.
* **Vote page lists the films in screening order** (with the intermission), so the audience can remember them, then links to the form.
* **Old links still work.** All 133 old addresses forward to the right place.
* **Fast.** No plugins, pictures resized for the web, only the first pictures load straight away.
* **Accessible.** Every picture has a description, there is a “skip to content” link, and the contrast is readable.
* **Better in search engines and on Facebook.** Every page has a description and a preview picture. Screening dates
  are marked up so Google can show them as events. There is a sitemap.
* **No tracking.** No cookies; YouTube trailers use YouTube’s privacy mode.
