# CoT 三分法调研：哪些"思考"可以被更便宜的机制替代

> origin: ai（基于成璐 2026-11-07 提出的 CoT 压缩/解压框架 + 效率论点）
> 日期: 2026-11-07 · 状态: 落盘待实验验证
> 本地覆盖检查: research/ 下无 CoT 必要性专题（lit-survey-arena.md 仅散见提及）→ 确认缺口后外查

## 核心命题

CoT 是混合体，按功能分三类，可替代性不同：

| 类 | 功能 | 替代机制 | 本调研证据强度 |
|----|------|---------|--------------|
| 1. 指令/强调类 | 让模型"记住"约束 | context 重复（instruction duplication） | 强（直接实验） |
| 2. 条件路由类 | "该用哪个范式"的决策 | 外部 if-else / prompt 结构 | 中（间接） |
| 3. 真推导类 | 多步依赖计算 | 不可替代 | 强（元分析界定范围） |

**待测主假设**: (b) 结构化无 CoT ≈ (a) 自由 CoT，且 token 省 70%+；差距残差 = 第 3 类真实成本。

## A. CoT 收益的任务边界（第 3 类的范围界定）

- **A1: 2409.12183**（ICLR 2025, "To CoT or not to CoT?"）— 100+ 论文元分析 + 20 数据集 × 14 模型自测。结论：**CoT 的强收益集中在数学/逻辑/符号推理**；MMLU 这类知识型任务上直接答 ≈ CoT。→ 这是"第 3 类"的实证边界：不是所有任务都值得花推理 token。conf 0.9（直接相关、大样本）。
- **A2: 2506.07142**（Wharton Prompting Science Report 2）— 独立复现方向一致：CoT 有效性高度任务依赖，且随模型变大收益递减（大模型裸答已内化了部分"思考"）。conf 0.8。
- **A3: 2608.09942**（When CoT Helps and When It Hurts）— 标题即立场：存在 CoT 有害区间。未读全文，作为方向性旁证。conf 0.5 [待核验细节]。

**对三分法的含义**: 第 3 类（真推导）只占任务分布的一部分——在检测/摘要/判断类任务（我们的 T0/T1/T2 场景）上，CoT 的理论收益本来就小。这直接支持"大部分 CoT 开销是 1+2 类"的先验。

## B. 过度思考与 test-time compute 预算（浪费的量化）

- **B1: 2507.02076**（Reasoning on a Budget, survey）— 系统综述自适应/可控 TTC。核心观察：**当前模型对简单题和难题花同样的推理算力**——简单题 overthink、难题 underthink。两层分类法（L1 控制生成长度 / L2 动态分配）。conf 0.85。
- **B2: 2510.21067**（Virtues of Brevity）/ **2510.09535**（Mitigating Overthinking through Reasoning Shaping）— 多条独立路线都在做"砍掉冗余思考步骤"，说明浪费是公认问题而非我们臆造。conf 0.7（未读全文）。

**对实验的含义**: 我们的 (a) vs (b) 对比本质上就是在测 B1 说的"固定算力 vs 按需算力"——如果 (b) 不掉点，证明该任务属于"overthink 区"。

## C. CoT 不忠实：答案先定，解释后补（表演性解压的直接证据）

- **C1: 2603.01437**（Post-Hoc Reasoning in CoT）— 机制层面证据：**instruction-tuned 模型经常在生成 CoT 之前就确定了答案**，后面的"推理链"是在为已定的答案找理由（pre-committed answer + post-hoc justification）。训练线性化了这个行为。conf 0.8（机制研究，方法可信）。
- **C2: 2508.19827**（Active Guidance or Unfaithful Post-hoc Rationalization?）— soft-reasoning 任务上测 CoT 动力学：CoT 对输出的实际影响（influence）与表面忠实度（faithfulness）**不对齐**——看着像在引导，实际没引导。conf 0.8。
- **C3: 2503.08679**（CoT in the Wild Is Not Always Faithful）/ **2607.23458**（Two Regimes of Unfaithfulness）— 同方向多源。conf 0.7。

