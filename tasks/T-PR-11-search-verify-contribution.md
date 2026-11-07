# T-PR-11: 信息搜集 × 校验 贡献函数——RL 侧合成目标现状 + pfb prompt 层离散版的定位

**状态**: dispatched → arena（2026-11-07）
**分支**: `arena/62fe3fd4-paradigm-routing`（与 T-PR-09/T-PR-10 同会话，接续执行）
**产出路径**: `research/search-verify-contribution-function.md` + `research/search-log-sv-contribution.json`

## 意图锚点（成璐微信调研结论，2026-11-07）

> "没有一个把'搜集质量 × 校验质量'合成一个可优化的贡献函数——全是单侧的。这正是我们的空档：pfb 的贡献独立性测量（每个组件 Δ 落到哪个 metric 维度）其实就是这个贡献函数的离散版，只是别人在 RL 梯度里做（不可分解），我们在 prompt 层做（可消融）。"

本任务把这个判断从"滚雪球印象"变成有判决的文献结论：**学界到底有没有人真的合成了这个函数？如果有，形式是什么、为什么没流行？如果没有，最接近的合成尝试卡在哪一步？**

## 背景（本地已有，勿重复搜）

- `pfb/lit-survey/2026-11-07-idea-list.md` #27：3 轮 arXiv 23 篇去重，结论"不存在，且被明确宣布为开放问题"（Proof-Carrying Cognition 2609.09776: binding constraint = verification gap）。
- 已知单侧组件清单（本轮要逐个核对其"是否偷偷做了合成"）：
  - SearchGym (2601.14615) — 环境保真度
  - Beyond Outcome Rewards (2608.12764) — 步级 credit assignment
  - GroundedPRM (2510.14942) — 树引导过程奖励
  - UnifiedPlayers (2609.20089) — planner×verifier 联合适应
  - MARCH (2603.24579) — 多智能体强化自检
- pfb 侧事实：stage-ablation 已实测 S8 质询循环的贡献分散模式（M1+0.237 / M4−0.240 / O6 0.783，n=3 复现），即"每个 prompt 组件 Δ 落到哪个 metric 维度"是可测的。

## 子问题

### Q1: 合成目标的直接搜索

- 搜索组合：(search/retrieval quality) × (verification/reward) joint objective / unified reward；retrieval-augmented generation + process reward model + joint training；agentic search RL with verification reward shaping。
- 判据：reward 函数里是否**同时**出现 (a) 对"搜了什么/搜得好不好"的项 和 (b) 对"校验/质疑命中真实错误"的项，且两者在同一优化目标里联合优化（而非两阶段先后训）。
- 两阶段的算不算？如果"先训 searcher 再训 verifier"或"verifier 给 searcher 当 reward"（单向依赖），记为**伪合成**，单独归类并说明缺了哪一侧。

### Q2: 最接近的 5 个候选逐个拆解

对每个候选给出：目标函数原文（抄录公式或伪代码）→ 搜集侧项存在吗 → 校验侧项存在吗 → 是乘积/加权和/嵌套还是只有一侧 → 判决（合成/伪合成/单侧）。候选至少含上面 5 个，外加搜索新发现的 ≤3 个。

### Q3: 为什么没合成——结构性障碍还是没人试

- 假说 A（reward 污染）：搜集质量难定义 ground truth（搜得多≠搜得好），所以没人敢把它写进 reward。找证据：有没有论文明确讨论过这个障碍后放弃？
- 假说 B（credit assignment 难度）：步级归因（Beyond Outcome Rewards 类）还没解决，合成更不可能。
- 假说 C（其实有人试了但失败了/效果差）：找负面结果。
- 三个假说各找 ≥1 条文献证据支持或反驳，允许"证据不足"判决。

### Q4: pfb 离散版的精确定位（写作用）

- pfb 的贡献独立性测量 vs RL 联合目标：写出两者的对应关系表（prompt 组件 ↔ reward 项；metric 维度 Δ ↔ 梯度方向；消融 ↔ 反事实信用分配）。
- 找出 pfb 版本的一个**具体优势**（可消融/可解释/无训练成本）和一个**具体劣势**（粒度粗/不能端到端优化），各配一句依据。这段文字将直接用于对外材料。

## 验收标准

- AC1: ≥150 行 markdown
- AC2: ≥8 个来源，其中 ≥4 个读到公式/实验表级别（不是 abstract-only）
- AC3: Q1 有明确判决句："合成目标存在 / 不存在 / 只有伪合成 N 例"
- AC4: Q2 的 5+ 候选逐条拆解表（目标函数原文 + 两侧存在性 + 判决）
- AC5: Q3 三假说各有判决 + 证据引用
- AC6: Q4 对应关系表 + 优劣势各一条（可直接引用的成文段落）
- 检索通道：arXiv API 为主 + proceedings 直访；禁止纯记忆引用；每条来源记 URL + 访问日期 + read/abstract-only。