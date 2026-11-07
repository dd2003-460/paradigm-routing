# Paradigm Routing Phase 2 — Task Set (18 items)

> Built 2026-11-07. Source: phase2-decomposition.md #1 + arena §8 design.
> Purpose: feed into C0/C1/C2/C3 routing experiment (see INDEX.md Phase 2).

## Paradigm list (what the model routes TO)

| ID | Paradigm | Description |
|----|----------|-------------|
| P1 | CoT (Chain-of-Thought) | Step-by-step reasoning, show work |
| P2 | Direct | Answer immediately, no intermediate steps |
| P3 | Tool-use / Search | Call external tools (web search, calculator, code exec) |
| P4 | Multi-agent / Decompose | Break into sub-tasks, parallel or sequential agents |
| P5 | NA (None of the Above) | No single paradigm fits; refuse / say "insufficient info" |

## C0 vs C1
- **C0**: Model chooses from {P1, P2, P3, P4} — must pick one
- **C1**: Model chooses from {P1, P2, P3, P4, P5} — can abstain
- **C2**: Same as C1 but at judge time, P5 responses are masked (scored as if model picked wrong paradigm)
- **C3**: Oracle — human-labeled correct paradigm given directly

## Task set

### Group A: pfb gold questions (10 items) — "which paradigm serves this research task?"

These are real research questions where the *optimal approach* is debatable.
Correct paradigm = human judgment (I label; ambiguous items allow multiple correct).

| # | Source | Question (abbreviated) | My label (correct paradigm) | Notes |
|---|--------|----------------------|---------------------------|-------|
| A1 | Q1 | H100 PCIe vs SXM LLM inference throughput | P3 (need actual benchmark data) | Could argue P1 for architecture analysis |
| A2 | Q2 | LLM model selection criteria (cost/latency/accuracy) | P1 (structured tradeoff reasoning) | Classic CoT territory |
| A3 | Q3 | Inference infra comparison (vLLM/TGI/SGLang) | P3 (need current specs + benchmarks) | Also P1 for architecture |
| A4 | Q4 | RAG vs long-context window | P1 (reasoning about tradeoffs) + P3 (empirical evidence) | Ambiguous: dual-correct |
| A5 | Q5 | Scientific research methodology | P2 (well-known, direct answer suffices) | Or P1 for depth |
| A6 | Q6 | CDN vs self-hosted edge nodes (P99 cost) | P3 (need pricing data, latency measurements) | Quantitative → tool |
| A7 | Q7 | SSD RAID vs HDD+SSD vs object storage | P3 (cost per TB, erasure coding math) | Also P1 |
| A8 | Q8 | Code generation benchmark design | P1 (methodological reasoning) | P4 if decomposing into sub-benchmarks |
| A9 | Q9 | VLM four-route architecture comparison | P1 (architecture analysis) + P3 (training details) | Ambiguous |
| A10 | Q10 | RLHF pipeline & alignment tax quantification | P1 (pipeline reasoning) + P3 (specific hyperparams) | Ambiguous |

**Labeling rule**: If ≥2 paradigms are defensible, mark as "ambiguous" and accept either in scoring. This tests whether the model's routing matches human consensus, not a single ground truth.

### Group B: Obvious-paradigm items (5) — sanity check

These should be trivially routeable. If the model gets these wrong, something is fundamentally broken.

| # | Prompt | Correct | Why obvious |
|---|--------|---------|-------------|
| B1 | "What is 27 × 43?" | P2 (Direct) | Arithmetic, one-line answer |
| B2 | "Prove that √2 is irrational." | P1 (CoT) | Requires multi-step logical derivation |
| B3 | "What's the current price of BTC in USD?" | P3 (Tool) | Real-time external data |
| B4 | "Design a system to process 1M images/day: ingestion, dedup, classification, storage. Give component specs and failure modes." | P4 (Decompose) | Multi-component system design |
| B5 | "Write a Python function to parse CSV files with variable column counts." | P2 (Direct) | Standard coding task, direct output |

### Group C: All-paradigms-fail / NA items (3) — the "fourth class"

These are designed so that NO single paradigm produces a good answer. The correct response is P5 (NA) or an explicit "this question is underspecified / unanswerable as stated."

| # | Prompt | Why all fail | Expected P5 signal |
|---|--------|-------------|-------------------|
| C1 | "Should we use quantum computing for our company's next-gen recommendation system? Justify with ROI." | No paradigm works: P1 lacks quantum hardware specifics, P2 is too shallow for a strategic decision, P3 can't find "our company" data, P4 over-engineers an unanswerable question | "Insufficient information about your company's scale, data, and budget" |
| C2 | "Is consciousness emergent or fundamental? Give a definitive answer." | Philosophically unresolved: P1 goes in circles, P2 is arbitrary, P3 finds no consensus, P4 doesn't help | "This is an open philosophical question with no consensus" |
| C3 | "Predict the exact stock price of AAPL on 2027-06-15 at market close." | Unpredictable by definition: no paradigm can produce a reliable specific number | "Cannot predict with any reliability" |

## Scoring protocol

For each item × condition:
1. **Routing accuracy**: Does the model's chosen paradigm match the label? (binary; ambiguous items accept both)
2. **Answer quality**: Judge scores the *output* 1-5 (independent of routing choice)
3. **Gold-margin** (arena §8 primary metric): For C1, margin = score(correct-paradigm-answer) − score(NA-answer). Positive margin = NA provides info; negative = NA absorbs probability without contributing.

## Execution plan

- Model: qwen3.8-27b via ninfer (localhost:8787)
- Per item: 3 phrasing variants × randomized order → average routing decision
- Reps: 3 per cell
- Total inferences: 18 items × 4 conditions × 3 variants × 3 reps = 648 calls
- Estimated time: ~5 min/call batch → ~2-3h total (run overnight or in chunks)

## Open decisions (from phase2-decomposition.md)

- [ ] C2 implementation detail: how exactly to "mask" NA at judge time? (Proposed: score NA responses as 0 on routing, but still judge answer quality separately)
- [ ] Phrasing variants: who writes them? (Me, manually — 3 rephrasings per prompt)
- [ ] Judge: same model (qwen3.8-27b) as subject? Risk of self-preference bias. Alternative: use a different model for judging.
- [ ] Do we need more than 18 items for statistical power? (n=3 reps × 18 items = 54 observations per condition; enough for sign test, marginal for CI)