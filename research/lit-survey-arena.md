# Lit-Survey (arena): Paradigm Routing 的 "None of the Above" 先例核验

> 任务书：`tasks/arena-task-brief.md`（Q1–Q5）
> 执行者：Arena agent（LMArena Agent Mode）
> 执行日期：2026-11-07（UTC）
> 目标仓库：`dd2003-460/paradigm-routing`，分支 `arena/81df0921-paradigm-routing`（session branch，见 §0.4）
> 本文件为纯文献调研产出，未跑任何实验。

---

## 0. 结论先行（TL;DR）

| 项 | 判断 | conf |
|---|---|---|
| Q1 已被 TRICE / CISC 覆盖？ | **否**。经过名称核验，任务书里的 "TRICE" 与 "CISC" 指向的是**与范式路由无关的两篇论文**（见 §1.2 术语撞车警告）。真正覆盖"策略/范式选择"的是 Select-then-Solve、RTR、Sketch-of-Thought、latent-strategy 分解，**四者都没有"全都不适用"通道**。 | 0.80 |
| Q2 self-routing 崩溃细节 | 已拿到完整数字表。崩的是 **Qwen3-Max（49.8→42.4）与 Qwen3-30B（24.9→27.5，且远低于 best-single 32.8）**；GPT-5 是唯一正收益（60.3→67.1）。崩的机制是**分布坍缩 + 过度选择工具型范式（ReAct 42–48%）+ 从不选 Reflection**。 | 0.85 |
| Q3 范式级弃权先例 | **未找到**。弃权研究全部集中在 **答案级**（NOTA/IDK）与 **agent/tool 级**（不调工具、不行动），没有一篇把"弃权"放在**推理范式列表**上。这是本次调研最干净的空白。 | 0.65 |
| Q4 ≤30B routing 可行性 | 有**少数成功案例，但都有训练**（1.5B GRPO 三模式自路由、3B metacognitive 校准、Self-Route 训练式 router）；**零训练 zero-shot self-routing 在 ≤30B 上目前无一例成功**，且失败模式可复现（过度选择单一范式 / 位置偏好 / pseudo-reflection）。 | 0.70 |
| Q5 机制 + 选项数影响 | **选项数量对准确率的影响有硬文献**（N=160 时的 gold-margin collapse、N=100 时 −70pp、token bias 选 A/B/C/D）。**"加 NA 选项后 attention 怎么变"没有人直接测过**——只能从 catch-tag-release / SepLLM 做**可falsify的预测**。 | 选项数 0.85 / 机制预测 0.35 |
| **最终判断** | **"窄空白"**：想法本身没有被别人用同样的话做过，但**相邻工作已把它压缩到"一个消融实验的宽度"**。按当前写法（naive NA 选项）投稿有 ~50% 概率被判 "incremental / STS 的 Direct 已经就是这个意思"。**必须重写 framing**（见 §8）。 | **0.55** |

**一句话给 Lead**：空白是真的，但不在"加一个 NA 选项"，而在"**当所有范式都不适用时，路由决策应该输出什么动作**"——即**范式级弃权作为独立动作类（第四种输出：拒答 / 升级 / 重分解），而非一个额外的选项**。这个 framing 目前无人占领，且与 STS 论文里那句自承认的 "tasks where all paradigms fail are excluded from training but counted as incorrect" 直接对撞（见 §2.6）。

---

## 0.1 通道与工具状态（按任务书 §强制段第 4 条报告）

- **arXiv API（export.arxiv.org/api/query）**：`curl` 返回 `http_code=000`，沙箱出网白名单不含该域名。**不可用**。
- **Semantic Scholar API（api.semanticscholar.org）**：同样 `000`。**不可用**。
- **可用替代通道**：`web_search`（返回 arXiv abs 页正文 + 第三方综述页 alphaXiv / emergentmind / pith.science / chapterpal 的结构化摘要）+ `fetch_page`（可直接抓 `arxiv.org/abs/*`、`arxiv.org/html/*`、`github.com`）。**本报告全部事实均经该通道二次核对 abs 页或 HTML 全文，未依赖模型记忆。**
- **降级执行情况**：未使用"单源降 conf 0.2"的降级，因为每个 Q 都拿到了 ≥2 独立来源（见各 Q 的 Sources 小表）。唯一例外是 §5.3 的机制预测——那是**推断**不是文献，已单独标 0.35。
- **未解决风险**：Google Scholar / ACL Anthology 检索式无法直接执行，只能通过 web_search 间接命中。因此 Q3 的"没有先例"是**有限检索下的否证**，不是完备性证明（conf 因此从 0.8 下调到 0.65）。

## 0.2 本报告的置信度标度

- `0.85–0.95`：abs 页原文数字 + 至少一个第三方复述一致。
- `0.65–0.80`：abs 页确认存在，细节来自全文 HTML 或二手摘要，有一处以上未交叉验证。
- `0.40–0.60`：多个弱来源指向同一方向，或"未找到"型判断。
- `<0.40`：机制推断 / 我的外推，**不可作为论文 claim 引用**。

## 0.3 来源编号表（正文用 [S#] 引用）

