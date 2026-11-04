#!/usr/bin/env python3
"""Check every arXiv eprint in a references.bib against arxiv.org/abs metadata (title + first author surname).
usage: verify_arxiv_ids.py <references.bib> [out.tsv]   -- polite: 1.5 s between requests."""
import re, sys, time, html, unicodedata, urllib.request
bib = open(sys.argv[1]).read(); out = sys.argv[2] if len(sys.argv) > 2 else None
def norm(t):
    t = unicodedata.normalize('NFKD', html.unescape(t)).encode('ascii', 'ignore').decode()
    t = re.sub(r'\\[a-zA-Z]+|[{}$\\"\'`^~]', '', t)
    return re.sub(r'[^a-z0-9]', '', t.lower())
rows = []
for m in re.finditer(r'@\w+\{([^,]+),(.*?)\n\}', bib, re.S):
    key, body = m.group(1), m.group(2)
    e = re.search(r'eprint = \{([^}]*)\}', body)
    if not e: continue
    t = re.search(r'title = \{(.*)\},\n', body); a = re.search(r'author = \{(.*?)\},\n', body)
    rows.append((key, e.group(1), t.group(1) if t else '', a.group(1) if a else ''))
res = []
for key, aid, title, auth in rows:
    for attempt in range(4):
        try:
            req = urllib.request.Request(f'https://arxiv.org/abs/{aid}', headers={'User-Agent': 'survey-bib-check/1.0'})
            page = urllib.request.urlopen(req, timeout=60).read().decode('utf8', 'ignore'); break
        except Exception as ex:
            page = ''; time.sleep(10 * (attempt + 1))
    at = re.search(r'<meta name="citation_title" content="([^"]*)"', page)
    aa = re.search(r'<meta name="citation_author" content="([^"]*)"', page)
    if not at:
        res.append((key, aid, 'FETCH_FAIL', '', '')); print(key, aid, 'FETCH_FAIL', flush=True); time.sleep(1.5); continue
    atitle = html.unescape(at.group(1)); afirst = html.unescape(aa.group(1)) if aa else ''
    first = re.split(r'\s+and\s+', auth.strip())[0].strip(' {}')
    sur_bib = norm(first.split(',')[0] if ',' in first else first.split()[-1] if first.split() else '')
    sur_arx = norm(afirst.split(',')[0])
    tok = norm(title) == norm(atitle)
    aok = sur_bib == sur_arx or sur_bib in norm(afirst) or norm(afirst.split(',')[0]) in norm(first)
    status = 'OK' if tok and aok else ('TITLE_MISMATCH' if not tok else '') + (' AUTHOR_MISMATCH' if not aok else '')
    res.append((key, aid, status.strip(), atitle, afirst))
    if status != 'OK': print(key, aid, status, '|', atitle, '|', afirst, flush=True)
    time.sleep(1.5)
if out:
    with open(out, 'w') as f:
        for r in res: f.write('\t'.join(r) + '\n')
print('checked', len(res), 'ok', sum(r[2] == 'OK' for r in res))
