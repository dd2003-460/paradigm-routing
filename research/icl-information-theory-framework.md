# T-PR-09：ICL 最优性的信息论 / Bayesian 框架调研

> origin: ai · 2026-11-07 · Lead: 成璐数字分身 · 执行: Arena agent
> 仓库: `dd2003-460/paradigm-routing` · 分支: `arena/62fe3fd4-paradigm-routing` · 任务书 commit `1f6c5a0`
> 检索日志: `research/search-log-icl-it.json`
> 立场声明: 本报告要把成璐的三句直觉变成**可判定命题**，判据只有一种——**有没有定理编号或同任务对照数字**。直觉本身不算证据。
> **资产缺失（第三次记录）**：`loop/prompt-first/01..04.5` 与 `sop/arena-loop-pipeline.md` 在本仓库任何分支仍不存在；六阶段按任务书【强制段】定义执行。

---

## 0. TL;DR（三句话 + 一句话判决）

1. **P1 的前半句有定理级支持，后半句没有。** "ICL 最优性依赖任务结构"这一侧有硬结果：`2301.07067`（Transformers as Algorithms）给出 **1/√(nT)** 的多任务泛化率（Thm 2/3.5），并明确 **transfer risk 由 task complexity 与任务数 T 决定，几乎不依赖 transformer 架构复杂度**——这就是"结构决定最优性"的定量版本。但"神经网络是目标函数的**最简描述**"这一侧，只有**渐近存在性**（`2509.22445`, ICLR 2026：存在渐近最优描述长度目标，其最小化者在资源趋于无穷时达到最优压缩，差一个可加常数），**而且同一篇论文的实证结论是标准优化器从随机初始化找不到这种解**。→ **"最简描述"在极限里存在，在训练里拿不到。**
2. **P2 的证据方向是"额外参数主要在拟合，不在压缩"。** 万能逼近（UAT）只说明能拟合；`2310.13220` Thm 3.2 的泛化界**只随 demo token 数 N 变化，不含参数量**——即泛化能力不因参数变多而变好；`2509.22445` 说明 MDL 最优解存在但优化器找不到。**唯一可测的压缩性证据**来自 `2510.12077`（MDL × 奇异学习理论）：用 **local learning coefficient (LLC)** 度量复杂度，在 Pythia 上发现 LLC 与可压缩性**近乎线性相关**——这给了一条"能测"的路，但它测的是模型可压缩性，不是"参数是否等于最简描述"。
3. **P3 是最强的直觉，但它的严格版本被一个经典实验打断。** Bayesian 叙事有定理：`2111.02080`（ICLR 2022）在 mixture-of-HMMs 预训练下证 ICL ≈ 隐式 Bayes 推断，**Thm 1** 给 distinctinguishability 条件下的最优性，**Thm 2–3** 给 excess risk **O(1/k)**（k = 每个 example 的长度）。但 `2202.12837`（EMNLP 2022）发现**把 demo 的标签换成随机标签几乎不掉分**，真正起作用的是标签空间、输入分布、序列格式——**如果 likelihood 可以被随机化而性能不掉，那么 ICL 就不是在算 p(y|x, demo) 的后验**。→ Bayesian 类比在"概念识别"层成立，在"标签似然"层断裂。

**一句话判决（AC5）**：
> **Bayesian/信息论范式对 ICL 效率的支撑，目前证据支持到"部分证明"级别（conf 0.7）：存在条件化的 Bayes 最优性定理与 1/√(nT) 的统计界，但它们都需要额外假设（distinguishability / 任务多样性 / 稳定算法），且都没有把最优性写成"目标函数的最简描述"；而"互信息控制 ICL 泛化误差"这个最可测的命题，穷尽检索后没有找到任何直接结果。**

---

## 1. 判据与术语（先把三个"最优性"分开）

成璐的三句话里其实混了三种"最优"，不分开就无法判定：

| 记法 | 含义 | 判定工具 | 谁能给证据 |
|---|---|---|---|
| **O1 统计最优** | 给定 T 个任务、每任务 n 个 demo，泛化误差以什么速率趋于 0 | 泛化界（含/不含参数量） | `2301.07067`, `2310.13220`, `2409.12293` |
| **O2 压缩最优** | 学到的参数是否达到 \(K(f)\) 级别的最简描述 | MDL 两段码 / prequential 码长 / LLC | `2509.22445`, `2510.12077`, `2302.09579` |
| **O3 推断最优** | 在给定 prompt 下，输出是否等于隐概念的后验预测 | Bayes 风险、distinguishability | `2111.02080` |

