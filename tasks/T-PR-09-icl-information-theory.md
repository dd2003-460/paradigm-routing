# T-PR-09: ICL 最优性的信息论/Bayesian 框架调研

**状态**: dispatched → arena（2026-11-07）
**分支**: `arena/62fe3fd4-paradigm-routing`（与 T-PR-07/08 同会话，T-PR-08 完成后接续）
**产出路径**: `research/icl-information-theory-framework.md` + `research/search-log-icl-it.json`

## 意图锚点（成璐原话，2026-11-07）

> "这几个最优性依赖任务结构是不是相当于神经网络是否是目标的最简描述？然后额外的参数和层只是模拟超级函数拟合各种规则? 但是我感觉确实有一些核心范式可以支持高效的 icl，例如 bayesian 和统计和信息理论下的建模"

拆成三个子命题：
- P1: "ICL 最优性依赖任务结构" ≡ "NN 是否是目标函数的最简描述"？
- P2: 额外参数/层 = 万能函数逼近器在拟合各种规则（而非学到压缩结构）？
- P3: Bayesian / 统计 / 信息论范式是 ICL 高效性的核心支撑（不是巧合，是结构性原因）？

## 背景

已有本地覆盖：
- `icl-generalization-survey.md` A3 条目：ICL ≈ 隐式贝叶斯推断（2111.02080），examples = likelihood，parametric knowledge = prior
- `compression-unified-view-2026-11-07.md`：MDL/Kolmogorov 压缩统一观
- T-PR-07 结论：瓶颈在 verifier 不在 decomposer；dense vs explicit search 条件性成立

本任务要补的是：**把 P1-P3 从直觉变成可检验的形式化命题，并找到学界已有的对应工作。**

## 子问题

### Q1: P1 的形式化——"最优性依赖任务结构" 与 "最简描述" 的关系

- **MDL 视角**：给定数据集 D 和模型族 M，MDL 选 argmin_m [L(D|m) + L(m)]。如果 ICL 的"最优 demo 选择"等价于 MDL 在 demo 空间上的优化，那"任务结构决定最优性"就自动成立——因为不同任务结构的 L(D|m) 项形状不同。
  - 有没有人把 ICL demo selection 显式写成 MDL 优化？（搜索关键词：MDL + in-context learning + demonstration selection）
  - 如果有，形式是什么？demo 的"描述长度"怎么定义？
- **Kolmogorov 视角**：K(f|D) = min_p { |p| : U(p, D) = f }。如果 NN 训练收敛到 K*（近似 Kolmogorov 复杂度），那"NN 是否是目标的最简描述"就是问：训练后的权重是否编码了 K* 级别的压缩？
  - 2509.22445（Bridging Kolmogorov and DL）给了渐近最优性结果——但那是 training 侧。inference 侧（ICL）有没有对应的"context 中的 demo 是否构成 x 的最简条件描述"的结果？
- **任务结构的具体含义**：什么算"任务结构"？（线性可分 vs 非线性？i.i.d. vs sequential？single-task vs multi-task？）不同结构下 ICL 的样本复杂度界分别是什么？

### Q2: P2 的检验——"额外参数 = 万能拟合器" 还是 "压缩结构"？

- **函数逼近定理 vs 压缩**：万能逼近定理（universal approximation）说足够宽的 NN 能拟合任何连续函数——但这不说明它学到了压缩结构。区分标准：
  - 如果额外参数只是在 memorize（记忆训练数据），那压缩率 ≈ 0（参数量 >> 数据复杂度）
  - 如果额外参数在 compress（提取规律），那压缩率 > 0（参数量 << 数据复杂度，且泛化好）
  - **可测判据**：给定 N 个参数和 D 个训练样本，比较 N 和 K(data)（用 LZ76/C 复杂度近似）。N >> K(data) → memorization regime；N ≈ K(data) → compression regime。
  - 有没有人做过这个测量？（搜索：neural network compression ratio + parameter count + dataset complexity）
