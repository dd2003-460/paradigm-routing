# origin: ai — 范式路由 Phase 2 任务分解

> 状态：decomp 完成，待执行（依赖本地 27B vLLM ✅ 已确认在线）
> 依据：INDEX.md §实验设计 + arena lit-survey-arena.md §8

## 正交子项

| # | 子项 | 预估时间 | 依赖 |
|---|------|---------|------|
| 1 | 任务集构造：10-20 题真实科研子任务 + 标注"正确范式/全不适用" | 2h 人工 | 无 |
| 2 | prompt 模板：4 条件（C0/C1/C2/C3）× 3 措辞变体 | 1h | #1 |
| 3 | 推理脚本：调 vLLM API，收集 routing decision + answer + logprobs | 2h | #2 |
| 4 | 判分：routing 准确率 + answer 质量（judge 27B temp=0）+ gold-margin | 1h | #3 |
| 5 | 统计分析：配对检验 + 预注册判决规则应用 | 1h | #4 |
| 6 | 落盘：results.jsonl + summary.md + 图表 | 1h | #5 |
| 7 | social 包装：README 更新 + 一段话结论 | 0.5h | #6 |

总计 ≈ 8-9h 纯执行（不含等模型响应），可拆成 2-3 个 session。

## 关键决策点

1. **任务从哪来**：pfb gold questions（已有 30 题 GPU 硬件调研）太窄；D1 项目的科研子任务更合适但需要筛选。最小可行：从 pfb 取 10 题 + 手工加 5 题"明显该用某范式"的 + 3 题"全范式都答不好"的困难题。
2. **"正确范式"怎么标**：每题人工判断"如果我是专家我会用什么方法"，标注为 Direct/CoT/ReAct/Plan-Execute/Reflection/NA。有歧义的题标"多范式均可"（routing 对其中任何一个都算对）。
3. **C2 (NA-masked) 怎么做**：模型看到 NA 选项做 routing，但 judge 评分时不知道 NA 存在 → 控制"NA 让模型不敢答"的 confound。实现：routing prompt 含 NA，answer prompt 不含 NA（两阶段）。
4. **logprobs 要不要**：vLLM 支持 `return_logprobs`，可以拿 top-k token 概率做校准分析。Phase 2 先不拿（减少复杂度），Phase 3 再加。

## 执行顺序

```
#1 任务集 → #2 prompt → #3 推理 → #4 判分 → #5 统计 → #6 落盘 → #7 social
         ↑ 可并行 ↑
```

#1 和 #2 可以并行（prompt 模板不依赖具体题目内容）。

## 风险 & 回退

- **27B routing 能力太弱**（全选一个范式）→ 不是 bug 是 finding，报告为 negative result
- **NA 假阳性率 > 50%**（模型动不动就说"都不适用"）→ 同上，negative result 仍有价值（证明小模型无法可靠弃权）
- **vLLM 中途挂掉** → 脚本加 checkpoint（每 10 题存一次中间结果）
- **判官偏差**（同族 27B 判自己的输出偏 lenient）→ 标注"仅相对有效"，后续 hetero-judge 补

## 验收标准

- [ ] ≥15 题 × 4 条件 × 3 reps = 180 次推理完成
- [ ] results.jsonl 含每题每条件的 routing decision + answer + score
- [ ] summary.md 含主指标表 + 预注册判决规则应用结果
- [ ] commit + push to main