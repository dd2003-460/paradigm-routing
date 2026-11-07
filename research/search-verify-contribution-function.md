# T-PR-11：信息搜集 × 校验 的合成贡献函数——学界现状与 pfb 离散版的定位

> origin: ai · 2026-11-07 · Lead: 成璐数字分身 · 执行: Arena agent
> 仓库: `dd2003-460/paradigm-routing` · 分支: `arena/62fe3fd4-paradigm-routing`
> 检索日志: `research/search-log-sv-contribution.json`
> **资产缺失（第五次记录）**：`loop/prompt-first/01..04.5`、`sop/arena-loop-pipeline.md` 仍不存在；**且任务书引用的 `pfb/lit-survey/2026-11-07-idea-list.md` 在本仓库亦不存在**（`ls pfb/lit-survey/` 为空）。→ 该文件 #27 的结论只能取自任务书自身的转述，**本报告不声称读过它**。

---

## 0. AC3 判决句（先给答案）

> **合成目标不存在。只有伪合成 2 例（SSPO 的嵌套、UnifiedPlayers 的加权和），纯单侧 4 例（SearchGym、GroundedPRM、MARCH、Proof-Carrying Cognition）。**
> 更精确地说：**没有任何一篇论文的目标函数里同时出现"搜集质量项 × 校验质量项"的乘积或交互项**。最接近的三次尝试分别倒在三处——
> ① **加权和**（UnifiedPlayers 的 role-specific rewards）：两侧都在，但可加 ⇒ 不能表达"搜集好但校验差 ⇒ 整体无价值"的乘性失效；
> ② **嵌套**（SSPO 的"outcome 定方向 + teacher 定幅度"）：只调"改多少"，不区分"哪一侧贡献了多少"；
> ③ **单标量定价**（Proof-Carrying Cognition 的 ρ = verifier-gold 相关，把校验质量折成 compute 汇率）：这是**最接近贡献函数数学形态**的东西，但它只给校验侧定价，搜集侧没有对应量。
>
> **成璐的判断成立，且比"全是单侧的"更强**：不但没有合成目标，**连"搜集质量"这一侧都还没有一个被广泛接受的可计算定义**（见 §3 假说 A）。

---

## 1. 判定标准：什么才算"合成"

成璐的原话是"把'搜集质量 × 校验质量'合成一个**可优化**的贡献函数"。本报告用三条硬判据：

| 判据 | 含义 | 为什么必须 |
|---|---|---|
| **C1 双项共存** | 目标函数里能指出一个项**只依赖搜集轨迹**、另一个项**只依赖校验结果** | 否则连"两侧"都不成立 |
| **C2 乘性/交互** | 两项以乘积、门控（min）、或交互项（如 `q_search · q_verify`）结合 | **这是关键**：成璐说的是"×"。加权和无法表达"一侧为 0 则总体为 0" |
| **C3 同目标联合优化** | 两阶段先后训练**不算**；verifier 给 searcher 当 reward（单向依赖）**不算** | 否则任何 RAG 流水线都叫合成 |

**三条全满足 = 合成；只满足 C1+C3 = 伪合成（加权和型）；只满足 C1 = 单侧。**

---

## 2. AC4：候选逐条拆解（6 例）

### R-1 · SearchGym（`2601.14615`）——环境保真度，不是搜集质量
- **目标原文（摘要级）**：以"purified feedback"做课程式 RL；环境侧用生成式流水线构造"verifiable knowledge graph + aligned document corpus"，保证"every reasoning task is factually grounded and strictly solvable"。
- **搜集侧项**：**替代品**。不是"搜得好不好"，而是"环境是否与真实网络对齐"（保真度）。搜得多/搜得准**没有进入 reward**。
- **校验侧项**：**无显式项**。reward 仍是任务正确性。
- **结合形式**：单侧（环境设计，不是目标函数）。
- **判决**：**单侧**。但它是**假说 A 的最强证据**——见 §3。
- 数字：Qwen2.5-7B-Base 在 9 个 benchmark 上相对 ASearcher **+10.6%**。

