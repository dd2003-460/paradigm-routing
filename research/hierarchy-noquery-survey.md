# 分层结构与无 query recall — 文献调研

> origin: ai · 2026-11-07 · 触发：成璐要求"轮次/段落分层结构 + 无 query recall 先调研"
> 本地覆盖检查：lit-survey-arena.md 仅 1 处提及 hierarchical partitioning（候选项选择场景）；proactive/salience detection 零覆盖 → 确认为缺口，本次外查。

## TL;DR

1. **分层结构对 recall 有效，但机制是"内容对齐"不是"token 锚点"**——placebo-controlled ablation（2610.10170）用乱序 heading path 当安慰剂，真实结构仍显著胜出，说明起作用的是结构携带的语义信息，不只是边界 token 本身。这跟我们 v4 的"labeled boundary"发现一致且互补：标签之所以有效，是因为它压缩了段内语义。
2. **多轮衰减有机制解释了**（2605.12922 "When Attention Closes"）：goal-defining token 的 attention channel 随轮次关闭，但 residual stream 里目标信息可能还在——不同架构失败模式不同（有的 attention 归零行为还在，有的 residual 可解码但行为已崩）。我们 turn-recall 在 4.7k token 没看到衰减，跟这篇"start strong then gradually degrade"的曲线吻合——衰减在更远处才露出来。
3. **role token 是结构性边界但不是语义边界**（2505.00626 "Illusion of Role Separation"）：fine-tuned 模型区分角色靠两个 proxy——任务类型 + 靠近文本开头的位置，不是真的理解 role token 语义。所以 chat template 的 user/assistant 标记是"带弱标签的边界"，介于我们 v4 的 `## Topic`（强标签）和 `[SEP]`（无标签）之间。
4. **无 query 主动觉察：学界基本空白**。找到的 inconsistency detection 工作（SIFiD、Absinth、SUMMAC 等）全是"给了 query/任务后判断一致性"，没有一篇做"不给任何提示、埋在长文中间、看模型自发提取"。我们的 proactive-detection 实验如果做成论文，这个 gap 是真实的。

## 论文清单

### A. 分层结构 × recall/retrieval

| ID | 标题 | arXiv | 核心发现 | 与我们实验的关系 |
|----|------|-------|---------|----------------|
| A1 | Does Document Structure Help Dense Retrieval? A Placebo-Controlled Ablation | 2610.10170 | 4 种结构处理（structure-aligned chunking / LLM-generated context / heading-path metadata / two-stage retrieval）统一协议对比 + 乱序 placebo。真实 heading path 胜 placebo（+0.010/+0.016 cov-nDCG@10），证明是内容不是 token 噪声。naive two-stage 反而伤检索。 | 直接支持 v4 结论：labeled boundary 有效因为标签携带语义。placebo 设计比我们 S2/S3 对照更严格（我们是裸分隔符，他们是乱序真标签） |
| A2 | Document Structure in Long Document Transformers | EACL 2024 (doi:10.18653/v1/2024.eacl-long.64) | section header / paragraph 层级元素对 long-doc transformer 的影响 | 早期工作，确认层级结构被模型利用 |
| A3 | Beyond Chunking: Discourse-Aware Hierarchical Retrieval for Long Doc QA | ACL 2026 (2506.06313) | discourse structure-aware 层次检索 > flat/heuristic chunking，long-doc QA | RAG 侧证据，跟 A1 同方向 |
| A4 | DeepRead: Document Structure-Aware Reasoning for Agentic Search | 2602.05014 | 结构感知推理增强 agentic search | 应用层，确认结构→导航效率 |

### B. 多轮衰减机制

| ID | 标题 | arXiv | 核心发现 | 与我们实验的关系 |
|----|------|-------|---------|----------------|
| B1 | When Attention Closes: How LLMs Lose the Thread in Multi-Turn Interaction | 2605.12922 | Goal Accessibility Ratio (GAR)：生成 token 对 goal-defining token 的 attention 随轮次下降。因果消融：force-close attention channel → Mistral recall 从近满分崩到 11%。不同架构失败模式不同（residual 存活 vs 全崩），编码出现层 2-27 不等 | 我们 turn-recall 4.7k token 无衰减 = 衰减曲线起点之前。下一步推 16k-32k 应该能看到 GAR 下降对应的行为退化 |
| B2 | Role-aware Heuristic Episodic Attention (REA) | 2610.00958 (注：arXiv 标注为误提交，实际是 2512.06869 新版本) | 三种失败模式：attention pollution / dilution / drift。Instructional Memory（全局约束专用 prefix）+ Episodic Memory（用户输入保留、模型回复压缩）+ heuristic retrieval（raw/compressed/omit 三档）。Long-MT-Bench+ judge score 6.32→7.36（+16.5%），latency -2.91× | 工程解法：按 role 分配不同持久性策略。对我们的 autoresearch 启示：重要事实放"instructional"位置（system/首条），普通对话可压缩 |
| B3 | Self-Recall Thinking (SRT) | 2605.15102 | 非相邻轮依赖追踪。Dependency Construction → self-recall chain → 选择性召回历史轮。无需外部 memory 模块 | 内生方案：让模型自己决定召回哪些轮。跟 B2 的外置管理互补 |

