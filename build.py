#!/usr/bin/env python3
"""Build darkcomedy.com.au into _site/  (Python 3.10+, standard library only)

    python3 build.py                 # build for https://darkcomedy.com.au
    python3 build.py --serve         # build, then preview at http://localhost:8000
    python3 build.py --base /repo    # build for a GitHub project address (user.github.io/repo)

Inputs (see README.md):
    site.json                 site-wide settings: current festival, links, contact details
    festivals/<year>-wodc<n>/ one self-contained folder per festival (festival.json + images)
    pages/*.html              about, contact, donate, enter
    theme/                    base.html (page shell), style.css, favicon.png
    old-wordpress-urls.json   old WordPress page addresses and where they now live
                              (old film pages, /<film-slug>/, are forwarded automatically)
"""
import argparse, functools, html, http.server, json, re, shutil, time
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parent
OUT = ROOT / '_site'
esc = html.escape

SITE = json.loads((ROOT / 'site.json').read_text())
OLD_URLS = json.loads((ROOT / 'old-wordpress-urls.json').read_text())
SHELL = Template((ROOT / 'theme/base.html').read_text())
BASE = ''  # path prefix, set by --base


# ---------- loading ----------

PLACES = ('1st', '2nd', '3rd', '4th', '5th')


def load_festival(folder):
    """festival.json plus the images found in the folder by naming convention."""
    f = json.loads((folder / 'festival.json').read_text())
    url = f'festivals/{folder.name}'
    f['id'], f['folder'] = folder.name, url
    f['artwork'] = f'{url}/artwork.jpg' if (folder / 'artwork.jpg').exists() else None
    f['logo'] = f'{url}/logo.png' if (folder / 'logo.png').exists() else None
    f['programme_pdf'] = f'{url}/programme.pdf' if (folder / 'programme.pdf').exists() else None
    f['gallery'] = [f'{url}/gallery/{p.name}' for p in sorted((folder / 'gallery').glob('*.jpg'))]
    for film in f['films']:
        # films/<slug>.jpg is the main image, then <slug>-2.jpg, <slug>-3.jpg…, then <slug>-poster.jpg
        found = sorted((folder / 'films').glob(f'{film["slug"]}*.jpg'),
                       key=lambda p: (p.stem.endswith('-poster'), len(p.stem), p.stem))
        found = [p for p in found if re.fullmatch(re.escape(film['slug']) + r'(-\d+|-poster)?', p.stem)]
        film['images'] = [f'{url}/films/{p.name}' for p in found]
        film['won'] = [f'{PLACES[i]}, {a["award"]}' for a in f.get('awards', [])
                       for i, pl in enumerate(a['places']) if pl['film'] == film['slug']]
    return f


FESTIVALS = sorted((load_festival(d) for d in (ROOT / 'festivals').iterdir() if (d / 'festival.json').exists()),
                   key=lambda f: f['year'], reverse=True)
CURRENT = next(f for f in FESTIVALS if f['id'] == SITE['current_festival'])

NAV = [('/programme/', 'Programme'), ('/#tickets', 'Tickets'), ('/vote/', 'Vote'), ('/donate/', 'Donate'),
       ('/archive/', 'Archive'), ('/enter/', 'Submit a film'), ('/about/', 'About'), ('/contact/', 'Contact')]


# ---------- output helpers ----------

def lookup(key):
    value = SITE
    for part in key.split('.'):
        value = value[part]
    return value


QR_CAPTIONS = {'vote': 'Scan to vote', 'donate': 'Scan to donate'}


def qr_code(name):
    """A QR code from print/ (qr-vote points at /vote/, qr-donate at /donate/; they never change), with download links."""
    caption = QR_CAPTIONS[name]
    return (f'<figure class="qr"><img src="/print/qr-{name}.svg" alt="QR code for darkcomedy.com.au/{name}/" width="160" height="160">'
            f'<figcaption>{caption}<br><small>Download for print: <a href="/print/qr-{name}.png" download>PNG</a> · '
            f'<a href="/print/qr-{name}.svg" download>SVG</a></small></figcaption></figure>')


def fill(text):
    """Replace placeholders in pages/*.html: {{links.donate}}-style values from site.json; {{qr.donate}} with a QR code."""
    def value(m):
        key = m.group(1)
        return qr_code(key[3:]) if key.startswith('qr.') else esc(str(lookup(key)))
    return re.sub(r'\{\{\s*([\w.]+)\s*\}\}', value, text)


def write(path, content):
    target = OUT / path.strip('/') if path.endswith('.html') else OUT / path.strip('/') / 'index.html'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content)


