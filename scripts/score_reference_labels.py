"""Score the two abstract rules against the reference labels (run from data/).
Reads reference_labels.csv; writes reference_scores.json with precision/recall/F1, shares, and per-year recall with
95% Wilson intervals (Sec. IX-B). If ai_precheck_labels.csv (first labeling pass) and second_pass_labels.csv (blind
second pass) are present, it also reports their agreement (raw and Cohen's kappa) and checks that the reference labels
differ from the first pass only on disagreements resolved as listed in label_adjudication.csv."""
import csv, json, math, os


def load(path):
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - h, 3), round(c + h, 3)]


def kappa(a, b):
    n = len(a); po = sum(x == y for x, y in zip(a, b)) / n
    pa = sum(a) / n; pb = sum(b) / n; pe = pa * pb + (1 - pa) * (1 - pb)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


rows = load('reference_labels.csv')
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
        d[f'recall_ci_{y}'] = wilson(tp_, tp_ + fn_) if tp_ + fn_ else None
        d[f'positives_{y}'] = tp_ + fn_
        d[f'rule_share_{y}'] = round(sum(a for a, _ in s) / len(s), 3)
        d[f'label_share_{y}'] = round(sum(b for _, b in s) / len(s), 3)
    out[lab] = d; print(lab, d)

if os.path.exists('ai_precheck_labels.csv') and os.path.exists('second_pass_labels.csv'):
    first = {r['id']: r for r in load('ai_precheck_labels.csv')}
    second = {r['id']: r for r in load('second_pass_labels.csv')}
    adj = {(r['id'], r['label']): r for r in load('label_adjudication.csv')} if os.path.exists('label_adjudication.csv') else {}
    agree = {}
    for lab, col in [('weights', 'trains_model'), ('harness', 'system_around_model')]:
        a = [int(first[r['id']][f'AI_{lab}']) for r in rows]; b = [int(second[r['id']][col]) for r in rows]
        f = [int(r[f'ref_{lab}']) for r in rows]
        for r, x, y, z in zip(rows, a, b, f):
            if x == y:
                assert z == x, f'{r["id"]} {lab}: reference label differs from two agreeing passes'
            elif adj:
                assert int(adj[(r['id'], lab)]['final']) == z, f'{r["id"]} {lab}: not resolved as in label_adjudication.csv'
        agree[lab] = {'n': len(rows), 'agreement': round(sum(x == y for x, y in zip(a, b)) / len(rows), 3),
                      'cohen_kappa': round(kappa(a, b), 4), 'disagreements': sum(x != y for x, y in zip(a, b)),
                      'changed_by_adjudication': sum(x != z for x, z in zip(a, f))}
        print('agreement', lab, agree[lab])
    out['first_vs_second_pass'] = agree

with open('reference_scores.json', 'w', encoding='utf-8', newline='\n') as fh:
    json.dump(out, fh, indent=1)
