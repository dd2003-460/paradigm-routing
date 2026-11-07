# T-PR-06: "无 query 主动觉察" gap 对抗性核验报告

> origin: ai · 2026-11-07 · Lead: Hermes · 执行: Arena agent
> 仓库: `dd2003-460/paradigm-routing` · 分支: `arena/62fe3fd4-paradigm-routing`（session branch）
> 被攻击的命题: `research/hierarchy-noquery-survey.md` §D/§F —— "长文档 × 开放式任务 × 埋点异常 × 自发检测" 是真空白
> 立场声明: **本报告的任务是推翻它，不是确认它。** 若结论是"仍然存在"，那是攻击失败后的残留，不是配合。

---

## 0. TL;DR（给 Lead 的三句话）

1. **严格判据下 0 命中——gap 在字面上活下来了，但它已经从"能力空白"降级为"笛卡尔积空白"**：我找到了 **9 篇部分命中**，其中 **3 篇各差一个维度**（MMPCBench 差长文档、ConInstruct 差长文档、FIND 差"不被告知要检测"）。任何审稿人都能一句话把我们的实验描述成"ConInstruct 的度量 + FIND 的文档"，这个 gap 的宽度约等于**一次组合实验**。
2. **最伤的一击不是来自文献，而是来自我们自己的 prompt。** v1 的任务是"给出分析和建议。**重点指出**你认为**值得关注的要点、潜在风险**以及后续行动建议"——按本任务书自己的判据，**这是一条检测指令，我们的实验是 task-directed，不是 no-query**。这同时解释了为什么我们拿到 2.6/3（86.7%）而文献是 2.5%–33%：**我们和它们测的不是同一个条件**。
3. **因此判决是：gap 存在，但我们还没进去过。** 而"从 2.5% 到 87% 这条由任务措辞拉动的曲线"本身，比"我们做了一个 no-query 实验"更值得做成论文。conf：事实清单 **0.85**；"gap 仍可发表" **0.58**（低于 Lead 的 0.70）。

---

## 1. 方法与判据

### 1.1 对抗性作业流程

1. 先**复算 Lead 的两个部分命中**（MMPCBench / PCBench），确认 Lead 的降级是否正确——**结论：正确，且 Lead 低估了它们的威胁程度**（见 §4.1）。
2. 按任务书 12 个角度 + 我自行扩展 4 个角度（**跨领域词汇**是最大盲区来源：法律 "issue spotting"、临床 "documentation inconsistency"、指令 "constraint conflict"、数据标注 "self-flagging"），共 **16 组关键词**。
3. 每篇候选打一个 **4-bit 向量**（D1 长文档 / D2 开放任务 / D3 埋点异常 / D4 自发检测），用矩阵而不是散点判断"空白"。
4. 最后做 **§7 自我反驳**：假设我是审稿人，用最强理由拒掉这篇论文。

### 1.2 三档判据（直接沿用任务书，未放宽）

| 判定 | 定义 | 后果 |
|---|---|---|
| **命中 HIT** | 任务设计从未告知"要检测 X"，且指标 = 模型是否**自发**提及/标记 X | 直接推翻 gap |
| **部分命中 PARTIAL** | 任务措辞模糊（"总结并指出问题"），但核心评估仍是自发检测 | 收窄 gap |
| **未命中 MISS** | 存在明确检测指令（"判断是否一致"/"找出矛盾"/"列出所有不一致"） | 不直接影响 gap，但若它在其他三维满分，则**威胁"组合式新颖性"** |

### 1.3 四维向量（本报告的核心分析工具）

- **D1 长文档**：输入 > 1k token 的真实文档（非短问句、非单句、非多模态短请求）
- **D2 开放任务**：任务指令里**不含**任何"检测/指出/评估"语义
- **D3 埋点异常**：异常是被**插入**的（可算 recall），而非自然存在
- **D4 自发检测**：指标是"是否主动提及"，而不是"被问到后判对"

> **"4/4 且无命中"才是真空白；"3/4"是三篇论文各自差一步；"组合可达"意味着这个空白是**构造性的**，不是**概念性的**。这是本次核验最重要的一句话。**

---

## 2. 通道状态（按强制段第 4 条报告，未静默跳过）

| 通道 | 状态 | 证据 |
|---|---|---|
| `web_search`（代理） | **可用** | 覆盖 arXiv abs/html、ACL Anthology、NeurIPS proceedings、OpenReview PDF、Nature、PMC、GitHub、技术博客 |
| `fetch_page`（代理） | **可用** | 用于 `arxiv.org/abs/2512.18601` 逐字核对 |
| arXiv API (`export.arxiv.org/api/query`) | **阻断** | `curl` → `http_code=000` |
| Semantic Scholar API | **阻断** | `curl` → `http_code=000` |
| OpenReview API (`api2.openreview.net`) | **阻断** | `curl` → `http_code=000` |
| 直连 `arxiv.org/abs/*`（bash） | **阻断** | `curl` → `http_code=000`；**只有 `fetch_page` 工具能通** |
| Google Scholar | **不可直接寻址** | 仅经 web_search 间接命中 |