def page(path, title, body, description=None, image=None, page_class='page', head=''):
    current = ' aria-current="page"'
    nav = '\n'.join(f'      <a href="{href}"{current if href == path else ""}>{label}</a>' for href, label in NAV)
    social = ' · '.join(f'<a href="{s["url"]}">{s["name"]}</a>' for s in SITE['social'])
    brand = (f'<img src="/{CURRENT["logo"]}" alt="{esc(SITE["name"])} {CURRENT["edition"]}" width="785" height="384">'
             if CURRENT['logo'] else f'<span class="brand-text">{esc(SITE["name"])}</span>')
    c = SITE['contact']
    write(path, SHELL.substitute(
        title=esc(SITE['name'] if title is None else f'{title} – {SITE["name"]}'),
        description=esc(description or SITE['tagline']), canonical=SITE['url'] + path,
        og_image=SITE['url'] + '/' + (image or CURRENT['artwork']), head=head, version=int(time.time()),
        page_class=page_class, site_name=esc(SITE['name']), tagline=esc(SITE['tagline']),
        slogan=esc(SITE['slogan']), brand=brand, nav=nav,
        body=body, year=CURRENT['year'], email=c['email'], phone=c['phone'], mobile=c['mobile'], social=social))


def img(src, alt, lazy=True):
    lazy = ' loading="lazy"' if lazy else ''
    return f'<img src="/{src}" alt="{esc(alt)}"{lazy} decoding="async">'


def paragraphs(items, cls=''):
    attr = f' class="{cls}"' if cls else ''
    return ''.join(f'<p{attr}>{esc(p)}</p>' for p in items)


# ---------- components ----------

def film_card(film, number=None, lazy=True):
    images = film['images']
    media = ''
    if images:
        fit = ' contain' if images[0].endswith('-poster.jpg') else ''
        media = f'<a class="film-media{fit}" href="/{images[0]}">{img(images[0], "Still from " + film["title"], lazy)}</a>'
    body = [f'<p class="film-num">{number:02d}</p>' if number else '',
            f'<h3>{esc(film["title"])}</h3>',
            f'<p class="film-info">{esc(film["info"])}</p>' if film.get('info') else '',
            ''.join(f'<p class="film-award">{esc(w)}</p>' for w in film['won']),
            paragraphs(film.get('synopsis', [])),
            f'<p class="film-quote">{esc(film["quote"])}</p>' if film.get('quote') else '']
    if film.get('credits'):
        body.append('<ul class="film-credits">' + ''.join(f'<li>{esc(c)}</li>' for c in film['credits']) + '</ul>')
    if len(images) > 1:
        body.append('<div class="film-gallery">' + ''.join(
            f'<a href="/{i}">{img(i, "Image from " + film["title"])}</a>' for i in images[1:]) + '</div>')
    return (f'<article class="film{"" if media else " no-media"}" id="{film["slug"]}">{media}'
            f'<div class="film-body">{"".join(body)}</div></article>')


def film_list(f):
    """Films in screening order; numbered when the order is known (an intermission is set)."""
    out, interval = [], f.get('intermission_after')
    for n, film in enumerate(f['films'], 1):
        out.append(film_card(film, n if interval else None, lazy=n > 2))
        if interval and n == interval and n < len(f['films']):
            out.append('<div class="intermission"><span>Intermission</span></div>')
    return '<div class="films">' + '\n'.join(out) + '</div>'


def screenings(f):
    rows = []
    for s in f.get('screenings', []):
        ticket = f'<a class="button" href="{esc(s["tickets"])}">Get tickets</a>' if s.get('tickets') else ''
        when = ' · '.join(x for x in (s['date'], s.get('time')) if x)
        rows.append(f'<li class="screening"><div><p class="screening-venue">{esc(s["venue"])}</p>'
                    f'<p class="screening-when">{esc(when)}</p></div>{ticket}</li>')
    return '<ul class="screenings">' + ''.join(rows) + '</ul>' if rows else ''


def rating_mark(f):
    """The official classification mark for the festival's rating ("R18+" -> theme/rating-r18.png), else the rating as text."""
    rating = f.get('rating')
    if not rating:
        return ''
    name = 'rating-' + re.sub(r'[^a-z0-9]', '', rating.lower()) + '.png'
    if (ROOT / 'theme' / name).exists():
        return f'<img class="rating" src="/theme/{name}" alt="Classification: {esc(rating)}" width="64" height="64">'
    return f'<span class="rating-text">{esc(rating)}</span>'