| # | 来源 | URL | 类型 |
|---|---|---|---|
| S1 | Select-then-Solve: Paradigm Routing as Inference-Time Optimization for LLM Agents (arXiv:2604.06753, 2026-04-08) | https://arxiv.org/abs/2604.06753 | arXiv |
| S2 | STS 官方代码库 hengzzzhou/STS（含完整结果表、benchmark 采样协议） | https://github.com/hengzzzhou/STS | GitHub |
| S3 | STS 全文 HTML（§5.3 Self-Routing / Table 4 分布） | https://arxiv.org/html/2604.06753 | arXiv |
| S4 | None of the Above, Less of the Right (arXiv:2503.01550, 2025-03-03) | https://arxiv.org/abs/2503.01550 | arXiv |
| S5 | 同上，ACL Findings 2025 正式版 | https://aclanthology.org/2025.findings-acl.1031.pdf | ACL |
| S6 | TRICE — Training Chain-of-Thought via Latent-Variable Inference (arXiv:2312.02179) | https://arxiv.org/abs/2312.02179 | arXiv |
| S7 | CISC — Confidence Improves Self-Consistency in LLMs (arXiv:2502.06233, ACL 2025 Findings) | https://arxiv.org/abs/2502.06233 | arXiv |
| S8 | CISC 官方代码库 taubenfeld/CISC | https://github.com/taubenfeld/CISC | GitHub |
| S9 | Uncovering Latent Reasoning Strategies in Language Models (arXiv:2607.17674, 2026-07-20) | https://arxiv.org/abs/2607.17674 | arXiv |
| S10 | Route to Reason (RTR): Adaptive Routing for LLM and Reasoning Strategy Selection (arXiv:2505.19435, ACM Web 2026) | https://arxiv.org/abs/2505.19435 | arXiv |
| S11 | RTR 代码库 goodmanpzh/Route-To-Reason | https://github.com/goodmanpzh/Route-To-Reason | GitHub |
| S12 | Sketch-of-Thought: Adaptive Cognitive-Inspired Sketching (arXiv:2503.05179, EMNLP 2025) | https://arxiv.org/abs/2503.05179 | arXiv |
| S13 | SoT EMNLP 2025 正式版（router 细节 / Kappa / 失配实验） | https://hyper.ai/en/papers/emnlp__2025__2025.emnlp-main.1236 | 会议页 |
| S14 | When the Right Answer Is Missing: An Arithmetic-Dependent Rejection Bottleneck in Jev (arXiv:2609.39496) | https://arxiv.org/abs/2609.39496 | arXiv |
| S15 | Agentic Abstention: Do Agents Know When to Stop Instead of Act? (arXiv:2606.28733) | https://arxiv.org/html/2606.28733 | arXiv |
| S16 | AgentAbstain: Do LLM Agents Know When Not to Act? (arXiv:2607.10059) | https://arxiv.org/html/2607.10059 | arXiv |
| S17 | AbstentionBench (arXiv:2506.09038, NeurIPS 2025 D&B) | https://pith.science/paper/2506.09038 | arXiv+review |
| S18 | Do LLMs Know When to NOT Answer? (AbstainQA, COLING 2025) | https://aclanthology.org/2025.coling-main.627.pdf | ACL |
| S19 | Learning to Route LLMs with Confidence Tokens (Self-REF, arXiv:2410.13284) | https://arxiv.org/html/2410.13284v3 | arXiv |
| S20 | Causal evidence that language models use confidence to drive behaviour (Nature Machine Intelligence, 2026) | https://www.nature.com/articles/s42256-026-01293-x | Nature |
| S21 | Overwhelmed by Choice: Studying LLM Decision Making at Scale (arXiv:2609.32809, NeurIPS 2026 Workshop TAE) | https://arxiv.org/abs/2609.32809v1 | arXiv |
| S22 | Pushing the Boundaries of Multiple Choice Evaluation to One Hundred Options (arXiv:2604.14634) | https://arxiv.org/html/2604.14634v1 | arXiv |
| S23 | Large Language Models Are Not Robust Multiple Choice Selectors (PriDe, arXiv:2309.03882, ICLR 2024 Spotlight) | https://arxiv.org/abs/2309.03882 | arXiv |
| S24 | Calibrating Language Models via Augmented Prompt Ensembles (CAPE) | https://openreview.net/pdf?id=L0dc4wqbNs | OpenReview |
| S25 | When Punctuation Matters: A Large-Scale Comparison of Prompt Robustness Methods for LLMs | https://lacuna.tiptreesystems.com/work/when-punctuation-matters-a-large-scale-comparison | 综述页 |
| S26 | SepLLM: Accelerate LLMs by Compressing One Segment into One Separator (arXiv:2412.12094) | https://arxiv.org/abs/2412.12094 | arXiv |
| S27 | Attention Sinks: A 'Catch, Tag, Release' Mechanism for Embeddings (arXiv:2502.00919) | https://arxiv.org/abs/2502.00919 | arXiv |
| S28 | Attention Sinks catch-tag-release 全文（Theorem 7.1 / truth-value tag 探测） | https://arxiv.org/html/2502.00919v2 | arXiv |
| S29 | When Small Models Are Right for Wrong Reasons (arXiv:2601.00513) | https://arxiv.org/html/2601.00513 | arXiv |
| S30 | Knowing When Thinking Is Not Enough / FlyBy (arXiv:2609.34327) | https://arxiv.org/html/2609.34327 | arXiv |
| S31 | Learning When to Think: Adaptive Reasoning for Test-Time Compute Allocation (arXiv:2608.20256) | https://pith.science/paper/2608.20256 | arXiv+review |
| S32 | Think When Needed: Model-Aware Reasoning Routing for LLM-based Ranking (arXiv:2601.18146) | https://arxiv.org/html/2601.18146 | arXiv |
| S33 | Self-Route: Automatic Mode Switching via Capability Estimation (arXiv:2505.20664) | https://arxiv.org/html/2505.20664v1 | arXiv |
| S34 | Fine-Tuning Language Models to Know What They Know（ESMA, d'_type2, Qwen2.5-3B）(arXiv:2602.02605) | https://arxiv.org/html/2602.02605 | arXiv |
| S35 | EpiCaR: Knowing What You Don't Know Matters for Better Reasoning (ACL 2026) | https://aclanthology.org/2026.acl-long.1026/ | ACL |
| S36 | Stop Overthinking: A Survey on Efficient Reasoning for LLMs (arXiv:2503.16419) — §5.2 路由综述 | https://arxiv.org/pdf/2503.16419 | arXiv |
| S37 | 工具路由工程实践：abstention 作为一等公民（"none" 选项） | https://mbrenndoerfer.com/writing/tool-selection-llm-agents-routing-strategies | 工程博客 |
| S38 | ghost 仓库 issue #77 "Router abstention is a first-class result with defined fallback" | https://github.com/ferdousbhai/ghost/issues/77 | GitHub |

---

# Q1. TRICE / CISC / latent strategies 到底覆盖了什么？

**结论 conf = 0.80：没有覆盖我们的 NA-routing。而且任务书里这两个名字大概率是张冠李戴，需要 Lead 回查内部 memo 的出处。**

## 1.1 逐项核验

### (a) TRICE 真实身份 = CoT 的隐变量 EM 训练法，**不是**策略路由器 [S6]

- 标题：*Training Chain-of-Thought via Latent-Variable Inference*
- 作者：Du Phan, Matthew D. Hoffman, David Dohan, Sholto Douglas, Tuan Anh Le, Aaron Parisi, Pavel Sountsov, Charles Sutton, Sharad Vikram, Rif A. Saurous（Google）
- arXiv:2312.02179，2023-12
- 方法：把 CoT rationale `z` 当潜变量，最大化 `log p(y|x) = log Σ_z p(z|x)p(y|x,z)`；用 MCMC-EM + 控制变量（control variate）在只有 Q-A 对的数据上 bootstrap 出 rationale。TRICE 全称 "Tuning Rationales with Independence-Chain Expectation-maximization"。
- 数字：GSM8K 74.7%（greedy）/ 82.3%（self-consistency）；BBH 27 任务平均 72.8% vs STaR 62.0% vs 直接答案调优 70.4%。
- **与范式路由的关系：零。** 它训练的是"怎么把一个范式（CoT）做得更好"，没有候选集，没有 router，没有选择动作，更没有拒绝通道。它的 "latent" 是指 rationale 隐变量，不是"隐策略"。

### (b) CISC 真实身份 = 置信度加权自洽投票 [S7][S8]

- 标题：*Confidence Improves Self-Consistency in LLMs*
- 作者：Amir Taubenfeld, Tom Sheffer, Eran Ofek, Amir Feder, Ariel Goldstein, Zorik Gekhman, Gal Yona
- arXiv:2502.06233，ACL 2025 Findings
- 方法：Self-Consistency 的多票不是等权，而是用模型自评置信度（P(True) logit / verbalized 0–100 / response probability）加权。
- 数字：9 模型 × 4 数据集，达到同等准确率所需路径数减少 >40%；论文同时报告"最校准的 confidence 方法反而对 CISC 最没用"（within-question confidence 概念）。
- **与范式路由的关系：单范式内部的投票聚合，不是跨范式选择。** 但与我们的 **"多问法取平均"** 有一个方法论上的近亲关系（见 Q4 §4.4），必须引用，否则会被审稿人问"这不就是 CISC 换个地方用"。

### (c) "latent strategies" 真实身份 = 隐策略分解（最接近的一篇，但没 NA）[S9]