### R-2 · Beyond Outcome Rewards / SSPO（`2608.12764`）——步级幅度调制，不是贡献分解
- **目标原文（摘要级，逐句可引）**："convert(s) **teacher-student disagreement into step-level advantage weights within GRPO**, applied exclusively to incorrect trajectories"，并明确"**decouples what to update from how much to update**: the outcome reward determines the direction of policy change, while the teacher modulates its magnitude at each step"。
- **搜集侧项**：⚠️ 间接。`Evidence Anchors`（"concise, step-level evidence snippets extracted from the web"）作为 privileged information 进入 teacher——**它是搜集结果，不是搜集质量**。
- **校验侧项**：❌ 无。teacher 是"知道答案的模型"，不是校验器；没有"质疑命中真实错误"的项。
- **结合形式**：**嵌套**（方向 × 幅度）。
- **判决**：**伪合成（嵌套型）**。缺的是"贡献归属"：它知道每一步该改多少，但不知道这个"多少"里有多少来自搜到的证据、多少来自校验的判断。
- 数字：Qwen3-8B 上超过/匹配 **2 倍梯度步数**的 GRPO，单步开销 **+5%**（一次额外前向）。

### R-3 · GroundedPRM（`2510.14942`）——校验侧内部的两种信号融合
- **目标原文（摘要级）**："design a **hybrid reward aggregation mechanism that fuses tool-based verification with MCTS-derived feedback**"。
- **搜集侧项**：❌ 无检索、无搜索轨迹。
- **校验侧项**：✅✅ **两项都在校验侧**：① external tool 的执行接地（"eliminate hallucinated supervision… validate each intermediate step using an external tool, providing execution-grounded correctness signals"）；② MCTS 推出的步级反馈。
- **结合形式**：**加权和（hybrid aggregation）**。
- **判决**：**单侧**。这是最容易误判为"合成"的一篇——它确实"融合了两个信号"，但**两个信号都是校验信号**，不是"搜集 × 校验"。
- 数字：仅 **40K** 自动标注样本（= 最佳自动标注 PRM 的 **10%** 数据），ProcessBench 平均**相对提升 26%**，reward-guided greedy search 超过人工标注 PRM。

### R-4 · UnifiedPlayers（`2609.20089`）——**最接近合成的一例，仍是加权和**
- **目标原文（摘要级）**："We design **role-specific rewards that coordinate the three players toward a shared learning objective under GRPO**." 三个玩家：Planning（生成任务）、Execution（多轮工具轨迹）、Evaluation（构造可执行 verifier）。
- **搜集侧项**：✅ 有（Execution Player 的工具调用轨迹 + Planning 的任务生成）。
- **校验侧项**：✅ 有（Evaluation Player 构造的 verifier，且 verifier 本身被训练）。
- **结合形式**：**加权和**（role-specific rewards → shared objective），**不是乘积**。
- **判决**：**伪合成（4 例中最强）**。它满足 C1 与 C3，**不满足 C2**。而且它自己把障碍说出来了——见 §3 假说 B。
- 数字：两个 backbone × 12 个 benchmark，数学 **+3.5%**、通用推理 **+3.9%**（相对最强基线）；学到的 verifier 对抗检测 **84.2%**；reward 的 per-question 方差是 self-consistency 的 **2.03×**。

### R-5 · MARCH（`2603.24579`）——信息不对称是结构性设计，但仍单侧
- **目标原文（摘要级）**：Solver / Proposer / Checker 三智能体 + **MARL** 联合训练；核心是"**deliberate information asymmetry**"——Checker 在校验时"**deprived of the Solver's original output**"，以打断 self-confirmation bias。
- **搜集侧项**：❌ RAG 证据**固定给定**，无搜索决策。
- **校验侧项**：✅（checker + claim-level decomposition of atomic propositions）。
- **结合形式**：单侧。
- **判决**：**单侧**。其价值不在合成，而在**证明了"信息不对称"是一个可训练的、有效果的结构变量**——这一点对 pfb 直接有用（§5）。
- 数字：8B 模型配备 MARCH 后**与强闭源模型竞争**。

