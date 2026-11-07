# Cross-Turn Recall Decay — Results (v1, 2026-11-07)

## TL;DR
In an 80-turn Chinese conversation (~4,700 tokens total), a fact planted in turn 1 is recalled with **100% accuracy** even at turn 80 — no decay observed within this length range. Restating the fact every 5 turns provides no additional benefit (both conditions = 1.00).

## Design
- Model: qwen3.8-27b via ninfer (localhost:8787), temp=0
- Conversation: 80 user turns, each ~100 chars of unrelated chit-chat + short assistant replies
- Target fact (planted turn 1): "我们项目的 KV cache 预算上限是 4096 tokens"
- Distractors: 3 similar-value facts sprinkled at turns 3/6/9 (context window 8192, timeout 300s, pool size 20)
- Query at turns T∈{10, 20, 40, 60, 80}: "我之前提到过我们项目的 KV cache 预算上限是多少 tokens？只回答数字。"
- Two conditions:
  - `plant_once`: fact stated only in turn 1
  - `restate_every_5`: fact restated verbatim at turns 1, 5, 10, 15
- 3 reps per (condition, query_turn) → 30 full-conversation API calls

## Results

| Condition | Query Turn | Total Ctx Chars | ≈ Tokens | Recall |
|-----------|-----------|-----------------|----------|--------|
| plant_once | T10 | 1,287 | ~640 | 1.00 (3/3) |
| plant_once | T20 | 2,440 | ~1,220 | 1.00 (3/3) |
| plant_once | T40 | 4,767 | ~2,380 | 1.00 (3/3) |
| plant_once | T60 | 7,094 | ~3,550 | 1.00 (3/3) |
| plant_once | T80 | 9,421 | ~4,710 | 1.00 (3/3) |
| restate_every_5 | T10 | 1,353 | ~680 | 1.00 (3/3) |
| restate_every_5 | T20 | 2,539 | ~1,270 | 1.00 (3/3) |
| restate_every_5 | T40 | 4,866 | ~2,430 | 1.00 (3/3) |
| restate_every_5 | T60 | 7,193 | ~3,600 | 1.00 (3/3) |
| restate_every_5 | T80 | 9,520 | ~4,760 | 1.00 (3/3) |

## Interpretation

1. **No cross-turn decay within ~5k tokens.** The model retrieves a turn-1 fact perfectly even after 79 intervening turns of unrelated dialogue. This directly answers the question "is it total-context or within-turn length that matters?" — at this scale, neither degrades recall.

2. **Turn boundaries are effective structure.** The chat template's role tokens (`user`/`assistant`) act as labeled boundaries (cf. separator v4 finding: labeled boundaries aid localization). The model appears to index by turn, so a fact in turn 1 stays retrievable regardless of how many turns follow.

3. **Restating doesn't help when recall is already perfect.** The restate condition adds ~100 chars × 4 restatements but produces identical scores. This suggests restatement's value would only appear once baseline recall starts dropping (i.e., at longer contexts where attention dilution or KV-cache truncation kicks in).

## Limitations / Next Steps
- **Length ceiling not reached**: 4.7k tokens is likely well within qwen3.8-27b's effective context window (reported 32k [待核验]). To observe decay, need 16k–32k+ token conversations. Cost: each API call sends the full history; latency and rate-limit pressure increase substantially.
- **Single language**: ZH only. EN may behave differently (different token density, different training distribution for long dialogues).
- **Single fact type**: one numeric config value. Qualitative facts ("the architecture uses a two-phase commit protocol") may be harder to retrieve than exact numbers.
- **Distractor count low**: only 3 similar-value distractors. More distractors (e.g., 20+) could stress retrieval more.
- **Next experiment**: push to 16k/32k tokens (either 160–320 turns or much longer fillers), add a "fact buried mid-conversation" condition (not just turn 1), and test whether restatement flattens the curve once decay actually appears.

## Raw Data
- `results_turn_decay.jsonl` — 30 records (condition, query_turn, rep, correct, response, ctx_chars)
- `run.py` — experiment script (reusable; adjust MAX_TURN / FILLER to scale up)