### C. Role token / 轮次边界的表示性质

| ID | 标题 | arXiv | 核心发现 | 与我们实验的关系 |
|----|------|-------|---------|----------------|
| C1 | The Illusion of Role Separation | 2505.00626 | fine-tuned 模型区分角色靠两个 proxy：(1) task type exploitation (2) proximity to begin-of-text。不是真正理解 role token 语义。data augmentation 能改善但不彻底 | 关键：chat template 的 `<\|user\|>` 是"弱标签边界"——有结构信号但语义内容少。在我们 v4 谱系上：`## Topic`（强标签）> role token（弱标签）> `[SEP]`（无标签） |
| C2 | Turn-Based Structural Triggers (TST) | 2601.14340 | 用 dialogue turn position 作为 backdoor 激活条件——证明 turn 位置是模型可利用的结构信号 | 反向证据：turn 边界确实被模型当作结构 cue 使用（否则 backdoor 不会 work） |
| C3 | Role Tokens Are Representationally Invisible | latent affect blog post | role token 在表示空间里几乎不可见 | 跟 C1 一致：role token 更多是训练时的格式信号，推理时不承载语义 |

### D. 无 query 主动觉察（gap 确认）

| ID | 标题 | 来源 | 核心发现 | Gap 分析 |
|----|------|------|---------|---------|
| D1 | SIFiD: Reassess Summary Factual Inconsistency Detection with LLM | ACL KnowLLM 2024 | 给 summary + source，判断是否一致。**需要明确任务指令** | 不是 no-query：任务本身就是"检测不一致" |
| D2 | Absinth: Inconsistency Detection in News Summaries | LREC 2024 | 同上，德语新闻摘要 | 同上 |
| D3 | SUMMAC: NLI-based Inconsistency Detection | TACL 2022 | NLI 模型判断 summary 是否被 source 支持 | 同上 |
| D4 | Self-Contradictory Hallucinations of LLMs | ICLR 2024 | 检测模型输出中的自相矛盾 | 检测对象是模型自己的输出，不是输入文档 |
| D5 | Positional Bias of Faithfulness for Long-form Summarization | 2410.23609 | 长文摘要的 positional bias：中间内容 faithfulness 低 | 最接近：说明模型读长文时中间部分"没读进去"，但仍是 query-based（给摘要任务后评估 faithfulness） |

**Gap 结论**：所有 inconsistency detection 工作都是 task-directed（"请检测 X"）或 output-directed（检测模型自己的输出）。没有一篇做 input-directed + no-query（"埋在输入里、不给提示、看模型是否自发提及"）。我们的 proactive-detection 实验填的就是这个空。

### E. 记忆系统里的轮次分段（工程侧）

| ID | 标题 | 来源 | 做法 |
|----|------|------|------|
| E1 | Bounded Conversational Memory (Hybrid Retrieval + Evidence Highlighting) | SIGDIAL 2026 | 连续轮次分组为 topically coherent segments，dual-index（keyword + semantic） |
| E2 | TSIM: Temporal-Semantic Interleaved Memory Reconstruction | EMNLP 2026 | turn stream → coherent episodes 分段 + index |
| E3 | MemORAI: Adaptive Graph Intelligence for Conversational Agents | Findings ACL 2026 | 指出 early 系统要么 turn-level 要么 session-level 分段，各有缺陷 |
| E4 | HEMI: Context LLMs (ICLR 2025) | ICLR 2025 | 模拟人脑 episodic memory：segment → store → similarity/recency/temporal-order 三因子召回 |

这些是"怎么帮模型管理记忆"的工程方案，共同假设：**模型天然不按轮次组织记忆，需要外部分段**。这跟 B1 的机制发现（attention 自然衰减）一致，也跟我们 turn-recall 负结果（4.7k 内不需要外部帮助）一致——短距离内模型自己能处理，长距离才需要外部分段。

## 对我们实验链的映射

```
v3/v4 separator (query-based, labeled boundary +20% EN)
    ↕ 机制解释
A1 (placebo: 内容是机制不是 token) + C1 (role token 是弱标签)
    ↓ 推到多轮
B1 (attention closes: 衰减机制) + B2/B3 (工程/内生解法)
    ↓ 推到无 query
D1-D5 (全是 task-directed → gap) + 我们的 proactive-detection (no-query, 2.6/3)
    ↓ 下一步
推长度到 16k-32k 看衰减曲线 + 更隐蔽 hook + 中性任务
```

## 待核验 / 边界

- [待核验] B2 的 arXiv ID：2610.00958 页面标注"This submission was made in error... instead of a new version for arXiv:2512.06869"——正式引用应查 2512.06869
- [待核验] 27B 模型的 context window 上限（我们假设 32k，未验证）——影响"推到 16k-32k"的实验设计
- 追到边界：no-query proactive detection 的 gap 是真的（搜了 8 组关键词、跨 ACL/EMNLP/ICLR/arXiv），但"没人做"≠"没人正在做"——可能有 preprint 未公开。置信度 0.85。
- A1 的 placebo 设计（乱序 heading）比我们的 S2/S3（裸分隔符）更强——他们证明了"结构形式本身不够，得是真语义"，我们证明了"带标签 vs 不带标签有差异"。两者合起来 = 标签必须携带正确语义才有用。