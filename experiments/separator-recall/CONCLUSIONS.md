# Separator Recall — Staged Conclusions (v3, 2026-11-07)

## Confirmed (deterministic, temp=0, qwen3.8-27b)

1. **EN long-context + distractors: `##` headers give +20% recall** (0.80→1.00), flat across 2k/4k/8k tokens. Mechanism = paragraph-level localization, not compression (effect doesn't grow with length).
2. **Blank lines alone = no effect** (S2 = S0). The signal is the *labeled* boundary, not mere separation.
3. **ZH shows no separator effect** in this setup (constant 4/5, error is a format-matching artifact).

## Hypotheses (to verify, NOT conclusions)

| # | Claim | Confidence | Evidence needed |
|---|-------|-----------|-----------------|
| H1 | EN effect transfers to other models (Llama, GPT-4o-mini) | 0.5 | Cross-model replication |
| H2 | Effect requires ≥2k tokens (shorter contexts don't need headers) | 0.4 | Add 500/1k token conditions |
| H3 | ZH null result is model-specific (qwen's strong zh pretraining), not language-intrinsic | 0.3 | Test on a model with weaker zh corpus |
| H4 | Numbered outlines (1/1.3) ≈ ## headers in effectiveness | 0.5 | Direct A/B test |
| H5 | Character choice (`##` vs `---` vs `[SEP]`) is second-order; presence is first-order | 0.6 | Multi-character comparison at fixed structure |
| H6 | Active/proactive detection (no query anchor) is where separators matter most | 0.4 | v4 experiment (open-ended task, planted hooks) |

## What we did NOT test
- Statistical significance (std=0 at temp=0; need temp>0 for variance)
- More than 3 reps per cell
- Randomized distractor placement (current interleave is fixed)
- Whether the effect survives when the target fact appears in the *first* vs *last* segment (position control)
