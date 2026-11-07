# T-PR-07：长程洞察的可分解性调研（Q1–Q4）

> origin: ai · 2026-11-07 · Lead: 成璐数字分身 · 执行: Arena agent
> 仓库: `dd2003-460/paradigm-routing` · 分支: `arena/62fe3fd4-paradigm-routing`
> 任务书: `tasks/T-PR-07-long-insight-decomposability.md`
> 任务性质: **纯文献调研**，无本地实验
> 立场声明: 本报告要回答的是机制问题（"洞察能不能被切开"），不是要证明"能切开"。
> 判决依据不是文献数量，而是**有没有人在同一任务同一预算下量过**；没有量过的地方一律标负结果。

---

## 0. TL;DR（给 Lead 的三句话）

1. **"长步长洞察"不是原子操作，它的正确分解单位是依赖图上的 k 跳链；而 k 跳链的 token 成本几乎正好是 k。** `2602.02909`（ICML '26）在 BAPO 模型内**证明了 token 下界**：全局聚合类（MAJORITY / MATCH3n）要 Ω(n) 步、可匹配上界 O(n)（Table 1 / Thm 4.1–4.3, 5.6–5.8）；而**指针追踪（pointer chasing）虽然是 BAPO-hard，其 token complexity 却随指针链长度而非输入规模增长**。→ **洞察属于后者：k 跳要 k 步，不多不少。** k 跳链有两条可互换的执行路线：把每一跳写进 context（k 步串行），或让 attention 在 context 内并行跳完（深度 Θ(log k)，Sanford et al. `2402.09268` §4）。所以"能不能分解"的分界线不是步数，而是**中间节点是否已经在 context 里**。
2. **Q1 的判决是"部分解决"，而且真正被解决的那部分不是成璐想问的那部分。** 已被实验证明可分解的是"**给定**原子步骤后，小模型能执行"（`2210.11416`：770M T5 用 80% 数据打赢 few-shot 540B PaLM）；没有被证明的是"**发现**这些原子步骤"。而所有跨域证据都指向后一半失败：`2510.05432`（AInstein）里模型解题成功率 >70% 但严格复现已发表解法 <19%，失败模式被作者命名为 *parametric knowledge boundary*——**恰恰是跨域类比迁移**。
3. **瓶颈不在"切不切得开"，在"切开后谁来验每一步"。** 三条独立证据链收敛到同一处：SCORE `2407.13692`（small LM 的 refiner 可迁移、verifier 不可迁移，"bottlenecked by the verifier rather than the refiner"）；PlanningBench `2605.20873`（GPT-5.4-medium Avg-pass 90.03% 但 All-pass 58.09%——局部每条都对，全局拼不起来）；Large Language Monkeys `2407.21787`（覆盖率随采样数 log-linear 上升，但多数投票/reward model 在数百样本后 plateau）。**这三条合起来是本任务最有价值的结论，也是与成璐原始直觉不同的地方**：她担心的是 ctx 不够长导致某一跳够不着；数据显示的是**每一步都够得着、但拼起来对不上、且没有可靠的选择器**。

**四子问题判决表（D2）**

| 子问题 | 判决 | 卡在哪（一句话） | conf |
|---|---|---|---|
| Q1 可分解性 | **部分解决** | "执行可分解"已证（蒸馏线）；"发现可分解"无正面证据，跨域类比是已观测的崩塌点 | 0.75 |
| Q2 ctx 下界 | **部分解决（比预期更靠前）** | **有任务内在的 token 下界**（BAPO：全局聚合类 Ω(n)，指针追踪类 Θ(链长)，`2602.02909`），也有资源相对下界（`CoT(t) ⊆ SPACE(t+log n)`）；缺的是"窗口长度 W → 可完成深度 D"的定量关系 | 0.75 |
| Q3 不可分解性 | **部分解决** | 三类不可分解性各有形式对应物，但 **pebbling game 未被接到 LLM CoT 上**——这是真实的工具缺口 | 0.65 |
| Q4 dense vs 显式搜索 | **部分解决** | 同题同预算 head-to-head 存在且互有胜负；**没有单一赢家**，crossover 由"难度 × verifier 质量"决定 | 0.7 |

---

## 1. 问题形式化与判据

### 1.1 把"长步长洞察"写成可检验的对象

成璐的原始表述是"一次跳跃把 A 领域结论连到 B 领域结论"。这个描述混了两件不同的事，必须先拆开，否则 Q1 无法判定：

设一个洞察 = 依赖图 $G$ 上从起点 $a\in A$ 到终点 $b\in B$ 的一条 k 跳路径 $a \to v_1 \to \dots \to v_{k-1} \to b$。

- **分解的可执行性（executability）**：给定 $\{v_1..v_{k-1}\}$，小模型能否逐步走完？——这是**计算**问题。
- **分解的可发现性（discoverability）**：$\{v_1..v_{k-1}\}$ 本身从哪来？——这是**搜索**问题。

两个问题的资源完全不同：前者吃串行步数与验证器，后者吃搜索预算与启发式。**本调研发现，文献对前者的回答是"能"，对后者的回答是"没有证据，且有反面证据"**。任何把两者混为一谈的"洞察可分解"结论都是无效的（这正是 §6 矛盾 #3 的解法）。

### 1.2 三档证据判据（不放宽）

| 档 | 定义 | 用法 |
|---|---|---|
| **已证明** | 定理形式给出，且条件写清（是否 conditional on 复杂度猜想） | 可直接作为判决依据 |
| **已实测** | 同一任务、同一预算下的对照数字 | 可作为判决依据，但需标注是否单一数据集 |
| **仅论证** | 只有 abstract / 二手转述 / 无对照数字 | 只能作旁证，不得支撑判决 |

### 1.3 conf 锚定规则（避免主观刷分）

- **0.85–0.95**：读到正文的定理编号/表格数字，且来源是一手 arXiv/会议版。
- **0.70–0.85**：读到正文数字但任务/设置单一，或结论需跨两处拼。
- **0.50–0.70**：只有摘录或二手转述，但与其他来源方向一致。
- **≤0.45**：只有摘要级信息，或与其他来源冲突未解决 → 同时必须进 §9 负结果清单。

### 1.4 通道情况（真实记录，不粉饰）

本轮 **arXiv abs/html 页面直访可用**（`fetch_page` 成功取得 `2402.12875` HTML 与 `2402.09268` HTML 正文），**PDF 直链失败**（`arxiv.org/pdf/*` 返回 Failed to fetch），**web_search 可用但质量参差**（泛化 query 大量返回博客/二手站，必须靠 arXiv 定向 query 才拿到可引 id）。完整 query 与命中见 `research/long-insight-search-log.json`。

> 一条实操教训（已写入 02 阶段工件）：**记忆中的 arXiv 编号会错**。本轮我按记忆把 Sanford/Hsu/Telgarsky 记成 `2402.05369`，实访该 id 是 *Noise Contrastive Alignment*（对齐方向论文）；正确编号是 `2402.09268`。凡未实访的编号一律不写进报告——这条规则在本轮拦截了 1 次张冠李戴。

---