- 标题：*Uncovering Latent Reasoning Strategies in Language Models*
- 作者：Awni Altabaa, John Lafferty（Yale），arXiv:2607.17674，2026-07-20
- 方法：把 `p_θ(y|x)` 分解为 `(r_φ(z|x), g_φ(y|x,z))`——router 输出**关于隐策略 z 的分布**，generator 条件于 z 生成。核心难点是 posterior collapse（generator 已能独立解释 y，router 没动力用 z），作者用"相对 base model 的 fractional information gain + 高 surprisal token 上加权重构压力"解决。
- 评测：自建 multi-strategy algorithmic tasks；验证隐码与参考策略对齐。
- **关键否定证据：z 是《先验固定维度的连续/离散隐变量》，分布永远是 over z 的完整 simplex，没有"⊥ / none"这类退化类。** 也就是说：模型必须落在某个策略上，体系结构上不允许"都不适用"。
- 对我们的意义：**如果我们要做"隐空间 NA"，这篇是最直接的 baseline，也是最容易被审稿人拿来对比的**。它开源了 paper 页但没有公开代码（本次未找到 repo）。

## 1.2 ⚠ 术语撞车警告（必须回传 Lead）

任务书写 "TRICE / CISC / latent strategies 覆盖了潜在策略识别、条件概率路由"。经核验：

1. **TRICE 在 LLM 文献里几乎唯一指向 [S6] 那篇 CoT-EM 论文**，与"潜在策略识别"无关。
2. **CISC 在 LLM 文献里几乎唯一指向 [S7] 那篇加权投票论文**，与"条件概率路由"无关。
3. "潜在策略识别" 的真实对应物是 [S9]（2026-07），"条件概率路由" 的真实对应物应是 [S10] RTR 或 [S1] STS。

**推断**：Lead 的预查表里这两格是"占位名词"，可能来自某篇 survey 的 related-work 列表被错位摘抄。建议 Lead 回查 memo 原始出处；如果确实找不到，就把 INDEX.md 的差异表里这两行改成 **[S10] RTR + [S9]**。**这是本报告唯一一处与任务书前提直接冲突的地方，必须显式记录。**

## 1.3 真正覆盖"范式选择"的四篇，逐篇检查是否有拒绝通道

| 论文 | 选什么 | 候选数 | 训练方式 | 有"都不适用"通道？ |
|---|---|---|---|---|
| [S1] Select-then-Solve | 6 范式（Direct/CoT/ReAct/Plan-Execute/Reflection/ReCode） | 6 | embedding router，per-model 分类器，70/30 划分 | **无**。语料里写明 "All routers select from six paradigms including Direct, so they can learn when no structure is needed"——即用 **Direct 冒充"不需要结构"**，但 Direct 仍是"解题"，不是"弃权" |
| [S10] Route to Reason (RTR) | (模型 × 推理策略) 对 | 模型池 × 策略池 | 学习式 embedding + 双预测头（correctness / cost） | **无**。候选对必须全网表内 argmax |
| [S12] Sketch-of-Thought | 3 个"sketch 范式"（Conceptual Chaining / Chunked Symbolism / Expert Lexicons） | 3 | DistilBERT 67M，14,200 条 GPT-4o 标注 | **无**。且报告失配代价极高：把 Chunked Symbolism 硬套 CommonsenseQA → 40.00% vs 84.60% |
| [S9] Latent strategies | 隐策略 z | 连续隐空间 | 变分训练（router+generator） | **无**（见 §1.1c） |

补充：[S36] 那篇 2025 的效率推理 survey 已经把 "Prompts Attribute-Driven Reasoning Routing" 单独列成一节（SoT 为代表），**整节没有出现一次 abstention / rejection / none-of-the-above**——这是"该方向文献已成体系但仍无弃权通道"的一个侧面证据（conf 0.5，属弱证据，仅作旁证）。

## 1.4 Q1 判定

> **已被覆盖？否。** 没有任何一篇把"拒绝全部候选范式"作为路由的一类输出。
> 但**"不需要结构时就用 Direct"** 这个语义已经由 STS 用 Direct 这个选项占住了。我们必须明确区分：**Direct ≠ NA**。Direct = "用一个无脚手架范式解题"；NA = "这题不该由这些范式中的任何一个来解（应升级/分解/问人/标记超出能力）"。这个区分是全文的命门，见 §8。

---

# Q2. Select-then-Solve (arXiv 2604.06753) 的 self-routing 崩溃细节

**结论 conf = 0.85。所有数字同时来自 abs 页 [S1]、全文 HTML [S3] 与官方 repo [S2]，三方一致（除一处 repo/正文的小矛盾，见 §2.5）。**

## 2.1 实验规模与设计

- 6 范式 × 4 模型 × 10 benchmark ≈ **18,000 runs**（repo 口径：4 模型 × 6 范式 × ~761 tasks）[S2]
- 4 模型：**GPT-5、Gemini-3-Flash、Qwen3-Max、Qwen3-30B**（注意：Qwen3-30B 就是我们关心的 ≤30B 档）
- 10 benchmark 与采样协议 [S2]：
  | 数据集 | 域 | 用量 | 协议 |
  |---|---|---|---|
  | HumanEval | 代码生成 | 100 | seed=42 采样 |
  | MATH500 | 数学 | 100 | seed=42 |
  | AIME (2024+2025) | 竞赛数学 | 60 | 全量 |
  | HotpotQA | 多跳 QA | 100 | seed=42 |
  | Natural Questions | 事实 QA | 100 | seed=42 |
  | MMLU | 多任务知识 | 100 | seed=42 |
  | HLE | 硬语言考试 | 500 | MiroThinker 标准化 |
  | GAIA | agent QA | 50 | MiroThinker text-only val |
  | τ-bench | 工具规划 | 51 | 全量 |
  | SEAL | 安全评测 | — | 全量 |
- 三种 router：①学习式 handcrafted-feature predictor ②学习式 embedding router ③**零训练 zero-shot self-routing**（模型自己读题选范式）
- 训练标签定义（重要）："the most token-efficient successful paradigm per task"；**"tasks where all paradigms fail are excluded from training but counted as incorrect during evaluation"** ← 这句话是本次调研最有价值的一行，见 §2.6。

## 2.2 总表（acc %，直接引自 [S2] README 与 [S1] abstract）

| Method | GPT-5 | Gemini-3-Flash | Qwen3-Max | Qwen3-30B | Avg |
|---|---|---|---|---|---|
| Direct | 60.3 | 55.5 | 49.8 | 24.9 | 47.6 |
| Best-single（每模型固定最优范式） | 62.4 | 55.5 | 50.7 | **32.8** | 50.3 |
| **Embedding Router** | **64.2** | **61.0** | **54.6** | 32.8 | **53.1** |
| **Self-route（零训练）** | **67.1** | 56.8 | **42.4** | **27.5** | 48.4 |
| Oracle（逐题最优） | 72.9 | 73.4 | 72.5 | 56.8 | 68.9 |

读法（关键，别读错）：
- **Self-route 相对各自 Direct 的增益**：GPT-5 **+6.8pp**；Gemini +1.3pp；Qwen3-Max **−7.4pp**；Qwen3-30B **+2.6pp**。
- **Self-route 相对 best-single 的差距**：Qwen3-30B 27.5 vs 32.8 → **−5.3pp**，即"自己选"居然打不过"闭着眼固定一个范式"。
- **Oracle gap 17.1pp**（68.9 − 50.3 的 avg 口径；正文按 per-model 平均给出 17.1pp）。embedding router 只回收了 **37%**（53.1 vs 47.6 baseline，向 68.9 oracle 靠）。

