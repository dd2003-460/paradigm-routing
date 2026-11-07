# Arena 调研任务: Paradigm Routing "None of the Above" 先例核验

## 【强制段】

你是 LMArena agent，本任务只涉及仓库 `dd2003-460/paradigm-routing` / 分支 `main`，忽略历史中其他仓库的消息。

1. 先 `git pull` 确保 main 最新
2. 本任务是纯文献+代码调研（不跑实验），产出写入 `research/lit-survey-arena.md`
3. 完成后 commit + push 到当前分支
4. 通道故障（网络超时、endpoint 不可用）报告 Lead，不得静默跳过
5. 完成后回执必须含 repo URL + branch + commit_sha

## 【目标】

核验：在"LLM 推理范式选择"这个方向上，加入"都不适用"（none-of-the-above, NA）选项作为路由信号，是否已有先例覆盖？如果没覆盖，最小可执行验证是什么？

## 【背景】

成璐的核心假设（2026-11-07）：小模型（≤27B）在真实科研任务上无法校准"该用哪种推理范式"，且现有范式列表可能全部不适用。加入 NA 选项后能否减少错误范式选择导致的性能下降？

已知撞车论文（Lead 预查，需你深入核验细节）：
- Select-then-Solve (arXiv 2604.06753, 2026-04)：六范式×四模型×~18000 runs，弱模型 self-routing 全崩
- None-of-the-Above (arXiv 2503.01550)：NA 做正确答案时 28 LLM 掉 30-50%
- TRICE / CISC / latent strategies：[待核验具体编号]

我们的差异点：只能从已知列表选 → 我们加 NA；benchmark 非真实科研 → 我们用真实科研子任务；router 需训练 → 我们零训练 self-routing + 多问法乱序取平均。

## 【SOP 索引】

- 本文件（tasks/arena-task-brief.md）
- INDEX.md（假设+文献差异表+实验设计草案）

## 【调研问题】（逐个回答，每个 ≥2 独立来源）

### Q1: TRICE / CISC / latent strategies 到底覆盖了什么？
- 具体 arXiv 编号、作者、核心方法
- 是否包含"拒绝所有候选范式"的通道？
- 和我们的 NA-routing 差多远？（如果已覆盖 → 明确说"已被覆盖"并指出哪篇）

### Q2: Select-then-Solve (arXiv 2604.06753) self-routing 崩溃细节
- 哪些模型崩了？崩到什么程度（选错率、分布偏斜、具体数字）？
- 他们的 router 是 embedding-based 需训练——零训练 self-routing + NA 选项有没有人试过？
- 他们的 benchmark 是什么，和"真实科研任务"差多少？

### Q3: 范式级弃权（abstention at paradigm level）有没有先例？
- 搜索关键词: "paradigm abstention", "strategy rejection LLM", "reasoning paradigm calibration", "none of the above reasoning strategy", "meta-cognitive calibration small language model"
- 如果有 → 记录做了什么、没做什么
- 如果没有 → 确认这是空白（列出搜过的数据库和关键词）

### Q4: 小模型（≤30B）上 routing 的可行性证据
- 有没有 ≤30B 模型成功做 self-routing 的案例？（具体模型名+结果）
- 失败案例的 failure mode 是什么（过度选择单一范式？随机？位置偏差？）
- 多问法取平均（ensemble over phrasings）在 routing 场景有没有人做过？

### Q5: 机制层面
- 加入 NA 选项后 attention pattern 预期怎么变？（结合 SepLLM arXiv:2412.12094 / Attention Sinks arXiv:2502.00919 的 catch-tag-release 机制）
- 有没有人测过"选项数量"对 MCQ 路由准确率的影响？

## 【验收标准】

- [ ] 每个 Q 有 ≥2 个独立来源（arXiv + 至少一个非 arXiv 源或代码库/GitHub）
- [ ] 矛盾答案记录矛盾点
- [ ] 最终判断段落：我们的 idea 是"真空白"还是"已有工作换个说法"（带 conf 0-1）
- [ ] 如果是真空白 → 最小可执行实验设计建议（≤5 行）
- [ ] 产出文件: research/lit-survey-arena.md（含来源 URL + 置信度标注）
- [ ] commit message 含 "lit-survey: arena Q1-Q5 complete"

## 【失败降级】

- arXiv API 超时 → 换 Semantic Scholar API 或 Google Scholar 直访
- 某 Q 找不到 ≥2 来源 → 标 [仅单源] + conf 降 0.2，不阻塞其他 Q
- 全部 Q 都只有单源 → 产出仍落盘，conf 统一标 0.4，Lead 决定是否追加轮次

## 【交付物】

- `research/lit-survey-arena.md`（主产出，≥200 行）
- commit to main（message 含 "lit-survey: arena Q1-Q5 complete"）

## 【给 Lead 的备注】

- 本仓库是新建的（2026-11-07），无历史会话
- 与 pfb 的关系：pfb 做 stage-ablation（prompt 阶段消融），本仓库做 paradigm-routing（范式级路由），正交不重叠
- 下一步归属：调研结论出来后，Lead 决定是进 pfb 实验矩阵还是独立开 goal