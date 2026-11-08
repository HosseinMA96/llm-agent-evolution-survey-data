"""Redraw the held-out sample for the independent human check (Sec. II-D / IX-B). Run from data/.

- Same LLM-agent corpus as bibliometrics.py (n = 6,965), excluding the 300 abstracts of validation_sample.csv.
- 50 abstracts, stratified to oversample 2024: 20 (2024) + 15 (2025) + 15 (2026); seed 20261107; order shuffled.
Writes heldout_sheet_blank.csv (the sheet given to the coder; no rule outputs) and heldout_rules.csv (keyword-rule
outputs, not shown to the coder). It never touches heldout_labels.csv; with --check it only verifies that the
archived heldout_rules.csv and the items of heldout_labels.csv match the redrawn sample.
"""
import csv, io, json, os, random, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bibliometrics import LLM, INTERNAL

R0 = json.load(open('harvest.json'))['records']
R = [r for r in R0 if r['topic_centric'] in (True, 'True') and re.search(LLM, r['abstract'], re.I)]
assert len(R) == 6965, len(R)
seen = {r['id'] for r in csv.DictReader(open('validation_sample.csv'))}
random.seed(20261107)
samp = []
for year, k in (('2024', 20), ('2025', 15), ('2026', 15)):
    pool = sorted((r for r in R if r['published'][:4] == year and r['id'] not in seen), key=lambda r: r['id'])
    samp += random.sample(pool, k)
random.shuffle(samp)

sheet, rules = io.StringIO(newline=''), io.StringIO(newline='')
w = csv.writer(sheet)
w.writerow(['item', 'id', 'year', 'link', 'title', 'abstract', 'trains_model', 'system_around_model', 'notes'])
for i, r in enumerate(samp, 1):
    w.writerow([i, r['id'], r['published'][:4], f"https://arxiv.org/abs/{r['id']}", r['title'],
                ' '.join(r['abstract'].split()), '', '', ''])
w = csv.writer(rules)
w.writerow(['id', 'year', 'regex_weights', 'regex_harness'])
for r in samp:
    w.writerow([r['id'], r['published'][:4], int(bool(re.search(INTERNAL['weights'], r['abstract'], re.I))),
                int(bool(re.search(INTERNAL['harness'], r['abstract'], re.I)))])

if '--check' in sys.argv:
    assert open('heldout_rules.csv', newline='').read() == rules.getvalue(), 'heldout_rules.csv differs'
    blank = list(csv.DictReader(io.StringIO(sheet.getvalue())))
    lab = list(csv.DictReader(open('heldout_labels.csv', newline='')))
    for b, l in zip(blank, lab):
        assert all(b[k] == l[k] for k in ('item', 'id', 'year', 'link', 'title', 'abstract')), b['id']
    assert len(blank) == len(lab) == 50
    print('OK: heldout_rules.csv and the items of heldout_labels.csv match the redrawn sample')
else:
    open('heldout_sheet_blank.csv', 'w', newline='').write(sheet.getvalue())
    open('heldout_rules.csv', 'w', newline='').write(rules.getvalue())
    print('wrote', len(samp), 'items: heldout_sheet_blank.csv, heldout_rules.csv')