def trailer(f):
    if not f.get('trailer'):
        return ''
    return (f'<div class="video"><iframe src="https://www.youtube-nocookie.com/embed/{f["trailer"]}" '
            f'title="{esc(f["title"])} trailer" loading="lazy" allowfullscreen '
            f'allow="encrypted-media; picture-in-picture"></iframe></div>')


def festival_card(f):
    href = '/programme/' if f is CURRENT else f'/archive/{f["year"]}/'
    cover = f['artwork'] or next((film['images'][0] for film in f['films'] if film['images']), None)
    badge = '<span class="badge">Now showing</span>' if f is CURRENT else ''
    tagline = f'<small class="edition-tagline">{esc(f["tagline"])}</small>' if f.get('tagline') else ''
    return (f'<a class="edition-card" href="{href}">{img(cover, f["title"]) if cover else ""}'
            f'<span class="edition-label">{badge}<strong>WoDC {f["edition"]}</strong> {f["year"]}'
            f'<small>{len(f["films"])} films</small>{tagline}</span></a>')


def awards(f):
    """Winners and audience comments, when festival.json has them."""
    if not f.get('awards'):
        return ''
    titles = {film['slug']: film['title'] for film in f['films']}
    cols = ''.join(
        f'<div class="award"><h3>{esc(a["award"])}</h3><ol>' + ''.join(
            f'<li><span class="place">{PLACES[i]}</span><a href="#{pl["film"]}">{esc(titles[pl["film"]])}</a>'
            f'{"<q>" + esc(pl["quote"].strip("“”")) + "</q>" if pl.get("quote") else ""}</li>'
            for i, pl in enumerate(a['places'])) + '</ol></div>' for a in f['awards'])
    said = ''
    if f.get('audience_comments'):
        said = ('<h3>What the audience said</h3><ul class="comments">'
                + ''.join(f'<li>{esc(c)}</li>' for c in f['audience_comments']) + '</ul>')
    return f'<h2 id="winners">Winners</h2><div class="awards">{cols}</div>{said}'


def event_data(f):
    """schema.org events, so search engines can show screening dates and ticket links."""
    events = []
    for s in f.get('screenings', []):
        m = re.search(r'(\d{1,2}) (\w{3})\w* (\d{4})', s['date'])
        t = re.search(r'(\d{1,2})[.:](\d{2})\s*pm', s.get('time', ''))
        if not m:
            continue
        month = 'JanFebMarAprMayJunJulAugSepOctNovDec'.index(m.group(2)) // 3 + 1
        start = f'{m.group(3)}-{month:02d}-{int(m.group(1)):02d}'
        if t:
            start += f'T{int(t.group(1)) % 12 + 12:02d}:{t.group(2)}:00+08:00'
        events.append({'@context': 'https://schema.org', '@type': 'ScreeningEvent', 'name': f['title'],
                       'startDate': start, 'location': {'@type': 'Place', 'name': s['venue'],
                                                        'address': s['venue'] + ', Western Australia'},
                       'image': SITE['url'] + '/' + f['artwork'], 'description': f.get('tagline') or SITE['tagline'],
                       'eventStatus': 'https://schema.org/EventScheduled',
                       **({'offers': {'@type': 'Offer', 'url': s['tickets']}} if s.get('tickets') else {})})
    return f'<script type="application/ld+json">{json.dumps(events)}</script>' if events else ''


# ---------- pages ----------

def build_home():
    f = CURRENT
    tiles = ''.join(f'<a class="poster-tile" href="/programme/#{film["slug"]}">{img(film["images"][0], film["title"])}'
                    f'<span>{n:02d} · {esc(film["title"])}</span></a>'
                    for n, film in enumerate(f['films'], 1) if film['images'])
    blurb = ''.join(f'<p>{p}</p>' for p in f.get('blurb', []))  # blurb may contain <strong>: trusted, our own file
    body = f'''
<section class="hero">{img(f["artwork"], f["title"] + " – festival artwork", lazy=False)}</section>
<section class="wrap intro">
  <p class="eyebrow">{esc(f["title"])}</p>
  <h1>{esc(f.get("intro") or f["title"])}</h1>
  <div class="blurb">{blurb}</div>
</section>
<section class="band" id="tickets">
  <div class="wrap"><div class="section-head"><h2>Screenings &amp; tickets</h2>{rating_mark(f)}</div>{screenings(f)}</div>
</section>
<section class="wrap">
  <h2>The {len(f["films"])} films</h2>
  <div class="poster-grid">{tiles}</div>
  <p><a class="button" href="/programme/">See the full programme</a></p>
</section>
<section class="band cta">
  <div class="wrap cta-inner">
    <div class="cta-item"><div><h2>Vote for your favourite</h2><p>Saw the show? Tell us which film was the most popular.</p><a class="button" href="/vote/">Vote now</a></div>
      <img class="qr-mini" src="/print/qr-vote.svg" alt="QR code for darkcomedy.com.au/vote/" width="120" height="120"></div>
    <div class="cta-item"><div><h2>Support the festival</h2><p>Tax-deductible donations keep dark comedy on the big screen.</p><a class="button" href="/donate/">Donate</a></div>
      <img class="qr-mini" src="/print/qr-donate.svg" alt="QR code for darkcomedy.com.au/donate/" width="120" height="120"></div>
  </div>
</section>
<section class="wrap">
  <h2>Past festivals</h2>
  <div class="edition-grid">{"".join(festival_card(x) for x in FESTIVALS if x is not CURRENT)}</div>
</section>'''
    where = ' and '.join(f'{s["venue"]} {s["date"]}' for s in f.get('screenings', []))
    page('/', None, body, description=f'{f["title"]}: {len(f["films"])} dark comedy short films from around the world. {where}.',
         page_class='home', head=event_data(f))


