#!/usr/bin/env python3
"""Coverage-gap analysis against competitor surveys.

usage: coverage_gap.py <paper_dir> <out.tsv> <arxiv_id> [<arxiv_id> ...]
For each competitor survey, fetch its reference list (Semantic Scholar; falls back to arXiv
IDs scraped from the arXiv HTML rendering when S2 has no parsed references). Aggregate how many
competitors cite each work, and report works cited by competitors but NOT by our references.bib
(matched by arXiv id, DOI, or normalized title). Output TSV: n_competitors, citations, year,
arxiv, doi, title  -- sorted by n_competitors then citations.
"""
import json, re, sys, time, urllib.request
paper, out, comps = sys.argv[1], sys.argv[2], sys.argv[3:]
bib = open(f'{paper}/paper/references.bib').read()
norm = lambda s: re.sub(r'[^a-z0-9]', '', (s or '').lower())
our_ax = set(re.findall(r'eprint\s*=\s*\{([^}]+)\}', bib)) | set(re.findall(r'arxiv\.org/abs/([0-9.]+)', bib))
our_doi = {d.lower() for d in re.findall(r'doi\s*=\s*\{([^}]+)\}', bib)}
our_ti = {norm(t)[:60] for t in re.findall(r'\btitle\s*=\s*\{(.+?)\},?\s*$', bib, re.M)}

def get(url, data=None):
    for att in range(6):
        try:
            req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json', 'User-Agent': 'coverage-gap/1.0'})
            return urllib.request.urlopen(req, timeout=90).read()
        except Exception as e:
            print('  retry', e, file=sys.stderr); time.sleep(10 * (att + 1))
    return None

agg = {}   # key -> dict(title, year, arxiv, doi, cites, by=set())
def add(comp, title, year, ax, doi, cites):
    key = ('ax:' + ax) if ax else ('doi:' + doi.lower()) if doi else ('t:' + norm(title)[:60])
    e = agg.setdefault(key, dict(title=title, year=year, arxiv=ax, doi=doi, cites=cites, by=set()))
    e['by'].add(comp)
    if not e['title'] and title: e['title'] = title

pending_s2 = []
for c in comps:
    raw = get(f'https://api.semanticscholar.org/graph/v1/paper/ARXIV:{c}/references?fields=externalIds,title,year,citationCount&limit=1000')
    refs = (json.loads(raw).get('data') or []) if raw else []
    time.sleep(3)
    if refs:
        for r in refs:
            p = r.get('citedPaper') or {}
            x = p.get('externalIds') or {}
            add(c, p.get('title') or '', p.get('year'), x.get('ArXiv', ''), x.get('DOI', '') if not str(x.get('DOI','')).startswith('10.48550') else '', p.get('citationCount') or 0)
        print(f'{c}: {len(refs)} refs (S2)', file=sys.stderr)
        continue
    html = get(f'https://arxiv.org/html/{c}')
    ids = set()
    if html:
        h = html.decode('utf8', 'ignore')
        ids = set(re.findall(r'(?:arXiv[:\s]*|arxiv\.org/(?:abs|pdf)/)(\d{4}\.\d{4,5})', h, re.I)) - {c}
    print(f'{c}: {len(ids)} arXiv refs (HTML fallback)', file=sys.stderr)
    for i in ids:
        add(c, '', None, i, '', 0); pending_s2.append(i)
    time.sleep(3)

# fill titles/citations for HTML-scraped ids via S2 batch
pending = sorted({i for i in pending_s2 if not agg['ax:' + i]['title']})
for k in range(0, len(pending), 400):
    raw = get('https://api.semanticscholar.org/graph/v1/paper/batch?fields=title,year,citationCount,externalIds',
              json.dumps({'ids': ['ARXIV:' + i for i in pending[k:k + 400]]}).encode())
    for i, r in zip(pending[k:k + 400], json.loads(raw) if raw else []):
        if r:
            e = agg['ax:' + i]; e['title'] = r.get('title') or ''; e['year'] = r.get('year'); e['cites'] = r.get('citationCount') or 0
            d = (r.get('externalIds') or {}).get('DOI', '')
            if d and not d.startswith('10.48550'): e['doi'] = d
    time.sleep(3)

rows = []
for e in agg.values():
    if (e['arxiv'] and e['arxiv'] in our_ax) or (e['doi'] and e['doi'].lower() in our_doi) or (e['title'] and norm(e['title'])[:60] in our_ti):
        continue
    rows.append((len(e['by']), e['cites'] or 0, e['year'] or '', e['arxiv'], e['doi'], e['title'].replace('\t', ' ')))
rows.sort(key=lambda r: (-r[0], -r[1]))
with open(out, 'w') as f:
    f.write('n_comp\tcites\tyear\tarxiv\tdoi\ttitle\n')
    for r in rows: f.write('\t'.join(map(str, r)) + '\n')
tot = len(agg); missing = len(rows)
print(f'unique works cited by competitors: {tot}; not cited by us: {missing}; cited by >=2 competitors and missing: {sum(r[0]>=2 for r in rows)}', file=sys.stderr)
