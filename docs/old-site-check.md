# Old WordPress site: has anything been lost?

Checked on 14 November 2026, the last time the old WordPress site was online and readable.

## What was saved

A full copy of the old site is in `~/Development/current/darkcomedy-wordpress-backup/` (99 MB, kept outside this
repository so the site stays small):

| Folder | What |
| --- | --- |
| `html/` | Every page of the old site as it looked in a browser (133 pages, one file each) |
| `uploads/` | Every file ever uploaded: 113 images, 4 PDF/Word files (originals, full size) |
| `rest/` | The site’s raw data: pages, posts, categories, the media list, the sitemaps |
| `all-urls.txt` | Every address the old site had (133) |

Nobody needs access to the old WordPress admin any more: everything it held is in that folder.

## How it was checked

1. **Text.** Every line of text on all 133 old pages was looked up on the new site (punctuation and capitals ignored).
2. **Images.** Every old image was compared with the new site’s images by a small fingerprint, so re-cropped and
   resized copies still count as found.
3. **Addresses.** Every old address was checked to lead somewhere on the new site.
4. **Links.** Every outside link on the new site was opened.

## Results

### Text: nothing lost

All film titles, credits, synopses and page text are on the new site. Some of it was corrected (see [fixes.md](fixes.md)).
Left out on purpose:

* WordPress furniture: post dates, “Previous Post / Next Post”, “Read More”, image size labels, category pages.
* The contact and partner **web forms**. They needed WordPress; the new pages give the email address instead.
* The home page slider text “ON NATIONAL TOUR” and the “Tour dates for our sister festival” link (the About page
  links to Over The Fence).
* “Welcome to our Archive page”, the 2020 “We’re Back!” post (just a donate button) and the footer credit “Site by Andrew van Leen”.

### Images: nothing lost that matters

69 of the 113 old images are on the new site. This check also added three things:

* **The 2025 (WoDC 6) banner**: `festivals/2025-wodc6/gallery/banner.jpg`.
* **A sharper still for “A Wreck in Paradise”** (2020).
* **The 2021 winners poster and the audience comments**, which were pictures of text. They are now real text on the
  [2020 page](../festivals/2020-wodc3/festival.json) (`awards`, `audience_comments`).

The other 41 were left out on purpose:

| How many | What | Why |
| ---: | --- | --- |
| 13 | Animated GIF teasers for the 2019 films | Tiny (320×240); the new site uses each film’s still |
| 3 + 3 + 2 + 3 | Logo variants: WoDC 2, the generic WoDC logo, WoDC 4, WoDC 5 promo banners | Same design as the festival artwork already shown |
| 4 + 4 | WoDC 3 header/background banners | Old WordPress theme decoration |
| 4 | Site icons (apple-icon, clapperboard) | Replaced by the new favicon |
| 3 | “FLASHBACK!” press-release drafts (April 2024, Backlot Perth) | Never published; was that event ever held? |
| 1 | Over The Fence “Godzilla” graphic | Sister festival |
| 1 | Stock photo of space | Old background |
| 1 | “Waiting Room” still, attached to Beyond The Bubble (2018) | It is not from that film; no film called Waiting Room was screened |

The 4 documents:

| File | Where it is now |
| --- | --- |
| WoDC5-voting.pdf | `festivals/2024-wodc5/programme.pdf`, also typed up as the 2024 page |
| WoDC6-Voting-info.pdf | `festivals/2025-wodc6/programme.pdf`, also typed up as the 2025 page |
| 23rd-OTF-entry-form.pdf | Not used: an old Over The Fence entry form (entries now go through FilmFreeway) |
| Menu-MKR-Dunsy.docx | Not used: a restaurant menu, uploaded by mistake |

The film stills for 2024 and 2025 were taken out of those two programme PDFs, except “The Sandwich” (2025), whose
picture in the PDF is too small to use.

### Addresses: all 133 still work

Old addresses forward to their new home: `/voting/` → `/vote/`, `/2019-archive/` → `/archive/2019/`, every film
page → that film on its festival page, and so on. Anything already printed or linked keeps working.
The list is in `old-wordpress-urls.json` (pages) and `build.py` (films, automatic).

One address changed meaning: `/dark-comedy-trailer/` was titled “WoDC 5 Trailer” but the video on it is the
**WoDC 6 (2025)** trailer (its YouTube title is “TRAILER WoDC6 2025”). It now forwards to the 2025 page, where that trailer is shown.

### Links

All outside links work (checked 14 Nov 2026) except **voces.org.au**, which shows a server error. The link was
removed from the About page.
