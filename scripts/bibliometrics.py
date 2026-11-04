"""Reproducible bibliometric analyses for Paper 1 (Section IX).

Usage: python3 scripts/bibliometrics.py   (run from literature/)
Inputs: harvest.json. Outputs: bibliometrics.json (+ stdout tables).
- Corpus: agent-titled records whose abstracts mention a language model (n=6,965).
- Theme shares on titles (Table VIII), internalization shares on abstracts (Table VII).
- Wilson 95% intervals for every share; vocabulary sensitivity variants; term-adoption series.
"""
import json, math, re, collections, random

LLM = r'language model|\bLLMs?\b|\bGPT|foundation model'
THEMES = {
    'Multi-agent': r'multi-?agent',
    'RL training': r'reinforcement|\bRL\b|policy optimi|GRPO|PPO',
    'GUI/web/computer use': r'\bGUI\b|\bweb\b|browser|computer[- ]use|\bOS\b|mobile|desktop|smartphone',
    'Software/coding': r'software|\bcode|coding|programming|repositor|\bSWE\b',
    'Memory': r'memory|memories',
    'Tool use': r'\btools?\b|tool[- ]use|tool[- ]calling|function[- ]calling',
    'Benchmark/eval': r'benchmark|evaluat',
    'Safety/security': r'safety|secur|attack|jailbreak|injection|risk|align|trust',
    'Planning/reasoning': r'plan|reason',
}
INTERNAL = {
    'weights': r'reinforcement learning|\bRL\b|fine-?tun(e|ed|ing)|post-?train|\bGRPO\b|\bPPO\b|\bDPO\b|policy optimi[sz]ation|\bSFT\b',
    'trainfree': r'training-free|train-free|tuning-free|without (any |additional |further )?(re)?(training|fine-?tuning|parameter updates|gradient)|no (additional |extra )?(training|fine-?tuning)',
    'harness': r'harness|scaffold|context engineering|context management|orchestrat',
    # Sensitivity: drop the two terms coined/popularized in 2025 ("harness", "context engineering").
    'harness_frozen2024': r'scaffold|context management|orchestrat',
    # Sensitivity: broad 2024-era vocabulary suggested by the reviewer.
    'harness_broad2024': r'scaffold|orchestrat|pipeline|workflow|framework|prompting',
    'harness_broad2024_noframework': r'scaffold|orchestrat|pipeline|workflow|prompting',
}
TERMS = {'harness': r'harness', 'context engineering': r'context engineering',
         'scaffold': r'scaffold', 'orchestrat': r'orchestrat', 'agentic (title)': None}

# Verb uses of "harness" ("to harness the power of LLMs") are false positives; strip them before matching.
VERB_HARNESS = re.compile(r'\b(to|can|we|that|which|they|and|effectively|fully|better|successfully|by|in|for)\s+harness(es|ed|ing)?\b'
                          r'|\b\w+\s+harness(es|ed)\b(?=\s+(the|their|its|this|these|a|an|LLM|large|multiple|collective))'
                          r'|\bharness(ing)?\s+(the|their|its|this|these|LLMs?|large|multiple|collective)\b', re.I)
CLEAN = {
    # Main measure after the sensitivity analysis: noun "harness" only.
    'harness_noun': r'harness|scaffold|context engineering|context management|orchestrat',
}

def wilson(k, n, z=1.96):
    if n == 0: return (0.0, 0.0)
    p = k / n; d = 1 + z*z/n
    c = (p + z*z/(2*n)) / d; h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / d
    return (max(0.0, round(100*(c-h), 1)), round(100*(c+h), 1))

def diff_test(k1, n1, k2, n2, z=1.96):
    """Difference p2-p1 in percentage points: Newcombe (Wilson-score) 95% CI and two-sided pooled z-test p-value."""
    p1, p2 = k1/n1, k2/n2
    l1, u1 = [x/100 for x in wilson(k1, n1)]; l2, u2 = [x/100 for x in wilson(k2, n2)]
    d = p2 - p1
    lo = d - math.sqrt((p2-l2)**2 + (u1-p1)**2); hi = d + math.sqrt((u2-p2)**2 + (p1-l1)**2)
    pp = (k1+k2)/(n1+n2); se = math.sqrt(pp*(1-pp)*(1/n1+1/n2))
    zz = d/se if se else 0.0
    pv = math.erfc(abs(zz)/math.sqrt(2))
    return {'diff_pp': round(100*d, 1), 'ci95_pp': (round(100*lo, 1), round(100*hi, 1)), 'z': round(zz, 2), 'p': float(f'{pv:.2g}')}

def shares(R, pats, field):
    tot = collections.Counter(r['published'][:4] for r in R); out = {}
    for k, p in pats.items():
        c = collections.Counter(r['published'][:4] for r in R if re.search(p, r[field], re.I))
        out[k] = {y: {'k': c[y], 'pct': round(100*c[y]/tot[y], 1), 'ci95': wilson(c[y], tot[y])} for y in sorted(tot)}
    return dict(sorted(tot.items())), out

