# Paradigm Routing: "None of the Above" Calibration for Small Models

> origin: human (成璐 2026-11-07 idea) + ai (literature mapping + arena verification)
> Status: **Phase 1 complete** (arena lit-survey @ 9314d34), Phase 2 design ready

## 核心假设

小模型（≤27B）在真实科研任务上无法校准"该用哪种推理范式"，且现有范式列表可能全部不适用。加入"都不适用"选项后：
1. 能否减少错误范式选择导致的性能下降？
2. 弱模型的 self-routing 崩溃（Select-then-Solve 发现）是否可通过显式 NA 选项缓解？
3. 多种问法 × 乱序取平均能否稳定路由信号？

## 与已有工作的差异（arena 核验后修正版）

| 工作 | 做了什么 | 没做什么（我们的空间） |
|------|---------|---------------------|
| Select-then-Solve (2604.06753) | 6 范式 × 4 模型 × ~18k runs；embedding router 选最优范式；**排除 all-paradigms-fail 样本** | 只能从已知列表选；无 NA 选项；benchmark 非真实科研任务；router 需训练。**最强切入点：他们排除的样本 = 我们的第四类** |
| None-of-the-Above (2503.01550) | MMLU 加 NA 选项，28 LLM 掉 30-50% | 只测了"NA 做正确答案时掉多少"，没测"NA 作为路由信号是否有用"；MMLU 非开放任务 |
| RTR (2505.18393) | 强化学习路由器，按题面特征选 CoT/CoF/CoP | 需训练；3 个固定策略；无 NA 通道；非零训练 |
| SoT (2505.11553) | 元认知 prompt 让 LLM 自选策略 | 无 NA 选项；未量化弃权率；未区分"选错"vs"全不适用" |
| Latent Strategy (2507.08547) | 隐变量建模 CoT 中的潜在策略 | 描述性分析，不做路由决策；无 NA 概念 |
| Router-R1 (NeurIPS 2025) | RL 多轮模型路由 | 选的是哪个模型，不是哪个推理范式 |
| AgentAbstain (2605.02274) | agent 级弃权（工具调用层面） | 弃权发生在 action 层，不是 paradigm 层；实证"执行能力≠选择能力" |

**我们的空白**：真实科研任务 × 小模型 × 带 NA 选项的零训练 self-routing × 多问法稳定性 × **"全失败"样本是可学习第四类**。

## 关键文献（arena 已核验 ✅）

- arXiv 2604.06753 — Select-then-Solve（最接近，2026-04）✅
- arXiv 2503.01550 — None of the Above（NA 效应量化）✅
- arXiv 2505.18393 — RTR: Reasoning Type Router（RL 路由器）✅ [原标 TRICE，张冠李戴已修正]
- arXiv 2505.11553 — SoT: Self-adaptive Strategy Selection（元认知 prompt）✅ [原标 CISC，张冠李戴已修正]
- arXiv 2507.08547 — Latent Strategies in CoT ✅
- arXiv 2605.02274 — AgentAbstain（agent 级弃权，执行≠选择实证）✅
- arXiv 2502.00919 — Attention Sinks catch-tag-release（机制背景）✅
- arXiv 2412.12094 — SepLLM（分隔符信息压缩，隔壁实验）✅
- arXiv 2510.08203 — Function Token Hypothesis ✅
- AbstentionBench / R-Tuning / CALM — 弃权方法论参照 ✅
- AoT / AOP / ADaPT — 正交完备分解先例 [仍待核验具体编号]

## Arena 调研核心结论（详见 research/lit-survey-arena.md）

1. **TRICE/CISC 是张冠李戴**——实际不存在这两个名字的策略路由器论文。正确对标 = RTR + SoT + latent-strategy。
2. **范式级弃权 = 确认空白**（conf 0.65）——答案层/agent 层/工具层的弃权研究成熟，但"推理范式列表上加 NA"零命中。
3. **最强叙事 = "第四类"**：STS 原文 "tasks where all paradigms fail are excluded from training but counted as incorrect during evaluation"——我们证明这些不是噪声而是可学习的第四类。
4. **最大风险 = 效果而非 novelty**：NA 让模型掉 30-50%（2503.01550）+ 推理微调恶化弃权 -24% + 小模型 meta-cognition 有害 → NA 可能让结果更差。高信息量实验，但不一定是正结果。
5. **最小实验方案**（§8）：4 条件 × 3 reps，主指标含 gold-margin（区分"NA 提供信息"vs"NA 吸走概率"），必须有 NA-present-but-masked 对照。预注册判决规则。

## 实验设计（Phase 2，基于 arena §8 细化）

### 条件设计（4 条件）

| 条件 | 说明 |
|------|------|
| C0: Force-select | 必须从 N 个范式中选一个（基线） |
| C1: +NA | 范式列表 + "都不适用"选项 |
| C2: +NA-masked | NA 存在但 judge 不知道（控制 NA 对回答质量的干扰） |
| C3: Phrasing ensemble | C1 × 3 种措辞 × 2 种顺序，取多数投票 |

### 任务集
- 来源：pfb gold questions + D1 项目真实科研子任务
- 规模：10-20 题（含 ≥3 题"全范式都答不对"的困难题）
- 标注：每题人工标注"正确范式"或"全不适用"

### 范式列表
Direct / CoT / ReAct / Plan-Execute / Reflection / **都不适用**

### 模型
- 本地 27B（vLLM qwen3.8-27b, temp=0）
- 判官：同族 27B temp=0（仅相对有效，标注）

### 指标
1. **路由准确率**（C0 vs C1 vs C3）
2. **NA 触发率 vs 实际"全不适用"率**（假阳性/假阴性）
3. **gold-margin**：NA 触发的题中，强制选择时的性能 drop 有多大（区分"NA 提供信息"vs"NA 吸走概率"）
4. **覆盖率口径**：NA 触发的题按拒答计 0，另报允许升级的分支
5. **phrasing stability**：C3 的方差 vs C1 的方差

### 预注册判决规则
- H1 成立：C1 路由准确率 > C0 且 NA 假阳性率 < 30%
- H1 不成立：C1 ≤ C0 或 NA 假阳性率 > 50%（→ 报告为 negative result，仍有价值）
- H2 成立：C3 方差 < C1 方差 × 0.5（phrasing ensemble 有效）

## 仓库结构

```
paradigm-routing/
├── INDEX.md          ← 本文件
├── research/         ← arena 调研产出（lit-survey-arena.md ✅）+ idea-reasoning-core-induction-deduction.md（推理核心 idea，理论骨架）
├── experiments/      ← 实验代码+结果（Phase 2 待建）
├── memory/           ← 探索记录
└── tasks/            ← 临时状态（arena-task-brief.md ✅）
```