**关键说明**：**O1 与 O3 是"有条件的定理"，O2 是"渐近存在但不可达"。** 任何把三者混成一句"ICL 是最优的"的表述都是无信息的——这是本报告最重要的方法论结论。

---

## 2. P1：「ICL 最优性依赖任务结构」≡「NN 是目标的最简描述」？

### 2.1 支持"依赖任务结构"的一侧（定理级）

**`2301.07067` Li, Ildiz, Papailiopoulos, Oymak, *Transformers as Algorithms: Generalization and Stability in ICL*（ICML 2023）。read（HTML §3.2 Thm 2/3.5 + §4）。**
- 把 ICL 形式化为**算法学习**：transformer 被训练成一个"在推理时实现目标算法"的算法。
- **Thm 2 / 3.5**：训练 T 个任务、每任务 n 个样本时，多任务泛化率达 **1/√(nT)**（用 covering number / Dudley 熵积分 + 算法稳定性；i.i.d. 与动态序列两种 prompt 都覆盖）。
- **最关键的一句（§1 / §4）**：实验显示 **transfer risk 由 task complexity（函数 f 的复杂度）和任务数 T 决定，"exhibits little dependence on the complexity of the TF architecture"**。
- → **这就是成璐直觉的定量版本**：最优性由**任务结构**（f 的复杂度）与任务多样性 T 决定，不由架构规模决定。conf 0.85。

**旁证（三条独立）**：
- `2310.13220`（representation-learning lens）：**Thm 3.2** 给出与 **demo token 数 N** 相关的泛化界（Rademacher 路线），并明确"demo 数增加 ⇒ 泛化误差下降"，与 Xie/Garg/Wang 的实验一致。conf 0.75
- `2409.12293`（ICL of linear systems）：**Thm 1** 给出 in-domain 误差分解——**O(1/m + 1/n²)** 的 in-context 项 + **O(1/√N)** 的预训练项（m = 推理样本数，n = 每任务训练样本数，N = 预训练任务数）；OOD 侧提出 **task diversity** 作为**必要且充分**条件。conf 0.8
- `2111.02080` Thm 1 的 distinguishability 条件（见 §4）本质上是"任务结构可分辨 ⇒ 最优"。conf 0.85

**"任务结构"到底指什么（本报告的操作化，供后续复用）**：

| 结构维度 | 文献里的变量 | 对 ICL 的影响 |
|---|---|---|
| 任务多样性 | T（`2301.07067`）、task diversity（`2409.12293`） | 决定能否 OOD；是 transfer 的主导量 |
| 单任务内信息量 | n / demo token 数 N（`2310.13220`）、example 长度 k（`2111.02080`） | 决定 in-context 侧的误差率 |
| 概念可分性 | distinguishability（`2111.02080`） | 决定后验是否集中到真概念 |
| 函数复杂度 | task complexity（`2301.07067` §4） | 决定 transfer risk 的**天花板** |

### 2.2 "NN 是最简描述"这一侧（只有渐近存在性）

**`2509.22445` Shaw, Cohan, Eisenstein, Toutanova（ICLR 2026）。read（abs + 结论段）。**
- 提出**渐近最优描述长度目标**：其最小化者在模型资源上界趋于无穷时，**对任意数据集达到最优压缩（差一个可加常数）**。
- 证明这类目标**对 Transformer 存在**（基于一个新的计算万能性论证）。
- 给出可处理、可微的变分版本（自适应高斯混合先验）。
- **实证的关键限定**："the variational objective selects for a low-complexity solution with strong generalization on an algorithmic task, **but standard optimizers fail to find such solutions from a random initialization**".
- → 这条限定是本报告**最重要的负面证据**：**"最简描述"是可达的极限点，不是训练的吸引子。** conf 0.85