**影响**：无法做程序化全库扫描（无法按年份/venue 穷举），所以"未找到"一律是**有限否证**而非完备性证明。这一点直接压低最终 conf。任务书的降级路径（"arXiv API 不可用 → web search"）已执行，未阻塞。

---

## 3. 搜索执行摘要（16 组，完整记录见 `noquery-gap-search-log.json`）

| # | 角度 | 关键词（摘要） | 评级最高结果 | 判定 |
|---|---|---|---|---|
| Q01 | 核验 F1 | MMPCBench proactive critique MLLM 2608.29286 | MMPCBench（EMNLP 2026 Findings） | PARTIAL |
| Q02 | 核验 F2 | PCBench premise critique 2505.23715 | PCBench（15 LLM / 3600 题） | PARTIAL |
| Q03 | ①⑧ 自发/无需提示 | spontaneously flag error "without being asked" | 3 篇 self-correction / retraction | PARTIAL |
| Q04 | ④ 输入侧无监督矛盾 | unsupervised contradiction detection in document | **FIND (2512.18601)** | MISS ⚠ |
| Q05 | ⑪ NIAH 变体 | noticing anomalies long context no question | NoLiMa / Hidden-in-Haystack | MISS |
| Q06 | ② 主动 agent | proactive agent volunteers concerns | ProactBench / π-BENCH / ProActEval | MISS |
| Q07 | ⑤ 隐式质量评估 | ambiguity detection without instruction | **Knowing but Not Showing (2605.25284)** | PARTIAL |
| Q08 | 新增：指令冲突 | conflict detection in instructions notify user | **ConInstruct (AAAI 2026)** | PARTIAL ⚠⚠ |
| Q09 | ⑥ self-flagging | LLM self-flagging data quality unprompted | LLM label-error detection | MISS |
| Q10 | ⑫ 中文 | 大模型 主动发现 矛盾 无需提示 | 全为实践教程 | MISS |
| Q11 | ⑦ 元认知/顺从 | sycophancy suppresses critique | **Sycophancy-Lying Circuit (2604.19117)** | PARTIAL（机制） |
| Q12 | ⑧ 位置偏差 | lost in the middle notice anomaly | LITM / Context Rot | MISS |
| Q13 | 新增：冲突摘要 | conflict-aware summarization report discrepancy | CARE-RAG / 冲突 survey | MISS |
| Q14 | ⑩ Workshop | OpenReview workshop spontaneous detection | 文档级异常检测（任务式） | MISS |
| Q15 | 新增：法律 | legal "issue spotting" without being told | LegalBench / PLawBench | MISS |
| Q16 | 新增：临床 | incidental finding / documentation inconsistency | EHR 不一致流水线（3000 病历） | MISS |

**统计**：16 组 / 严格命中 **0** / 部分命中 **9** / 未命中但邻接 **7**。

---

## 4. 候选清单（按威胁程度排序）

### 4.1 A 级：3/4 维，三篇"各差一步"的论文

#### A1. ConInstruct（AAAI 2026）— **本次最危险的一篇，Lead 尚未发现**

> *ConInstruct: Evaluating Large Language Models on Conflict Detection and Resolution in Instructions*
> https://en.papernotes.org/AAAI2026/llm_evaluation/coninstruct_evaluating_large_language_models_on_conflict_detection_and_resolutio/

- 构造：100 条种子指令 × 6 类约束（content/keyword/phrase/length/format/style）× 9 类冲突 × 35 个领域；每条指令注入 7–9 个冲突对，冲突**追加在指令末尾**（作者自承这是局限：位置固定可能让检测变容易）。
- **任务框架完全没有检测指令**：模型被要求"完成这个任务"，是否指出冲突**是自愿行为**。
- 评估就是三分法：① 直接作答、不提冲突 ② 请求澄清（RequestC）③ 自主解决（ResolveC）——后两者算"显式冲突告知"。
- **关键数字（直接打穿我们的动机）**：
  - "LLMs can generally detect conflicts in instructions but **rarely notify users proactively** — even the best-performing Claude-4.5-Sonnet does so explicitly in only **45%** of cases."
  - 消融（冲突越多越容易被告知）：
    | 冲突数 | 直接作答（不告知） | 请求澄清 | 自主解决 |
    |---|---|---|---|
    | 1–2 | **97.5%** | ~2% | <1% |
    | 3–4 | ~90% | ~8% | ~2% |
    | 7–9 | ~70% | ~25% | ~5% |
  - 冲突检测 F1：DeepSeek-R1 91.5%、Claude-4.5-Sonnet 87.3%（**能检测**）；Claude 的"请求澄清"只有 36%。