## 2. Q1：可分解性——frontier 的长链洞察能否被人工分解后被小模型复现？

### 2.1 正面证据：分解的**执行**确实可以下放（3 条独立来源）

**（1）`2210.11416` Distilling Step-by-Step（Hsieh et al., Findings of ACL 2023）**
做法：从 LLM 抽取 rationale 作为额外监督信号，与标签一起做多任务训练小模型。核心数字（ACL Anthology 正文摘要+结论）：**770M T5 用 80% 的数据打赢 few-shot prompted 540B PaLM**，而同样 T5 用 100% 数据做标准 finetune 仍追不上。三个发现中第二条明确写"用显著更小的模型规模超过 few-shot prompted LLM"。conf **0.85**。
读法注意：这条证明的是**老师给的原子步骤可被学生执行**，不是"学生能自己想出步骤"。它对本任务的价值是划出 Q1 的一半边界。

**（2）SCORE / `2407.13692` Small Language Models Need Strong Verifiers to Self-Correct Reasoning（ACL Findings 2024）**
这篇是 Q1 里最锋利的一篇，因为它把"分解"拆成了 verifier 与 refiner 两个角色，并量了谁可迁移：
- 用同一批 small LM 自生成 critique 数据训练 refiner，**refiner 可迁移**；换不同 verifier，最终准确率差异巨大（正文 §Experiments，逐 verifier 对比）。
- 接 GPT-4 verifier：Gemma-7b-it 五个数据集平均 **+8.3**。
- 论文原话（正文结论段）："the final accuracies vary a lot among different verifiers… **bottlenecked by the verifier rather than the refiner**"；并引 Gu et al. 2024 / Oh et al. 2024 / West et al. 2023 说明"模型能解题但不能验证自己的推理"。
- 更狠的一句：**把错误位置直接告诉小模型，它能修；让它自己找错，几乎不涨**（该对比来自二手综述转述，conf 0.6，故只作方向性引用；一手支持是上面 Fig.3 混淆矩阵：gpt-4-verifier + SCORE-refiner 更容易把错的改对而不是把对的改错）。

conf（一手部分）**0.85**。→ **Q1 的第一个结构性结论：分解产出的原子步骤可由小模型执行；但"这一步对不对"的判断不可下放。**

**（3）`2412.06769` Coconut（COLM 2025）**——见 §5.2，它同时是 Q1 与 Q4 的证据：连续思考替代显式 CoT 后，**ProsQA 97.0 vs CoT 77.5**（token 14.2 vs 49.4），但 **GSM8K 34.1 vs CoT 42.9**。说明"步骤显式化"不是普遍占优，任务结构决定一切。conf **0.85**。

### 2.2 反面证据：分解在哪些任务上崩塌（4 条独立来源）

| 崩塌类型 | 来源 | 现象 | conf |
|---|---|---|---|
| **跨域类比迁移**（正是成璐问的那种跳） | `2510.05432` AInstein | 1,214 篇 ICLR 2025 论文题，模型 >70% 可行解，但严格复现已发表解法 **<19%**；失败被命名为 *parametric knowledge boundary*："模型在熟悉的方法论疆域内可靠重建，**当解法需要跨领域类比迁移时失败**"（正文 §6 Discussion；附录 L.3 给了 CPU 投机执行 → AI agent 加速的具体漏答案例） | 0.8 |
| **全局一致性** | `2605.20873` PlanningBench | GPT-5.4-medium **Avg-pass 90.03% / All-pass 58.09%**；Seed-2.0-pro-high 84.02 / 44.33；且 All-pass 随约束条数下降（GPT-5.4-xhigh 2–6 项 63.4% → 15+ 项 40.0%）。作者结论：失败"mainly reflect constrained reasoning and **global consistency** limitations rather than formatting issues" | 0.85 |
| **长程规划深度** | `2505.12135` LLM-BabyBench | "simulation accuracy is close to saturated while **planning completion collapses as the required plan grows longer**"；非推理模型在 ~15 步以上近乎归零；关键定性结论：**模型知道自己该做什么，却排不出步骤**（§4.3 "models know what to do but can't do it"），且 **Decompose 任务在更长的 horizon 上直接失效** | 0.8 |
| **并行子任务** | `2505.18642` Skip-Thinking | chunk-wise CoT 蒸馏：小模型在需要**并行的多子任务**推理的 LLC 数据集上不升反降，串行可分解的任务上才受益 | 0.55（仅摘录级，方向与上三条一致） |

**合起来看**：分解失败的四种形态里，三种（全局一致性、长程规划、并行子任务）都是"结构"问题，只有第一种（跨域类比）是"发现"问题。而**成璐问的那种"一次跳跃"恰好落在唯一没有被解决的那一格**。

### 2.3 Q1 判决

> **部分解决。** "已给定原子步骤 → 小模型可执行"有正面、可复现的实测支持（`2210.11416`、`2407.13692`），conf 0.85。**"原子步骤可被自动发现"没有正面证据**，且跨域类比迁移是已被量化的崩塌点（`2510.05432`），conf 0.8。边界在：**分解把"计算"降级成功，把"搜索"留给了一个我们还没有的 verifier**。
>
> 卡在哪：没有任何论文做过"把 frontier 模型的一条长步长洞察人工切成原子步骤，再让 7B 模型照做"的**同题同预算**对照。这条实验空缺是真实的（§9 N1）。这也是本任务唯一"听起来该有、但确实没有"的实验。

---

## 3. Q2：ctx 下界——存在"至少需要 k 个推理 token / k 层依赖"的下界吗？窗口是硬约束吗？

> **本节包含一次自我纠正。** 我第一轮检索（前 15 条 query）后曾写下"不存在任务内在的常数 k 下界"，那是**错的**。在针对"minimum reasoning budget"补做定向检索时命中了 BAPO 线（`2602.02909`）与 token complexity 线（`2503.01141`），它们给的**正是任务内在下界**。原判断已撤回，过程记录在 §3.1 末尾与 search-log 的 `self_corrections` 字段。这条纠正本身就是本报告的 D5 证据：**"没找到"必须写成"这几条 query 下没找到"，不能写成"不存在"。**

### 3.1 任务内在下界：**存在**（BAPO / token complexity 线）

**`2602.02909` Tomlinson, Schnabel, Swaminathan, Neville, *Reasoning about Reasoning: BAPO Bounds on Chain-of-Thought Token Complexity in LLMs*（ICML '26, 31 页）**
做法：扩展 bounded attention prefix oracle（BAPO）模型——一个刻画"解题需要多少信息流过模型"的抽象——到多步 CoT（BAPO-CoT），再证 token 下界。**Table 1（完整摘录）**：

| 问题 | 下界 | 上界（构造） | 另一上界 |
|---|---|---|---|
| MAJORITY | **Ω(n)**（Thm 4.1） | O(n log n)（Thm 5.6） | n+1（Prop 5.4） |
| MATCH3n（三元素匹配） | **Ω(n)**（Thm 4.2） | O(n)（Thm 5.7） | n+1（Prop 5.4） |
| REACHABILITY | **Ω(m)**，m=边数（Thm 4.3） | O(n²)（Thm 5.8） | m+3（Prop 5.4） |
| 任意可判定语言 | — | O(t(n)·max(n,s(n)))（Thm 5.5） | n+1（Prop 5.4） |
| 任意语言 | — | **（open）** | n+1（Prop 5.4） |

