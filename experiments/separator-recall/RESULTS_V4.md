# Separator v4 — Multi-character Head-to-Head (2026-11-07)

## TL;DR
The "character choice is second-order" hypothesis is **refuted** for English. The first-order variable is not separator *presence* but whether the boundary carries a **topic label**. Labeled boundaries (`##`, `###`, numbered lists) → 1.00 recall; unlabeled boundaries (blank line, `[SEP]`) → 0.80, same as no separator. Chinese: flat 0.80 everywhere.

## Setup
- Model: qwen3.8-27b via ninfer (localhost:8787), temp=0
- Task: retrieve 5 target facts from 20-fact document (5 targets + 15 distractors), ~4k tokens
- 6 formatting conditions × 2 langs × 3 reps = 36 cells, 180 inferences total
- Script: `run_v4.py`; raw data: `results_v4.jsonl`

## Results

| Cond | Format | EN mean acc | ZH mean acc |
|------|--------|-------------|-------------|
| S0 | single newline (no structure) | 0.800 | 0.800 |
| S1 | `## Topic` headers + `---` | **1.000** | 0.800 |
| S2 | blank lines only | 0.800 | 0.800 |
| S3 | `[SEP]` token | 0.800 | 0.800 |
| S4 | `### Topic` headers | **1.000** | 0.800 |
| S5 | numbered list `1. 2. 3.` | **1.000** | 0.800 |

All std = 0 (temp=0, deterministic).

## Order analysis

| Lang | Δ_presence (best sep − S0) | Δ_character (best sep − worst sep) | ratio | Verdict |
|------|---------------------------|------------------------------------|-------|---------|
| en   | +0.20                     | +0.20                              | 1.00  | char effect NOT negligible |
| zh   | +0.00                     | +0.00                              | n/a   | no first-order effect |

## Interpretation

1. **First-order variable = labeled boundary, not presence.**
   - Labeled: `## Topic`, `### Topic`, `1.` → all give 1.00 EN
   - Unlabeled: blank line, `[SEP]`, plain newline → all give 0.80 EN (= baseline)
   - The model needs to know *what* a new segment is about, not just *that* a new segment starts. This matches SepLLM's mechanism: segment information gets compressed into the separator token — but compression requires the separator to be an anchor that can carry a label.

2. **This refines (not contradicts) the "presence > character" claim from lit-survey.**
   The literature said "has separator vs not" matters and "which character" doesn't. Our result says the real split is "labeled vs unlabeled boundary". Within the labeled class, character choice (`##` vs `###` vs `1.`) IS second-order (all 1.00). So:
   - First order: does the boundary carry a topic label? (+0.20 EN)
   - Second order: which label syntax? (~0 within labeled class)

3. **Chinese null result (again).** All six conditions flat at 0.80. Consistent with v3. Hypothesis H3 (model-specific, not language-intrinsic) still open — would need a different model to test.

## Limitations
- Single model (qwen3.8-27b), single length (4k), n=3 reps, temp=0 (no variance)
- Only 5 target facts; the EN error pattern is always the same one fact (quantum coherence distractor)
- `[SEP]` may be uninformative specifically because it's rare in qwen's pretraining corpus (vs markdown which is heavily represented) — this confounds "unlabeled" with "unfamiliar token"

## Next steps (if pursued)
- Add a "labeled but unfamiliar" condition (e.g. `@@@ Topic`) to separate label-semantics from token-familiarity
- Cross-model replication (Llama/GPT-4o-mini) for the EN labeled-boundary effect
- ZH: test on a model with weaker zh pretraining to check H3