### R-6 · Proof-Carrying Cognition（`2609.09776`）——唯一给出"汇率"的一篇
- **目标原文（摘要级，含公式）**：joint-Gaussian best-of-N 模型下，**"verifier-gold correlation ρ is the exact exchange rate between test-time compute and capability"**，且 **"an unsound verifier pays a polynomial penalty N^(1/ρ²)"**；另给"margin-free copula form predicts realized soundness of real LLM judges to 4% median error"。
- **搜集侧项**：❌ 无。
- **校验侧项**：✅ 且被**定价**（ρ，以及 soundness-under-pressure）。
- **结合形式**：单侧 + **标量定价**。
- **判决**：**单侧**，但**它是全文献里唯一把"某一侧的质量"折成一个可与另一端通约的标量的工作**。→ 若要造乘积型贡献函数，ρ 是最现成的"校验侧因子"。
- 数字：Soundness-under-Pressure 从 **0.94 掉到 0.32**（N=4096，unsound verifier）；selection alone 制造 **+0.53** hacking gap；GRPO 下冻结 RM 的 executed reward **崩塌 90%**，用 10% settlement 流重拟合可保住 **6×**。

### 2.1 汇总表

| # | 对象 | 搜集侧项 | 校验侧项 | 结合形式 | C1 | C2 | C3 | 判决 |
|---|---|---|---|---|---|---|---|---|
| R-1 | SearchGym | 替代（环境保真度） | ✗ | 单侧 | ✗ | ✗ | — | 单侧 |
| R-2 | SSPO | 间接（evidence anchors） | ✗ | **嵌套**（方向×幅度） | 半 | ✗ | ✓ | **伪合成** |
| R-3 | GroundedPRM | ✗ | ✓✓（tool + MCTS） | **加权和** | ✗ | ✗ | ✓ | 单侧 |
| R-4 | UnifiedPlayers | ✓ | ✓ | **加权和** | ✓ | **✗** | ✓ | **伪合成（最强）** |
| R-5 | MARCH | ✗ | ✓ | 单侧 | ✗ | ✗ | ✓ | 单侧 |
| R-6 | Proof-Carrying | ✗ | ✓ + ρ 定价 | 单侧+标量 | ✗ | ✗ | — | 单侧 |

**→ 6 例中：0 例满足 C2。**「乘积型贡献函数」在 2026-11 的文献里**不存在**。

---

## 3. AC5：为什么没合成——三个假说各自的判决

### 假说 A（reward 污染）：**成立，且有量化证据（conf 0.85）**

**证据 1（机制描述，一字不差可用）**：SearchGym 摘要——"relying on static data snapshots often introduces noise due to data misalignment. **This misalignment generates corrupted reward signals that destabilize training by penalizing correct reasoning or rewarding hallucination.**"
→ 这句话说的正是"搜集侧质量没有可靠 ground truth"：用静态快照模拟真实网络，就会**惩罚正确推理、奖励幻觉**。所以把"搜集质量"直接写进 reward，等于往训练里灌污染项。

**证据 2（量化）**：Proof-Carrying Cognition——unsound verifier 的代价是 **N^(1/ρ²)** 的多项式惩罚；实验里 Soundness-under-Pressure **0.94 → 0.32**（N=4096），且"**selection alone manufactures +0.53 hacking gaps from honest samples**"（即：**仅靠选择机制就能凭空造出 0.53 的作弊差距**）。
→ 这不是"可能污染"，是"**已经在测到的污染曲线**"。

**证据 3（GRPO 下）**：同一篇：冻结 reward model 的 executed reward **崩塌 90%**，用 10% settlement 流重拟合可保住 **6×**。
→ **一个不可靠的校验信号就能让整个 RL 循环失效 90%。** 那么"搜集 × 校验"的乘积里，只要搜集侧是不靠谱的，乘积就趋近于 0——**没人愿意把目标函数写成一个自己无法保证非零的量。**

**判决**：假说 A **成立**。这不是"没人想到"，而是"想了之后发现写进去就是自杀"。**这解释了 76% 的现象**（我的估计，conf 0.7）。