定理原话（§4）："**Any constant-bandwidth BAPO-CoT for MAJORITY on length-n inputs uses Ω(n) CoT tokens**, so the token complexity of MAJORITY is at least Ω(n)."
置信度关键点：这是**在其模型内**的无条件下界（只依赖"每个 token 的带宽为常数"这个假设），不是 conditional on P≠NP 之类的猜想；但它的解释力受 BAPO 抽象本身限制（§7 B7）。

**最关键的一条不是 Ω(n)，而是反例那一句**（§4）：论文证明**指针追踪（pointer chasing）虽然是 BAPO-hard，其 token complexity 却随指针链长度而非输入规模增长**。→ 这意味着"token 下界"不是一个统一常数，而是**按问题结构分成两类**：
- **全局聚合类**（majority / match-3 / 需要看到全部输入的约束检查）→ **Ω(n)，不可压缩**；
- **依赖链类**（reachability / pointer chasing / k 跳）→ **Θ(链长)**，与输入规模脱钩。

**`2503.01141` Lee, Che, Peng, *How Well do LLMs Compress Their Own CoT? A Token Complexity Approach*** 给了这条线的实证侧：提出 **token complexity 假设**（Assumption 1：对问题 i 和模型 π 存在阈值 τ^π_i，链长超过就成功、不足就失败），并实测**在问题级别存在尖锐阈值**——"across all prompts, the LLM correctly solves the question **if and only if** the response length is above a certain threshold"。数字：**token complexity 单独就能以 94% 准确率预测不同 CoT 压缩策略的表现**。conf 0.8（正文级，PDF 摘录）。

**实证侧的第二条**（`2602.02909` 自己的实验）：frontier reasoning 模型在这三类任务上**近似线性**增长 reasoning token；把预算压到理论下界以下，**准确率随问题规模崩塌到随机水平**。conf 0.8。这一条把"下界"从纸面推到了可观测行为。

> **自我纠正说明**：我最初的 5 条 query 都没有命中这条线，因为它们问的是"circuit complexity / pebbling / lower bound for transformers"，而这条线的关键词是 **"token complexity" / "reasoning budget" / "how many tokens"**——**下界的证明工具是通信复杂度，不是电路复杂度**。这就是我第一轮漏检的原因，也是本报告给后续研究者最重要的一条检索教训（§9 N6）。

### 3.2 资源相对下界：也存在，且与 §3.1 **互补而非冲突**

**`2310.07923` Merrill & Sabharwal（ICLR 2024）** 主包含式（正文 Equation 1）：

$$\mathrm{TIME}(t(n)) \subseteq \mathrm{CoT}(t(n)) \subseteq \mathrm{SPACE}(t(n)+\log n) \subseteq \widetilde{\mathrm{TIME}}(t(n)^2+n^2)$$

三个 regime：$t=\Theta(\log n)$ 只到 **L**（论文自陈"没有找到任何具体推理问题是 log 步能帮上忙的"）；$t=\Theta(n)$ 可模拟任意自动机（NC¹），落在 context-sensitive 内；$t=\mathrm{poly}(n)$ **恰好等于 P**。conf 0.85。

**`2402.12875` Li, Liu, Zhou, Ma（ICLR 2024）**：Thm 3.1 常数精度常数深度无 CoT ⊆ **AC⁰**；Thm 3.3 **T 步 CoT ⇔ 可表达任何 size-T 布尔电路**，$T=\mathrm{poly}(n)$ 得 **P/poly**；推论：线性步数即可算所有正则语言（含 $S_5$ 上的非可解群复合）。conf 0.85。

**两条线的关系（本节的核心消解，与 §6.2 矛盾 #4 是同一件事）**：

| 方向 | 工具 | 给出的东西 | 例子 |
|---|---|---|---|
| **下界** | **通信复杂度**（每个 token 只能搬运常数比特 ⇒ 需要多少 token 才能把信息运进/运出） | Ω(f(n)) | `2602.02909` Thm 4.1–4.3 |
| **上界** | **电路模拟**（t 步能模拟 size-t 电路） | O(g(n)) | `2402.12875` Thm 3.3、`2310.07923` Eq.1 |

**它们不矛盾，因为量的是不同的东西**：上界说"给你 t 步你能做到什么"；下界说"这个任务的信息量决定了你至少要多少步"。二者夹出的是**真实的 token 复杂度带**。我第一轮只看到上界一侧，就误推到"没有下界"——这是典型的**单侧证据外推**。

### 3.3 把两条下界合起来读"洞察"：k ≈ 依赖链长度，不是输入规模

综合 §3.1 的两类结构与 §3.2 的上界，可以得到一个对成璐问题直接有用的判断（**我的综合，非引用结论，conf 0.65**）：

> 一条"把 A 领域结论连到 B 领域结论"的洞察，若其结构是**链式**（$a\to v_1\to\dots\to b$，每一步只需局部信息），则其 token 下界是 **Θ(k)**，k = 链上跳数——**不是输入规模，也不是"领域跨度"**。若其结构含**全局约束**（"这个 B 必须同时满足 A 的全部条件"），则会跳到 **Ω(n)** 一档，此时**任何压缩都会随规模增长而失败**（`2602.02909` §8 的原话："for tasks whose minimal required reasoning scales as Ω(n), any compression method that enforces an input-size-agnostic budget will eventually fail as n grows"）。

**这正好把 §1.1 的二分落到了量化层面**：成璐直觉里的"长步长"如果是**链式跳转**，它可以被切开且成本线性可控；如果是**全局一致性约束**，它不可压缩。**两种东西在直觉上都是"一次跳跃"，在复杂度上是两个不同的类。** 这是本报告对"边界在哪"的正面回答。

### 3.4 窗口是硬约束吗？——**分两条路线，答案相反**

- **串行路线（写 CoT）**：中间状态由模型写出、落在 context 里，**不受输入窗口限制，受生成长度限制**。依赖链可任意长，只要有地方放。
- **并行路线（不写，靠 attention 一次跳完）**：要求 k 跳路径上的中间节点**同时在窗口内**。此时窗口是**硬约束**。

`2402.09268` Sanford, Hsu, Telgarsky（ICML 2024）量化了并行路线：Thm 3.1（$R$ 轮 MPC ⇒ 深度 $O(R)$）/ Thm 3.4（反向）；Cor 3.3（连通性可用**对数深度**解）；Cor 3.5（该深度在 **MPC 猜想 Conjecture 2.4** 下最优）；§4（k-hop 诱导头：**$\Theta(\log k)$ 深度既必要又充分**，且训练模型经验上遵守同一阈值）。conf 0.85/0.8。

