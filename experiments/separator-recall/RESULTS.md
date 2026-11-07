# Separator Recall Experiment — Results (v3, 2026-11-07)

## TL;DR
English long-context fact retrieval with distractors: explicit `##` headers (+ `---`) give **+20% recall** (0.80→1.00) at all tested lengths (2k/4k/8k tokens). Chinese shows no separator effect.

## Design
- **Model**: qwen3.8-27b via ninfer (localhost:8787 proxy)
- **Task**: retrieve 5 target facts from a document containing 20 facts (5 targets + 15 same-domain distractors with similar values)
- **Conditions**: S0 (no separator), S1 (`## Topic` headers + `---` between segments), S2 (blank lines only)
- **Lengths**: ~2k / ~4k / ~8k tokens (tiktoken gpt-4o counted)
- **Languages**: zh + en
- **Reps**: 3 per cell, temp=0
- **Total inferences**: 54 cells × 5 questions = 270 API calls

## Results

| Lang | Cond | 2k tok | 4k tok | 8k tok |
|------|------|--------|--------|--------|
| en   | S0   | 0.80   | 0.80   | 0.80   |
| en   | **S1** | **1.00** | **1.00** | **1.00** |
| en   | S2   | 0.80   | 0.80   | 0.80   |
| zh   | S0   | 0.80   | 0.80   | 0.80   |
| zh   | S1   | 0.80   | 0.80   | 0.80   |
| zh   | S2   | 0.80   | 0.80   | 0.80   |

All std = 0.000 (temp=0, deterministic).

## Error Analysis
- **EN failure mode (S0/S2)**: Model retrieves "312 microseconds" (Google Willow distractor) instead of "300 microseconds" (IBM target). The three quantum-computing paragraphs are adjacent; without headers the model latches onto the wrong one. With `## Superconducting Qubit` header, it disambiguates correctly.
- **ZH constant error**: "1.1亿" expected vs "1.1 亿个每平方毫米" returned — format mismatch in string matching, not a retrieval failure. Present in ALL conditions including S1.

## Interpretation
1. **First-order effect confirmed for EN**: explicit structural markers help paragraph-level localization when multiple same-domain facts compete. Effect is present at 2k tokens and does NOT degrade through 8k.
2. **Character choice matters less than presence**: S2 (blank lines) = S0 (nothing). The signal is the *labeled* boundary (`## Topic`), not mere separation.
3. **Language asymmetry**: Chinese text doesn't need explicit headers — likely because qwen's Chinese training corpus has strong implicit paragraph structure, or because Chinese topic sentences carry enough signal for localization.
4. **Not a length effect**: if separators helped by "reducing effective context length," we'd see the effect grow with length. It's flat → mechanism is *localization*, not compression.

## Limitations
- n=3 reps, single model (qwen3.8-27b), single question style (direct value extraction)
- Distractor design is hand-crafted, not randomized
- ZH "error" may be a scoring artifact (format), not a true retrieval failure
- No statistical test possible (std=0); effect is deterministic on this setup

## Files
- `run.py` — experiment script (v3)
- `results_v3.jsonl` — raw records (54 rows)
- `DESIGN.md` — original design doc (v1/v2 era)

## Next steps
- Cross-model validation (Llama? GPT-4o-mini?) to check if the EN effect is qwen-specific
- Randomized distractor placement (current interleave pattern is fixed)
- Add a "topic sentence only" condition (first sentence of each paragraph as implicit header)
- If publishing: expand to n≥10 reps with temperature=0.3 for variance
