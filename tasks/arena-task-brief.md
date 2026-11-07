# Arena 调研任务书: Paradigm Routing "None of the Above"

> 目标仓库: paradigm-routing (本地 /Users/a1-6/Desktop/workspace/paradigm-routing/)
> 派发日期: 2026-11-07
> 状态: PENDING — 等 arena 会话确认

## 任务目标

核验以下问题，产出结构化调研笔记（写入 research/lit-survey-arena.md）：

### Q1: TRICE / CISC / latent strategies 到底覆盖了什么？
- 具体 arXiv 编号、作者、核心方法
- 它们是否包含"拒绝所有候选范式"的通道？
- 和我们的 NA-routing 差多远？（如果已覆盖 → 我们的 idea 需要重新定位）

### Q2: Select-then-Solve (arXiv 2604.06753) self-routing 崩溃细节
- 哪些模型崩了？崩到什么程度（选错率、分布偏斜）？
- 他们的 router 是 embedding-based 需训练——零训练 self-routing + NA 选项有没有人试过？
- 他们的 benchmark 是什么（GAIA/HumanEval/...），和"真实科研任务"差多少？

### Q3: 范式级弃权（abstention at paradigm level）有没有先例？
- 搜索关键词: "paradigm abstention", "strategy rejection LLM", "reasoning paradigm calibration", "none of the above reasoning strategy"
- 如果有 → 记录做了什么、没做什么
- 如果没有 → 确认这是空白

### Q4: 小模型（≤30B）上 routing 的可行性证据
- 有没有 ≤30B 模型成功做 self-routing 的案例？
- 失败案例的 failure mode 是什么（过度选择单一范式？随机？）
- 多问法取平均（ensemble over phrasings）在 routing 场景有没有人做过？

### Q5: 机制层面
- 加入 NA 选项后 attention pattern 预期怎么变？（结合 SepLLM / Attention Sinks 的 catch-tag-release）
- 有没有人测过"选项数量"对 MCQ 路由准确率的影响？

## 验收标准

- [ ] 每个 Q 有 ≥2 个独立来源（arXiv + 至少一个非 arXiv 源或代码库）
- [ ] 矛盾答案记录矛盾点
- [ ] 最终判断：我们的 idea 是"真空白"还是"已有工作换个说法"
- [ ] 如果是真空白 → 最小可执行实验设计建议
- [ ] 产出文件: research/lit-survey-arena.md（含来源 URL + 置信度标注）

## 边界

- 不跑实验，只做文献+代码调研
- 重点看 2025-2026 的工作（这个方向迭代很快）
- 关注 GitHub 上有没有开源的 paradigm router 实现