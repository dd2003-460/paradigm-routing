# T-PR-14: LLM 推理能否套用经典搜索算法的最优性保证？

> origin: human（成璐 2026-11-08 提问）+ ai（任务书结构化）
> 日期: 2026-11-08 · 状态: 待派发
> 仓库: `dd2003-460/paradigm-routing` · 会话: 复用 `arena/62fe3fd4-paradigm-routing`
> 上游: `research/cot-necessity-survey.md` §G（已有 best-of-n vs 回溯对照，但未触及最优性定理）
> 下游: 补全 `idea-reasoning-core-induction-deduction.md` 的"搜索视角"维度

## 【背景】

成璐提出：LLM 推理（尤其 CoT / test-time compute）能否套用广搜（BFS/best-of-n）和深搜（DFS/backtracking）的经典计算机最优搜索算法？已知 landscape 是非凸、随机、可能病态的。问：(a) 经典搜索算法的最优性/完备性定理在这种条件下是否仍成立？(b) 有没有天才已经做过这个交叉？(c) 如果直接搬不通，正确的抽象是什么？

本地已有（不重复查）：
- `cot-necessity-survey.md` §G：G1（Wei 2022 空草稿消融）、G2（2504.07052 best-of-n vs 回溯，回溯不总划算）、G3（Anthropic scratchpad 可压缩）、G4（2605.30757 CoT vs 循环 transformer 记忆预算）
- `reasoning-activation-mechanisms.md`（T-PR-13）：三墙模型、表示墙
- `search-verify-contribution-function.md`：搜索-验证贡献函数（已读，与本题相关但不重叠）

## 【子问题】

### Q1: 经典搜索最优性定理在 LLM token 空间是否适用？
- BFS/DFS 的完备性定理假设：有限分支因子、均匀边权、无环或可检测环、确定性转移。LLM 自回归生成违反了哪些？
- 具体地：token 空间的"边权"是 log-prob（非负但非均匀），"节点"是 prefix（指数增长），"目标"是 answer token（稀疏）。BFS 在这里 = beam search，DFS = greedy/temperature sampling。这些有最优性保证吗？
- **关键区分**：beam search 不是 BFS（它剪枝），greedy 不是 DFS（它不回溯）。所以"LLM 默认解码 ≈ 深搜"这个类比本身就不精确。

### Q2: 非凸/随机/病态 landscape 下，什么搜索策略有理论保证？
- 经典结果：局部搜索在非凸 landscape 上无全局最优保证；模拟退火有收敛到全局最优的概率界（需温度调度满足条件）；MCTS 在博弈树上有 regret bound（但假设对抗性对手，LLM 场景无此结构）。
- LLM 的 loss landscape 已被证明高度非凸（Tsipras et al. 2018, "Mixed Curvature and Asymmetry in Loss Landscapes of Deep Neural Networks"）且存在 spurious local minima。
- **核心问题**：test-time compute（CoT、self-consistency、best-of-n）本质上是在哪个空间做搜索？是 latent space（连续、高维、非凸）还是 token sequence space（离散、组合爆炸）？这两个空间的搜索性质完全不同。

### Q3: 有没有人已经做了"LLM reasoning as search"的形式化？
- 检索方向：
  - "reasoning as search" / "LLM tree search" / "MCTS for LLM" / "best-of-n optimality" / "test-time compute scaling laws"
  - 重点找：是否有论文把 CoT/self-consistency 形式化为搜索问题并给出复杂度/最优性界
  - 已知相关工作（需核验是否覆盖本题）：
    - Self-Consistency (Wang et al. 2022) — majority voting over samples，无最优性定理
    - Tree of Thoughts (Yao et al. 2023) — 显式 BFS/DFS on thought tree，有启发式但无最优性保证
    - MCTS for LLM (e.g., RAP, rStar-Math) — 借用 MCTS 框架，但 regret bound 不直接适用（无对抗对手）
    - "The Illusion of State" (2024?) — 质疑 CoT 是否真的在维护中间状态
    - 任何把 test-time compute 与 computational complexity (P vs NP, circuit complexity) 联系的工作

### Q4: 如果直接搬不通，正确的抽象是什么？
- 候选方向：
  - (a) LLM 推理 ≈ 近似贝叶斯推断（amortized inference），不是搜索——训练时已把搜索"烧进"权重，推理时只是前向传播
  - (b) CoT ≈ 外部化的工作内存 + 受限搜索（只在前几个 token 分支，后面 greedy），所以最优性只适用于前缀选择
  - (c) test-time compute 的正确框架是 "compute-optimal inference"（Kaplan et al. scaling laws 的推理侧版本），不是搜索
  - (d) 信息论视角：CoT 增加的是 mutual information between prompt and answer，不是搜索深度
- 判据：哪个抽象能解释 G2 的观察（best-of-n ≥ 回溯）？能解释 G3（scratchpad 可压缩）？能预测 S8B 的结果？

### Q5: 动态适配能力——模型能否学会根据任务特征自动选择搜索策略？（成璐 2026-11-08 追加）
背景：成璐判断"通用最优是幻想，场景适配才是真的"。问题聚焦为：能不能培养 meta-level 的动态适配能力（整理/写SOP/完整结构搜索和研究推进）。
- Q5.1: 路由信号——什么任务特征决定该广搜 vs 深搜？已有文献是否识别了这些信号？（候选：答案空间大小、是否有唯一解、任务是否可分解、错误代价对称性）
- Q5.2: 切换成本——从一种策略切到另一种的 token/时间/准确率代价有没有被量化过？
- Q5.3: 可激发性——这种 meta-level 策略选择能用 prompt 激发（如"先评估任务复杂度再决定推理深度"），还是必须微调？与 T-PR-13 三墙模型的关系：撞的是哪面墙？
- Q5.4: 与"整理/写SOP/研究推进"的具体映射——成璐说的这三个动作分别对应搜索策略的哪个维度？（整理=剪枝？写SOP=缓存已探索路径？研究推进=迭代深化？）

## 【验收标准】

- AC1: Q1 给出逐条违反清单（BFS/DFS 假设 vs LLM 实际），每条带文献或推导
- AC2: Q2 给出≥2 个在非凸/随机条件下仍有保证的搜索策略及其定理陈述（含条件）
- AC3: Q3 列出≥5 篇直接相关论文（标题+arXiv ID+一句话结论），标注哪些覆盖了本题、哪些没覆盖
- AC4: Q4 给出推荐抽象 + 理由 + 它能解释/预测哪些已知现象
- AC5: 来源≥12，其中≥5 读到公式/定理级
- AC6: 反方质询≥3（攻击本报告的核心判断）

## 【约束】

- 不要重复查 cot-necessity-survey.md §G 已有的 G1-G4
- 重点在"数学支撑"——要定理、要条件、要反例，不要纯叙事
- 如果某个子问题穷尽检索后确认"学界也没定论"，明确说"这是前沿空白"并给出最小可执行实验设计
- 产物写入 `research/reasoning-as-search-survey.md`，搜索日志 `research/search-log-reasoning-as-search.json`