def main():
    R0 = json.load(open('harvest.json'))['records']
    tc = [r for r in R0 if r['topic_centric']]
    R = [r for r in tc if re.search(LLM, r['abstract'], re.I)]
    yrs_tc = collections.Counter(r['published'][:4] for r in tc)
    yrs = collections.Counter(r['published'][:4] for r in R)
    res = {'corpus_n': len(R), 'topic_centric_by_year': dict(sorted(yrs_tc.items())),
           'llm_by_year': dict(sorted(yrs.items())),
           'queries_2022': dict(collections.Counter(q for r in tc if r['published'][:4] == '2022' for q in r['queries'].split(';')))}
    tot, th = shares(R, THEMES, 'title'); res['themes'] = th; res['n'] = tot
    _, it = shares(R, INTERNAL, 'abstract'); res['internal'] = it
    for r in R: r['abstract_noverb'] = VERB_HARNESS.sub(' ', r['abstract'])
    _, cl = shares(R, CLEAN, 'abstract_noverb'); it.update(cl)
    _, cl2 = shares(R, {'harness_term_noun': r'harness'}, 'abstract_noverb'); it.update(cl2)
    both = collections.Counter(r['published'][:4] for r in R
                               if re.search(INTERNAL['weights'], r['abstract'], re.I) and re.search(INTERNAL['harness'], r['abstract'], re.I))
    res['internal']['weights_and_harness'] = {y: {'k': both[y], 'pct': round(100*both[y]/tot[y], 1), 'ci95': wilson(both[y], tot[y])} for y in tot}
    # term adoption across the whole corpus (abstracts)
    res['term_adoption'] = {t: {y: round(100*sum(1 for r in R if r['published'][:4] == y and re.search(p, r['abstract'], re.I))/tot[y], 1) for y in tot}
                            for t, p in TERMS.items() if p}
    res['agentic_in_title'] = {y: round(100*sum(1 for r in R if r['published'][:4] == y and re.search(r'\bagentic\b', r['title'], re.I))/tot[y], 1) for y in tot}
    # Robustness of title-theme shares: same rules on abstracts, and titles excluding the "agentic" buzzword.
    _, res['themes_abstract'] = shares(R, THEMES, 'abstract')
    _, res['themes_title_no_agentic'] = shares([r for r in R if not re.search(r'\bagentic\b', r['title'], re.I)], THEMES, 'title')
    # Two-proportion comparisons for every change discussed in the text
    nT = {y: tot[y] for y in tot}
    def cmp(series, a, b): return diff_test(series[a]['k'], nT[a], series[b]['k'], nT[b])
    pairs = [('2024', '2025'), ('2025', '2026'), ('2024', '2026')]
    res['comparisons'] = {'themes': {k: {f'{a}->{b}': cmp(v, a, b) for a, b in pairs + [('2023', '2026')]} for k, v in th.items()},
                          'internal': {k: {f'{a}->{b}': cmp(v, a, b) for a, b in pairs} for k, v in it.items()}}
    # Multiple-comparison correction over the family of tests interpreted in Section IX (Holm and Benjamini-Hochberg)
    FAMILY = [('themes', 'Multi-agent', '2024->2025'), ('themes', 'Multi-agent', '2025->2026'),
              ('themes', 'Safety/security', '2024->2026'), ('themes', 'Benchmark/eval', '2024->2026'), ('themes', 'Benchmark/eval', '2025->2026'),
              ('themes', 'Memory', '2025->2026'), ('themes', 'GUI/web/computer use', '2024->2026'), ('themes', 'Software/coding', '2024->2026'),
              ('themes', 'Planning/reasoning', '2024->2026'),
              ('internal', 'weights', '2024->2025'), ('internal', 'weights', '2025->2026'), ('internal', 'trainfree', '2024->2026')] + \
             [('internal', v, yp) for v in ['harness', 'harness_noun', 'harness_frozen2024', 'harness_broad2024_noframework'] for yp in ['2024->2025', '2025->2026']]
    C = res['comparisons']; ps = [C[g][k][yp]['p'] for g, k, yp in FAMILY]; m = len(ps)
    order = sorted(range(m), key=lambda i: ps[i]); holm = [0]*m; run = 0
    for r, i in enumerate(order): run = max(run, min(1, (m - r) * ps[i])); holm[i] = run
    bh = [0]*m; run = 1
    for r, i in reversed(list(enumerate(order))): run = min(run, ps[i] * m / (r + 1)); bh[i] = run
    res['multiple_comparisons'] = [{'test': f'{g}:{k}:{yp}', 'p': ps[i], 'p_holm': float(f'{holm[i]:.2g}'), 'p_bh': float(f'{bh[i]:.2g}'),
                                    'holds_holm_0.05': holm[i] < 0.05, 'holds_bh_0.05': bh[i] < 0.05} for i, (g, k, yp) in enumerate(FAMILY)]
    res['wilson_wald_note'] = 'ci95 = Wilson score interval, z=1.96'
    res['regex'] = {'llm_filter': LLM, 'themes': THEMES, 'internal': INTERNAL}
    json.dump(res, open('bibliometrics.json', 'w'), indent=1)
    # validation sample for human annotation (fixed seed)
    random.seed(20261102)
    samp = random.sample([r for r in R if r['published'][:4] in ('2024', '2025', '2026')], 300)
    with open('validation_sample.csv', 'w') as f:
        import csv
        w = csv.writer(f); w.writerow(['id', 'year', 'title', 'abstract', 'regex_weights', 'regex_harness',
                                       'A1_weights', 'A1_harness', 'A2_weights', 'A2_harness'])
        for r in samp:
            w.writerow([r['id'], r['published'][:4], r['title'], r['abstract'],
                        int(bool(re.search(INTERNAL['weights'], r['abstract'], re.I))),
                        int(bool(re.search(INTERNAL['harness'], r['abstract'], re.I))), '', '', '', ''])
    print('n', tot)
    for k, v in it.items(): print(f"{k:32s}", *[f"{v[y]['pct']:5.1f} {v[y]['ci95']}" for y in tot])
    for k, v in th.items(): print(f"{k:22s}", *[f"{v[y]['pct']:5.1f} {v[y]['ci95']}" for y in tot])
    print('adoption', res['term_adoption']); print('agentic title', res['agentic_in_title']); print('2022', res['queries_2022'], res['topic_centric_by_year'])

if __name__ == '__main__':
    main()