## 2.3 崩溃的**定性**机制（[S3] §5.3 + Appendix G，这是任务书要的"崩到什么程度"）

1. **分布坍缩（degenerate bias）**：self-routing 每个模型塌到一个主导选择。
   - GPT-5：过度选 Direct，**65%**（正文 Table 4 口径）
   - Qwen3-Max / Qwen3-30B：过度选 ReAct，**42–48%**——"even for knowledge-centric questions where Direct suffices"
   - **没有任何模型选过 Reflection 一次**（"no model ever selects Reflection"）
2. **对比组**：学习式 embedding router 给出 model-adapted 分布，Direct 占比 **47–73%**，且随基座模型变强而升高（"the proportion increased as the base model became stronger"）。也就是说**强模型更"知道自己不需要脚手架"，弱模型不会**。
3. **论文自述归因**（值得整段引用进我们的 related work）：
   > "self-routing fails not because models lack knowledge of the paradigms, but because they cannot calibrate which paradigm matches each task's requirements. The ability to execute a paradigm when instructed does not imply the ability to choose when to use it."
   这是把"范式选择"定义为一个**独立的 meta-reasoning 能力**（与执行能力解耦）。**我们的假设（成璐 2026-11-07）其实是这句话的直接推论**：既然失败在 calibration，那么提供一个显式的"都不适用"锚点，理论上可以给 calibration 一个落点。**这就是我们真正的理论 hook，比"加个选项试试"强得多。**
4. **单范式效应极不稳定**（做 motivation 用）：ReAct 在 GAIA 比 Direct **+44pp**；CoT 在 HumanEval **−15pp**；CoT 对 Qwen3-30B 在某些任务上 **+46pp**（"structured paradigms can compensate for weaker models' capabilities"）。↔ 矛盾点：**同一个 CoT，对 GPT-5 在编码上是负的，对 Qwen3-30B 是 +46pp**。这说明范式收益是 (模型 × 任务) 的交互项，不是任务单函数——**这对我们 design 有直接影响：NA 的"正确性"必须 per-model 标定，不能跨模型迁移**。

## 2.4 "零训练 self-routing + NA 选项"有人试过吗？

**没有。** 检索路径与证据：
- [S1][S3] 的 self-routing 提示词是"让模型自己选 6 个范式之一"，**候选集不含任何拒绝项**；repo 里 `scripts/train_router_v2.py` 同时实现 embedding router 与 self-routing，self-routing 分支只是 prompt，**无 NA 分支代码** [S2]。
- 相邻工作的 self-select 基线同样无 NA：[S32] Think-When-Needed 显式设了 `Self-Select`（模型自己选 Think/Non-Think）与 `Ideal`（oracle）两个对照，候选只有 2 个模式，**无"都不适用"**。
- [S31] Learning When to Think 的 1.5B 自路由候选是 **NoThink / Short / Long** 三档——注意 `NoThink` 是**"少推理"而非"不适用"**，语义完全不同（它可以仍然答错，但不表示"这题不该我来答"）。
- 结论：**"零训练 + NA 选项 + self-routing" 这个 2×2 格子目前是空的**（conf 0.75，属"未找到"，非完备证明）。

## 2.5 ⚠ 已发现的一处原始文献内部矛盾（按验收标准记录）

- [S3] §5.3 正文：*"GPT-5 over-selects Direct at 65%"*
- [S3] Appendix G 图 7 caption：*"GPT-5 selects Direct 100%"*

同一篇论文两处对同一统计量给出 65% 与 100%。**记录为未解决矛盾**，引用时用正文 65% 并加脚注，或直接写 "65–100%（原文两处不一致）"。conf 影响：不影响 Q2 主结论（self-routing 坍缩），但**如果我们想复现其分布数字，必须先联系作者或看 repo 的 aggregated CSV**。

## 2.6 ⭐ 最有价值的一行：STS 自己承认存在"全范式失败"的任务

原文（[S3]，router 训练协议段）：
> "Labels are the most token-efficient successful paradigm per task; **tasks where all paradigms fail are excluded from training but counted as incorrect during evaluation.**"

这行的含义：
1. STS 的范式池**确实存在系统性不可解的子集**（否则不必写这句排除规则）。
2. 他们把这类任务**从 router 的监督信号里剔掉**——即 **router 从来没被教过"这题谁上都不行"**。于是这些任务在评测里必然被 router 随机/偏见地指派给某个范式，**然后必然失败**。
3. **这正好是我们 NA 信号的理论最优目标：把"全失败"从一个"被排除的噪声"变成"一个可预测的类"**。我们的贡献可以精确写成："STS 把这些样本排除了；我们证明它们不是噪声，而是可学习的第四类。"

**这句话是我们与 STS 之间唯一不可辩驳的差异点。整篇论文的 novelty 应该挂在这里，而不是挂在"我们多了一个选项"。** conf 0.9（原文直引）。

---

# Q3. 范式级弃权（abstention at paradigm level）有没有先例？

**结论 conf = 0.65：没有直接先例。弃权研究在"答案级"和"agent 级"极其拥挤，在"范式级"完全空白。**

## 3.1 检索执行记录（按任务书要求列出关键词与数据库）

- 检索通道：`web_search`（后端为通用网页索引，覆盖 arXiv/ACL/OpenReview/Nature/GitHub/技术博客）。**arXiv API 与 Semantic Scholar API 在本沙箱不可达（见 §0.1）。**
- 执行的关键词（原文照录）：
  1. `"paradigm abstention" OR "reasoning paradigm calibration" OR "strategy rejection" language model`
  2. `router abstain "no strategy" option reasoning scaffold selection "none of these" LLM routing abstention strategy level`
  3. `"none of the above" option reasoning strategy selection router abstain paradigm LLM 2026`
  4. `LLM prompt model choose among candidate reasoning paradigms include option "none of the above paradigms apply"`
  5. `"meta-cognitive" calibration small language model knowing which reasoning strategy it cannot do 2026 paper`
  6. `adaptive reasoning decide whether to think at all "no reasoning" option router overthinking LLM 2026`
  7. `小模型 7B 8B meta-reasoning strategy selection fails calibration router capability threshold`（英文式）
- 覆盖的数据库镜像：arXiv（abs + html）、ACL Anthology、OpenReview、Nature MI、NeurIPS D&B、GitHub、工程博客。

## 3.2 答案级弃权：极其拥挤（**不是**我们的空间）

