# Paradigm Routing: "None of the Above" Calibration for Small Models

> origin: human (成璐 2026-11-07 idea) + ai (literature mapping)
> Status: pre-research, arena dispatch pending

## 核心假设

小模型（≤27B）在真实科研任务上无法校准"该用哪种推理范式"，且现有范式列表可能全部不适用。加入"都不适用"选项后：
1. 能否减少错误范式选择导致的性能下降？
2. 弱模型的 self-routing 崩溃（Select-then-Solve 发现）是否可通过显式 NA 选项缓解？
3. 多种问法 × 乱序取平均能否稳定路由信号？

## 与已有工作的差异

| 工作 | 做了什么 | 没做什么（我们的空间） |
|------|---------|---------------------|
| Select-then-Solve (2604.06753) | 6 范式 × 4 模型 × 10 bench，embedding router 选最优范式 | 只能从已知列表选；无 NA 选项；benchmark 非真实科研任务；router 需训练 |
| None-of-the-Above (2503.01550) | MMLU 加 NA 选项，28 LLM 掉 30-50% | 只测了"NA 做正确答案时掉多少"，没测"NA 作为路由信号是否有用"；MMLU 非开放任务 |
| TRICE / CISC / latent strategies | 潜在策略识别、条件概率路由 | 未覆盖"全都不适用"的拒绝通道 |
| Router-R1 (NeurIPS 2025) | RL 多轮模型路由 | 选的是哪个模型，不是哪个推理范式 |

**我们的空白**：真实科研任务 × 小模型 × 带 NA 选项的零训练 self-routing × 多问法稳定性。

## 关键文献（待 arena 深入核验）

- arXiv 2604.06753 — Select-then-Solve（最接近，2026-04）
- arXiv 2503.01550 — None of the Above（NA 效应量化）
- arXiv 2502.00919 — Attention Sinks catch-tag-release（机制背景）
- arXiv 2412.12094 — SepLLM（分隔符信息压缩，隔壁实验）
- arXiv 2510.08203 — Function Token Hypothesis
- TRICE / CISC — [待核验具体 arXiv 编号]
- AoT / AOP / ADaPT — 正交完备分解先例 [待核验]

## 实验设计草案（arena 调研后细化）

### Phase 1: 文献补查（arena）
- TRICE/CISC 到底覆盖了什么，和我们的 NA-routing 差多远
- Select-then-Solve 的 self-routing 崩溃细节（哪些模型、崩到什么程度）
- 有没有人做过"范式级弃权"（abstention at paradigm level）

### Phase 2: 最小实验（本地 27B）
- 任务集：从 pfb gold questions + 真实科研子任务中取 10-20 题
- 范式列表：Direct / CoT / ReAct / Plan-Execute / Reflection / **都不适用**
- 问法变体：3 种措辞 × 2 种顺序（固定/乱序）× n=3 reps
- 指标：路由准确率 vs 强制选择的基线；NA 触发率 vs 实际"全错"率
- 判官：同族 27B temp=0（仅相对有效，标注）

### Phase 3: 机制分析（可选）
- NA 选项出现时 attention pattern 变化（接 SepLLM 的分隔符机制）
- 置信度（logprob）与路由正确性的相关性

## 仓库结构

```
paradigm-routing/
├── INDEX.md          ← 本文件
├── research/         ← arena 调研产出
├── experiments/      ← 实验代码+结果
├── memory/           ← 探索记录
└── tasks/            ← 临时状态
```