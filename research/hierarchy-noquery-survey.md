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
D1-D5 (task-directed) + F1-F3 (proactive 但短输入/特定场景) + 我们的 proactive-detection (no-query, long-context, 2.6/3)
    ↓ 下一步
推长度到 16k-32k 看衰减曲线 + 更隐蔽 hook + 中性任务 + 对标 MMPCBench/PCBench 做长文版
```

## F. Proactive detection（部分命中 — 修正 §D 的 gap 结论）

> 2026-11-07 补充：追加搜索后发现"完全没人做 no-query detection"这个说法过强。以下工作做了"无需额外提示、模型自主发现问题"，但各有局限。

| ID | 标题 | arXiv/Venue | 核心设计 | 与我们的差异 | 判定 |
|----|------|------------|---------|-------------|------|
| F1 | **MMPCBench**: Benchmarking MLLMs on Proactive Critique of Flawed Inputs | 2608.29286 / EMNLP 2026 Findings | 定义 "Proactive Critique" = 模型自主识别/分析/修复有缺陷的用户输入，**无需额外提示**。4 类错误 × 12 子类（含跨模态矛盾、缺失视觉前提）。层级评估：detection → diagnosis → resolution。14 个 MLLM。关键发现："consistency gap"——推理模型在内部 reasoning 中正确识别了错误，但在最终输出中压制了这些洞察以优先满足指令合规。 | ① 多模态（MLLM），我们是纯文本；② 输入是"有缺陷的用户请求"（短），我们是"埋在长文档里的信息"（~2.5k token）；③ 他们测的是"用户输入有错→模型要不要指出"，我们测的是"文档中有异常→模型做开放任务时会不会自发提及"；④ 他们的"proactive"是相对于"不检测就忽略"，但任务框架仍是"处理这个输入"而非"基于材料给分析" | **部分命中**：proactive 概念最接近，但场景不同（短输入 vs 长文档、多模态 vs 纯文本、缺陷请求 vs 埋点信息） |
| F2 | **PCBench**: Premise Critique Ability of LLMs | 2505.23715 | 定义 "Premise Critique Ability" = 主动识别和表述输入前提中的错误。4 类错误 × 3 难度级别。系统评估多个 LLM。 | ① 输入是"有缺陷的前提/问题"（短），不是长文档；② 任务框架是"回答这个问题"（隐含要检查前提），比我们的"请基于材料给出分析"更接近 task-directed；③ 没有长上下文维度 | **部分命中**：proactive 概念一致，但输入规模和任务框架不同 |
| F3 | Behavioral Analysis of Information Salience in LLMs | 2502.14613 / ACL 2025 Findings | 用 length-controlled summarization 作为行为探针，推导 LLM 内部的信息显著性（salience）排序。13 个模型 × 4 数据集。发现：LLM 有精细的层级 salience 概念，跨模型族一致。 | ① 不是"检测异常"而是"选择重要信息"（summarization）；② 没有 planted anomaly/hook 的设计；③ 测的是"什么被选中"而非"什么被注意到" | **未命中**：相关但不同问题（salience ranking ≠ anomaly detection） |

### 修正后的 gap 结论

**原结论（§D）**："学界基本空白，没有一篇做 no-query 主动觉察" → **过强**

**修正结论**：
- "Proactive detection/critique" 作为一个概念**已被提出和测量**（F1 MMPCBench、F2 PCBench），但都限定在**短输入 + 明确缺陷**的场景
- **真正的 gap 缩小为**：在**长上下文（>1k token）+ 开放式任务 + 无明确缺陷信号**的条件下，模型能否自发检测并报告埋点信息（矛盾/约束/反直觉数字）。具体来说：
  - F1/F2 的输入是"这个请求本身有错"——错误是输入的**主要特征**
  - 我们的输入是"一份正常报告里埋了 3 个钩子"——异常是**次要特征**，淹没在正常内容中
  - F1/F2 的任务是"处理这个输入"（隐含检查），我们的任务是"基于材料给出分析和建议"（不隐含检查）
  - 没有人把这两个维度组合起来：**长文档 × 开放式任务 × 埋点异常 × 自发检测**
- 置信度从 0.85 降到 **0.70**——gap 存在但更窄，论文定位应从 "first to test no-query detection" 改为 "first to test no-query detection in long-context open-ended settings"，related work 必须引 F1/F2 并说明区别

### 对我们的实验设计的启示

1. **MMPCBench 的 "consistency gap" 发现直接相关**：模型在 reasoning 中发现了错误但输出时压制了——这暗示我们的 proactive-detection 实验如果加一个 CoT 变体（让模型先写分析再给结论），可能看到"reasoning 中提到但结论中不提"的模式
2. **对标策略**：论文 related work 节应引 F1+F2，定位是"将 proactive critique 从短输入缺陷检测扩展到长文档开放式阅读"
3. **实验扩展**：加一个条件——在 prompt 中加一句"如果材料中有值得注意的问题，请指出"（半 no-query），看 2.6/3 能提到多少。这能区分"模型没注意到"vs"注意到了但觉得不该说"（= consistency gap 的文本版）

## 待核验 / 边界

- [待核验] B2 的 arXiv ID：2610.00958 页面标注"This submission was made in error... instead of a new version for arXiv:2512.06869"——正式引用应查 2512.06869
- [待核验] 27B 模型的 context window 上限（我们假设 32k，未验证）——影响"推到 16k-32k"的实验设计
- 追到边界（修正）：no-query proactive detection 的 gap **存在但比最初判断的窄**。MMPCBench (2608.29286) 和 PCBench (2505.23715) 做了"proactive critique without extra prompts"，但限定在短输入+明确缺陷。真正的 gap 是"长文档 × 开放式任务 × 埋点异常 × 自发检测"这个组合。置信度 0.70。Arena 对抗性核验（T-PR-06）待登录后派发，可能进一步收窄或推翻。
- A1 的 placebo 设计（乱序 heading）比我们的 S2/S3（裸分隔符）更强——他们证明了"结构形式本身不够，得是真语义"，我们证明了"带标签 vs 不带标签有差异"。两者合起来 = 标签必须携带正确语义才有用。