- **Scaling law 的压缩解读**：Chinchilla 的 loss(N, D) 曲线——在什么 N/D 比值下模型从 memorization 切换到 compression？有没有相变（phase transition）证据？
- **MoE 的特殊性**：MoE 的稀疏激活是否天然倾向于 compression regime（每个 expert 只负责一个子空间，总有效参数 << 总参数）？

### Q3: P3 的核心——Bayesian/信息论范式如何使 ICL 高效

这是用户直觉最强的部分，需要最严格的调研：

**(a) ICL as Bayesian inference（已有线索，需扩展）**
- 2111.02080（GPT-3 era）：ICL ≈ 隐式贝叶斯推断。后续有没有更严格的形式化？
- **关键问题**：prior 是什么？是 parametric knowledge（预训练学到的分布）吗？如果是，那 ICL 的效率取决于 prior 和 true posterior 的距离——**这就是"任务结构决定 ICL 效率"的信息论表述**。
- 有没有人量化过"prior-posterior 距离"对 ICL 样本复杂度的影响？

**(b) Information-theoretic bounds on ICL**
- 搜索：information-theoretic bound + in-context learning / sample complexity + ICL / mutual information + demonstrations
- 已知结果：
  - Von Oswald et al. 2023（ICL = gradient descent in function space）——这是机制解释，不是信息论界
  - Min et al. 2022（ICL = implicit MAP estimation）——接近 Bayesian 但没给信息论界
  - 有没有人给出 I(x; demo) 或 I(y; context) 的下界/上界？
- **核心命题待验证**：如果 ICL 的泛化误差可以被 I(target; context) 的某个函数控制，那"高效 ICL"就等价于"context 携带了关于 target 的高互信息"——这是可测的。

**(c) Statistical learning theory 视角**
- VC dimension / Rademacher complexity 能不能套到 ICL 上？
- ICL 的"假设空间"是什么？（所有可能的 prompt→completion 映射？还是固定模型在不同 context 下的行为集合？）
- 有没有 PAC-Bayes 风格的 ICL 泛化界？（PAC-Bayes 天然适合 Bayesian 叙事）

**(d) 为什么 Bayesian 范式"天然"支持 ICL**
- 用户的直觉：Bayesian 更新 = 先验 × 似然 → 后验。ICL 中 context = 新 evidence，parametric knowledge = prior，输出 = posterior prediction。
- 这个类比在哪里精确成立、在哪里断裂？
  - 精确成立的条件：模型内部真的在做 Bayes 更新（有定理支撑吗？）
  - 断裂的地方：真实 LLM 的 attention 机制不完全等于 Bayes 更新（哪里不等价？）
- **可操作推论**：如果 ICL ≈ Bayes 更新，那"最优 demo 选择"应该最大化 posterior 的信息增益（即减少最大不确定性）——这给出了一个具体的 demo selection 准则。有没有人试过这个准则？

### Q4: 与 T-PR-07 结论的连接

T-PR-07 说"瓶颈在 verifier 不在 decomposer"。在本框架下：
- decomposer = 生成候选步骤（≈ prior sampling）
- verifier = 评估步骤质量（≈ likelihood evaluation）
- 如果 verifier 不可迁移（SCORE 2407.13692），信息论解释是什么？（verifier 需要的是 task-specific likelihood，而 prior 可以跨任务共享？）

## 验收标准

- AC1: ≥200 行 markdown
- AC2: ≥10 个来源，其中 ≥5 个读了原文
- AC3: P1/P2/P3 每个子命题有明确判决（"已证明 / 部分证明 / 仅论证 / 无文献"）+ 最强已有结果
- AC4: Q3(d) 的"Bayesian 类比在哪里精确成立、在哪里断裂"必须逐条列出
- AC5: 结尾给出一句话："Bayesian/信息论范式对 ICL 效率的支撑程度，目前证据支持到什么级别"
- AC6: 如果找到可操作的 demo selection 准则（来自信息论/Bayesian），单独标出并评估实用性

## 检索通道

arXiv API（主）+ 直访 ICML/NeurIPS/ICLR proceedings。禁止纯记忆引用。每条来源记录 URL + 访问日期 + read/abstract-only。