**这是三分法里最硬的一块证据**: 如果答案在 CoT 开始前就定了，那 CoT 的"推理"功能（第 3 类）在这些模型上根本没发生——它退化成第 1 类（格式/强调）甚至纯输出装饰。注意 C1 说的是 instruction-tuned 模型；reasoning 模型（o1/R1 系）是否同样 pre-commit 仍有争议，我们的 27b 属于哪边需要实验判定——这正是 (a) vs (b) 能回答的。

## D. 第 1 类的替代机制：context 重复（有直接实验支持）

- **D1: 2609.04024**（Instruction Duplication as an Inference-Time Control Primitive）— **直接命中**: 把程序性指令在 prompt 里重复一遍（不改权重、不改解码），7 个模型 × 300 题 × 16800 次生成，指令从 1 份到 2 份显著提升确定性遵循率。→ "指令跟随靠 context 出现次数，不靠模型思考"有了受控实验背书。conf 0.85。
- **D2: 2510.14842**（Boosting Instruction Following at Scale）— 方向一致：加指令数量提升遵循率（2 条指令 +7pt，10 条 +4pt），但用的是 post-generation boosting 变体。conf 0.7。
- **D3: 2410.07103**（Repetition for Multi-Hop Reasoning）— 重复关键信息可解锁多跳推理，说明重复的作用不止于"强调"，还能充当中间锚点。conf 0.7。

**设计含义**: 实验条件 (b) 的"context 强化关键约束"应具体化为**关键约束重复 2 次**（D1 的最小有效剂量），而不是随意加话——这样 (b) 失败时可以归因到"重复不够"而非"机制无效"。

## E. 第 2 类的替代机制：显式路由（证据较间接）

- **E1: 2506.16655**（Arch-Router）/ **2506.09033**（Router-R1）— 这些是"LLM 当路由器选下游模型"的工作，证明路由决策可以独立成一个轻量环节，但不直接证明"prompt 里的 if-else 能替代模型自主选范式"。conf 0.5（类比证据）。
- 本地已有支撑: separator v4 结果（标签边界 Δ_presence=+0.20）表明**结构化标记改变了检索行为而无需额外推理**——这是我们自己的小型第 2 类替代证据。

**诚实评估**: 第 2 类是三分法里证据最弱的一环。学界没有直接做过"显式路由 prompt vs 模型自主路由"的对照（至少本轮没搜到）。我们的实验 (a) vs (b) 会第一次在 no-query detection 场景上给出这个数据点——这是个潜在贡献点，不只是验证。

## F. 实验设计的直接输入

1. **条件 (b) 的具体化**: 关键约束重复 2 次（D1 剂量）+ 显式路由句（"若发现 X 类异常则报告，否则只总结"）——两个组件分别对应第 1、2 类替代。
2. **任务选择暗示**: A1/A2 说 CoT 收益集中在数学/逻辑——我们的文档检测任务偏"soft reasoning"（C2 的定义），理论上正是 CoT 收益最小的区域，(b)≈(a) 的先验概率高。
3. **判据补充**: 除准确率外记录 (a) 的回答里"反思句式占比"（如"让我再检查/可能/等等"），如果 (a) 高 (b) 低且准确率不变 → 直接观测到表演性解压被砍掉（呼应 C1/C2）。
4. **模型类型标注**: 跑之前确认 27b 是否经过 reasoning 蒸馏——C1 的 pre-commit 现象在 instruction-tuned 上强，reasoning 模型上未知，结果解读依赖这个标注。**已核验（2026-11-07, HF config.json）**: Qwen3.8-27B = qwen3_5 hybrid（48 GDN + 16 full attention, hidden 5120, GQA 24/4, 256K ctx, MTP 模块），标准 instruct 对齐、无 reasoning 蒸馏痕迹 → C1 证据可直接用于本实验解读。

## F. 重复剂量曲线：1/2/3 次的边际效益（2026-11-07 补查）