`2603.21676`（*Thinking Deeper, Not Longer: Depth-Recurrent Transformers*）从工程侧给了同一条轴的第三种支付方式：**vertically 叠层**（共享权重块在潜空间迭代），明确论证"每个水平推理步至少花 1 个 token，迅速耗尽窗口；32 层模型无论题多难都只做 32 层"。conf 0.6（预印本，单一来源，仅作旁证）。

**三条支付方式并列**：k 跳可以付 $k$ 个 token（串行）、付 $\Theta(\log k)$ 层深度（并行 attend）、或付 $R$ 次循环迭代（vertical，不占窗口）。**这是"窗口不是墙"的确切含义：换一种货币付即可。** `2605.30757`（本地 §G4）的"CoT=可扩展工作内存 vs 循环=固定小空间"是同一件事的理论表述，作为第二独立来源。

### 3.5 负结果（D5）：**"窗口长度 W → 可完成深度 D"的定量关系，仍未找到**

补做 3 条定向 query（`context window length limit reasoning chain depth quantitative relation`、`lost in the middle long chain`、`minimum reasoning budget ...`）后：**没有任何论文给出 $D_{\max}=f(W)$**。第三条第命中的是 token 复杂度线，它给的是 $f(\text{问题结构})$，**不含窗口变量 W**。最接近的三样东西都不构成答案：检索衰减研究（测信息定位，不测依赖深度）、Sanford 的 log-depth（测深度换并行，只要窗口装得下路径就与 W 无关）、`2605.30757`（只给空间类别的定性对应）。

因此：**"超过窗口的依赖链是否真的不可达"仍然没有直接答案**，conf 0.45，进 §9 N2。可用的最强间接结论仍是 §3.4 的路线二分：**串行路线把中间状态外置，所以窗口本身不是不可达性的来源**。

### 3.6 Q2 判决

> **部分解决（比我第一轮判断更靠前）。**
> **已解决**：① **存在任务内在 token 下界**（`2602.02909` Thm 4.1–4.3：全局聚合类 Ω(n)、可匹配上界 O(n)/O(n log n)/O(n²)，且指针追踪类为 Θ(链长)）；② **存在尖锐的经验阈值**（`2503.01141`：if-and-only-if 阈值，token complexity 预测压缩策略表现 94%）；③ **存在资源相对下界**（`2310.07923` Eq.1、`2402.12875` Thm 3.1/3.3）；④ 并行路线的深度需求为 $\Theta(\log k)$（`2402.09268` §4）。
> **未解决**：**窗口 W 与可完成深度 D 的定量关系不存在**（3 条定向 query，conf 0.45）。
> **卡在哪**：没有人把"窗口长度"当显式自变量扫描；也没有人把 BAPO 式的 token 下界算到"跨域洞察"这种**语义跳跃**上（BAPO 只覆盖形式化任务族，见 §7 B7）。

## 4. Q3：不可分解性——哪些推理是"不可分解的长步骤"？

### 4.1 三类不可分解性，各自的**形式对应物**（理论优先）

| 类型 | 直觉描述 | 形式化对应 | 状态 |
|---|---|---|---|
| **T1 全局一致性** | 每一步局部都对，全局约束不满足 | **两条独立的形式对应**：(a) 电路侧——无 CoT 的常数深度模型只有 $O(1)$ 深度，无法在不落盘的情况下传播全局约束（`2402.12875` Thm 3.1：AC⁰）；(b) **通信侧——全局聚合类问题的 token 下界是 Ω(n)，任何与输入规模无关的预算都会随 n 增长而失败**（`2602.02909` Thm 4.1/4.2 + §8） | **已证明**（模型内）＋**已实测**（`2605.20873`，`2602.02909` 实验） |
| **T2 长依赖链** | k 跳依赖链不能压缩 | **深度下界**：k-hop 需 $\Theta(\log k)$ 深度（`2402.09268` §4，必要性 conditional）；**token 侧**：指针追踪的 token complexity 随链长而非输入规模（`2602.02909` §4），即 $\Theta(k)$ 而非 Ω(n) | **部分已证明**（充分性构造性；深度必要性 conditional；token 侧在 BAPO 模型内无条件） |
| **T3 非单调回溯 / 并行搜索树剪枝** | 需要退回、需要同时持有多个分支 | **无 CoT 时无中间状态可回退**（AC⁰/TC⁰ 无草稿 ⇒ 不能在树上前缀复用）；CoT = 可回溯工作内存（`2605.30757` 空间类比）；隐式 BFS 可在连续状态里发生（`2412.06769`） | **仅论证 + 小规模实测**（Coconut 的 BFS 现象是观察，不是定理） |

### 4.2 已证明 vs 猜想的**严格分离**（任务书要求）

**无条件下界（可直接用）**
- 常数精度、常数深度 transformer 无 CoT ⊆ **AC⁰**（`2402.12875` Thm 3.1）→ 推论：**任何 AC⁰ 之外的问题，在不写草稿的情况下不可解**。这是一条真正的"必须写点什么"的下界，但注意它的量词是"常数深度/常数精度"，不是"k 步"。
- $R$ 轮 MPC ⇔ 深度 $O(R)$ 的 transformer（`2402.09268` Thm 3.1/3.4）→ 双向模拟，无条件下成立。
- $\mathrm{CoT}(t) \subseteq \mathrm{SPACE}(t+\log n)$（`2310.07923` Eq.1）→ 空间侧下界无条件下成立。
- **MAJORITY / MATCH3n 需 Ω(n) 个 CoT token，REACHABILITY 需 Ω(m)**（`2602.02909` Thm 4.1–4.3，**在 BAPO 模型内无条件**，只假设每 token 常数带宽）。→ 这是本报告找到的**最强的一条"不可压缩"下界**，也是 T1 的定量版本。

**条件性结论（**不得**当定理用）**
- transformer 的 $\log$ 深度对连通性"最优"——**conditional on MPC 猜想**（`2402.09268` Conjecture 2.4 / Cor 3.5）。
- k-hop 的 $\Theta(\log k)$ 中的**必要性**一侧。
- 任意"CoT 比循环网络更省"的强陈述：`2605.30757` 的空间-类别对应是**论证性**的（本地 §G 已标 conf 0.75）。

**为什么这个分离重要**：常见论证"长思维链是必要的，因为理论证明 transformer 太浅"其实只用到 AC⁰/TC⁰ 一侧；一旦允许写草稿，**没有任何无条件定理阻止模型用任意短的草稿 + 更宽的网络解决问题**——这正是 §3.2 的"资源相对"含义。**把 conditional 结论说成已证明，是本领域当前最常见的过度声明。**

### 4.3 pebbling game：**经典工具存在，但没被接到 LLM CoT 上**（最重要的负结果）

