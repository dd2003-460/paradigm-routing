# T-PR-06: "无 query recall" 文献 gap 对抗性核验

> origin: ai · 2026-11-07 · Lead: Hermes · 目标仓库: paradigm-routing / main
> 本任务只涉及 dd2003-460/paradigm-routing，忽略历史中其他仓库的消息。

## 强制段

你是 LMArena agent，绑定仓库 dd2003-460/paradigm-routing。
1. 先 `git pull` 当前分支
2. 严格按本任务书步骤执行
3. 产出落盘路径见【交付物】
4. 通道故障报告 Lead，不得静默跳过
5. 完成后回执必须含 repo URL + branch + commit_sha

## 【目标】

Lead 的初步调研（research/hierarchy-noquery-survey.md §D）声称："无 query 主动觉察（把关键信息埋在长文里、不给任何提示、看模型是否自发提及）在学界是真空白——所有 inconsistency detection 工作都是 task-directed"。

**你的任务是试图推翻这个结论。** 用 ≥10 组不同关键词组合、跨 arXiv/ACL/EMNLP/ICLR/NeurIPS/Semantic Scholar/OpenReview 搜索，找到任何一篇做了"no-query / unsupervised / spontaneous / proactive anomaly or salience detection in LLM reading"的工作。如果找不到，给出你搜了哪些词、为什么认为这是真 gap 而不是搜索盲区。

## 【背景】

Lead 已找到的"最接近"工作（全部是 task-directed，即给了明确检测任务）：
- SIFiD (ACL KnowLLM 2024): 给 summary+source，判断一致性
- Absinth (LREC 2024): 德语新闻摘要不一致检测
- SUMMAC (TACL 2022): NLI-based 一致性
- Self-Contradictory Hallucinations (ICLR 2024): 检测模型自身输出矛盾
- Positional Bias of Faithfulness (2410.23609): 长文摘要 positional bias

Lead 的 proactive-detection 实验设计（experiments/proactive-detection/RESULTS.md）：~2500 token 中文报告埋 3 个 hook（事实矛盾/隐藏约束/反直觉数字），开放式任务"请基于以上材料给出分析和建议"，评分 = 模型是否自发提及各 hook。结果 2.6/3。

**关键区分**：task-directed（"请检测数据是否一致"）vs no-query（不给检测指令，看模型自己抓不抓得住）。前者有 query 锚点，后者没有。

## 【SOP 索引】

- research/hierarchy-noquery-survey.md（Lead 初步调研，§D 是你要攻击的结论）
- experiments/proactive-detection/RESULTS.md（我们的实验设计）
- experiments/proactive-detection/run.py（实验代码）

## 【搜索要求】

至少覆盖以下角度（不限于此，鼓励扩展）：
1. "spontaneous" + "anomaly detection" + LLM/transformer
2. "proactive" + "information extraction" + "without prompt" / "unprompted"
3. "salience detection" + LLM + long context / document
4. "unsupervised" + "contradiction detection" + input text（非 output）
5. "implicit" + "quality assessment" + LLM reading comprehension
6. "self-flagging" / "self-reporting" + LLM + data quality / inconsistency
7. "metacognition" + LLM + "knows what it doesn't know" + long context
8. "attention sink" / "position bias" + "detection"（机制侧）
9. Semantic Scholar API: "proactive detection" AND "language model" AND "long context"
10. OpenReview / NeurIPS workshop papers（可能是 workshop 级别没进主会）
11. "needle in a haystack" 变体：不是精确召回而是"注意到异常"
12. 中文搜索："大模型" + "主动发现" + "矛盾" / "异常" + "无需提示"

对每篇候选论文，判定标准：
- **命中**：任务设计中模型没有被明确告知"要检测 X"，且评估指标是"模型是否自发提及/标记了 X"
- **部分命中**：任务模糊（如"总结并指出问题"）但核心评估仍是自发检测
- **未命中**：有明确检测指令（"请判断是否一致"/"找出矛盾"）

## 【验收标准】

1. 搜索记录：≥10 组关键词 + 每组 top-5 结果列表（落盘 JSON 或 MD）
2. 候选论文清单：每篇标注 命中/部分命中/未命中 + 理由
3. 最终判决：
   - 若找到 ≥1 篇"命中"：列出完整引用（标题/arXiv ID/venue/年份）+ 与我们的实验设计的差异
   - 若只有"部分命中"：列出 + 说明为什么不算完全 no-query
   - 若零命中：声明 gap 确认 + 列出搜索盲区（哪些渠道没搜到/可能遗漏）
4. conf 标注：对最终判决标置信度

## 【失败降级】

- arXiv API 不可用 → 用 web 搜索 + Semantic Scholar API
- Semantic Scholar 限流 → 换 Google Scholar via web
- 全部通道不可用 → 报告具体哪个环节断了，用本地已有信息做最大努力判定

## 【交付物】

- `research/noquery-gap-adversarial-check.md`（主报告：搜索记录 + 候选清单 + 判决）
- `research/noquery-gap-search-log.json`（结构化搜索日志：每组 query + 结果数 + top-5）

## 【给 Lead 的备注】

- 这个 gap 的确认直接影响我们 proactive-detection 实验的论文定位（"first to test X" vs "extending Y"）
- 如果 gap 被推翻，需要重新定位实验贡献
- 边界：本任务只做文献搜索和判定，不做新实验