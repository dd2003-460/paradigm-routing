# T-PR-10: "更强的模型"机制分解——MoE 激活 / 联系强度 / 校准，哪个决定所需步数？

**状态**: dispatched → arena（2026-11-07）
**分支**: `arena/62fe3fd4-paradigm-routing`
**产出路径**: `research/model-capability-step-count-mechanisms.md` + `research/search-log-model-capability.json`

## 意图锚点（成璐原话，2026-11-07）

> "更强的模型是什么意思，moe激活更大，或者联系更强?或者校准更好?这些能看到吗"

T-PR-07 说"模型层是软的：同一个洞察换更强的模型所需步数会降"，但没说"强"是哪个维度、能不能观测。本任务把这句话拆成三个可测候选机制，并回答"能不能看到"。

## 背景

已有本地覆盖：
- `long-insight-decomposability-survey.md`：BAPO token 下界（结构层硬的）；"模型层软的"只有一句话，无机制分解
- `lit-survey-arena.md` L194：self-routing 失败在 calibration 不在 knowledge——"执行范式的能力 ≠ 选择何时用范式的能力"
- T-PR-08：MoE 专家相似度实测（Mixtral 0.2-0.4，DeepSeekMoE ~0），单专家 0.95 逼近 6 专家集成
- Qwen3.8-27B config（已验证）：64 层 = 48 GDN + 16 full_attn，hidden 5120，GQA 24Q/4KV，256K ctx

## 三个候选机制（用户直觉的精确化）

### M1: "MoE 激活更大" = 有效容量随任务复杂度扩展？

- **操作化定义**：给定同一任务，不同模型在推理时实际激活的参数比例（MoE: 路由选择的 expert 数 × expert 大小；dense: 全部参数）。"激活更大"意味着模型能调动更多专用子网络来处理复杂步骤。
- **可测性**：
  - MoE 侧：routing logits 可以直接读（activation pattern per layer per token）。有没有人测过"复杂推理任务 vs 简单任务"的 routing entropy / 激活 expert 数差异？
  - Dense 侧：没有显式激活概念，但有 attention entropy / head utilization 作为代理指标。
- **与步数的关系**：如果"强模型"= 每步能调动更多专用容量，那"所需步数减少"的解释就是：每步信息处理量更大 → 总步数更少。这对应 compression-unified-view 里的"解压带宽"概念。
- **关键问题**：有没有直接证据表明"激活参数量 ∝ 任务复杂度"且"激活参数量 ↑ → 所需推理步数 ↓"？还是这只是 scaling law 的间接推论？

### M2: "联系更强" = 跨 token / 跨层的依赖建模能力？

- **操作化定义**：模型能在多远的距离上建立有效依赖。三种度量：
  - (a) Attention span：attention weight 的有效范围（entropy 或 half-life）
  - (b) State retention：SSM/hybrid 中 state 对早期 token 的记忆衰减率
  - (c) Functional dependency：给定输入第 i 个 token，输出第 j 个 token 对其的梯度敏感度（i << j 时是否仍显著）
- **与步数的关系**：如果"强模型"= 能在一步内 attend 到更远的上下文依赖，那长链推理可以"跳步"——不需要串行写出中间状态，因为中间状态已经在 context 里被 attend 到了。这直接对应 T-PR-07 的"并行 attend 路线受窗口限制"。
- **可测性**：
  - (a)(b) 可以直接从 forward pass 读出（attention matrix / state trajectory）
  - (c) 需要 backprop，成本高但可行
- **关键问题**：有没有人量化过"attention span / state retention 与推理链长度的关系"？即：模型能 attend 多远 ↔ 它能一次处理多长的推理链？

### M3: "校准更好" = 知道自己不知道，从而避免无效步？

- **操作化定义**：模型的 confidence 与其实际正确率的匹配程度（ECE = Expected Calibration Error）。"校准好"意味着：
  - 不确定时会表达不确定（而非自信地胡说）→ 不会浪费步数在错误方向
  - 确定时不会过度保守 → 不会冗余验证
- **与步数的关系**：这是最间接的机制。校准不直接减少"每一步的信息处理量"，而是减少"走错路后的回溯成本"。在搜索框架下（T-PR-07 的 ProsQA/GSM8K 对比），校准好的模型 = 更好的 selector（知道哪条路值得走），而不是更好的 searcher。
- **可测性**：
  - ECE 可以直接算（logprob vs correctness）
  - 更精细的：per-step calibration（推理链中每一步的 confidence vs 该步骤的正确性）——这个有没有人做过？
- **关键问题**：有没有证据表明"校准误差与推理步数效率相关"？即：同样答对的题，校准好的模型用的步数更少（因为少走弯路）？

## 核心问题："这些能看到吗？"

逐个回答：
1. **M1（激活）**：MoE 可以直接看 routing activation；dense 只能用 proxy（attention entropy）。**可见性：高（MoE）/ 中（dense）**
2. **M2（联系）**：attention matrix 和 state trajectory 都是 forward pass 的直接输出。**可见性：高**
3. **M3（校准）**：logprob 直接可读，ECE 标准计算。**可见性：高**

但"可见"≠"解释了步数减少"。真正的检验是：**控制其他两个变量，单独变一个，看步数怎么变。** 这在文献里存在吗？

## 子问题

### Q1: 有没有工作直接测量"模型能力维度 X 变化 → 推理所需步数变化"？

- 搜索关键词：
  - "reasoning steps" + "model size" OR "capability" + "chain of thought length"
  - "test-time compute" + "scaling" + "steps" OR "tokens"
  - "inference efficiency" + "model capability" + "reasoning depth"
- 已知线索：
  - test-time compute scaling（Snell et al. 2024, arXiv 2403.16952 [待核验]）：compute budget 增加 → 性能提升，但这是"给更多步"不是"每步更强"
  - 有没有反向的实验：固定步数预算，比较不同模型的 per-step 信息增益？

### Q2: M1/M2/M3 三者之间有没有相关性数据？

- 比如：更大的模型（通常 M1+M2 都更强）是否也校准更好（M3）？还是独立维度？
- 如果有独立性证据，那"强"就不是单一维度，用户的三选一是假选项——可能是组合效应。

### Q3: 在本地 27B 上能不能做最小实验？

- 我们有一个 qwen3.8-27b（64 层 GDN+attn hybrid）。虽然它不是 MoE，但可以：
  - 测 M2：不同长度 prompt 下 attention 有效 span 的变化
  - 测 M3：同一批题目，不同 temperature 下的 ECE vs 成功率
  - 不能测 M1（不是 MoE），但可以测 attention entropy 作为 proxy
- 这个实验的价值：不是发论文，是建立"在本地模型上这三个维度确实可观测"的 baseline，为后续 pfb 实验提供工具链。

## 验收标准

- AC1: ≥180 行 markdown
- AC2: ≥8 个来源，其中 ≥4 个读了原文
- AC3: M1/M2/M3 每个有明确判决："有直接证据 / 有间接证据 / 无文献" + 最强已有结果
- AC4: "这些能看到吗"逐条回答（可见性评级 + 具体方法）
- AC5: 如果找到"控制一个变量变另一个"的因果实验，单独标出
- AC6: 结尾一句话："在现有文献中，'更强模型 → 更少步数'的最主要机制是 ___（conf __）"

## 检索通道

arXiv API（主）+ 直访 proceedings。禁止纯记忆引用。每条来源记录 URL + 访问日期 + read/abstract-only。