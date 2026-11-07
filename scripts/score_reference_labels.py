"""Score the two abstract rules against the author-verified reference labels (run from data/).
Reads reference_labels.csv; writes reference_scores.json with precision/recall/F1, shares, and per-year recall (Sec. IX-B)."""
import csv, json
rows = list(csv.DictReader(open('reference_labels.csv')))
out = {}
for lab in ['weights', 'harness']:
    p = [int(r[f'regex_{lab}']) for r in rows]; t = [int(r[f'ref_{lab}']) for r in rows]
    tp = sum(a and b for a, b in zip(p, t)); fp = sum(a and not b for a, b in zip(p, t)); fn = sum(b and not a for a, b in zip(p, t))
    pr = tp / (tp + fp); rc = tp / (tp + fn)
    d = {'n_reference': len(rows), 'precision': round(pr, 3), 'recall': round(rc, 3), 'f1': round(2 * pr * rc / (pr + rc), 3),
         'rule_share': round(sum(p) / len(rows), 3), 'label_share': round(sum(t) / len(rows), 3)}
    for y in sorted({r['year'] for r in rows}):
        s = [(a, b) for a, b, r in zip(p, t, rows) if r['year'] == y]
        tp_ = sum(a and b for a, b in s); fn_ = sum(b and not a for a, b in s)
        d[f'n_{y}'] = len(s); d[f'recall_{y}'] = round(tp_ / (tp_ + fn_), 3) if tp_ + fn_ else None
        d[f'label_share_{y}'] = round(sum(b for _, b in s) / len(s), 3)
    out[lab] = d; print(lab, d)
json.dump(out, open('reference_scores.json', 'w'), indent=1)