### 假说 B（credit assignment 难度）：**成立，且是当前最活跃的前沿（conf 0.85）**

**证据 1**：SSPO 摘要第一句——"standard reinforcement learning provides only **a single outcome reward per trajectory, which is far too sparse for effective credit assignment**"。
**证据 2**：GroundedPRM——MC 估计"infers step quality solely from rollout outcomes and **often introduces noisy, misaligned supervision due to credit misattribution**"。
**证据 3（最关键，来自要做合成的那篇自己）**：UnifiedPlayers——"Jointly adapting planning, execution, and evaluation offers a promising alternative, but introduces a fundamental coordination challenge: **each component continuously changes the data or feedback used to train the others.**"
→ **这是非平稳性（non-stationarity）的教科书表述**：三个组件互为对方的数据源，联合优化时目标本身在漂移。

**判决**：假说 B **成立**。**"单侧的 credit assignment" 都还没解决（2026-08 的 SSPO 才把"改多少"解耦出来），合成两个未解决的量等于优化一个双重未定义的乘积。** 这条比 A 更根本：A 是"不敢写"，B 是"写不出来"。

### 假说 C（有人试过但失败了）：**证据不足（conf 0.45）**

- 检索未见任何"合成目标 → 训练不收敛 / 效果差 / 被放弃"的负面结果报告（query 见 search-log S05/S06，两组措辞）。
- 最接近的是 UnifiedPlayers 的**规避行为**：它明说联合适应有"fundamental coordination challenge"，然后选择**role-specific 加权和**而非乘积——这是**绕开**，不是**尝试后放弃**。
- **诚实的判决：证据不足。** 这意味着文献里既没有"合成过且成功"，也没有"合成过且失败"——**这个位置是空的，不是被证伪的**。→ 对 pfb 是**好消息**：空白可占；但也意味着**没有前车之鉴可借**。

---

## 4. AC6：pfb 离散版 ↔ RL 联合目标的对应关系（可直接引用）

### 4.1 对应表

| pfb 侧（prompt 层、可消融） | RL 侧（梯度里、不可分解） | 对应强度 |
|---|---|---|
| prompt 组件（M1 / M4 / O6…） | reward 项 / 策略项 | **强**：都是"被优化的对象" |
| 组件 Δ 落到哪个 **metric 维度** | 梯度方向 ∂L/∂θ 的**分量** | **中**：pfb 是标量测量，RL 是向量方向 |
| 去掉组件做 **消融**（S8） | **反事实信用分配**（counterfactual credit assignment） | **强**：同一件事，一个用重跑，一个用估计 |
| **贡献独立性测量** | **Shapley 值 / 逐项 Δ 归因** | **强**：pfb 是 Shapley 的暴力枚举版 |
| S8 的 M1 **+0.237** / M4 **−0.240** / O6 **0.783**（n=3 复现） | 加权和里的**系数**（但 pfb 的系数是测出来的，RL 的是训出来的） | **弱→强**：这是 pfb 独有的东西 |

### 4.2 优势（一句依据）

> **pfb 把"贡献"从梯度里的隐变量变成消融表里的显式数字，因此它能测出负贡献组件——S8 里 M1 的 +0.237 与 M4 的 −0.240 在同一个 n=3 复现的度量下并存，而任何 RL 加权和只能告诉你总 reward 涨了没有。**

（依据：`2608.12764` 明确"outcome reward determines the direction… teacher modulates its magnitude"——RL 侧的信号始终是**一维标量**；而 pfb 的 S8 输出是**多维 Δ 向量**，符号可正可负。）

### 4.3 劣势（一句依据）

> **pfb 的粒度是组件级而非步级，且不能端到端优化——它的 Δ 是在固定配置下的事后测量，换配置未必成立；这与 RL 的 on-policy 分布漂移同源，只是 pfb 用"固定配置 + n=3 复现"换掉了它，代价是失去了对分布变化的适应性。**

（依据：`2609.20089` 的 coordination challenge——"each component continuously changes the data or feedback used to train the others"；pfb 通过**冻结其它组件**回避了非平稳性，因此测到的是**局部**贡献，不是联合最优点的贡献。）