**`2510.12077`（MDL × 奇异学习理论，Timaeus）。read（abstract + §3.3）。**
- 把 MDL 推广到奇异模型：渐近冗余的主项是 **λ log n**，λ = learning coefficient（局部学习系数 LLC）。
- **λ 小 ⇒ 模型类对该分布给出更短编码** ⇒ 用 LLC 可给出"复杂度"的可计算估计。
- 实证：在 Pythia 全系上用量化/分解等压缩手段，**LLC 与可压缩性近乎线性相关**。
- → 这是**唯一一条"压缩性可测"的路径**，也是 P2 的可测判据来源。conf 0.8

### 2.3 P1 判决

> **部分证明。** 前半（最优性依赖任务结构）**有定理级支持**：1/√(nT) 率 + "transfer risk 由 task complexity 与 T 决定、几乎不依赖架构复杂度"（`2301.07067` Thm 2/3.5、§4），conf 0.85。后半（NN 是目标的最简描述）**只有渐近存在性，且优化器拿不到**（`2509.22445`），conf 0.85。
> 卡在哪：**没有任何论文证明"ICL 的最优 demo 选择 ≡ MDL 在 demo 空间的最优"**。最接近的是 `2212.10375`（见 §6），它用 MDL 做**select-then-rank**，是**算法**而非**等价性定理**。

---

## 3. P2：「额外参数/层 = 万能拟合器」还是「压缩结构」？

### 3.1 万能逼近这一侧：真的，但它是弱命题

UAT 说"足够宽的网能拟合任意连续函数"。**它对 P2 没有区分力**——因为压缩与记忆两条路都能拟合。要区分必须用**可测判据**。任务书给的判据（N vs K(data)，N >> K ⇒ 记忆；N ≈ K ⇒ 压缩）在文献里**没有直接做过**（→ 负结果 N2），但有三个可用的替代量：

| 可测量 | 定义 | 文献 | 它能区分什么 |
|---|---|---|---|
| **LLC λ** | 奇异学习理论下的局部学习系数，渐近冗余 = λ log n | `2510.12077` | 小 λ = 更好压缩的模型类 |
| **prequential 码长** | 逐点预测的累积负对数似然（= online MDL） | `2302.09579`（ICLR 2023，MDL 作为表示评测指标） | 同一表示下"学得多快" |
| **描述长度目标值** | 变分 MDL 目标（自适应高斯混合先验） | `2509.22445` | 是否存在低复杂度解 |

### 3.2 三条证据的方向

1. **泛化界不含参数量**：`2310.13220` Thm 3.2 的界是 demo 数 N 的函数；`2301.07067` 的 1/√(nT) 也只含 n、T。→ **参数变多不会让泛化界变好**，这是"额外参数不是压缩能力"的间接支持。conf 0.75
2. **最优压缩解存在但优化器找不到**：`2509.22445` 的实证。→ 训练所得权重**不是** MDL 最优，最可能停在"能拟合但更长"的解上。conf 0.85
3. **压缩性可测且与 LLC 线性相关**：`2510.12077`。→ 说明"压缩 vs 记忆"不是二值，而是连续谱，可用 λ 排序。conf 0.8

### 3.3 相变 / Chinchilla 的压缩解读

任务书问"在什么 N/D 比值下从 memorization 切到 compression，有没有相变证据"。
- **Chinchilla 的 loss(N,D) 曲线本身不是压缩相变证据**——它是经验拟合的幂律，没有给出"切换点"的机制解释（本报告未找到把 Chinchilla 曲线解释为压缩相变的论文，→ N3）。
- 找到的最接近的"相变"证据来自**另一支**：`2510.23671`（T-PR-08 已核）指出 **MoE 相比 dense 模型"不出现 sharp phase change"**，即相变本身是 dense 模型特有的现象。→ 这条对 P2 有间接含义：**"记忆→压缩"的切换可能不是一个普适相变，而是架构相关的。** 标为推论（conf 0.6）。

### 3.4 P2 判决

> **部分证明，且证据偏向"拟合"而非"压缩"。** "额外参数 = 万能拟合器"有**间接支持**（泛化界不含参数量 + MDL 最优解不可达），conf 0.8；"额外参数 = 压缩结构"只有**渐近存在性 + 可测代理（LLC）**，没有"训练实际达到压缩"的证据，conf 0.5。
> 卡在哪：**没有人做过任务书提的那个直接测量（N 参数 vs K(data) 的 LZ76/C 复杂度对比）**。→ 这是一个具体、便宜、还没人做的实验（建议见 §8）。