任务书点名要看 pebbling。实查结果：
- pebbling game 是**成熟的时空权衡工具**，有完整下界理论：如经典教材结果"任何 $n$ 顶点有界度图不需超过 $O(n/\log n)$ 空间，且存在需要 $\Omega(n/\log n)$ 的图"（Savage, *Models of Computation* Ch.10，"Space–Time Tradeoffs"，Theorem 10.7.1 / 10.8.1 的表述），以及 $(S+1)T=\Omega(n^2)$ 形式的权衡。
- 这条理论**天然对应 CoT**：pebble = context 里的中间状态，pebbling 策略 = CoT 策略，最小 pebble 数 = 最小工作内存。**但穷尽检索（search-log Q5、Q13、Q14）没有找到任何论文把 pebbling 数作为 CoT 所需 context 的下界来证。**
- 最接近的不是 pebbling，而是**空间类别的黑箱对应**（`2605.30757`）、**MPC 轮数对应**（`2402.09268`），以及**通信复杂度对应的 BAPO token 下界**（`2602.02909`）。三者都比 pebbling 粗：pebbling 能给出"这个 DAG 至少需要 s 个 pebble"这种**图特定的**下界，而上面三条给的是**问题类级别**的下界。

> **重要修正（自我纠正第二处）**：我第一轮写的"没有把通信复杂度接到 CoT 上"是错的——`2602.02909` 正是用通信复杂度（BAPO 量化信息流）给 CoT 定 token 下界。**正确的缺口只剩 pebbling 一条**：pebbling 特有的"图特定、可算工作内存"能力仍未被用于 CoT。

**结论**：pebbling 是**剩下的**工具缺口，也是给 Lead 的立项理由（任务书【给 Lead 的备注】已预留）。**如果要把"这条具体洞察需要多少工作内存"变成可计算的下界（而不只是问题类级别），pebbling 是唯一现成的形式化语言，而它现在是空的。** conf 0.75（"没有"这类结论的上限，因为检索不可能完备）。

### 4.4 实测侧的不可分解性（三条，均为同族证据）

- `2605.20873`：Avg-pass 90.03 vs All-pass 58.09——**局部全对但全局不对**是 T1 的直接实测。
- `2505.12135`：规划完成率随步数崩塌，且 Decompose 比 Plan 更早失效——**分解本身在长 horizon 上失效**，这是对"分解万能"最直接的实测反驳。
- `2307.13702`（Lanham et al.，Anthropic 2023）：CoT 的**内容**而非长度在起作用——filler token 替换 CoT 不涨（正文 §2.5/Fig.5）；且 AOC（answer-on-CoT 依赖度）任务差异极大：AQuA >60%，ARC-Easy / ARC-Challenge / OpenbookQA <10%。**推论的推论**：在 AOC <10% 的任务上，"链"本来就不是推理的载体，谈它的"可分解性"没有意义。conf 0.85。

### 4.5 Q3 判决

> **部分解决。** 三类不可分解性都有形式对应物，且下界强度比我初判的更强：
> - **T1（全局一致性）已有定量下界**：Ω(n) 个 CoT token（`2602.02909` Thm 4.1/4.2，BAPO 模型内无条件）——**"全局约束类洞察不可压缩"现在是定理，不是直觉。**
> - **T2（长依赖链）有深度下界与 token 下界各一条**：$\Theta(\log k)$ 深度（`2402.09268` §4，必要性 conditional）、Θ(链长) token（`2602.02909` §4，无条件但限于 BAPO 抽象）。
> - **T3（非单调回溯）仍然只有观察**（Coconut 的 BFS 现象 + 本地 G2 的"回溯不总划算"），**无定理**。
> 卡在哪 ①：**pebbling game 仍未接到 CoT 上**（见 §4.3，conf 0.75）。卡在哪 ②：**没有任何下界是针对"语义跳跃"（跨域类比）本身的**——BAPO 的 Ω(n) 只覆盖形式化任务族。
> 一句话边界：**能证明的是"全局聚合类至少 Ω(n) 步"和"k 跳链只需 Θ(k) 步"，不能证明的是"发现那条链"需要多少步——后者是搜索成本，不是 token 成本。**

---

## 5. Q4：dense（权重内隐式搜索）vs 显式外部搜索，谁更会跳出局部最优？

### 5.1 判据：只接受同题同预算

任务书明确禁止跨论文拼数字。本节只收满足"同一任务 + 同一预算 + 同模型"的对照，共 4 组。

**（A）`2408.03314` Snell et al.——显式搜索内部的同预算对照（MATH / PaLM-2-S*，预算单位 = generation）**
- 低预算：beam search 显著优于 best-of-N。
- 高预算：beam search 收益递减，**常低于 best-of-N 基线**（正文 §5.2 / Fig.3 左）。
- lookahead search（最贵）**在同预算下普遍最差**。
- 分难度看：easy bin 上 beam 随预算增大**掉分**（"额外优化放大了 PRM 学到的伪特征"）；medium bin 上 beam 稳定更好；hardest bin **两种方法都推不动**。
- compute-optimal 路由（按难度选策略）可用**最多 4× 更少算力**（16 vs 64 generations；revision 侧 64 vs 256）超过 best-of-N。
conf **0.85**。→ **含义：显式搜索不是单调有效的；"更会搜索"取决于预算档与验证器质量，而不是搜索树的形状。**

**（B）`2412.06769` Coconut——显式 CoT vs 隐式连续思考（同模型同任务，Table 1）**

| 任务 | CoT | No-CoT | Coconut | iCoT | token 数（CoT / Coconut） |
|---|---|---|---|---|---|
| GSM8K | **42.9** ±0.2 | 16.5 ±0.5 | 34.1 ±1.5 | 30.0* | 25.0 / 8.2 |
| ProntoQA | 98.8 ±0.8 | 93.8 ±0.7 | **99.8** ±0.2 | 99.8 | 92.5 / 9.0 |
| ProsQA | 77.5 ±1.9 | 76.7 ±1.0 | **97.0** ±0.3 | 98.2 ±0.3 | 49.4 / 14.2 |

conf **0.85**。→ **含义：需要 BFS 式回溯的图搜索（ProsQA）上隐式赢，且只花 1/3 token；纯算术链（GSM8K）上显式赢。** 注意 iCoT（隐式 CoT 蒸馏）在 ProsQA 上 98.2 / 8.2 token，比 Coconut 更好——**隐式这一侧的上限还没探到，这也说明"dense 更高效"不是 Coconut 一个方法的偶然。**

**（C）`2407.21787` Large Language Monkeys——搜索预算 vs 选择器（同任务，扫样本数到 10,000）**
- SWE-bench Lite：DeepSeek-Coder-V2 从 1 样本 15.9% → 250 样本 **56%**，超过当时单样本 SOTA 43%。
- GSM8K/MATH（Llama-3）：覆盖率随样本数 **log-linear** 增长到 **>95%**（10,000 样本）。
- **但**："common methods for picking from a sample collection（majority voting 与 reward models）**plateau beyond several hundred samples** and fail to fully scale with the sample budget."
conf **0.85**。→ **含义：这是本报告最锋利的一条。它把"跳出局部最优"的问题重新定义了——正确答案几乎总是被采样到（覆盖率 >95%），失败在"认不出来"。所谓"跳不出局部最优"，绝大多数情况下不是搜索不足，是验证不足。**