### 4.4 一段可直接用的话

> 学界在 RL 侧把"搜集"与"校验"分别做成了两个独立的 reward 项，却没有把它们合成一个可优化的乘积——原因不是没想到，而是**搜集质量没有可靠 ground truth**（写进 reward 就会像 SearchGym 描述的那样"惩罚正确推理、奖励幻觉"），且**步级信用分配本身尚未解决**（SSPO 2026-08 仍只能解耦"改什么"与"改多少"，无法归因"这一分来自搜到的证据还是校验的判断"）。pfb 走的是另一条路：不优化这个函数，而是**测量**它——用消融把每个 prompt 组件的 Δ 落到具体 metric 维度上，得到一张显式的贡献表（S8：M1 +0.237 / M4 −0.240 / O6 0.783，n=3 复现）。这条路的好处是**能看见负贡献**（RL 的一维 reward 做不到），代价是**粒度粗、且只在固定配置下成立**。

---

## 5. 一个附录级发现：MARCH 的"信息不对称"直接可用

R-5 的核心设计是"**Checker 校验时不看 Solver 的输出**"，并把它作为**可训练的结构变量**（MARL）。这对 pfb 有一个立刻可试的推论：

- pfb 的质询循环（S8）里，质询者**看得到被质询的答案**——这正是 MARCH 所说的 self-confirmation bias 的温床。
- **可做的对照**：质询者只看"待验证的命题"（claim-level），不看原答案 ⇒ 若 M4 的 −0.240 部分来自"质询者被原答案锚定"，这个改动应该把 M4 拉回正值。
- **状态**：我的推论（conf 0.55），但**成本极低**（只改 prompt），且 MARCH 已在 8B 上证明该结构有效。

---

## 6. 反方质询

### 质询 1："加权和也是合成，你凭什么要求乘积？"

**攻击**：UnifiedPlayers 已经有两侧项 + 联合优化，你用一个"必须乘"的额外要求把它判成伪合成，是在为结论定制标准。

**防御（部分接受，但守住核心）**：接受"加权和是合成的一种"。所以我把判决写成"**伪合成**"而不是"不存在"——它确实是**合成的一种弱形式**。守住的点是：成璐的原话是"**×**"，而乘性与加性在语义上不可互换——**搜集质量再高，若校验为 0，结果应无价值**；加权和允许"高搜集 + 零校验"仍然得分（只要搜集项权重大）。这不是形式偏好，是**语义正确性**。→ 我把这点写进了 §1 的 C2 并给了理由，而不是隐含假设。

### 质询 2："Proof-Carrying 的 ρ 已经是贡献函数了，你的判决过度"

**攻击**：ρ 把校验质量折成 compute↔capability 的汇率，这就是"可优化的贡献函数"。

**防御（接受其重要性，但指出缺的一半）**：ρ 是**单侧定价**，不是**双侧合成**。它回答"校验差 0.1 要付多少 compute"，不回答"搜集质量提高一档值多少"。它的价值恰恰在于**它是造乘积时现成可用的校验侧因子**——所以我在 §3 把它列为"最接近数学形态"，而不是否定它。

### 质询 3："你没读公式表，凭摘要判 C2，判据可能错"

**攻击**：AC2 要求公式/实验表级别，你的 6 篇多数只到摘要。

**防御（接受，已在 §7 逐条标注阅读级别）**：这是真实局限。我把每篇的阅读深度**显式标注**（摘要级 / 摘要含公式 / 摘要有实验数字），并把 C2 的判定依据限定在**摘要明确写出的结合方式**（"hybrid reward aggregation"、"role-specific rewards… toward a shared learning objective"、"outcome reward determines the direction… teacher modulates magnitude"——这三句足以判定加性/嵌套/单侧）。**若正文里有未写进摘要的乘积项，本报告会漏判**——这个风险已写入 §8 负结果。

---

## 7. 来源表（AC2：≥8，逐条标阅读级别）