def build_programme():
    f = CURRENT
    body = f'''
<section class="wrap page-head">
  <p class="eyebrow">{esc(f["title"])}</p>
  <div class="section-head"><h1>Programme</h1>{rating_mark(f)}</div>
  <p class="lead">{len(f["films"])} short films, in screening order.</p>
  {screenings(f)}
</section>
<section class="wrap">{film_list(f)}</section>'''
    page('/programme/', 'Programme', body, page_class='programme', head=event_data(f),
         description=f'The {f["title"]} programme: ' + ', '.join(x['title'] for x in f['films']) + '.')


def build_vote():
    f = CURRENT
    form = esc(SITE['links']['vote_form'])
    order = ''.join(f'<li><a href="/programme/#{film["slug"]}">{esc(film["title"])}</a>'
                    f'{" <small>(" + esc(film["info"]) + ")</small>" if film.get("info") else ""}</li>'
                    + ('<li class="intermission-item">Intermission</li>' if n == f.get('intermission_after') else '')
                    for n, film in enumerate(f['films'], 1))
    body = f'''
<section class="wrap narrow page-head">
  <p class="eyebrow">{esc(f["title"])}</p>
  <h1>Vote for the most popular film</h1>
  <p class="lead">To refresh your memory, here are the films in screening order. Then cast your vote!</p>
  <p><a class="button button-big" href="{form}">Vote now</a></p>
  {qr_code("vote")}
  <ol class="film-order">{order}</ol>
  <p><a class="button" href="{form}">Vote now</a></p>
</section>'''
    page('/vote/', 'Vote', body, description=f'Vote for the most popular film at {f["title"]}.', page_class='vote')


def build_archive():
    body = f'''
<section class="wrap page-head">
  <h1>Festival archive</h1>
  <p class="lead">Every A World of Dark Comedy programme since 2018.</p>
  <div class="edition-grid">{"".join(festival_card(f) for f in FESTIVALS)}</div>
</section>'''
    page('/archive/', 'Archive', body, page_class='archive',
         description='Every A World of Dark Comedy festival programme since 2018.')
    for i, f in enumerate(FESTIVALS):
        newer, older = (FESTIVALS[i - 1] if i else None), (FESTIVALS[i + 1] if i + 1 < len(FESTIVALS) else None)
        pager = '<nav class="pager">' + (
            f'<a href="/archive/{older["year"]}/">← WoDC {older["edition"]} ({older["year"]})</a>' if older else '<span></span>') + (
            f'<a href="/archive/{newer["year"]}/">WoDC {newer["edition"]} ({newer["year"]}) →</a>' if newer else '') + '</nav>'
        gallery = ('<h2 id="gallery">From the festival</h2><div class="gallery">' + ''.join(
            f'<a href="/{g}">{img(g, f["title"])}</a>' for g in f['gallery']) + '</div>') if f['gallery'] else ''
        extras = ''.join([
            '<p><a class="button" href="/programme/">This is the current festival – see the programme</a></p>' if f is CURRENT else '',
            f'<p><a class="button" href="/{f["programme_pdf"]}">Printed programme (PDF)</a></p>' if f['programme_pdf'] else ''])
        head_media = (img(f['artwork'], f['title'] + ' artwork', lazy=False) if f['artwork'] else '') + trailer(f)
        body = f'''
<section class="wrap page-head">
  <p class="eyebrow"><a href="/archive/">Archive</a></p>
  <h1>WoDC {f["edition"]} – {f["year"]}</h1>
  <p class="lead">{esc(f.get("tagline") or f["title"])}</p>
  <div class="edition-head">{head_media}</div>
  {screenings(f) if f is not CURRENT else ""}
  {extras}
</section>
<section class="wrap">
  {awards(f)}
  <h2>The {len(f["films"])} films</h2>
  {film_list(f)}
  {gallery}
  {pager}
</section>'''
        page(f'/archive/{f["year"]}/', f'WoDC {f["edition"]} ({f["year"]})', body, image=f['artwork'],
             description=f'{f["title"]} ({f["year"]}): ' + ', '.join(x['title'] for x in f['films']) + '.',
             page_class='edition')


