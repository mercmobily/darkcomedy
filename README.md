# darkcomedy.com.au

The website of **A World of Dark Comedy**, an international dark-comedy short-film festival in Perth.
It is built by one Python script from plain files and hosted for free on GitHub Pages. There is no WordPress and no database.

## What is where

```
site.json                 the site's settings: current festival, links (vote form, donations, FilmFreeway), contact details
festivals/                one folder per festival, all built the same way
  2026-wodc7/
    festival.json         the text: screenings, blurb, films (credits, synopsis, quote)
    artwork.jpg           the festival poster: home page picture and share preview
    logo.png              the festival logo, shown in the site header (current festival only)
    films/                film pictures, named after the film: bite-or-bark.jpg, bite-or-bark-2.jpg, just-men-poster.jpg
    gallery/              (if any) extra pictures for the archive page
    programme.pdf         (if any) the printed programme
    print/                (if any) logo and artwork files for the printer, not published
pages/                    About, Contact, Donate, Submit a film (plain HTML)
theme/                    page shell (base.html), styles (style.css), favicon
print/                    QR codes for printed material: vote and donate (they never change)
old-wordpress-urls.json   old WordPress addresses and where they now lead
build.py                  builds the site into _site/
docs/                     notes: fixes to the old text, improvements, check of the old site
AGENTS.md                 step-by-step instructions for next year's festival (for an AI assistant or a person)
```

## Pages

| Address | Made from |
| --- | --- |
| `/` | the current festival (`site.json` → `current_festival`) |
| `/programme/` | the current festival's films, in screening order |
| `/vote/` | the film order, then a link to the voting form (`links.vote_form`) |
| `/archive/`, `/archive/<year>/` | every festival |
| `/about/`, `/contact/`, `/donate/`, `/enter/` | `pages/` |

Every old WordPress address (`/voting/`, `/2019-archive/`, `/broccolli/` …) forwards to its new page from `404.html`.

## Editing

```sh
python3 build.py --serve      # build and preview at http://localhost:8000
```

Needs only Python 3.10 or newer. The usual jobs (new artwork, ticket links, next year's festival) are described in
[AGENTS.md](AGENTS.md).

## Publishing

Every push to `main` is built and published by `.github/workflows/deploy.yml`
(repository **Settings → Pages → Source: GitHub Actions**).

Until the domain is moved, the site is at `https://<github-user>.github.io/<repository>/`. To serve it at darkcomedy.com.au:

1. Add a file called `CNAME` at the top of this folder, containing the single line `darkcomedy.com.au`, and push.
2. In **Settings → Pages**, set the custom domain to `darkcomedy.com.au` and tick **Enforce HTTPS** once it is offered.
3. Change only the web records in the domain's DNS. The domain uses the old host's name servers (ns1/ns2.syrahost.com),
   so the records are edited in that host's **cPanel → Zone Editor**, not on the Crazy Domains “DNS Settings” page:
   * `darkcomedy.com.au`, four A records: 185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153
     (replacing the old A record)
   * `darkcomedy.com.au`, four AAAA records: 2606:50c0:8000::153, 2606:50c0:8001::153, 2606:50c0:8002::153,
     2606:50c0:8003::153 (replacing the old AAAA record)
   * `www`, CNAME: `<github-user>.github.io`

**Leave the MX and `mail` records alone.** Email for production@darkcomedy.com.au is still handled by the old host.
