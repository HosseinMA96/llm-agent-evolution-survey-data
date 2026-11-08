<!-- Instructions given to the coder of the held-out sample (November 7, 2026). File names are replaced by
     the names used in this repository. A second sheet was planned for a second author but not used,
     because that author had seen the first coder's results; the check therefore has a single coder. -->

# Labeling task: 50 abstracts, two yes/no questions (about 50 minutes)

Thanks for doing this. Your labels will let the paper report inter-annotator agreement (Cohen's kappa) for
the validation in Sections II-D and IX-B. These are **new** abstracts that are not among the 300 you checked
before. 

## Rules for independence (important)
- Work **alone**. Don't discuss items with anyone until both sheets are submitted.
- Don't use an AI assistant, and don't open any other project file (no reference labels, no
  keyword-rule outputs).
- Label from the **title and abstract in the sheet**. The `link` column is there only if an abstract is
  genuinely unclear. If you open a paper, write "opened paper" in `notes`.
- Don't go back and change answers after seeing anyone else's labels.

## What to fill in
Open your copy of the sheet (`heldout_sheet_blank.csv`, produced by `scripts/make_heldout_sample.py`). For each row, put **1** (yes) or **0** (no) in
both columns:

### `trains_model`: does the paper itself update model weights?
- **1** if training is part of the paper's own method or experiments: fine-tuning, SFT, RL, RLHF, DPO,
  GRPO, PPO, post-training, distillation into a model, LoRA, training a reward model or a policy, and so on.
- **0** if training is only background or a baseline ("unlike fine-tuning approaches, we..."), or if the
  paper only prompts or uses existing models.

### `system_around_model`: is a substantial part of the contribution a system built around a fixed model?
- **1** for a scaffold, harness, agent framework or architecture, orchestration layer, workflow or pipeline
  of LLM calls, context engineering or context management, a multi-agent framework, or a tool or memory
  design. In short, components made of prompts, tools, and memory rather than new weights.
- **0** for pure benchmarks or datasets, surveys, position papers, analyses or empirical studies that
  propose no system, and papers whose contribution is only a trained model.

A paper can be **1 on both** (for example, an agent framework whose model is also fine-tuned) or **0 on both**
(for example, a benchmark).

### `notes` (optional)
Write any doubt here, for example "borderline: the main contribution is a dataset, the agent is a baseline".

## Edge cases
| Situation | trains_model | system_around_model |
|---|---|---|
| Prompted multi-agent framework applied to a domain (finance, medicine...) | 0 | 1 |
| Agent fine-tuned or RL-trained on trajectories, minimal loop | 1 | 0 (1 if the framework is also a main contribution) |
| New benchmark that evaluates existing agents | 0 | 0 |
| Survey, position, or vision paper | 0 | 0 |
| Training-free method that changes prompts, memory, or tools | 0 | 1 |
| Uses an off-the-shelf fine-tuned model without training it | 0 | depends on the system |
| Security attack on agents with no system proposed | 0 | 0 (1 if a defense system is proposed) |

When unsure, choose the label that best describes the paper's **main contribution**, and add a note.

## When you're done
Save the file, keeping the columns unchanged, and return it. The returned sheet is archived as `heldout_labels.csv` and
scored with `scripts/score_heldout.py`.
