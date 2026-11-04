"""Print LaTeX rows for Tables VII-VIII of Paper 1 from bibliometrics.json (run from literature/)."""
import json
d = json.load(open('bibliometrics.json'))
def cell(v): return f"{v['pct']:.1f} {{\\scriptsize[{v['ci95'][0]:.1f}, {v['ci95'][1]:.1f}]}}"
I = d['internal']
rows = [('Weight updates (RL, fine-tuning, post-training)', 'weights'),
        ('Scaffold, full vocabulary$^{a}$', 'harness'),
        ('\\quad full, verb uses of \\emph{harness} removed', 'harness_noun'),
        ('\\quad frozen 2024 vocabulary$^{b}$', 'harness_frozen2024'),
        ('\\quad broad 2024 vocabulary$^{c}$', 'harness_broad2024_noframework'),
        ('\\quad noun \\emph{harness} alone', 'harness_term_noun'),
        ('Explicitly training-free', 'trainfree'),
        ('Both weight updates and full scaffold vocabulary', 'weights_and_harness')]
print('% Table VII rows'); 
for lab, k in rows: print(lab, '&', ' & '.join(cell(I[k][y]) for y in ['2024', '2025', '2026']), '\\\\')
T = d['themes']; order = ['Multi-agent', 'Benchmark/eval', 'Safety/security', 'Memory', 'Planning/reasoning', 'Tool use', 'RL training', 'Software/coding', 'GUI/web/computer use']
names = {'Multi-agent': 'Multi-agent', 'Benchmark/eval': 'Evaluation, benchmarks', 'Safety/security': 'Safety, security', 'Memory': 'Memory',
         'Planning/reasoning': 'Planning, reasoning', 'Tool use': 'Tool use', 'RL training': 'Reinforcement learning', 'Software/coding': 'Software, coding', 'GUI/web/computer use': 'GUI, Web, computer use'}
print('% Table VIII rows')
for k in order: print(names[k], '&', ' & '.join(cell(T[k][y]) for y in ['2023', '2024', '2025', '2026']), '\\\\')
