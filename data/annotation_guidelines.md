# Annotation guidelines: validation sample for Paper 1, Sec. IX-B

Files: annotator 1 fills `annotator1_labels.csv`, annotator 2 fills `annotator2_labels.csv`
(the same 300 abstracts, 2024–2026, seed 20261102). Work **independently**; do not open
`validation_sample.csv`, `ai_precheck_labels.csv`, or each other's sheet while labeling.
Put 1 or 0 in `trains_model` and `system_around_model`; use `notes` for doubts.

For each abstract, fill in 1 (yes) or 0 (no):

- **trains_model**: does the paper itself **update model weights**? This covers fine-tuning, SFT, RL,
  RLHF, DPO, GRPO, PPO, post-training, distillation into a model, and LoRA. Count it only if
  training is part of the paper's own method or experiments. Mark 0 if the abstract mentions
  training only as background ("unlike fine-tuning approaches, we…") or as a baseline.
- **system_around_model**: is a substantial part of the contribution **the system around a fixed model**?
  This covers a scaffold, harness, orchestration layer, workflow or pipeline of LLM calls, context
  engineering or management, a multi-agent framework, or an agent architecture whose components
  are prompts, tools and memory rather than new weights. A paper can score 1 on both questions.
  Mark 0 for pure benchmarks, surveys, or position papers that propose no system.

Time per abstract: about 1 minute. When unsure, choose the label that best describes the paper's
**main contribution**, and add a note in an extra `notes` column.

Then run: `python3 scripts/score_annotation.py` (from `literature/`).