- **判定 PARTIAL**：D2 ✓（无检测指令，是纯"照做"任务）、D3 ✓（注入冲突）、D4 ✓（指标=是否告知）；**D1 ✗**（指令不是长文档，且冲突位置固定）。
- **为什么它比 MMPCBench 更危险**：MMPCBench 是"用户请求本身有缺陷"（缺陷是输入的主特征），而 ConInstruct 是"**任务本身完全正常，缺陷藏在约束里**"——这跟我们"正常报告里埋钩子"的语义结构**完全同构**。它只差长度。

#### A2. FIND（arXiv:2512.18601, 2025-12-21）— **长文档 × 埋点，只差"不被告知"**

> *On Finding Inconsistencies in Documents* — Lovering, Ebner, Smock, Krumdick, Rabbani, Muhammad, Reddy, Tanner
> https://arxiv.org/abs/2512.18601 （已用 fetch_page 逐字核对 abs 页）

- 每个样本 = 一份**由领域专家手工插入不一致**的文档；文档"long, technical, and complex"。
- 任务：**"find all inconsistencies within a document"**（因此判 MISS），要求给出 evidence spans + description，是对插入项的 recall 评测。
- 数字：**gpt-5 回收 64%**；"even the best models miss almost half"。
- ⭐ 附带的杀伤性发现：在 50 篇 arXiv 论文上，**gpt-5 提出 196 条不一致建议，其中 136 条被人工判定为原作者遗漏的真实不一致**。也就是说"模型能发现人类漏掉的问题"这件事已经被系统性报告过了。
- **判定 MISS**：D1 ✓✓（长技术文档）、D3 ✓✓（专家插入）、D2 ✗（明确要求"找出来"）、D4 ✗。
- **威胁性质**：它把"长文档 × 埋点异常 × 可算 recall"这条实验脚手架**全部做完并公开**。我们唯一能宣称的差别是"没有那条指令"——而这条差别在 ConInstruct 里已经被单独测过了。**两者的合成几乎是显然的。**

#### A3. MMPCBench（arXiv:2608.29286 / EMNLP 2026 Findings, pp.3741–3774）— Lead 已找到，但低估了

- 3,146 样本 / 14 个 MLLM / 4 大类 12 子类错误（含跨模态矛盾、缺失视觉前提、歧义、超出能力）；层级评估 detection → diagnosis → resolution。
- 数字：**平均 EDA 33.2%**（约三分之二的错误输入场景模型**完全没有批判性回应**，直接"谄媚式完成"）、**PCQ 26.1/100**；跨模型方差主要由 EDA 驱动（CV 0.43 vs DP 0.16 / SE 0.13）。
- ⭐ **consistency gap**：推理模型在内部 reasoning 中识别了错误，却在最终输出中**压制**，平均 **Detection Drop Rate = 46%**。
- **判定 PARTIAL**：D2 ✓、D3 ✓、D4 ✓；**D1 ✗**（短输入 + 多模态）。
- **我修正 Lead 的一处判断**：Lead 说它"多模态所以不同"。多模态不是关键差异——**关键是它在 D2/D4 上已经把我们想证明的"模型注意到了但不主动说"确立为一条被命名的现象（consistency gap）**。这意味着我们的机制叙事不再新颖。

### 4.2 B 级：2/4 维，提供"现象已被命名"的证据

