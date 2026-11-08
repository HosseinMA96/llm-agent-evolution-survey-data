"""Score the keyword rules against the held-out human labels (Sec. II-D / IX-B). Run from data/.

Reads heldout_labels.csv (one coder, 50 abstracts) and heldout_rules.csv; reports labeled shares and each rule's
precision and recall with 95% Wilson intervals. Writes heldout_scores.json. A single coder gives no
inter-annotator agreement, so no kappa is computed.
"""
import csv, json, math


def wilson(k, n, z=1.96):
    if not n: return None
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - h, 3), round(c + h, 3)]


def rule_vs(pairs):
    tp = sum(p and t for p, t in pairs); fp = sum(p and not t for p, t in pairs)
    fn = sum(t and not p for p, t in pairs)
    return {'n': len(pairs), 'positives': tp + fn, 'labeled_share': round((tp + fn) / len(pairs), 3),
            'labeled_share_ci': wilson(tp + fn, len(pairs)),
            'rule_share': round((tp + fp) / len(pairs), 3), 'tp': tp, 'fp': fp, 'fn': fn,
            'rule_precision': round(tp / (tp + fp), 3) if tp + fp else None,
            'rule_precision_ci': wilson(tp, tp + fp),
            'rule_recall': round(tp / (tp + fn), 3) if tp + fn else None,
            'rule_recall_ci': wilson(tp, tp + fn)}


lab = {r['id']: r for r in csv.DictReader(open('heldout_labels.csv', newline=''))}
key = {r['id']: r for r in csv.DictReader(open('heldout_rules.csv', newline=''))}
assert set(lab) == set(key) and len(key) == 50
out = {'n': len(key), 'coders': 1}
for q, rule in (('trains_model', 'regex_weights'), ('system_around_model', 'regex_harness')):
    assert all(lab[i][q] in ('0', '1') for i in key), q
    out[q] = rule_vs([(int(key[i][rule]), int(lab[i][q])) for i in key])
    print(q, out[q])
json.dump(out, open('heldout_scores.json', 'w'), indent=1)