**（D）`2212.07677` von Oswald et al.——"dense = 隐式梯度下降"的机制证据**
Proposition 1：单层线性 self-attention 的权重构造等价于**在回归损失上做一步梯度下降**；训练出来的 Transformer 权重与该构造吻合；深度 $K$ 层对应 $K$ 步 GD，且训练所得模型通过**曲率修正**超过朴素 GD。conf 0.8（理论+合成回归任务，非语言任务）。
→ **含义：这是"dense net 在权重里做搜索"唯一的可引证据，但它给的是"隐式优化"的能力，不是"跳出局部最优"的证明。** 把它当作 Q4 的正面答案是过度解读（见 §7 B3）。

### 5.2 Q4 判决

> **部分解决，且没有单一赢家。** 同题同预算的 head-to-head 存在 4 组，结论一致：**crossover 由"任务结构 × 预算档 × verifier 质量"决定**——需要回溯的图搜索上隐式/dense 更省更好（ProsQA +19.5pp，1/3 token）；纯串行算术上显式 CoT 赢（GSM8K +8.8pp）；显式搜索内部 beam/lookahead/BoN 互有胜负且随预算翻转（Snell）。
> 最关键的一条不是"谁赢"，而是 `2407.21787` 显示 **覆盖率 >95% 而选择器在数百样本后 plateau**：**"跳不出局部最优"主要是选择问题，不是搜索问题。**
> 卡在哪：没有任何实验在同一模型上同时对比 "连续思考 / CoT / 树搜索 + PRM / 纯采样" 四种范式在同一预算下跨多个难度档。四组证据各自只覆盖两两比较。

---

## 6. 02.5 交叉核对（D3/D4）

### 6.1 与本地三篇 survey 的对照（D4）

| 本地文献 | 覆盖了什么 | 与本报告的关系 | 重叠/新增 |
|---|---|---|---|
| `cot-necessity-survey.md` §G（G1 `2201.11903` / G2 `2504.07052` / G3 Anthropic paraphrase / G4 `2605.30757`） | CoT 作为**搜索预算**：空占位符提升缩水；固定算力下回溯 vs best-of-N；草稿可被同义改写而性能不掉；CoT=可扩展工作内存 | **G4 是本报告 Q2 机制的既有表述，直接复用不再重查**；G2 是 Q4 的第五组同预算证据（回溯不总是更划算），与 Snell 的"beam 高预算反超"同向；G3（草稿可改写不损失）**削弱**"步骤内容必须逐字忠实"的假设，是 Q1 的一记侧击 | 重叠 G2/G4；新增 Q1 的 refiner/verifier 分离（`2407.13692`）、Q4 的覆盖率 vs 选择器分离（`2407.21787`） |
| `second-order-theory-survey.md` | 二阶理论空白，含 test-time compute scaling | 本报告 Q2/Q3 正好填了它的一个格：**"步骤数 = 复杂度资源"的一阶理论已经有了（`2310.07923`/`2402.12875`），二阶的（任务内在下界）没有** | 新增：把"二阶空白"具体化为"pebbling 未接线"（§4.3） |
| `icl-generalization-survey.md`（D2 `2602.03485` Self-Verification Dilemma；B1 `2510.02370` confidence routing） | 自我验证多为**确认性 recheck**，极少纠错；模型内部已在做置信度路由 | **D2 与本报告 §2.1(2) 的 SCORE 结论独立同向**——两条不同证据链都说"验证器是瓶颈"。这是本报告 D3 要求的关键结论双来源。B1 为 Q4 提供"路由已有雏形"的旁证 | 重叠并可互相加强 |

### 6.2 四条矛盾（不掩饰，逐条记录）

**矛盾 #1：log 步数到底有没有用？**
- `2310.07923`：$\Theta(\log n)$ 步只到 L，"我们没有找到任何具体推理问题是 log 步能帮上忙的"。
- `2402.12875`：线性步数才解锁正则语言；且其框架下"$T$ 步 ⇔ size-$T$ 电路"，小 $T$ 自然对应弱能力。
- **但** `2402.09268` §4：**$\Theta(\log k)$ 深度**（不是 log 步 CoT）足以做 k-hop，且训练出的模型确实在这个阈值上转变。
- **判决**：不是真矛盾，**是"深度"与"步数"两个资源的混淆**。log 步 *CoT* 几乎无用（两篇一致）；log 层 *深度* 非常有用（第三篇）。这条消解本身构成了 §3.4 的机制结论。记录在此以免后人重复踩坑。

**矛盾 #2：CoT 的提升来自"内容"还是"多算一点"？**
- `2307.13702`：filler token 替换 CoT **不涨** → 内容重要。
- `2201.11903`（本地 G1）：只输出占位符提升**大幅缩水但不为零** → 预算本身贡献一小块。
- **判决**：量级不同但方向可兼容——内容贡献主体，纯预算贡献残值。**对本任务的含义：不能把"洞察"降解成"多给点 token"。** conf 0.8。

**矛盾 #3（最重要）：长链能不能被压短？**
- `2402.12875`：线性步数才能算正则语言/非可解群 → 看似"长链不可压"。
- `2402.09268`：k-hop 的 $\Theta(\log k)$ 深度即够 → 看似"长链可压成对数深"。
- **判决（本报告的核心消解）**：两者量的是不同资源，接口在**中间节点是否在 context 里**。若 $\{v_i\}$ 已在上下文（或可由窗口容纳），attention 可并行跳完，压缩成立；若中间节点必须由模型**生成**（因为它们不在输入里），则必须串行落盘，压缩不成立。**→ 这就是"可分解性"的真正边界，也是 Q1 的 executability/discoverability 二分在理论侧的镜像。** 这条消解是本报告自评最有价值的一步，conf 0.7（推论性，但由三条定理共同约束）。

**矛盾 #4（本轮新增，且是最有生产性的一条）：token 下界是"任务内在"还是"资源相对"？**
- `2602.02909` / `2503.01141`：每个问题有**内在**最小链长（token complexity hypothesis），并有 Ω(n) 定理。
- `2310.07923` / `2402.12875`：$t$ 步 CoT ⇔ 复杂度类，$t$ 是**资源**，能解什么由模型（宽度/精度/深度）与任务复杂度之差决定。
- **判决**：不矛盾，**是下界与上界的分工**——通信复杂度（每 token 常数带宽 ⇒ 信息搬运量）给下界，电路模拟（$t$ 步 ⇒ size-$t$ 电路）给上界，两者夹出 token 复杂度带（§3.2）。**但有一条真张力需要标注**：`2503.01141` 的阈值 $	au^{\pi}_i$ **是按模型 π 索引的**（同一问题换模型阈值变），而 BAPO 的 Ω(n) 是渐近的、模型无关的。所以**"任务内在"只在渐近/结构意义上成立；有限规模上 k 确实随模型变**。我第一轮把后者说成"没有任务内在下界"，错在把有限规模的模型依赖当成了本质。conf 0.7。

### 6.3 关键结论的双来源检查（D3）

