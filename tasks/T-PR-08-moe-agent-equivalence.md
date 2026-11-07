# T-PR-08: MoE vs Mixture-of-Agents 数学等价性调研

**状态**: dispatched → arena（2026-11-07）
**分支**: `arena/62fe3fd4-paradigm-routing`（与 T-PR-07 同会话，T-PR-07 完成后接续）
**产出路径**: `research/moe-agent-equivalence-survey.md` + `research/search-log-moe-agent.json`

## 意图锚点（成璐原话，2026-11-07）

> "或者庞大的moe可以由一些大部分正交的小agent模拟吗，他们的纠缠，激活，有什么数学等价性吗，在什么层次等价性没有证明"

## 背景

MoE = 大量专家 FFN + top-k 路由；Mixture of Agents (MoA) = 多个独立 LLM agent 分层协作（LLM 层的 MoE）。用户直觉：如果小 agent 之间大部分正交，它们的组合行为可能复现巨型 MoE 的某些性质。需要严格界定"等价"在哪一层成立、哪一层不成立、哪一层没人证过。

## 子问题

### Q1: 已知形式化结果（必须逐条列出并读原文）

- **Mixture of Agents (MoA)** — Wang et al. 2024 (arXiv 2406.04692)：分层 proposer + aggregator，实证优于单模型。有没有给出任何形式化等价性？还是纯经验？
- **Mixture-of-Experts 的形式化理论**：
  - Switch Transformer (Fedus et al. 2021, arXiv 2101.03961)：routing 作为 learned discrete choice，有 capacity factor / load balancing loss 的分析，但无等价性定理
  - GShard (Lepikhin et al. 2020, arXiv 2006.16668)：early work
  - 有没有论文把 MoE 前向传播写成显式的 piecewise-linear / piecewise-smooth 函数，然后和 ensemble 比较？
- **Ensemble theory ↔ MoE**：
  - Classic ensemble (Bauer & Krause 2019, arXiv 1906.02640 "Deep Ensembles") 和 MoE 的关系有没有人正式写过？
  - Bagging / stacking 的泛化界 (Wolpert 1992; Breiman 1996) 能否直接套到 MoE expert 上？expert 不是 i.i.d. 采样，这个 gap 有人量化过吗？
- **Sparse autoencoders as feature decompositions**：
  - SAE (Bricken et al. 2023, arXiv 2303.08774) 把 residual stream 分解为 sparse features——这和 MoE expert 的"每个 expert 负责一个子空间"在数学结构上是什么关系？
  - Anthropic's SAE interpretability work 有没有把 expert activation pattern 和 SAE feature 对齐过？

### Q2: "正交性"假设下的等价条件

- 如果 N 个 expert 的输出方向两两正交（或近似正交），top-k routing 退化为简单的线性组合——此时 MoE 前向传播是否等价于一个固定权重的 ensemble？
- 正交性的度量：cosine similarity of expert output subspaces? 有没有人测过真实 MoE（Mixtral 8x7B, DeepSeek-V3, Qwen3-MoE）expert 之间的实际正交程度？
- **关键反例搜索**：什么条件下正交性假设必然失败？（expert 共享底层 embedding / shared attention 层 / router 的非线性）

### Q3: "纠缠"（entanglement）的精确含义

用户说的"纠缠"需要拆成两个层面分别调研：

**(a) 信息论纠缠**：多 agent 系统中，agent i 的输出对 agent j 的状态有影响（通过 message passing / shared context）。这对应电路复杂度里的 communication complexity——有没有下界说"要模拟 N 个纠缠 agent 需要多少 bit 通信"？

**(b) 量子计算类比**：MoE 的 routing 是不是某种 classical analog of quantum superposition？（大概率不是，但需要找到最接近的形式化尝试并说明为什么不是。）

**(c) 动力学纠缠**：训练过程中 expert 权重相互影响（shared parameters, load balancing loss 耦合所有 expert 的梯度）。这种 training-time entanglement 在 inference-time 是否消失？

### Q4: 等价性未证明的层次（核心交付物）

按以下层次逐一判定"已证明 / 部分证明 / 完全空白"：

| 层次 | 内容 | 当前状态 |
|------|------|---------|
| L0: 单 token 前向 | 给定输入 x，MoE(x) vs Σ wᵢ·Agentᵢ(x) | ? |
| L1: 序列级行为 | 多 token 生成时的分布匹配 | ? |
| L2: 训练动力学 | 优化轨迹是否收敛到等价参数 | ? |
| L3: 泛化保证 | 样本复杂度 / 泛化界是否可迁移 | ? |
| L4: 涌现能力 | scaling 时新能力出现的方式是否相同 | ? |

每格必须给出：(i) 是否有文献覆盖；(ii) 最强已有结果是什么（论文 + 定理编号）；(iii) 距离完整证明缺什么。

### Q5: 实用推论

如果 L0-L1 等价成立但 L2-L4 不成立，那"用小 agent 模拟大 MoE"的实际意义是什么？成本-性能曲线怎么画？有没有已经有人在做的系统（如 vLLM multi-instance, OpenAI function calling chains）被分析过等价性？

## 验收标准

- AC1: ≥250 行 markdown
- AC2: ≥12 个来源，其中 ≥6 个读了原文（标注 "read" vs "abstract-only"）
- AC3: Q4 表格完整填写，每格有明确判定
- AC4: 至少 2 个反方质询（例如"正交性假设是否过于理想化以至于无实际意义"），附防御或修正
- AC5: 结尾给出一句话判决："MoE 可以被正交小 agent 模拟到什么程度，目前证据支持什么"

## 检索通道

arXiv API（主）+ 直访 ICML/NeurIPS/ICLR proceedings。禁止纯记忆引用。每条来源记录 URL + 访问日期 + read/abstract-only。