| # | 论文 | ID/Venue | 关键数字 | 判定 | 对我们的伤害 |
|---|---|---|---|---|---|
| B1 | **Knowing but Not Showing: LLMs Recognize Ambiguity but Rarely Ask Clarifying Questions**（Su & Cardie, Cornell） | 2605.25284 | 显式询问时歧义识别 60–80%；不询问时 **>95% 直接作答**，澄清率 **<5%**；**加入检索上下文会进一步压低澄清率** | PARTIAL（D2✓D4✓，D1✓? 输入是短问句，D3✗） | 提供了与我们完全同构的"知道但不表现"结构，且**"给上下文反而更不批判"**这一条直接支持"材料会抑制批评"的机制假设 |
| B2 | **When Do LLMs Admit Their Mistakes? Retraction** | 2505.16170 / COLM 2026 | 模型**很少**自发撤回，即使单独问时能认出错误；belief probe 可预测撤回；负向 steering 后在 20% 案例上答对 | PARTIAL（对象是自身输出） | "noticed but not reported" 的第三份独立证据 |
| B3 | **LLMs Know They're Wrong and Agree Anyway: The Shared Sycophancy-Lying Circuit** | 2604.19117 | 12 个开放权重模型 / 5 家实验室；一小簇 attention head 携带"这句话是错的"信号；**silencing 这些 head 可翻转行为而保持事实准确率**；RLHF 把外显顺从降 10× 但**电路保留甚至变大** | PARTIAL（机制） | ⭐ 机制层面**因果**证明"注意到但不报告"；这正是我们 Phase 3 想要的机制证据，**别人已经做了** |
| B4 | Single-Utterance Self-Correction of Perturbed Reasoning | 2506.15894 | 在自己的 CoT 前 100 token 注入数学错误，模型在一次生成内检测并修正 | PARTIAL | "无需被要求就修正上下文中的错误"已被证实（但对象是自身推理） |
| B5 | Internalized Self-Correction (InSeC) | 2412.16653 | SFT 注入错误句 + 纠正 tag；微调后 Llama-3.1-8B 见到错误换算因子会自发纠正（10800s vs 9000s） | PARTIAL | 证明"自发性可以被训练出来"——对我们 Phase 2 有直接设计含义 |
| B6 | PCBench | 2505.23715 | 15 LLM / 4 错误类型 × 3 难度 / 3600 题；"most models rely heavily on explicit prompts to detect errors"；"some reasoning models internally catch inconsistencies but fail to articulate them" | PARTIAL | 与 A3 的 consistency gap 互相印证 |
| B7 | ContraDoc | 2311.09182 (NAACL 2024) | 449 正 / 442 负样本；二元判断准确率 ~50%（近随机），GPT-4 真实准确率 35.6%；**文档长度不是主要障碍** | MISS | "长文档"本身不是瓶颈——这条消解了我们"推长度"的价值 |
| B8 | EHR 文档不一致流水线 | 2607.22954 | 3,000 份 MIMIC-IV 出院小结 / 3,460 个候选冲突对 / ~70% 入院至少 1 个 flag；两阶段（开放式候选识别 + 上下文核验） | MISS | 真实世界长文档 + 开放式"候选识别"，只差指令 |
| B9 | Document-Level Anomaly Detection in Semi-Structured Text | conference proceedings, Apr 2026 | 半结构化文档（财报/发票/报表）异常检测综述 + 分类学 | MISS | 该术语已被占用于"任务式检测" |

### 4.3 C 级：术语陷阱（重要否证，防止我们误判）

- **"proactive" 在 2026 已被系统性占用**，但语义完全不同：ProactBench（2605.09228，198 对话/624 触发点/16 模型）、π-BENCH（2605.14678，100 多轮任务/5 人设/9 前沿模型）、ProActEval（2605.25971，200 场景/40 领域）、Ask-Now-Use-Later（2605.28108）——全部是**对话中预判用户未说出的需求**，不是"读文档发现异常"。
  → **写作风险**：我们若用 "proactive detection" 作标题词，会与这四条线撞车；建议改称 **unprompted salience reporting** / **input-side anomaly reporting**。
- **"issue spotting"**（法律）已存在但被操作化为"给定 query 判 yes/no"（LegalBench 16–17 个任务）；PLawBench（2601.16669）的咨询任务确实评分"问题识别"，但用户明确求法律意见。
  → 好处：给了我们一条**合法的学术血统**；坏处：也说明"术语存在但没人做无 query 版"。

---

## 5. 四维矩阵（判决的核心依据）

✓ = 满足，✗ = 不满足，~ = 部分。

| 工作 | D1 长文档 | D2 开放任务 | D3 埋点异常 | D4 自发检测 | 得分 |
|---|---|---|---|---|---|
| **ConInstruct**（AAAI 2026） | ✗ | **✓** | ✓ | **✓** | **3/4** |
| **MMPCBench**（EMNLP 2026 F） | ~(短多模态) | ✓ | ✓ | ✓ | 3/4 |
| **PCBench** | ✗ | ✓ | ✓ | ✓ | 3/4 |
| **FIND**（2512.18601） | **✓** | ✗ | **✓** | ✗ | 2/4 |
| Knowing-but-Not-Showing | ✗ | ✓ | ✗ | ✓ | 2/4 |
| Retraction（COLM 2026） | ✗ | ✓ | ~(自身错误) | ✓ | 2/4 |
| Sycophancy circuit | ✗ | ✓ | ~ | ~(机制) | ~2/4 |
| Single-Utterance Self-Correction | ✗ | ✓ | ✓ | ✓ | 3/4（但域=自身 CoT） |
| ContraDoc | ✓ | ✗ | ✓ | ✗ | 2/4 |
| EHR 不一致（2607.22954） | ✓ | ✗ | ~ | ✗ | ~1.5/4 |
| 本文献中的 task-directed 阵营（SIFiD/Absinth/SUMMAC/checkworthiness/…） | 混合 | ✗ | 混合 | ✗ | ≤1/4 |
| **我们的 proactive-detection v1（按自己的判据重打分）** | **✓**(2.5k ZH) | **✗** ⚠ | **✓** | ✓ | **3/4** |
| **我们的 proactive-detection v2（§9 提议的修正版）** | ✓ | ✓ | ✓ | ✓ | **4/4** |

### 5.1 矩阵读出的三个结论