| 结论 | 来源 1 | 来源 2 | 状态 |
|---|---|---|---|
| 验证器是瓶颈，不是分解器 | `2407.13692`（refiner/verifier 分离，+8.3 只在强 verifier 下） | `2602.03485`（本地：reflection 多为确认性 recheck） | ✅ 双来源，方向一致 |
| 局部对 ≠ 全局对 | `2605.20873`（Avg 90.03 / All 58.09） | `2505.12135`（计划越长越崩，"知道该做什么做不出"） | ✅ 双来源 |
| 步骤数是复杂度资源 | `2310.07923` Eq.1 | `2402.12875` Thm 3.1/3.3 | ✅ 双来源 |
| 存在内在 token 下界 | `2602.02909` Thm 4.1–4.3（定理） | `2503.01141`（if-and-only-if 经验阈值 + 94% 预测） | ✅ 理论+实证双来源 |
| 全局聚合不可压缩、链式可压到 Θ(k) | `2602.02909` Table 1 + §4（pointer chasing 次线性） | `2605.20873`（全局一致性失败） | ✅ 双来源，但语义不同（定理 vs 实测） |
| 并行（dense/attention）可压缩串行 | `2402.09268` §4 | `2412.06769`（连续思考 BFS 现象，实测侧） | ⚠️ 理论侧强、实测侧弱（单一数据集） |
| 跨域类比是崩塌点 | `2510.05432` | 仅此一条 | ❌ **单来源**，已在 §7 标为最脆弱结论 |

---

## 7. 边界与开放（8 条，其中 B1/B5/B7/B8 是对本报告自身的限制）

- **B1（最脆弱）**：`2510.05432` 是"跨域类比失败"的**唯一**直接量化来源，且它是"从参数化记忆复现科研解法"的 benchmark，不是"洞察题"benchmark。**若它错了，Q1 的反面证据只剩 planning 一族（那是"全局一致性"不是"跨域跳跃"）。** 这是我给 Q1 只打 0.75 而不是 0.85 的原因。
- **B2**：`2402.09268` 的 $\Theta(\log k)$ 中**必要性**一侧依赖 MPC 猜想；我在 §4.2 已把它归入"条件性结论"。任何 downstream 引用必须保留这个限定词。
- **B3**：`2212.07677` 的等价只在**线性回归/合成任务**上成立；"dense net 在权重里做隐式搜索所以更高效"目前**没有语言任务上的同预算证据**。§5.1(D) 已按此限量引用。
- **B4（任务书 Q1 的直接空缺）**：没有任何论文做"人工把 frontier 洞察切成原子步骤 → 小模型在**同题同预算**下复现"的对照。`2210.11416` 是 teacher 给步骤，不是人工分解 insight；`2407.13692` 是修错不是复现洞察。**这条空缺是本任务最值得对外声明的"未见前人"点（见 §9 N1）。**
- **B5**：Q2 的"窗口 vs 深度"定量关系不存在（§3.5）。若有人做 W-scan 实验，§3.4 的二分（串行不受窗口限、并行受窗口限）是可以直接检验的假设。
- **B7（对 BAPO 下界的限制）**：`2602.02909` 的下界建立在 **BAPO 抽象**上——关键是"每个 token 只承载常数带宽的信息"。这对**潜空间推理**（Coconut 式连续思考，`2412.06769`）**不直接适用**：一个连续 thought 的"带宽"可以远大于一个 token，因此它的实际下界可能低于 Ω(n)。**任何人引用 Ω(n) 去论证"必须写 n 个 token"都必须先声明"潜空间路线被排除"。** 这条限制我在 §3 没有充分展开，在此补明。conf 0.65。
- **B8**：`2602.02909` 的三个任务（majority / match-3 / reachability）**没有一个涉及"语义类比"**。把 Ω(n) 或 Θ(k) 平移到"跨域洞察"上是我的推断（§3.3，conf 0.65），不是论文结论。
- **B6**：Q3 的 T3（非单调回溯不可分解）**没有任何定理**，只有 Coconut 的观察。任务书 Q3 点名的"并行搜索树剪枝"因此仍是开放格。

---

## 8. 来源表（AC2：≥15 个 arXiv id/URL，标注读到哪一层）

图例：**【全文】** = 读到正文的定理/表格/章节编号；**【正文级】** = 读到正文数字但未覆盖全文；**【摘录】** = 只有片段/二手转述。

| # | arXiv / URL | 标题（简称） | 层级 | 引用位置 | conf |
|---|---|---|---|---|---|
| 1 | `2402.12875` | CoT Empowers Transformers to Solve Inherently Serial Problems（ICLR 2024） | **全文**（HTML §1、§3.1 Thm 3.1、§3.3 Thm 3.3） | §3.2, §4.1, §4.2, §6.2 | 0.85 |
| 2 | `2310.07923` | The Expressive Power of Transformers with CoT（ICLR 2024） | **全文**（Eq.1；Knowl 3/5/6/8 定理陈述） | §3.2, §4.2 | 0.85 |
| 3 | `2402.09268` | Transformers, Parallel Computation, and Logarithmic Depth（ICML 2024） | **全文**（HTML §1.1：Thm 3.1/3.4、Cor 3.3/3.5、Conj 2.4、§4） | §3.4, §4.1, §4.2, §6.2 | 0.85 |
| 4 | `2602.02909` | **Reasoning about Reasoning: BAPO Bounds on CoT Token Complexity**（ICML '26） | **全文**（Table 1；Thm 4.1/4.2/4.3/5.5/5.6/5.7/5.8；Prop 5.4；§4 pointer-chasing；§8） | §3.1, §3.3, §4.1, §4.2, §9 | 0.85 |
| 5 | `2503.01141` | How Well do LLMs Compress Their Own CoT? A Token Complexity Approach | 正文级（Assumption 1、if-and-only-if 阈值、94% 预测） | §3.1, §6.2 | 0.8 |
| 6 | `2412.06769` | Coconut: Training LLMs to Reason in a Continuous Latent Space（COLM 2025） | **全文**（Table 1 + §4.2） | §2.1, §5.1(B), §7 B7 | 0.85 |
| 7 | `2407.13692` | Small LMs Need Strong Verifiers to Self-Correct Reasoning（ACL Findings 2024） | **全文**（Fig.3 + 结论段 "bottlenecked by the verifier"） | §2.1, §6.3 | 0.85 |
| 8 | `2407.21787` | Large Language Monkeys（2024） | **全文**（15.9→56%；>95% @10k；selector plateau） | §5.1(C), §0 | 0.85 |
| 9 | `2408.03314` | Scaling LLM Test-Time Compute Optimally（2024） | **全文**（§5.2/§6.2、Fig.3/Fig.8、4× 数字） | §5.1(A) | 0.85 |
| 10 | `2605.20873` | PlanningBench | **全文**（Table 2 All/Avg-pass、错误分析表、难度分组） | §2.2, §4.4 | 0.85 |
| 11 | `2505.12135` | LLM-BabyBench: Can LMs Plan in Worlds They Can Simulate? | 正文级（§4.3 "know what to do but can't do it"） | §2.2, §4.4 | 0.8 |
| 12 | `2510.05432` | AInstein: Can LLMs Solve Research Problems From Parametric Memory Alone? | 正文级（§5.2、§6 "parametric knowledge boundary"、附录 L.3） | §2.2, §7 B1 | 0.8 |
| 13 | `2210.11416` | Distilling Step-by-Step（Findings ACL 2023） | 正文级（ACL Anthology：770M/80% 数据 > 540B） | §2.1 | 0.85 |
| 14 | `2307.13702` | Measuring Faithfulness in CoT Reasoning（Anthropic 2023） | **全文**（§2.3 AOC、§2.5 filler token、Fig.7 逆 scaling） | §4.4, §6.2 | 0.85 |
| 15 | `2212.07677` | Transformers Learn In-Context by Gradient Descent | 正文级（Proposition 1 + 曲率修正） | §5.1(D), §7 B3 | 0.8 |
| 16 | `2306.02896` | Representational Strengths and Limitations of Transformers（NeurIPS 2023） | 正文级（abstract：sparse averaging / triple detection） | §4.4 旁证（通信复杂度方法） | 0.8 |
| 17 | `2603.21676` | Thinking Deeper, Not Longer: Depth-Recurrent Transformers | 【摘录】（abstract + §1/§2.1：水平 CoT 每步耗窗口、32 层固定深度） | §3.4 | 0.6 |
| 18 | `2505.18642` | Skip-Thinking（chunk-wise CoT 蒸馏） | 【摘录】（LLC 并行子任务失败） | §2.2 | 0.55 |
| 19 | Savage, *Models of Computation* Ch.10（`cs.brown.edu/.../ModelsOfComputation_Chapter10.pdf`） | Space–Time Tradeoffs / pebbling | 正文级（Thm 10.7.1 / 10.8.1 表述） | §4.3 | 0.8 |
| 20 | `2201.11903` | Wei et al. 2022（本地 §G1） | 本地已核 | §6.2 | 0.9（继承） |
| 21 | `2605.30757` | CoT and Compressed Looped Transformers（本地 §G4） | 本地已核 | §3.4, §4.1 | 0.75（继承） |
| 22 | `2504.07052` | To Backtrack or Not to Backtrack（本地 §G2） | 本地已核 | §6.1 | 0.8（继承） |
| 23 | `2602.03485` | Self-Verification Dilemma（本地 icl §D2） | 本地已核 | §6.3 | 0.85（继承） |