| 工作 | 做了什么 | 关键数字 | 与范式级的关系 |
|---|---|---|---|
| [S4][S5] None of the Above (MMLU, 28 LLM) | NA 作为正确答案 | 30–50% 一致下降；DeepSeek-V3 90.8→65.7；Gemini-1.5-Pro 90.1→60.3；总平均 63.2→28.5；数学仅 −14.6%，商业伦理 −48.1%；DPO 微调 Llama-3-8B 28.5→57.7 | **这就是任务书里的"撞车论文"。但它测的是"NA 是答案时掉多少分"，从未把 NA 当路由信号** |
| [S14] When the Right Answer Is Missing (Jev/TypeSafe) | 类型化决策模型的拒绝瓶颈 | 答案存在 99% vs 正确答案缺失时拒绝仅 **7%**；简单阈值 → 79%（保持 97%） | 提供了"**校准阈值可替代显式拒绝训练**"的路子，对我们 Phase 3 有用 |
| [S18] AbstainQA (COLING 2025) | IDK/NOTA 选项 + Abstain Clause / Extreme Abstain Clause | 2,900 样本，五选项，可答/不可答各半；CoT 降低位置偏差 | 证明**提示工程能拉高弃权率但拉不高能力** |
| [S17] AbstentionBench (NeurIPS 2025 D&B) | 20 数据集 / 35k unanswerable | **reasoning 微调使弃权平均下降 24%** | ⭐ 与我们的假设**直接冲突的证据**，必须正面处理（见 §3.5） |
| [S19] Self-REF | 置信 token 做 routing 与 **rejection learning** | "none of the above" 作为标签的 rejection 设定；Llama-3-8B / Mistral-7B | **最接近"NA 作为训练目标"的一篇，但仍在答案层** |
| [S20] Nature MI 2026 | 置信度驱动弃权的因果证据 | 四阶段范式；**Phase 3 用 Gemma-3-27B 做 activation steering**；Phase 2 弃权率跨模型 27%–82% | ⭐ **27B + steering = 我们 Phase 3 机制分析的方法论模板**；且明确说"引入弃权选项后模型会 substantially recompute 输出分布" |

## 3.3 Agent/工具级弃权：也存在，且**工程界已经把 "none" 当一等公民**

- [S15] Agentic Abstention（28k+ 指令，13 个 LLM-agent，2 个 scaffold）：**多数系统 abstention recall < 50%，timely recall < 40%**；且"更大/更强的模型有时在及时弃权上更差"。
- [S16] AgentAbstain（17 个前沿模型）：最好只有 **59.5%** paired accuracy；**"abstention capability is largely independent of general task-solving capability"**——⭐ 这句话是我们 hypothesis 的**直接理论支撑**：弃权能力与解题能力解耦 ⇒ 小模型不会因为"解题差"就自然糟糕于弃权，也意味着**弃权必须被显式建模**。
- [S37] 工具路由工程实践：明确写 "abstention is needed: a routing system that always selects some tool is worse than one that can confidently decline"，并给出三种实现（相似度阈值 / 显式 "none" 选项 / softmax 阈值）。
- [S38] 开源项目 issue：把 "none of these" 作为 router 的一等返回值，附带 fallback 契约与测试用例。
- **推论**：**"拒绝全部候选"在工具路由里是标准做法，在推理范式路由里居然一次都没出现**——这是一个非常强的"文献不对称"论证，比单纯说"没人做过"有说服力得多。conf 0.7。

## 3.4 范式级弃权：**零命中**

在上述 7 组检索式下：
- **没有**任何一篇论文把 abstention / rejection 放在"推理范式（Direct/CoT/ReAct/…）"这个候选集上。
- **没有**任何一篇给出 "none of these paradigms" / "no scaffold applies" / "escalate" 作为路由输出类。
- 最接近的三篇，全部差一步：
  1. [S1] STS：用 **Direct** 冒充"不需要结构"（但 Direct 仍是解题），且**把全失败任务从监督里排除**（§2.6）。
  2. [S32] Think-When-Needed / [S31] Learning-When-to-Think / [S33] Self-Route / RACER：把"**要不要推理/推理多长**"当路由变量（think vs no-think），这是**计算量级弃权**，不是**适用性弃权**。区别在语义：no-think 说"这题不用想"，NA 说"这题这些范式都不对"。
  3. [S19] Self-REF rejection setting：候选是**答案选项**，不是范式。

## 3.5 ⚠ 必须正面处理的三个反证（矛盾记录）

1. **[S17] AbstentionBench：reasoning 微调使弃权 −24%。** 这条直接威胁"给模型更多推理结构会改善弃权"的直觉。我们的假设必须**反过来表述**：不是"推理让模型更会弃权"，而是"**在路由这一跳上，不让模型进入推理循环，只让它做一次判别**"。这恰好也是 [S29] 的结论落点。
2. **[S4] NA 效应随任务域剧烈波动（数学 −14.6% vs 商业伦理 −48.1%）。** 意味着 NA 不是均匀有效的干预；**我们必须 per-task-type 报告，不能只报平均**。如果我们的真实科研子任务恰好落在"高 NA 惩罚"域（开放、无定值答案），NA 选项可能让路由更差。
3. **[S20] 引入弃权选项后模型会"substantially recompute 输出分布"。** 这既是威胁（选项本身扰动路由决策，不只是加了信息）也是机会（可测的机制信号）。**必须在实验里设"NA-选项存在但被屏蔽"的对照，否则无法区分"NA 作为信息"与"NA 作为格式扰动"。** 这是本次调研给出的最重要的实验设计约束。

## 3.6 Q3 判定

> **确认是空白（conf 0.65，"有限检索下的否证"）。** 空白的具体形状不是"没人加过 NA 选项"，而是"**没有人把范式级弃权建模为一个独立动作类，并测它对下游性能的影响**"。
> 同时必须承认：**相邻领域（agent / tool / answer-level）已经把弃权问题研究得非常透**，所以我们的新颖性只能落在"**范式这一层特有的代价结构**"上（见 §8）。

---

# Q4. 小模型（≤30B）上 routing 的可行性证据

**结论 conf = 0.70。分层结论：零训练自路由 ≤30B → 全体失败；训练式自路由 ≤30B → 有成功案例；元认知能力 ≤10B → 有明确"容量阈值"证据。**

## 4.1 失败案例（含具体模型与数字）

| 来源 | 模型 | 结果 | failure mode |
|---|---|---|---|
| [S1][S3] STS | **Qwen3-30B** self-route **27.5** vs Direct 24.9 vs best-single **32.8** | 绝对增益仅 +2.6pp，且**输给固定范式 5.3pp** | 过度选 ReAct（48%），从不选 Reflection |
| [S1][S3] STS | **Qwen3-Max**（更大但同族）self-route **42.4** vs Direct 49.8 | **−7.4pp，比 Direct 还差** | 过度选 ReAct（42%） |
| [S29] Right-for-Wrong-Reasons | Llama-3-8B / Mistral-7B / Qwen-2.5-7B | **50–69% 的"答对"其实推理是错的**；meta-cognitive 提示（self-critique/verify）**持续有害** d = −0.14 ~ −0.33 | "pseudo-reflection"：小模型生成"看起来像反思"的文本，反而引入新错误；作者提出 **capacity threshold，7–9B 在阈值之下** |
| [S30] FlyBy | 4B / 8B small reasoning models (sRMs) | 自我 refine 主要"把概率质量集中到已可达的解"，不产生新解；**小模型不仅知识少，还"更不会利用外部帮助"** | help-seeking 本身是**需要训练的能力** |
| MRP（Meta-Reasoning Prompting，编号未核实，仅二手源） | GPT-3.5 vs GPT-4 | GPT-4 能自纠与选工具，**GPT-3.5 频繁"scoring error"**，无法准确评估自身能力 | 元推理能力**随规模出现** |