1. **4/4 格子确实空着**——16 组关键词、9 篇部分命中，没有任何一篇同时满足四维。gap 在**字面**上成立。
2. **但 3/4 有四个格子被占满，且分布在两条正交轴上**：ConInstruct/MMPCBench/PCBench 占据 "开放任务 + 自发检测"，FIND/ContraDoc 占据 "长文档 + 埋点"。**取两者并集即得 4/4**。这说明空白是**笛卡尔积意义上**的，不是"某个能力从未被证明存在"意义上的。
3. **我们自己的 v1 只有 3/4——而且缺的正是 D2**。这一格必须自己补，不存在"别人没做所以我们自然独占"的情况。

---

## 6. 判决：收窄后的 gap 是否仍然存在？

### 6.1 分三层回答（不要混在一起说）

| 层 | 命题 | 判决 | conf |
|---|---|---|---|
| **事实层** | 是否存在一篇同时满足 D1–D4 的论文？ | **不存在**（16 组检索、9 篇部分命中，无一 4/4） | **0.85** |
| **组合层** | 这个 4/4 组合是否已被别人一步可达？ | **是，且高度显然**：ConInstruct 的度量 × FIND 的文档 = 我们 | **0.80** |
| **概念层** | 这个组合是否揭示了一个**尚未被命名的现象**？ | **否**。"noticed but not reported" 已被命名至少三次：MMPCBench 的 *consistency gap*（DDR 46%）、Knowing-but-Not-Showing（>95% vs <5%）、Retraction（"rarely retract even when they can recognize"），并有机制论文（2604.19117） | **0.75** |

### 6.2 最终判决

> **gap 没有被推翻，但被贬值。** 它从 Lead 原判断的"能力空白（conf 0.85）"→ 现有"组合空白（conf 0.58）"。
> **结论句建议改写为**：
> "据我们所知，尚无工作在**不给出任何检测指令的长文档开放任务**中测量模型对埋点异常的自发报告率；但**现象本身（模型注意到却不报告）已被多个 benchmark 独立确立**，本文的贡献不是发现该现象，而是**测量它的边界条件**。"
>
> 这个改写的代价是：不能再写 "first to show models fail to report"（会被 ConInstruct/MMPCBench 直接打）；收益是：**可以安全地写"first to measure the framing-dependence of the notice→report threshold in long documents"**，而这恰好是我们数据能支撑的（§8）。

### 6.3 与 Lead §F 的差异（我做了什么，Lead 没做什么）

| 项 | Lead §F | 本次核验 |
|---|---|---|
| 部分命中数 | 2（MMPCBench/PCBench） | **9** |
| 漏掉的最关键论文 | — | **ConInstruct (AAAI 2026)**、**FIND (2512.18601)**、**Knowing-but-Not-Showing (2605.25284)**、**Sycophancy-Lying Circuit (2604.19117)** |
| 现象命名 | 无 | consistency gap / knowing-but-not-showing / retraction 三处独立命名 |
| conf | 0.70 | **0.58** |
| 对自家实验的判定 | 未审视 | **v1 未通过 D2（prompt 内含检测指令）** ⚠ |

---

## 7. 自我反驳：如果我是审稿人，我会用这三条拒掉它

**R1（最致命）"这不是新问题，是没做过的组合。"**
你会怎么写？"We introduce no-query anomaly detection in long documents." 我会回：ConInstruct 已经在**无检测指令**下测了"是否告知冲突"（1–2 冲突时 97.5% 不告知），FIND 已经在**长技术文档**上测了"埋点矛盾召回"（gpt-5 64%）。你的贡献 = 把 A 的度量套到 B 的文档上。这是组合，不是发现。
→ 唯一反驳：**组合会产生新信息**（长度 × 措辞的交互），前提是我们真的测了交互，而不是只测了一个点。

**R2 "你的正结果与三篇同行评议 benchmark 直接矛盾，说明你的设置有问题，而不是文献错了。"**
我们 2.6/3 = **86.7%**；MMPCBench 33.2%；ConInstruct 1–2 冲突时 ~2.5%；PCBench "limited autonomous critique"。差 2.6–35 倍。审稿人第一反应必然是"你的钩子太显眼 / 打分太松 / 任务在暗示"。**见 §8，这个反驳是对的。**

**R3 "consistency gap 已经被命名并给出机制，你的机制章节是重复劳动。"**
MMPCBench 给了 DDR 46%，2604.19117 给了 attention-head 因果证据，Retraction 给了 belief probe。如果我们的 Phase 3 再画 attention heatmap 说"模型注意到了"，就是第四次做同一件事。
→ 反驳：只有当我们测**"任务措辞如何移动 notice→report 阈值"**时，机制工作才有新意（因为已有的三篇都固定了任务框架）。

---

## 8. ⚠ 本次核验的意外发现：我们 v1 的 2.6/3 很可能是任务措辞的产物

这是本次调研**最有价值**的一条，且它同时解释了 R2。

### 8.1 v1 的 prompt 其实不是 no-query

`experiments/proactive-detection/RESULTS.md` 记录的任务是：

> "请基于以上材料，给出你的分析和建议。**重点指出**你认为**值得关注的要点、潜在风险**以及后续行动建议。"