统计：**外部 arXiv/URL 19 条**（#1–19），其中 **10 条读到全文/定理/表格级**（#1,2,3,4,6,7,8,9,10,14），满足 AC2"≥8 篇读原文"。另有本地已核 4 条（#20–23）作为交叉引用，**不计入**外部数。AC2 要求 ≥15 个 arXiv id/URL：**达标（19）**。

## 9. 负结果清单（D5：诚实标注，不编）

| # | 未找到的东西 | 试过的渠道 | 结论 | conf 上限 |
|---|---|---|---|---|
| N1 | "人工分解 frontier 洞察 → 小模型同题同预算复现"的对照实验 | search-log Q02/Q04/Q07/Q12（Q1 组全部）+ Q06/Q10 | **穷尽渠道后未找到。** 现有蒸馏论文都是 teacher 提供步骤，不是人工分解 insight；SCORE 是修错不是复现 | 0.45 |
| N2 | attention 窗口长度 W 与可完成依赖深度 D 的定量关系 $D_{\max}=f(W)$ | search-log Q09/Q16/Q17/Q18（Q2 组 4 条）：context window limit × reasoning depth / lost in the middle / minimum reasoning budget | **未找到。** Q17 命中了 token 复杂度线，但它给的是 $f(\text{问题结构})$，**不含 W**；最接近的检索衰减研究与 log-depth 结果都不构成 $f$ | 0.45 |
| N3 | 用 pebbling game 给 CoT 上下文预算证下界的论文 | search-log Q05（pebbling × CoT）；Q16–Q18 未再命中同族 | **未找到。** 经典 pebbling 下界齐全（Savage Ch.10），但没有被接到 CoT 上。**注意与 N6 的区别：通信复杂度已被接上（`2602.02909`），pebbling 没有** | 0.75 |
| N4 | "非单调回溯不可分解"的定理 | Q05/Q10（backtracking + CoT 方向）| **未找到定理**；只有 Coconut 的观察（隐式 BFS）与本地 G2 的实测（回溯不总划算） | 0.4 |
| N5 | 同模型同预算下"连续思考 / CoT / 树搜索+PRM / 纯采样"四范式跨难度对照 | Q06/Q08/Q11/Q14（Q4 组全部） | **未找到。** 现有都是两两比较（Snell、Coconut、Monkeys） | 0.5 |
| **N6**（对我自己检索的负结果） | "任务内在 token 下界"这条线 | 前 5 条 query 用 circuit complexity / pebbling 词汇全部落空；**改用 "minimum reasoning budget / token complexity" 后一次命中** | **不是文献不存在，是我的关键词错了。** 教训：**下界要找通信复杂度词汇，不是电路复杂度词汇**。本条作为 D5 的自我审计记录保留 | — |

**通道失败记录**：`arxiv.org/pdf/*` 直链在本轮全部 `Failed to fetch`（一次是真失败，一次是编号误命中——后者实为对齐方向论文 *Noise Contrastive Alignment*）；改用 `arxiv.org/abs/*` 与 `arxiv.org/html/*vN` 后成功。搜索引擎可通但泛化 query 噪声极高（"insight" + LLM 类 query 返回认知心理学论文与博客，无 arXiv 对照实验），必须用 arXiv 定向 phrasing。以上均已记入 search-log 的 `channel_notes`。

---

## 10. 对成璐三个担忧的逐条回应

1. **"会不会超出模型注意力的 ctx 范围"** → **不是主要原因。** 串行写 CoT 的路线自己造中间状态，窗口大小不影响可达性（只影响生成长度）；并行 attend 的路线才受窗口限制（§3.4）。且没有任何文献给出窗口→深度的定量门槛（N2）。**真正卡住的是"用不用得上自己刚写下的东西"**（planning 一族失败，§2.2）。
2. **"有没有下界要求"** → **有，而且有两层，都要看。** ① **结构层（真正回答她的问题）**：全局聚合类问题 Ω(n) 步、不可压缩；链式 k 跳只需 Θ(k) 步——**所以"洞察要多少步"取决于它是链式还是全局约束式，而不取决于它"跳得多远"**（§3.1/§3.3）。② **模型层**：$t$ 步 CoT ⇔ 能解 SPACE(t) 内的问题，所以同一个洞察换更强的模型所需步数会降（`2503.01141` 的阈值 $	au^\pi_i$ 按模型索引）。**结论：k 由"问题结构 + 模型能力"共同决定，其中结构那部分是硬的。**
3. **"dense net 在搜索上是否效率更高"** → **在需要回溯的图搜索上，是的，且省 token**（ProsQA +19.5pp / 1/3 token）；**在串行算术上不是**（GSM8K −8.8pp）。而**"跳不出局部最优"的主因是选择器而非搜索器**（覆盖率 >95% vs selector plateau，§5.1(C)）——这条最该进入下一轮实验设计。

---

*报告完。检索日志：`research/long-insight-search-log.json`；loop 工件：`loop-artifacts/stages/01..04.5/`。*