def build_pages():
    for src in sorted((ROOT / 'pages').glob('*.html')):
        text = src.read_text()
        title = re.search(r'<!--\s*title:\s*(.*?)\s*-->', text).group(1)
        page(f'/{src.stem}/', title, f'<section class="wrap narrow prose">{fill(text)}</section>', page_class=src.stem)


def build_extras():
    # Old addresses forward from the 404 page, so they add no folders to the site.
    # Tries the whole old path, then its first part (WordPress image pages were /<film>/<image>/).
    films = {film['slug']: ('/programme/' if f is CURRENT else f'/archive/{f["year"]}/') + '#' + film['slug']
             for f in FESTIVALS for film in f['films']}
    forward = ('<script>(function(){var base=' + json.dumps(BASE) + ',map=' + json.dumps({**films, **OLD_URLS}, sort_keys=True)
               + ';var p=location.pathname.slice(base.length).replace(/^\\/+|\\/+$/g,""),'
               'to=map[p]||map[p.split("/")[0]];if(to)location.replace(base+to);})();</script>')
    page('/404.html', 'Page not found', f'''{forward}
<section class="wrap narrow page-head"><h1>Page not found</h1><p class="lead">That page has vanished into the dark.
Try the <a href="/programme/">programme</a>, the <a href="/archive/">archive</a> or the <a href="/">home page</a>.</p></section>''',
         page_class='notfound')
    urls = ['/', '/programme/', '/vote/', '/archive/'] + [f'/archive/{f["year"]}/' for f in FESTIVALS] + \
           [f'/{p.stem}/' for p in sorted((ROOT / 'pages').glob('*.html'))]
    (OUT / 'sitemap.xml').write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + ''.join(f'  <url><loc>{SITE["url"]}{u}</loc></url>\n' for u in urls) + '</urlset>\n')
    (OUT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {SITE["url"]}/sitemap.xml\n')
    (OUT / '.nojekyll').write_text('')


def copy_files():
    (OUT / 'theme').mkdir(parents=True)
    for name in ['style.css', 'favicon.png'] + sorted(p.name for p in (ROOT / 'theme').glob('rating-*.png')):
        shutil.copy(ROOT / 'theme' / name, OUT / 'theme' / name)
    shutil.copytree(ROOT / 'festivals', OUT / 'festivals', ignore=shutil.ignore_patterns('festival.json', 'print'))  # print/ is for printers, not the web
    shutil.copytree(ROOT / 'print', OUT / 'print')  # the vote and donate QR codes: shown on the site and downloadable
    for extra in ('CNAME',):  # custom-domain file for GitHub Pages, if present
        if (ROOT / extra).exists():
            shutil.copy(ROOT / extra, OUT / extra)


def apply_base():
    """Prefix root-relative links with --base (for previews at user.github.io/repo)."""
    if not BASE:
        return
    for f in OUT.rglob('*.html'):
        t = re.sub(r'((?:href|src)=")/(?!/)', rf'\1{BASE}/', f.read_text())
        f.write_text(t)


def main():
    global BASE
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--base', default='', help='path prefix, e.g. /darkcomedy')
    ap.add_argument('--serve', action='store_true', help='preview at http://localhost:8000 after building')
    args = ap.parse_args()
    BASE = args.base.rstrip('/')
    if OUT.exists():
        shutil.rmtree(OUT)
    copy_files()
    build_home(); build_programme(); build_vote(); build_archive(); build_pages(); build_extras()
    apply_base()
    print(f'Built {sum(1 for _ in OUT.rglob("*.html"))} pages from {len(FESTIVALS)} festivals into {OUT.name}/')
    if args.serve:
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(OUT))
        print('Preview: http://localhost:8000  (Ctrl+C to stop)')
        http.server.ThreadingHTTPServer(('127.0.0.1', 8000), handler).serve_forever()


if __name__ == '__main__':
    main()