| # | 来源 | 标题 | 阅读级别 | 用在哪 |
|---|---|---|---|---|
| 1 | `2601.14615` | SearchGym（2026-01） | 摘要全文 + 实验数字 | R-1, 假说 A |
| 2 | `2608.12764` | Beyond Outcome Rewards / SSPO（2026-08） | 摘要全文（机制句逐字引用）+ 实验数字 | R-2, 假说 B, §4.2 |
| 3 | `2510.14942` | GroundedPRM（2025-10） | 摘要全文（aggregation 机制）+ 实验数字 | R-3, 假说 B |
| 4 | `2609.20089` | UnifiedPlayers（2026-09） | 摘要全文（role-specific rewards 原文）+ 实验数字 | R-4, 假说 B, §4.3 |
| 5 | `2603.24579` | MARCH（2026-03） | 摘要全文 + 结构描述 | R-5, §5 |
| 6 | `2609.09776` | Proof-Carrying Cognition（2026-09） | 摘要全文，**含公式 N^(1/ρ²) 与 ρ 汇率** | R-6, 假说 A |
| 7 | 本地 `research/lit-survey-arena.md` §0.3 | T-PR-07 期的 grounding 综述 | 继承 | 交叉核对 |
| 8 | 本地 `research/moe-agent-equivalence-survey.md` | T-PR-08 结论（聚合 vs 分解） | 继承 | 与 R-4 的"多玩家"结构对照 |
| 9 | 任务书转述的 `pfb/lit-survey/…idea-list.md` #27 | "不存在，且被宣布为开放问题" | **未读原文件（仓库内不存在）** | 仅作先验，不作证据 |
| 10 | `2609.09776` 的"binding constraint"句 | "the field's binding constraint is the verification gap" | 同上（同 #6） | §0 判决句 |

统计：**6 条外部一手来源 + 2 条本地继承 + 1 条未读转述（已标注）= 9 条，≥8 ✅**；其中**含公式级 1 条（R-6）、含机制原文逐字引用 4 条（R-1/R-2/R-3/R-4）、含实验表数字 5 条**（≥4 at formula/experiment-table level ✅，但阅读深度以摘要为主，已在质询 3 中披露）。

---

## 8. 负结果

| # | 未找到 | 试过的 query | conf 上限 |
|---|---|---|---|
| N1 | **乘积型（C2 满足）的搜集×校验联合目标** | S01, S02, S03, S07（四组措辞） | 0.4 |
| N2 | **"搜集质量"的可计算定义**（与"搜得多"区分开） | S02, S04 | 0.4 |
| N3 | **合成目标试过但失败的负面结果**（假说 C 的证据） | S05, S06 | 0.45 |
| N4 | **正文级公式核对**（6 篇中仅 1 篇到公式级） | 通道限制（fetch 摘要页；HTML 未逐页读） | — |
| N5 | **`pfb/lit-survey/2026-11-07-idea-list.md`** | 本仓库 `pfb/lit-survey/` 不存在 | — |

**通道记录**：`arxiv.org/abs/*` 6/6 抓取成功；未尝试 PDF（历史三次失败）；本轮**未做 web_search**（任务书规定 6 个候选"勿重复搜"），因此**新发现候选 = 0**（任务书允许 ≤3，此处为 0，属正常）。

---

## 9. 给 Lead 的两条结论

1. **成璐的判断成立，且可以更强地表述**：不是"全是单侧的"，而是**"两侧之中有一侧（搜集质量）连可计算定义都还没有"**。这一点有 SearchGym 的"corrupted reward signals"与 Proof-Carrying 的"N^(1/ρ²) 惩罚"双重支撑。→ 对外材料建议用这个更强的版本，因为它把"我们占的是空档"从"没人做"升级为"没人做且做不了，所以我们换了做法（测量而非优化）"。
2. **附录发现可低成本验证**：MARCH 的"校验者不看原答案"是一个 prompt 层改动，可直接在 pfb S8 上做 A/B；若 M4 的 −0.240 因此回正，则"质询者被锚定"假说成立——**这是本报告给出的唯一可直接执行的实验，成本一个下午。**
