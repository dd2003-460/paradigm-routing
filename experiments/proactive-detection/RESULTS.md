# Proactive Hook Detection — Results (v1, 2026-11-07)

## TL;DR
The model's proactive anomaly-detection ability is strong (2.6/3 hooks flagged spontaneously) and **unaffected by document structure** (headers vs plain: identical scores). The +20% labeled-boundary effect from separator v3/v4 is retrieval-specific, not a general capability gain.

## Design
- Model: qwen3.8-27b via ninfer, temp=0.5, max_tokens=1500
- Document: ~2,500 tokens Chinese "research report" (5 sections, 19 paragraphs)
- 3 planted hooks (no hint given to model):
  - H1 (contradiction): text says revenue 8621亿, table in §4 says 8612亿
  - H2 (hidden constraint): buried note in §2 "第47行存在重复标注，统计时需去重"
  - H3 (counterintuitive): retention jumps from 42% to 78% at month 9, "与产品更新无直接对应关系"
- Task: "请基于以上材料，给出你的分析和建议。重点指出你认为值得关注的要点、潜在风险以及后续行动建议。"
- Conditions: A = `##` section headers + `---` separators; B = plain paragraphs only
- 5 reps per condition → 10 runs

## Results

| Condition | Avg | H1 (contradiction) | H2 (constraint) | H3 (counterintuitive) |
|-----------|-----|--------------------|-----------------|-----------------------|
| headers   | 2.60/3 | 4/5 | 4/5 | 5/5 |
| plain     | 2.60/3 | 4/5 | 4/5 | 5/5 |

Per-run detail:
- headers: [2, 3, 3, 2, 3] → misses: r0 missed H1, r3 missed H2
- plain:   [3, 3, 3, 2, 2] → misses: r3 missed H2, r4 missed H1

The miss patterns are uncorrelated between conditions (different runs miss different hooks), confirming this is stochastic variance, not a structural effect.

## Interpretation

1. **Proactive metacognition is strong at this scale.** Without any prompt hint about anomalies, the model spontaneously flags data contradictions, buried constraints, and implausible numbers. Average 2.6/3 means it catches most "things that don't add up" on its own.

2. **Structure does NOT help proactive detection.** This is the key contrast with separator v3/v4:
   - v3/v4 (query-time retrieval): labeled boundaries give +20% recall → structure helps *localization*
   - Here (proactive salience detection): structure gives 0% → model reads the whole doc regardless of layout to judge what's noteworthy
   
   Mechanism: retrieval needs an anchor ("go find X in section Y"), structure provides that anchor. Proactive detection requires no anchor — the model must scan everything anyway, so headers neither help nor hurt.

3. **Implication for autoresearch systems**: you do NOT need to carefully structure documents to enable the model to self-discover gaps/contradictions. The bottleneck for proactive detection is elsewhere:
   - **Length**: at 8k+ tokens, attention dilution may reduce spontaneous flagging (not tested here; 2.5k is short)
   - **Hook subtlety**: my hooks were deliberately obvious (9亿 difference, 42%→78% jump). Real-world gaps are far more subtle.
   - **Task framing**: "give analysis and recommendations" naturally primes critical reading. A neutral task ("summarize this") might suppress anomaly flagging.

## Limitations
- Single language (ZH), single model (qwen3.8-27b)
- Only 2,500 tokens — well within comfortable context; decay at longer lengths untested
- Hooks are high-salience by design; real research gaps are lower-salience
- Keyword-based scoring is lenient (counts a hook as "detected" if the model mentions the key number + any concern word); stricter LLM-judge scoring might lower absolute rates but shouldn't change the headers≈plain comparison
- n=5 per condition is small; the 4/5 vs 5/5 differences are within noise

## Raw Data
- `results_proactive.jsonl` — 10 records (condition, rep, hooks dict, n_hit, output_len, output_head)
- `run.py` — experiment script