- **F1: 2609.04024**（同 D1，读全文后修正）— 1→2 次：All-8 诊断 90.22%→93.17%（+2.95pp），消除 30.2% 剩余失败；但**最终答案准确率两边完全相同（60.21%）**——改善的是轨迹可控性不是答对率。副作用：premature commitment +0.77pp。未测 3 次。conf 0.9。
- **F2: 2512.14982**（Prompt Repetition Improves Non-Reasoning LLMs）— ×2 赢 47/70 组合、0 输；**×3 在检索型任务（NameIndex/MiddleMatch）显著超过 ×2**，多数任务持平。机制：因果 LM 前半段看不到后半段，重复让每个 token 都能 attend 到所有其他 token。推理模型上收益中性偏正。conf 0.85。
- **F3: 2412.07923**（Asking Again and Again）— 问题重复 1/3/5 次：最多 +6% 但统计不显著；大模型对重复更不敏感。conf 0.75。
- **F4: Zenodo 预注册研究**（agent pipeline 指令重复，3 实验 4306 消息）— 全部 null，天花板效应。conf 0.6（非同行评审）。
- **F5: 2608.02639**（Instruction Stacking Collapse）— 复杂规则维度的关键证据：**遵循率随约束条数非线性崩塌**（1 条 ~96% → 20 条最低 20%），根因是指令间冲突而非数量本身；弱模型用 LLM 改写重组找回 +11pp，强模型无感。conf 0.8。
- **F6: 2505.13514**（Induction Head Toxicity）— 重复的暗面：induction head 主导输出 logits 触发"重复诅咒"，过度重复导致失控复读。conf 0.7。

**剂量结论**: 2 次附近饱和；2→3 的额外收益只在检索型任务出现（我们是检测任务，不适用）；过多重复稀释优先级信号并诱发重复诅咒。**条件 (b) 剂量定 2 次**。

## G. "CoT = 搜索预算"假说的对照证据（2026-11-07 补查）

- **G1: Wei et al. 2022 消融**（2201.11903）— "variable compute only"（只输出 `....` 占位符不加内容）提升大幅缩水但不为零：**空草稿没用，草稿内容是主体**，token 预算本身贡献一小块。支持三分法第 3 类需要的是中间状态而非字数。conf 0.9。
- **G2: 2504.07052**（To Backtrack or Not to Backtrack）— 固定算力下比长 CoT 回溯试错 vs best-of-n 并行采样：**回溯不总是更划算**，显式回溯链常只是变啰嗦不提分。→ 对系统设计的含义：裸答 + 外部多次采样 + 便宜判官选优，产投比可能高于单条长链试错。conf 0.8。
- **G3: Anthropic 2025**（Do reasoning models use their scratchpad like we do?）— 把 Claude 3.7 的 scratchpad 换成同义改写再蒸馏回去，性能不掉 → 草稿里没有藏在格式里的隐藏计算，草稿内容基本就是字面意思，**可被压缩/改写而不损失功能**（草稿是可外置的中间产物）。conf 0.8。
- **G4: 2605.30757**（CoT and Compressed Looped Transformers）— 理论版：CoT 与循环 transformer 的区别在记忆预算——CoT 把中间状态存在 context（可无限增长），循环状态固定大小（跑再久也是小空间推理者）。"草稿=可扩展工作内存"的复杂度理论表述。conf 0.75。

**对实验的含义**: (a) 组加廉价变体 **(a') 允许草稿但限 50 token**——若 (a')≈(a)，直接证明"预算不够大就不起作用"，把搜索预算假说钉死。

## H. 边界与未解

- C1 的"pre-commit"是否普遍到 reasoning 模型？未解，需专门实验（可后续加条件 (d): 强制先答后释 vs 先释后答，看答案是否改变）。
- 第 2 类的直接对照文献缺失——我们的数据可能是首批之一。
- "token 省 70%" 是预设阈值不是预测值；实际省多少取决于 (a) 基线有多啰嗦，跑完才知道。