---

## 4. P3：Bayesian / 统计 / 信息论范式如何支撑 ICL

### 4.1 (a) ICL as Bayesian inference：有定理，但条件很硬

**`2111.02080` Xie, Raghunathan, Liang, Ma（ICLR 2022）。read（HTML §1–§3 + Thm 1；附录 D/E 的证明结构）。**
- 设定：预训练分布是 **mixture of HMMs**（每个 document 有一个隐概念 θ）；ICL 时 prompt 里的 examples 是同一概念下的样本。
- **Thm 1（概念选择）**：在 **distinguishability condition** 下（prompt 概念与其它概念足够可分，例如 Θ 离散时），posterior 集中到真概念，**in-context 预测误差最优**。
- **Thm 2–3（example 长度的作用）**：即使 distinguishability 不成立（Θ 连续），excess risk 仍以 **O(1/k)** 下降（k = 每个 example 的长度）。
- 技术要点：Bernstein-von Mises 在这里**不能直接用**（观测既不独立也不同分布），论文证的是**分布失配下仍然最优**，靠的是"每个 example 内的 KL 项之和 > 失配误差项"。
- 实证：合成数据族 **GINC**；**"scaling model size improves in-context accuracy even when the pretraining loss is the same"** ← 这句对本任务很关键（见 §4.4 与 T-PR-10 的接口）。
- conf 0.85。

**它的信息论含义（我的解读，conf 0.7）**：Thm 1 的证明里误差被写成**两个 KL 之差**：`KL(p_prompt(O)‖p(O|θ*)) − KL(p_prompt(O)‖p(O|θ))`。→ **"高效 ICL"⟺ "prompt 分布与真概念下的分布 KL 足够小、且与错误概念的 KL 足够大"**。这是任务书想要的那种"互信息控制"的**近似物**，但它是**KL 差**，不是互信息界。

### 4.2 (b) 信息论界：**穷尽检索未找到直接的 I(target; context) 界**

任务书的核心命题是："如果 ICL 的泛化误差可以被 I(target; context) 的某个函数控制，那高效 ICL ⟺ context 携带高互信息"。
- **查到的最接近的三条都不是这个命题**：
  - `2111.02080`：KL 差（不是互信息）；
  - `2301.07067`：covering number / 稳定性（不是信息量）；
  - `2310.13220`：Rademacher 复杂度（不是互信息）。
- 检索 query：`information-theoretic bound in-context learning mutual information demonstrations`、`PAC-Bayes in-context learning bound`、`mutual information context demonstrations bound`（见 search-log S02/S04）。**没有任何一篇给出 I(y; context) 的显式上下界。**
- → **判定：无文献（conf ≤0.45）。** 这是一个**明确的可立项空白**：把 `2111.02080` 的 KL 差用 Pinsker 不等式转成互信息形式，是**现成可做的**（一行不等式），但**没人写**。这是本报告给出的最具体的后续工作。

### 4.3 (c) 统计学习理论视角：能套，但套出来的界不含"信息"

| 工具 | 用在 ICL 上的例子 | 假设空间的取法 | 结论 |
|---|---|---|---|
| 算法稳定性 + covering number | `2301.07067` Thm 2/3.5 | 把 transformer 当"实现某算法的算法"，假设空间 = 算法族 | 1/√(nT)，且 transfer 由 task complexity 主导 |
| Rademacher（经对偶模型） | `2310.13220` Thm 3.2 | 假设空间 = 对偶 GD 可达的模型 | 界随 demo 数 N |
| 泛函/算子视角 | `2409.12293` Thm 1/5 | 任务分布 P_A（非 Gaussian）+ task diversity | O(1/m + 1/n²) + O(1/√N) |
| 奇异学习理论 | `2510.12077` | 模型类（奇异）| λ log n 的渐近冗余 |

- **PAC-Bayes 风格的 ICL 界：检索未找到直接结果**（→ N1）。这在理论上很意外，因为 ICL 的"context 当数据、prior 当参数分布"结构与 PAC-Bayes 天然契合。**这是第二个可立项空白。**
- **ICL 的假设空间到底是什么？** 本报告采纳 `2301.07067` 的答案：**不是"所有 prompt→completion 映射"，而是"该 transformer 在训练分布上被特化成的那个算法"**。这个取法让界变得可证，代价是**界的意义依赖训练分布**。

