"""Score the regex labels against human annotation (run from literature/ after filling validation_sample.csv).
Reports Cohen's kappa between annotators and precision/recall/F1 of each regex against the reference labels:
the adjudicated label (ADJ_*) when present, otherwise the cases where both annotators agree."""
import csv, json
rows = list(csv.DictReader(open('validation_sample.csv')))
# Preferred input: separate blind sheets annotator1_labels.csv / annotator2_labels.csv (columns trains_model, system_around_model).
import os
if os.path.exists('annotator1_labels.csv') and os.path.exists('annotator2_labels.csv'):
    s1 = {r['id']: r for r in csv.DictReader(open('annotator1_labels.csv'))}
    s2 = {r['id']: r for r in csv.DictReader(open('annotator2_labels.csv'))}
    for r in rows:
        if r['id'] in s1 and r['id'] in s2:
            r['A1_weights'], r['A1_harness'] = s1[r['id']]['trains_model'], s1[r['id']]['system_around_model']
            r['A2_weights'], r['A2_harness'] = s2[r['id']]['trains_model'], s2[r['id']]['system_around_model']
def kappa(a, b):
    n = len(a); po = sum(x == y for x, y in zip(a, b)) / n
    pa = sum(a) / n; pb = sum(b) / n; pe = pa * pb + (1 - pa) * (1 - pb)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0
out = {}
for lab in ['weights', 'harness']:
    done = [r for r in rows if r[f'A1_{lab}'].strip() in '01' and r[f'A2_{lab}'].strip() in '01' and r[f'A1_{lab}'].strip() and r[f'A2_{lab}'].strip()]
    if not done: print(lab, ': no annotations yet'); continue
    a1 = [int(r[f'A1_{lab}']) for r in done]; a2 = [int(r[f'A2_{lab}']) for r in done]
    ref = []
    for r, x, y in zip(done, a1, a2):
        adj = r.get(f'ADJ_{lab}', '').strip()
        ref.append((int(r[f'regex_{lab}']), int(adj) if adj in ('0', '1') else (x if x == y else None)))
    ref = [(p, t) for p, t in ref if t is not None]
    tp = sum(p and t for p, t in ref); fp = sum(p and not t for p, t in ref); fn = sum((not p) and t for p, t in ref)
    prec = tp / (tp + fp) if tp + fp else float('nan'); rec = tp / (tp + fn) if tp + fn else float('nan')
    out[lab] = {'n_annotated': len(done), 'n_reference': len(ref), 'cohen_kappa': round(kappa(a1, a2), 3),
                'precision': round(prec, 3), 'recall': round(rec, 3), 'f1': round(2 * prec * rec / (prec + rec), 3) if prec + rec else None,
                'agreement': round(sum(x == y for x, y in zip(a1, a2)) / len(done), 3)}
    print(lab, out[lab])
json.dump(out, open('annotation_scores.json', 'w'), indent=1)
