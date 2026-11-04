# Data and scripts for "From Prompted Reasoners to Autonomous Agents" (survey)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23936708.svg)](https://doi.org/10.5281/zenodo.23936708)

Supporting data for the survey *From Prompted Reasoners to Autonomous Agents: A Survey of the
Evolution of LLM-Based Agents, 2022–2026* (H. Mohasel Arjomandi, preprint, November 2026).
Harvest date: November 1, 2026. Submission window: January 1, 2022 – October 31, 2026.

This repository contains the arXiv harvest, the screening sheet, the keyword rules and scripts
that produce every count, interval, and test in Section IX, the 300-abstract validation sample
with its annotation sheets, and the bibliography checks.

## Contents

| Path | What it is | Used in the paper |
|---|---|---|
| `data/harvest_config.json` | The five arXiv queries (Q1–Q5), date window, title rule | §II-A |
| `data/harvest.json` | All 12,804 unique harvested records (id, title, date, abstract, matched queries, agent-title flag) | §II-A, Fig. 1, §IX |
| `data/screening.csv` | The same records as a screening sheet | §II-A |
| `data/harvest_summary.json` | Per-query, unique, and quarterly counts | §II-A, Fig. 1 |
| `data/bibliometrics.json`, `bibliometrics_stdout.txt` | Output of `bibliometrics.py`: corpus counts (n = 6,965), theme and internalization shares with Wilson 95% intervals, vocabulary-sensitivity variants, two-proportion tests, Holm and Benjamini–Hochberg corrections, term adoption | §II-D, Tables VII–VIII, Fig. 6, §IX |
| `data/validation_sample.csv` | Random 300 corpus abstracts from 2024–2026 (seed 20261102) with the output of the two abstract rules | §II-D, §IX-B |
| `data/annotation_guidelines.md` | Labeling instructions for the validation sample | §IX-B |
| `data/annotator1_labels.csv`, `annotator2_labels.csv` | Blind labeling sheets for two independent annotators | §IX-B |
| `data/ai_precheck_labels.csv` | **Preliminary** labels produced with an AI assistant (see below) | §II-D, §IX-B (preliminary figures) |
| `data/arxiv_id_check.tsv` | Title and first-author check of every arXiv reference | §II-B |
| `data/coverage_gaps.tsv` | Works cited by the 18 compared surveys but not by this one, with how many surveys cite each | §II-C |
| `scripts/harvest.py` | Reproducible arXiv harvest (`python3 scripts/harvest.py data/harvest_config.json <out_dir>`) | §II-A |
| `scripts/bibliometrics.py` | Recomputes the corpus, Tables VII–VIII, all tests, and redraws the validation sample | §II, §IX |
| `scripts/make_tables.py` | Prints the LaTeX rows of Tables VII–VIII from `bibliometrics.json` | Tables VII–VIII |
| `scripts/score_annotation.py` | Cohen's kappa between annotators and precision/recall/F1 of each rule against the reference labels | §IX-B |
| `scripts/verify_arxiv_ids.py` | Checks arXiv IDs in a BibTeX file against arxiv.org | §II-B |
| `scripts/coverage_gap.py` | Builds `coverage_gaps.tsv` from the compared surveys' reference lists (Semantic Scholar / arXiv HTML) | §II-C |

## Reproduce the numbers

The scripts use only the Python standard library. Run them from `data/`:

```bash
cd data
python3 ../scripts/bibliometrics.py      # writes bibliometrics.json and validation_sample.csv
python3 ../scripts/make_tables.py        # LaTeX rows of Tables VII–VIII
python3 ../scripts/score_annotation.py   # after both annotator sheets are filled
```

`bibliometrics.py` reproduces the archived `bibliometrics.json` and `validation_sample.csv`
exactly. A fresh harvest with `harvest.py` will differ slightly, because arXiv metadata changes
over time; use the archived `harvest.json` to reproduce the paper's numbers.

## Annotation status and limitations

- The validation figures in the current preprint (precision and recall of the two abstract rules)
  are **preliminary**. They come from `ai_precheck_labels.csv`, which was labeled with the help of
  an AI assistant and is **not** a human annotation. The two blind sheets
  (`annotator1_labels.csv`, `annotator2_labels.csv`) are released empty for independent labeling;
  this repository will be updated with the human labels, Cohen's kappa, and the scores from
  `score_annotation.py`.
- The keyword rules are listed at the top of `bibliometrics.py` and in the paper. They measure how
  papers describe themselves, not what they do; §IX-B discusses what this means for the scaffold rule.
- arXiv over-represents academic work relative to industrial systems.
- `coverage_gaps.tsv` reflects the reference lists available on November 1–2, 2026.

## Citation

Archived on Zenodo: [10.5281/zenodo.23936708](https://doi.org/10.5281/zenodo.23936708) (all versions; v1.0 is
[10.5281/zenodo.23936709](https://doi.org/10.5281/zenodo.23936709)).

## Licence

Data (`data/`): CC BY 4.0. Scripts (`scripts/`): MIT. arXiv titles and abstracts are reproduced
from the arXiv API metadata.