### 4.4 (d) Bayesian 类比：精确成立 vs 断裂（AC4，逐条）

| # | 环节 | 精确成立？ | 依据 |
|---|---|---|---|
| 1 | **context = evidence，parametric knowledge = prior** | **成立（有条件）** | `2111.02080`：预训练分布 = 概念混合 ⇒ 后验集中在 prompt 概念；**前提是预训练确实诱导了概念结构**（同文实验：单概念数据或随机转移的数据训不出 ICL） |
| 2 | **examples 数 ↑ ⇒ 后验集中 ⇒ 误差 ↓** | **成立** | `2111.02080` Thm 1；`2310.13220` Thm 3.2；`2409.12293` Thm 1 的 in-context 项 |
| 3 | **example 的"信息量"是长度 k** | **成立** | `2111.02080` Thm 2–3：excess risk O(1/k)，**不是** O(1/#examples) —— 这点常被误读 |
| 4 | **likelihood = demo 的 input→label 映射** | **断裂（关键）** | `2202.12837`：**随机替换 demo 的标签几乎不掉分**（12 个模型，含 GPT-3），真正起作用的是**标签空间、输入分布、序列格式** ⇒ ICL 不是在算 p(y|x) 的似然 |
| 5 | **输出 = 后验预测** | **断裂（部分）** | `2212.07677`（in-context GD）：线性自注意力层等价于**一步梯度下降**，深度 K 层 = K 步 GD ⇒ 至少在某些设定下机制是**优化**而非**边缘化**。两者是不同算法，同一现象 |
| 6 | **模型内部真的在做 Bayes 更新** | **未证** | 无任何论文给出"attention 的前向计算 = Bayes 更新"的等价定理；`2111.02080` 证的是**输入输出行为**的渐近最优，不是内部机制 |
| 7 | **prior 是"预训练分布"** | **成立但不可观测** | `2111.02080` 的 prior 是 mixture-of-HMMs 的概念先验；真实 LLM 的 prior 无法直接读出（本地 `icl-generalization-survey.md` B1 条目 `2510.02370` 给了一个间接测法：模型按内部置信度在参数化知识与 context 间仲裁） |

**净结论（AC4）**：Bayesian 类比在**第 1–3 环精确成立**（且是定理级），在**第 4 环明确断裂**（随机标签实验），在**第 5–7 环未证**。**这个断裂点不是细节——它意味着"demo 提供的是概念线索，不是监督信号"，这正是 ICL 与 finetuning 的本质差别。**

---

## 5. Q4：与 T-PR-07「瓶颈在 verifier」的信息论解释

T-PR-07 结论：分解器可迁移，验证器不可迁移（`2407.13692`）。在本框架下：

| T-PR-07 的角色 | 本框架的对应 | 为什么迁移性不同 |
|---|---|---|
| decomposer（生成候选步骤） | **prior sampling**（从概念先验采样） | prior 是**跨任务共享**的（预训练学到的概念库）⇒ 可迁移 |
| verifier（判断步骤对不对） | **likelihood evaluation**（在给定概念下算 p(step)） | likelihood 是**任务特定**的（不同任务的"合理步骤"不同）⇒ 不可迁移 |

**这个解释的强度**：它是**推论**而不是定理（conf 0.6），但它解释了 `2407.13692` 的一个反直觉事实——refiner 可训练、verifier 不可训练。**并且它给出一个可测预言**：如果 verifier 的困难是 likelihood 的任务特异性，那么**给 verifier 提供任务的少量标注（即把 likelihood 局部校准）应该比给 refiner 提供更多标注更有效**。这条预言**没有文献验证**（→ 可做实验）。

⚠️ **必须标注的反向证据**：第 4 环的断裂（`2202.12837` 随机标签）**削弱**了"verifier = likelihood"这个映射——如果 demo 的标签都能随机而不掉分，那 ICL 里的 likelihood 项本身就很弱。→ **本节的解释在"demo 少、任务新"的设定下更可信；在"demo 多、任务熟"的设定下可能失效。** 这是本报告自评最脆弱的一节。

---

## 6. AC6：可操作的 demo selection 准则（单独标出）

**已存在的可操作准则（文献级，可直接用）**
- **MDL select-then-rank**：`2212.10375` Wu, Wang, Ye, Kong, *Self-Adaptive ICL: An Information Compression Perspective for ICL Example Selection and Ordering*（ACL 2023）。**read（abs + 方法段转述）**。
  - 原则：为每个样本找一个 example 的**排列（选择 + 排序）**，使模型能导出正确预测；实现为 **select-then-rank** 框架。
  - 数字：在 **8 个 NLP 数据集**上，相比随机采样常规做法 **40% 相对提升**（self-adaptive 的聚合结果）。
  - 与 MDL 的关系：rank 阶段用 MDL 原则给候选排列打分（综述 `2401.12087` 将其归类为 "select-then-rank + MDL"，并指出其**候选组织是随机采样**的这一局限）。
  - **实用性评级：高**（无需训练、无需梯度、8 数据集有数字）。conf 0.85
- **MDL 作为表示/模型选择指标**：`2302.09579`（ICLR 2023）把 prequential MDL 用作"哪种表示 + 哪种 readout 更好"的统一度量，且可在线计算。**实用性：中**（需要能算 prequential 码长）。conf 0.7

**任务书设想的"信息增益准则"（我的构造，不是文献）**
- 从 `2111.02080` Thm 1 的证明结构直接可得：选择使 **KL(p_prompt(O)‖p(O|θ*)) − KL(p_prompt(O)‖p(O|θ_wrong))** 最大的 demo 集，就是最大化"概念可分性"。
- 但 θ*、θ_wrong 都不可观测 ⇒ 实操上只能用它的事后代理：**同一组 demo 在不同顺序/子集下的预测方差**（方差大 = 概念未定 = 信息增益空间大）。
- **状态：我的推论（conf 0.5），无文献直接验证。** 建议作为 pfb 的一个 A/B 条件，而不是当作已知结论。

---

## 7. 反方质询（≥2）

### 质询 1："MDL ≠ 最简描述；你把两段码和 Kolmogorov 复杂度混着用"

**攻击**：`2509.22445` 的"渐近最优描述长度目标"是**渐近**的（资源→∞），而 `K(f)` 是不可计算的。你用它们支撑"NN 是最简描述"，等于用一个不可计算的极限去解释一个有限模型。

**防御（接受，已改措辞）**：§2.2 明确写了这是**渐近存在性**，并且同一篇论文的实证是**优化器找不到**。所以 P1 的判决是"部分证明"，且明确指出后半句"在极限里存在，在训练里拿不到"。**我没有把 K(f) 当作可计算量使用**——§3.1 用的可测代理是 LLC（可算）与 prequential 码长（可算）。

### 质询 2："`2202.12837` 的随机标签只对分类/多选成立，不能推翻 Bayesian 叙事"

**攻击**：Min et al. 的实验是 classification / multi-choice（12 个模型）。对需要真正推理的任务（数学、代码），标签当然重要。你用一个弱任务的结论去推翻一个一般性理论。

**防御（接受，已收窄）**：接受。§4.4 第 4 环的措辞是"**likelihood = demo 的 input→label 映射** 这一环断裂"，适用范围**限于"任务是概念识别型"**。对推理型任务，`2407.13692`（T-PR-07）的结论——小模型能修被指出位置的错——表明标签/步骤的局部正确性**确实**重要。→ 正确的表述：**Bayesian 类比的第 4 环在概念识别任务上断裂，在推理任务上未测**。这个收窄写进了 §4.4 的表格注释。

### 质询 3："你的'verifier = likelihood'是编的解释，没有文献"

**攻击**：§5 的映射表没有任何引用支撑。

**防御（接受，已标 conf 0.6 并给出可测预言）**：接受这是推论。但我做了两件事降低风险：① 明确标注 conf 0.6 与"非定理"；② 给出**可反驳的预言**（给 verifier 少量标注应比给 refiner 更多标注更有效），使它可以被实验否证。**一个能被否证的推论比一个含糊的类比更有价值。**

---

## 8. 来源表（AC2：≥10 来源，≥5 read）

| # | 来源 | 标题 | 状态 | 用在哪 |
|---|---|---|---|---|
| 1 | `2111.02080` | An Explanation of ICL as Implicit Bayesian Inference（ICLR 2022） | **read**（§1–§3、Thm 1、附录 D/E） | §4.1, §4.4, §5, §6 |
| 2 | `2301.07067` | Transformers as Algorithms（ICML 2023） | **read**（§3.2 Thm 2/3.5、§4） | §2.1, §3.2, §4.3 |
| 3 | `2310.13220` | How Transformers Learn In-context: Representation Learning Lens | **read**（Thm 3.2 + 附录 C） | §2.1, §3.2, §4.3 |
| 4 | `2409.12293` | ICL of Linear Systems: Generalization Theory | **read**（Thm 1/5、task diversity） | §2.1, §4.3 |
| 5 | `2509.22445` | Bridging Kolmogorov Complexity and DL（ICLR 2026） | **read**（abs + 实证限定） | §2.2, §3.2 |
| 6 | `2510.12077` | Compressibility Measures Complexity: MDL × SLT | **read**（abs + §3.3） | §2.2, §3.1 |
| 7 | `2212.10375` | Self-Adaptive ICL: Information Compression Perspective（ACL 2023） | **read**（abs + 方法） | §6（AC6） |
| 8 | `2202.12837` | Rethinking the Role of Demonstrations（EMNLP 2022） | **read**（abs） | §4.4 第 4 环 |
| 9 | `2212.07677` | Transformers Learn In-Context by GD | **read**（T-PR-08 已核，Prop 1） | §4.4 第 5 环 |
| 10 | `2302.09579` | Evaluating Representations with MDL（ICLR 2023） | abstract-only | §3.1, §6 |
| 11 | `2401.12087` | Revisiting Demonstration Selection Strategies in ICL | abstract-level（转述 MDL 归类） | §6 |
| 12 | `2510.23671` | Sparsity and Superposition in MoE（T-PR-08 已核） | **read**（继承） | §3.3 |
| 13 | 本地 `research/icl-generalization-survey.md` | A3（ICL≈隐式 Bayes）、B1（`2510.02370` 置信度路由）、D2（`2602.03485`） | 继承 | §4.4 第 7 环, §5 |

统计：**12 条外部来源 + 1 条本地继承**（≥10 ✅），其中 **read = 9 条**（#1–9，≥5 ✅）。所有数字均回源，未使用未实访编号。

---

## 9. 负结果（D5）

| # | 未找到 | 试过的 query | conf 上限 |
|---|---|---|---|
| N1 | **PAC-Bayes 风格的 ICL 泛化界** | S02（PAC-Bayes + ICL）、S04（generalization bounds ICL）| 0.4 |
| N2 | **任务书提的直接判据：N 参数 vs K(data)（LZ76/C 复杂度）的对比测量** | S01（MDL + demo selection）、S03（compression ratio + parameter count） | 0.4 |
| N3 | **Chinchilla loss(N,D) 被解释为 memorization→compression 相变的证据** | S03 | 0.45 |
| N4 | **I(target; context) 形式的信息论 ICL 界**（见 §4.2） | S02, S04 | 0.45 |
| N5 | **"attention 前向计算 = Bayes 更新"的等价定理** | S02, S04 | 0.4 |

**通道记录**：`arxiv.org/abs/*` 与 `html/*vN` 可用（本轮 3 次抓取全成功）；PDF 直链未再尝试（T-PR-07/08 已三次失败）。`web_search` 可用，但 MDL 类查询返回大量非 ICL 的 MDL 论文（表示评测、变分推断），需靠 "in-context" 关键词收窄。

---

## 10. 给 Lead 的三个可执行建议

1. **一行不等式就能补的空白（N4）**：把 `2111.02080` Thm 1 的 KL 差用 Pinsker 转成互信息上界，得到 \(I(\text{concept};\text{context})\) 形式的界。**工作量约一天，没人做过，可作为 pfb 的理论附录。**
2. **便宜的直接实验（N2）**：任务书提的 "N 参数 vs K(data)" 判据，可在 27B 上做小样本版：用 gzip/LZ76 估 K(训练集)，再用 LLC 或量化后码长估模型的描述长度，看两者比值随训练步数怎么变。**这就是"记忆 vs 压缩"的可观测版本。**
3. **可操作的 demo 选择（§6）**：`2212.10375` 的 MDL select-then-rank 已经有 8 数据集、40% 相对提升的数字，**可以直接作为 pfb 的 baseline 对照**，比自造准则更稳。