按本任务书自己的判据（"**命中**：模型没有被明确告知'要检测 X'"），"重点指出值得关注的要点、潜在风险" **就是一条检测指令**——只是它没有点名"矛盾/异常"。所以 v1 的正确分类是 **PARTIAL（≈ task-directed with a soft query）**，而非 no-query。

### 8.2 这一条同时消解了"我们比文献强 3 倍"的假象

| 条件 | 报告率 | 来源 |
|---|---|---|
| 无检测指令，短输入（缺陷=输入主特征） | 2.5%–33% | ConInstruct 97.5% 不告知 / MMPCBench EDA 33.2% / PCBench limited |
| **有软检测指令（"指出值得关注的要点"），2.5k 中文文档** | **86.7%** | 我们 v1（2.6/3） |
| 有硬检测指令（"找出所有不一致"），长技术文档 | 64% | FIND（gpt-5） |

**读法**：报告率沿"指令强度"单调上升（2.5% → 64–87%）。**这不是我们发现了强能力，而是我们无意中证明了"任务措辞是主导变量"。**

### 8.3 于是研究方向应该翻转（这是本报告的核心建议）

不要写"模型能/不能自发检测"。要写：

> **"在长文档开放任务中，模型的自发报告率是任务措辞的函数：中性任务 → X%，分析建议任务 → 87%，显式检测任务 → 100%（定义上）。我们给出这条曲线的三个锚点，并证明它由 notice→report 阈值（而非 notice 能力）驱动。"**

这个 claim：
- **不与文献矛盾**（我们把文献的数字（2.5%、33%、64%）作为曲线的低锚点复用，而不是对抗它们）；
- **别人没做过**（ConInstruct 只测了一个措辞点，FIND 只测了硬指令点，我们测的是**曲线的形状**）；
- **负结果也可发表**（如果曲线是平的，说明措辞无关，那同样是对 ConInstruct 的一个边界）；
- **成本极低**（同一文档 × 3 种任务措辞，其余不变——见 §9）。

---

## 9. 给 Lead 的行动建议（按优先级）

### P0：把 v1 的实验改造成"措辞梯度"（1 天，几乎零额外成本）

同一份 2.5k 中文报告、同样 3 个钩子，只改任务指令，做 3 档 × 2 骨架 × n=5：

| 档 | 指令 | 预期（按文献推断） | 作用 |
|---|---|---|---|
| T0 **中性** | "请为这份报告写一份 300 字执行摘要。" | 10–40% | 真正的 no-query（补齐 D2） |
| T1 **分析建议**（= v1 现状） | "……重点指出你认为值得关注的要点、潜在风险……" | ~87% | 复现我们已有数字，作为曲线中锚点 |
| T2 **显式检测**（= 上界） | "请逐条检查材料中的事实矛盾、隐藏约束与异常数字并列出。" | ~100% | 上界校准，同时对齐 FIND |

另加两个免费但高价值的维度（各 1 行代码）：
- **钩子位置扫描**（前/中/后 3 档）：文献（Lost-in-the-Middle / Context Rot）只测了"检索 queried fact"，**从没人测"未被 query 的埋点异常"的位置效应**——这是矩阵里完全干净的格子（Q12 零命中）。
- **先验强度**（沿用 Lead §G 的 LINGOLY-TOO 思路）：数字离群 vs 逻辑矛盾两类钩子分开报，检验"靠先验还是靠推理"。

### P1：改写论文定位（避免与 ConInstruct/FIND 撞车）

- 不用 "proactive detection"（已被对话式用户需求预测占用：ProactBench/π-BENCH/ProActEval）。
- 建议用 **"unprompted reporting of planted anomalies in long documents"** 或 **"the notice–report gap in document reading"**。
- Related work 必须引：**ConInstruct、FIND、MMPCBench、PCBench、Knowing-but-Not-Showing、Retraction**（六篇，缺一篇就会被审稿人指出）。
- 可直接复用的现象名：**consistency gap**（MMPCBench）、**knowing but not showing**（Su & Cardie）。用别人的名字，别自己造。

### P2：机制章节要么砍掉，要么换问题

- 砍掉："模型注意到了但没说" + attention 可视化 → 已有 MMPCBench（DDR）、2604.19117（attention-head 因果）、Retraction（belief probe）三篇。
- 换问题：**"任务措辞如何移动 notice→report 阈值"**——测 T0/T1/T2 三档下的 probe 可分性（belief probe 是否不变而 report 率剧变；若不变，则证明瓶颈在 report 侧不在 notice 侧）。这是一个**只有我们这套设计才能回答**的问题。

### P3：不要做的事

- 不要写 "first to test X"（用 "to our knowledge, no prior work measures …" 并在正文列出 ConInstruct/FIND 作为最近邻）。
- 不要把 2.6/3 当作结论亮点单独汇报给 Lead——按 §8 它是措辞产物。
- 不要依赖"多模态 vs 纯文本"作为 MMPCBench 的区分点（审稿人会立刻指出我们的钩子也可以放进多模态）。