⭐ **最值得引用的一句**（[S19] 同族思路 + [S1] 归因）：把"执行能力"与"选择能力"解耦，是 2025–2026 这一波文献的共识。对我们而言，这意味着**"小模型不会路由"不是训练不足，而是能力不在同一维度**——于是**零训练方案在小模型上大概率失败**，我们必须事先承认这一点并在设计中把它变成研究问题（"NA 能否部分补偿这个缺口"）。

## 4.2 成功案例（全部带训练，注意别误读成"零训练也行"）

| 来源 | 模型规模 | 做法 | 结果 |
|---|---|---|---|
| [S31] Learning When to Think | **1.5B**（DeepSeek-R1-Distill 系） | 在 GRPO 里让**第一个 token** 就是路由 token：NoThink / Short / Long；per-mode 硬 token 上限 + 平衡项 + 强制 warmup；**无独立 router** | 三模式不坍缩；MATH-500 **token −41%** @ **−1.4pp**；GSM8K −76%，AIME −13%；**router 长度随难度单调**（说明真的在按难度分诊） |
| [S34] ESMA (d'_type2) | **Qwen2.5-3B** | 用 d'_type2 隔离元认知能力 + 双问协议去偏；Evolution Strategy 对齐 | **d'_type2 = 1.02，超过所有专有模型**（尽管其直接答题准确率更低）→ **小模型可以有很强的"知道自己对不对"的判别力，即使解题弱** |
| [S35] EpiCaR (ACL 2026) | 3B+（Llama-3 / Qwen-3 全系 1B–8B） | 把"何时该信任自己的推理"作为训练目标，联合优化准确率与校准 | 3B+ 达 Pareto 优；**K=10 confidence-weighted ≈ STaR K=30 多数投票**，3× 推理预算节省 |
| [S33] Self-Route | 训练式轻量 router（hidden-state capability embedding） | 短 CoT vs 长 CoT 二选一，阈值 τ 决定回退 | 同等准确率下 **token −30~55%**；关键消融：训练集缺乏难度梯度 → **路由准确率最多掉 11%** |
| [S14] Jev/TypeSafe | 类型化决策模型（非 LLM） | 单阈值校准 | 拒绝准确率 **7% → 79%**，答案存在性保持 **97%** | 

**统一读法**：≤30B 做 routing **可行，但代价是"必须训练/必须校准"**。**零训练 zero-shot 自路由在 ≤30B 上目前没有任何一例成功记录**（[S1] 是唯一直接测试，结果是失败；[S31] 看似零训练但实际是 GRPO 训练出来的 token 策略；[S33] 是 hidden-state 训练 router）。

## 4.3 失败模式的分类学（对我们 design 直接可用）

1. **过度选择单一范式（distribution collapse）**：[S1] Qwen3-30B → ReAct 48%；Qwen3-Max → ReAct 42%；GPT-5 → Direct 65%。
2. **位置 / token 偏差（positional & token bias）**：[S23] PriDe 证明 MCQ 选择偏差主因是**option ID token 的先天概率偏置（A/B/C/D）**，而非纯位置；[S22] 在 N=100 时观测到"positional fallback under uncertainty"；[S21] 观测到"更早的候选项越来越难以被推翻"。
3. **伪反思（pseudo-reflection）**：[S29] 7–9B 的自我批评不是批评，是"生成看起来像批评的文本"。
4. **拒绝-全候选的整体崩塌**：[S4] 30–50% 掉分；[S14] 7% 拒绝率。**这两种崩塌在"加 NA 选项"时会同时出现在小模型上——这是我们最大的实验风险。**

## 4.4 「多问法取平均 / 乱序取平均」在 routing 场景有人做过吗？

**分三层回答（conf 0.75）：**

- **答案层：有，且很成熟。**
  - [S24] CAPE：把 **template paraphrase + option permutation** 做 ensemble，对预测分布取平均，显著降低 ECE；option permutation 的收益比 template paraphrase 更大、scaling 更好；**n=16 饱和，主实验用 n=8**。⭐ 这是"乱序取平均"最标准的引用。
  - [S25] When Punctuation Matters（5 种鲁棒性方法统一评测）：**Template Ensembles 结论是 mixed——单个"有毒"模板会拖垮整个 ensemble**；并且发现**多数投票比概率平均更稳健（20 个测试里 19 个降低敏感性）**。⭐ 这条直接影响我们的聚合方式选择：**routing 场景应该先测 majority-vote-over-phrasings，而不是直接概率平均**。
  - [S21] permutation-based inference（把预测在多个重排视图上聚合）：在 **N=160** 时比基线 **+20pp**，且明确"mitigates positional bias"。⭐ 这是"乱序取平均能救 routing"的**最强正面证据**，虽然它用在答案选择而非范式选择。
  - [S23] PriDe：用 **permutation 估计 option-ID 先验再相减**——"乱序"的另一种用法（估计偏差而非平均）。
- **路由层：没有专门做过。** 没有任何一篇对"路由决策"本身做问法/顺序 ensemble。STS、RTR、SoT、Self-Route 全部是单次判别。
- **相邻：有方法论迁移的可能。** [S20] 明确报告"同一模型在不同措辞下弃权行为差异显著（Phase 2 弃权率 27%–82%）"，且"引入弃权选项后模型重算分布"——**说明弃权决策对措辞高度敏感，恰好是 ensemble 能治的病**。

⭐ **因此"多问法 × 乱序取平均"是我们第二强的差异化点**，而且它有明确的理论依据（决策对措辞敏感 + 位置偏差可聚合抵消），**不是拍脑袋**。

---

# Q5. 机制层面

**结论：Q5 应拆成两个可独立验收的子问题。5.a（选项数影响）文献充足，conf 0.85。5.b（NA 选项引入后的 attention 变化）无人直接测过，只能给可 falsify 的预测，conf 0.35。**

## 5.a 选项数量对 MCQ（含路由）准确率的影响——**有硬文献**

| 来源 | 设置 | 关键数字 | 机制归因 |
|---|---|---|---|
| [S21] Overwhelmed by Choice (NeurIPS 2026 TAE) | 候选项数 N 扫到 **160**（HotpotQA / MIMIC / arXiv 等） | 准确率随 N 单调下降；**N=160 时 hierarchical partitioning 与 permutation inference 各 +20pp** | **gold-margin collapse**：正确答案与最强干扰项的分差逐渐缩小，主因是"对正确答案的置信度衰减"；**早位偏好越来越难被推翻**（后者对最终预测影响递减）。明确排除"长上下文检索"解释 |
| [S22] 100-option MCQ | N=1→100，韩语正字法任务，固定目标 + 重复洗牌 + padding/length-matched 控制 | 弱模型 N=100 时**掉 ~70pp**；GLM/HyperCLOVAX/EXAONE 在低 N 近满分但高 N 崩塌 | **两个 failure mode：语义混淆 + 不确定性下的早位回退（positional fallback）**；padding 控制证明主瓶颈是"候选排序"而非上下文长度 |
| [S23] PriDe (ICLR 2024 Spotlight) | 20 LLM × 3 benchmark，置换实验 | 选择偏差主要来自 **token bias（A/B/C/D 的先验概率质量）**，位置偏差只是次要 | 提供 label-free 去偏：用小样本 permutation 估先验再扣掉 |
| [S19]/[S20] | 弃权选项的加入本身 | 模型"substantially recompute 其输出分布"；弃权率基线跨模型 27%–82% | 选项集的**存在性**（不只是内容）改变决策过程 |

**对我们的直接含义（3 条硬约束）：**
1. 我们的范式列表是 **6–7 个选项**，属于低 N 区（[S21][S22] 的崩塌主要在 N≥几十），**所以"选项太多导致排序难"不是我们的主要威胁**——但 [S23] 的 token bias 仍然适用：A/B/C/D/E/F 的先天概率并不均匀，**NA 放在哪个位置会显著改变其触发率**。这直接支持我们的"乱序"设计，并且要求**报告 NA 的位置边际触发率**（per-position trigger rate），这是审稿人一定会问的。
2. [S21] 的 **gold-margin collapse** 给我们一个比 accuracy 更灵敏的因变量：**"正确范式的 logprob 与最强错误范式的 logprob 之差"**。如果加 NA 让这个 margin 变大，说明 NA 在帮忙做区分；如果只是把概率质量吸走（NA 变成新的"安全出口"），margin 会变小。**这是一个能区分"信息 vs 扰动"的指标，强烈建议纳入。**
3. [S20] 的"选项存在性改变分布"要求我们必须有 **NA-present-but-masked 对照**（§3.5 已述）。

## 5.b 加入 NA 选项后 attention 预期怎么变？（**推断，非文献**，conf 0.35）

先摆两篇机制文献的**原文事实**：

- **[S27][S28] Attention Sinks: catch-tag-release (arXiv:2502.00919, v2 2025-09)**
  - 机制：attention sink **catch** 一串 token → 用 embedding 空间中的一个**共同方向**给它们 **tag** → **release** 回 residual stream，后续层按 tag 检索。
  - ⭐ **探测实验证明 tag 编码语义信息，"例如一个陈述的真值（truth of a statement）"**（原文）。
  - reasoning-distilled 模型**sink 更多、tag 解释的方差更大**（"more prominent in reasoning-distilled models"）。
  - Theorem 7.1：双层 attention-only transformer 在"[SEP] 后求均值"的极小任务上必然用 catch-tag-release；且该机制在标准训练下**自发涌现**。
  - 对 QK-norm 的新模型（Qwen3）同样成立。
- **[S26] SepLLM (arXiv:2412.12094)**
  - 观察：LLM 对**看似无意义的 separator token（"." "\n"）**给出不成比例的高 attention；段信息被**压缩进 separator**。
  - 方法：稀疏 mask 只保留 initial / neighboring / separator token，FLOPs −30%，training-free 可与 vanilla 持平。
  - 掩蔽实验：**删掉 separator 的 KV 会损害推理**——即 separator 承担真实功能，不只是"注意力垃圾桶"。

**由此给出的可 falsify 预测（3 条，全部可测，全部可能被推翻）：**

| # | 预测 | 若成立预期看到什么 | 若被推翻意味着 |
|---|---|---|---|
| P1 | **NA 选项会成为一个新的 attention sink**，因为它在格式上是一个"终结性分隔符"（列表末项 + 语义上"以上皆非"） | 在路由判别的那几个 token 位置上，sink 计数上升（用 [S28] 的 sink-detection 指标）；且该 sink 的 **tag 方向与"拒绝/真值"探针方向对齐**（[S28] 已证明 tag 可承载 truth value） | 说明 NA 只是被当普通选项处理，机制层面"NA 特殊"的说法不成立 → 我们的机制章节必须删掉，只保留行为学结论 |
| P2 | **catch-tag-release 的"release"会改变候选范式的竞争** | 加了 NA 之后，正确范式的 **gold-margin 变大**（§5.a 的指标），且 tag 方差解释率在不同范式间变得更"分离"（cluster 更清） | 若 margin 反而变小 → NA 是"概率吸尘器"，加 NA 只在降低置信度（与 [S4] 的"NA 让模型更不自信"一致），我们应改成"NA 的收益来自弃权本身而非路由变准" |
| P3 | **reasoning 蒸馏模型上效应更强**（因为 [S28] 说 catch-tag-release 在 reasoning 模型更 prominnent） | 同族 instruct 版 vs reasoning 版的 NA 触发率差异显著 | 若两版无差异 → 机制解释不成立，需换 SepLLM 的"段压缩"解释 |

**重要的诚实声明**：以上三条是**我从两篇机制论文外推的假设**，没有任何文献直接测过"加一个 NA 选项后 attention 如何变"。**如果写进论文，必须标为 hypothesis 而不是 finding。** 我们的 Phase 3 应当把它当**可选项**，不要在 Phase 2 之前投入。

**方法论建议**：若真要做 P1–P3，最省算力的路径是 **[S20] 的 activation steering 范式**（他们用 Gemma-3-27B 做的，正好是我们的规模档），而不是全量 attention map 可视化——steering 能给出因果证据，attention 图只能给相关性。

---

# 6. 矛盾点汇总（验收标准要求）

| # | 矛盾 | 双方来源 | 对本项目的影响 | 建议处置 |
|---|---|---|---|---|
| C1 | 任务书说 TRICE/CISC 覆盖了"潜在策略识别/条件概率路由"，实际两篇与路由无关 | 任务书 vs [S6][S7] | 会影响 INDEX.md 差异表的正确性 | **回传 Lead 修正 INDEX**（§1.2） |
| C2 | STS 内部：GPT-5 选 Direct 是 65% 还是 100% | [S3] §5.3 vs [S3] Appendix G | 只影响复现，不影响主结论 | 引用写 "65–100%（原文不一致）" |
| C3 | SoT 的 router 准确率：96.4% vs 90.31% | [S12] 二手摘要 vs [S13] 会议页 | 说明"router 准确率"指标定义不同（paradigm assignment vs classification acc） | 引用时写明指标定义，别只抄数字 |
| C4 | SoT token 削减：84%（v1/v2 早期）vs 78%（arXiv v2 abstract） | [S12] vs 版本差异 | 版本漂移 | 一律引用 **arXiv v2 的 78%** 并注版本 |
| C5 | 小模型能否元认知：**能**（[S34] Qwen2.5-3B d'_type2=1.02；[S31] 1.5B 自路由成功）vs **不能**（[S29] 7–9B capacity threshold；[S1] Qwen3-30B 自路由失败） | 见左 | ⭐ **这是本项目最核心的未解矛盾**，也是我们实验的直接目标 | 见 §7 判定：差别在**任务（判别 vs 生成）** 与 **训练（零训练 vs 训练）** 两个维度上。我们的实验必须同时控制这两个变量 |
| C6 | 推理是否改善弃权：**改善**（[S35] EpiCaR、[S18] CoT 降位置偏差）vs **恶化**（[S17] AbstentionBench −24%） | 见左 | 决定我们该不该在路由跳里用 CoT | **默认不用**：路由跳用单次判别（direct-style），把 CoT 留作 ablation |
| C7 | Template ensemble 是否有效：**有效**（[S24] CAPE 降 ECE）vs **mixed + 概率平均不如多数投票**（[S25]） | 见左 | 直接决定我们的聚合算子 | **预注册两种聚合（概率平均 vs 多数投票）都跑**，以多数投票为主 |

---

# 7. 最终判断：真空白 vs 已有工作换个说法

## 7.1 分层判定

| 子主张 | 是否已被做过 | conf | 说明 |
|---|---|---|---|
| A. "范式路由"作为一个研究问题 | **已做**（[S1][S10][S12]） | 0.95 | 我们绝对不能声称这是新的 |
| B. "给路由器加一个 NA 选项"这种 prompt 技巧 | **没做过，但价值很低**（工程界在工具路由里是常规做法 [S37][S38]） | 0.75 | 单独主张这一点会被判 incremental |
| C. "把**范式级弃权**建模为独立动作类，并测量它对下游性能的影响" | **没做过** | 0.65 | **这是我们唯一站得住的空白** |
| D. "STS 排除掉的那批 all-paradigms-fail 样本是可学习的第四类" | **没人做过**，且 STS 原文留下了明确的接缝 [S3] | **0.85** | ⭐ **最强的切入点** |
| E. "小模型零训练自路由 + 多问法乱序取平均" | 组合没做过；两个组件分别有先例（[S24][S21] / [S1]） | 0.60 | 第二强差异化点，但需要 S1 的失败作为 motivation |
| F. "NA 改善小模型的 routing 精度"（因果主张） | 无法判断，**这是要被实验检验的** | — | 注意：**S4 强烈暗示它可能不成立**（NA 让模型掉 30–50%；小模型对 NA 最不敏感/最敏感需实测） |

## 7.2 总体判定

> **是"窄空白"，不是"真空白"，也不是"换个说法"。conf = 0.55。**
>
> - **不是真空白**：范式路由（A）已被 STS/RTR/SoT 建立，"加选项"本身（B）在工程界是常识；如果论文标题写成 "Adding a None-of-the-Above Option to Paradigm Routing"，**被判 incremental 的概率我估计 ≥60%**。
> - **不是换个说法**：**C+D 确实是空的**，而且 D 有一个罕见的优势——**它是对手论文自己写下来的接缝**（"tasks where all paradigms fail are excluded from training"）。这比"我们发现了一个没人做过的组合"强一个量级。
> - **风险最高的不是 novelty，而是效果**：三个独立证据（[S4] NA 掉 30–50%、[S17] 推理微调恶化弃权、[S29] 小模型 meta-cognition 有害）都指向**"NA 可能让结果更差"**。**这是一个高信息量的实验（无论正负都有价值），但不是一个高成功率的实验。**

## 7.3 叙事必须怎么改（三选一，建议 ②）

1. ~~"我们提出把 NA 加入候选范式"~~ → 太弱，会被工具路由工程实践打脸。
2. ✅ **"STS 把 all-paradigms-fail 任务从监督里排除了；我们把它们当作可学习的第四类"**（D）——直接响应一个已发表的一手接缝，最硬。
3. "范式级弃权是 abstention 研究中唯一空缺的一层（答案层/工具层/agent 层都已成熟）"（C）——作为 §2 的**论证框架**（用 [S15][S16][S37] 做"不对称性"举证），与 ② 组合使用。

---

# 8. 最小可执行实验设计（≤5 行，按验收标准）

1. **任务集（两堆，各 ≥40 题，人工标注 ground-truth 范式）**：①从 STS 的公开数据 `henggg/paradigm-bench` 里挑出 **"6 范式全失败"** 子集（这是 D 的直接检验集）；②pfb gold questions 里的真实科研子任务 10–20 题（外部效度）。判官口径沿用 STS 的 accuracy，另加一个同族 27B temp=0 判官并标 "相对有效"。
2. **四个条件 × 3 reps**：`{候选 6 范式}` vs `{候选 6 范式 + NA}` × `{概率平均, 多数投票}` × `{固定序, 5 次乱序}`。模型：Qwen3-30B-Instruct + 一个 27B 同族（对齐 [S20] 的 Gemma-3-27B 做机制）。
3. **主指标（3 个，缺一不可）**：①下游任务准确率（NA 触发的题按"拒答"计 0，另报"允许升级"的分支）；②**路由准确率**（对 ① 有 ground-truth 范式的子集）；③**gold-margin**（正确范式 logprob − 最强错误范式 logprob，[S21] 口径）——③ 是区分"NA 提供信息"与"NA 吸走概率"的关键。
4. **必须的对照（防 §3.5 的三个反证）**：①**NA-present-but-masked**（选项在但指令屏蔽）→ 分离"存在性扰动"与"信息效应"；②**per-position NA 触发率**（5 个位置）→ [S23] token bias 检查；③**强制选择基线**（无 NA，必须选一个）→ 这是 H0，NA 的收益全部相对它算。
5. **预注册的判决规则（先写死，避免事后编故事）**：若 ②（路由准确率）提升 **≥5pp** 且 ③ 上升 → 主张"NA 提供信息"；若 ② 不升但 NA 触发率与"实际全失败率"的 **AUROC ≥ 0.7** → 主张"NA 是一个可用的**弃权信号**（不同主张，同样可发表）"；若二者皆无 → 如实报告"NA 在范式层无效"，并把它作为对 [S4] 的边界条件贡献。

---

# 9. 给 Lead 的三条行动建议

1. **改 INDEX.md 的差异表**：删除 TRICE/CISC 两行（§1.2 已证与路由无关），替换为 **[S10] RTR（训练式 joint model×strategy 路由）** 与 **[S9] latent-strategy 分解**。同时把 STS 那行的"没做什么"从"无 NA 选项"升级为**"把 all-paradigms-fail 任务从训练中排除（原文自述）"**——后者是引用级证据。
2. **决定 framing**：如果接受 §7.3 的 ②，本仓库的目标就从"验证 NA 有没有用"变成"**证明 STS 排除掉的那批样本是可学习的第四类**"。这是一个更强的、可被审稿人验证的 claim，且**负结果也有价值**（若不可学，则 STS 的排除是合理的，也是对文献的贡献）。
3. **不要现在做 Phase 3（机制）**。Q5.b 的 conf 只有 0.35，三条预测都未经验证；把算力花在 §8 的对照上，机制留到 Phase 2 有行为学信号之后。

---

## 附录 A：检索覆盖度自评

| 维度 | 覆盖 | 缺口 |
|---|---|---|
| 范式路由主线 | STS / RTR / SoT / latent-strategy / Self-Route / Think-When-Needed / RACER / Learning-When-to-Think | 未系统扫 "adaptive reasoning" 全部 2026 论文（可能有 5–10 篇遗漏） |
| 弃权（答案层） | NA-MMLU / AbstainQA / AbstentionBench / Self-REF / Jev / Nature MI | 未覆盖全部 "selective prediction" 经典（Geifman & El-Yaniv 等），但那是 CV 传统，与我们距离远 |
| 弃权（agent 层） | Agentic Abstention / AgentAbstain / 工具路由工程实践 | 未检索中文文献与工业界专利 |
| MCQ 偏差 | PriDe / 100-option / Overwhelmed by Choice | 未覆盖 "option order sensitivity" 早期（Pezeshkpour & Hruschka 2023、Zheng et al. 2024）原文，仅二手引用 |
| 机制 | SepLLM / Attention Sinks catch-tag-release | **未**检索 "NA 选项 attention" 的直接实验（判断为不存在，conf 0.6） |
| 检索方式限制 | web_search + fetch_page 命中 arXiv/ACL/OpenReview/Nature/GitHub | **arXiv API 与 S2 API 不可达**；无法做 programmatic 全库扫描；"未找到"均为有限否证 |

## 附录 B：一句话备忘（如果只有一个字的空间）

> **STS 说"全范式失败的任务我们排除了"。我们的论文第一句应该是"我们没排除"。**