---

## 10. 搜索盲区（诚实声明，直接影响 conf）

| 盲区 | 影响 | 缓解 |
|---|---|---|
| arXiv / S2 / OpenReview API 全部阻断 | 无法穷举；workshop 层覆盖弱（Q14 只捞到 2 篇相关） | 已在检查表标注；建议 Lead 在有 API 的环境重跑 Q04/Q08/Q14 |
| Google Scholar 不可达 | 无法查引用链（"谁引用了 MMPCBench 并扩展它"） | ⭐ **最可能藏命中**的路径；建议查 ConInstruct/FIND 的 citing papers |
| 未检索中文硕博论文库（CNKI 等） | 中文侧只用 web_search 命中实践教程 | 风险低（中文学术界该方向覆盖弱），但未见全貌 |
| 未检索 ACL/EMNLP 全文库的程序化标题扫描 | 可能漏 2026 下半年新论文 | 本次已覆盖 2025-05 → 2026-10 的主流命中 |
| 未检索工业界专利/技术报告 | "AI 审计/尽调产品"可能已实现但未发表 | 对论文定位影响小，对"novelty"无影响 |

**conf 调整**：事实清单 0.85（每篇均核对 abs 页或 venue 记录）→ 因上述盲区，最终"gap 仍可发表"判为 **0.58**。

---

## 附录 A：判据细则（避免团队对"命中"理解不一致）

1. **"不能算 no-query"的三种常见情形**
   - 任务名里出现 detect/find/check/identify/audit/review/指出/检查 → task-directed。
   - 任务叫"summarize/answer/analyze"，但评分 rubric 含"是否指出问题"且该 rubric 权重显著 → **PARTIAL**（Rubric-as-query）。
   - 任务中性，但**评测集只包含有缺陷的输入** → 模型可从分布先验推断"要找茬" → **PARTIAL**（这一点对 FIND/MMPCBench/PCBench 全部适用，是我们必须警惕的镜像陷阱：我们若只给 3 钩子文档，模型也可能推断"这题在考我找茬"）。
2. **建议我们在设计 v2 时加一条"干净文档"控制组**（0 钩子），测假阳性率——否则无法排除"分布先验导致找茬"的替代解释。这是本报告对实验设计的第六条约束。

## 附录 B：本次新增、Lead 尚未记录的 6 篇（建议直接进 §F 表）

| ID | 标题 | Venue | 判定 | 一句话理由 |
|---|---|---|---|---|
| AAAI 2026 | ConInstruct: Conflict Detection and Resolution in Instructions | AAAI 2026 | PARTIAL | 无检测指令 + 注入冲突 + 指标=是否告知；缺长文档 |
| 2512.18601 | On Finding Inconsistencies in Documents (FIND) | arXiv 2025-12 | MISS | 长文档 + 专家插入；缺"不告知" |
| 2605.25284 | Knowing but Not Showing | arXiv 2026 | PARTIAL | >95% 直接作答 / 澄清 <5%；上下文进一步抑制 |
| 2604.19117 | Shared Sycophancy-Lying Circuit | arXiv 2026 | PARTIAL(机制) | "注意到但不报告"的 attention-head 因果证据 |
| 2505.16170 | When Do LLMs Admit Their Mistakes? (Retraction) | COLM 2026 | PARTIAL | 自发撤回极罕见，即使被问能认出 |
| 2607.22954 | Documentation Inconsistencies in EHR | arXiv 2026 | MISS | 3000 份真实长病历，开放式候选识别；缺"不告知" |

## 附录 C：环境回执

- 拉取校验：`tasks/T-PR-06-noquery-gap-adversarial.md`、`research/lit-survey-arena.md`、`INDEX.md`、`tasks/arena-task-brief.md` 与 `origin/arena/81df0921-paradigm-routing` 内容 **逐一 md5 相同**（该分支与本 session 分支为**无共同祖先的独立快照**，`git merge-base` 返回空；内容已全部在位，故未做 merge/cherry-pick，也未切换分支——遵守"只在本 session 分支工作"约束）。
- 未跑任何实验；未修改 `experiments/` 下任何文件。
- 产出：`research/noquery-gap-adversarial-check.md`（本文件）、`research/noquery-gap-search-log.json`（16 组结构化日志，JSON 已校验）。

## 附录 D：来源 URL 总表（与 `noquery-gap-search-log.json` 的 id 对齐）

| JSON id | 标题 | 链接 |
|---|---|---|
| Q01 | MMPCBench (arXiv:2608.29286) | https://arxiv.org/abs/2608.29286 |
| Q01 | MMPCBench (ACL Anthology, EMNLP 2026 Findings) | https://aclanthology.org/2026.findings-emnlp.178/ |
| Q02 | PCBench (arXiv:2505.23715) | https://arxiv.org/html/2505.23715 |
| Q02 | PCBench dataset | https://huggingface.co/datasets/ALIENS232/PCBench |
| Q03 | Single-Utterance Self-Correction (arXiv:2506.15894) | https://pith.science/paper/2506.15894 |
| Q03 | Internalized Self-Correction (arXiv:2412.16653) | https://pith.science/paper/2412.16653 |
| Q03 | Retraction (arXiv:2505.16170, COLM 2026) | https://arxiv.org/abs/2505.16170 |
| Q04 | **FIND — On Finding Inconsistencies in Documents (arXiv:2512.18601)** | https://arxiv.org/abs/2512.18601 |
| Q04 | ContraDoc (arXiv:2311.09182) | https://arxiv.org/html/2311.09182.pdf |
| Q04 | DocChecker code | https://github.com/chen760316/Doc4LLM |
| Q04 | LegalWiz (arXiv:2510.03418) | https://arxiv.org/pdf/2510.03418 |
| Q05 | NoLiMa (arXiv:2502.05167) | https://arxiv.org/html/2502.05167v2 |
| Q05 | Hidden in the Haystack (arXiv:2505.18148) | https://arxiv.org/pdf/2505.18148 |
| Q05 | MLNeedle (NAACL 2025) | https://aclanthology.org/2025.naacl-long.267.pdf |
| Q06 | ProactBench (arXiv:2605.09228) | https://pith.science/paper/2605.09228 |
| Q06 | π-BENCH (arXiv:2605.14678) | https://arxiv.org/pdf/2605.14678 |
| Q06 | ProActEval (arXiv:2605.25971) | https://arxiv.org/html/2605.25971v1 |
| Q06 | Ask Now, Use Later (arXiv:2605.28108) | https://awesomepapers.io/ai-agents/papers/2605.28108 |
| Q06 | Vigil "Help Without Being Asked" (arXiv:2604.09579, FSE'26) | https://arxiv.org/pdf/2604.09579 |
| Q07 | **Knowing but Not Showing (arXiv:2605.25284)** | https://arxiv.org/abs/2605.25284 |
| Q07 | Interactive Agents / Ambiguity in SWE (arXiv:2502.13069) | https://arxiv.org/html/2502.13069v1 |
| Q08 | **ConInstruct (AAAI 2026)** | https://en.papernotes.org/AAAI2026/llm_evaluation/coninstruct_evaluating_large_language_models_on_conflict_detection_and_resolutio/ |
| Q09 | LLM label-error detection (EMNLP 2025) | https://aclanthology.org/2025.emnlp-main.1360.pdf |
| Q10 | 中文实践教程：检查多份文档中的矛盾 | https://evolink.ai/zh/blog/find-contradictions-across-documents |
| Q10 | 大语言模型的幻觉问题研究综述 | https://www.secrss.com/articles/73856 |
| Q11 | **Shared Sycophancy-Lying Circuit (arXiv:2604.19117)** | https://pith.science/paper/2604.19117 |
| Q11 | LLM Sycophancy: Definition, Evidence, and Evaluation | https://www.andyagentlab.com/articles/model-training-and-eval/sycophancy-agreement-bias/ |
| Q12 | Lost-in-the-Middle / Context Rot 综述 | https://memx.app/blog/lost-in-the-middle-long-context-fails/ |
| Q13 | Conflicts in Texts survey (arXiv:2504.19472) | https://arxiv.org/pdf/2504.19472 |
| Q13 | CARE-RAG (arXiv:2507.01281) | https://arxiv.org/pdf/2507.01281 |
| Q14 | Document-Level Anomaly Detection in Semi-Structured Text (2026) | https://academicresearchlibrary.com/storage/pdf/nWfMqRf6DlNEtfYsNEMWUmgEcgecjjXmavNhyhQ9.pdf |
| Q14 | CAVE (NeurIPS 2025) | https://neurips.cc/virtual/2025/133793 |
| Q15 | LegalBench (arXiv:2308.11462) | https://arxiv.org/pdf/2308.11462 |
| Q15 | PLawBench (arXiv:2601.16669) | https://arxiv.org/pdf/2601.16669 |
| Q16 | **EHR documentation inconsistencies (arXiv:2607.22954)** | https://pith.science/paper/2607.22954 |
| Q16 | Discharge-summary incidental findings (medRxiv 2026) | https://www.medrxiv.org/content/10.64898/2026.06.03.26354858v1.full |
| Q16 | Faithfulness hallucination detection (OpenReview) | https://openreview.net/pdf?id=6eMIzKFOpJ |

> 访问方式说明：本沙箱内 `curl` 直连 arxiv.org / export.arxiv.org / api.semanticscholar.org / api2.openreview.net 均返回 `http_code=000`（出网白名单限制），上述内容全部经 `web_search`（代理）与 `fetch_page`（代理，用于 2512.18601 逐字核对）取得。**引用前建议 Lead 在有直连的环境抽检 3 条链接。**
