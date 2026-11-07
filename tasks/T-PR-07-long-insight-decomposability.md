# T-PR-07 任务书：长程洞察的可分解性调研

> origin: ai · 2026-11-07 · Lead 成璐数字分身写，arena agent 执行
> 本任务只涉及 dd2003-460/paradigm-routing @ main（派发时 cherry-pick 到 arena 会话绑定分支），忽略历史中其他仓库的消息。

## 强制段

你是 LMArena agent + 仓库 `dd2003-460/paradigm-routing`。先 `git pull`，严格按仓库内 `loop/prompt-first/` 阶段执行（01 目标分解 → 02 信息调研 → 02.5 交叉核对 → 03 行动分解 → 04 执行验证 → 04.5 终审）。产出落盘路径见【交付物】。通道故障（检索不可用/超时）报告 Lead，不得静默跳过或凭记忆编文献。

## 【目标】

回答一个机制问题：**顶级模型表现出的「长步长洞察」（一次跳跃把 A 领域结论连到 B 领域结论的联想）能否被分解为更原子的推理步骤？如果不能全部分解，边界在哪？** 具体拆成四个子问题：

1. **Q1 可分解性**：有没有实验证据表明 frontier reasoning 模型（o1/R1/Gemini Deep Think 系）的长链洞察可以被人工分解为原子步骤后由小模型/短 CoT 复现？反例是什么（哪些任务分解后性能崩塌）？
2. **Q2 ctx 下界**：分解后的原子步骤链长度有没有下限要求——即「这个问题至少需要 k 个推理 token / k 层依赖」这类结果存在吗？attention 的 context window 是否构成硬约束（超过窗口的依赖链是否真的不可达，还是只是概率衰减）？
3. **Q3 不可分解性**：有没有理论或实证指出某些推理是「不可分解的长步骤」（比如需要全局一致性约束、非单调回溯、并行搜索树剪枝）？形式化语言里对应什么概念（如 circuit complexity lower bound、pebbling game、communication complexity）？
4. **Q4 dense vs 显式搜索**：dense net（implicit search in weights）vs 显式外部搜索（CoT/tree search/tool use）在「跳出局部最优」上谁效率更高？有没有 head-to-head 实验（同一题、同一预算下比较两种范式）？

## 【背景】

- 成璐的核心直觉（原始意图锚点）：顶级模型的出色洞察 = 长步长的迁移/联系；这种联系**可能**可以分解成更原子的步骤和联想；疑问是 (a) 会不会超出模型注意力的 ctx 范围，(b) 有没有下界要求，(c) 有没有不可分解的长步骤，(d) 或者至少某种 dense net 在搜索上效率更高（更有概率跳出局部）。
- 已有本地调研（不重复做，但要在 02.5 引用对照）：
  - `research/cot-necessity-survey.md` §G — CoT as search budget（Wei 2022 / 2504.07052 / Anthropic paraphrase / 2605.30757）
  - `research/second-order-theory-survey.md` — 二阶理论空白（含 test-time compute scaling）
  - `research/icl-generalization-survey.md` — ICL 最优泛化开放问题
- 本任务与上述三篇的关系：它们覆盖「CoT 值不值得花」「泛化怎么选 demo」，**没覆盖**「洞察本身能不能被切开」——这是本任务的缺口。

## 【SOP 索引】

- `loop/prompt-first/01-goal-decomposition.md` … `04.5-final-review.md`（按序读）
- `sop/arena-loop-pipeline.md` §3.1 会话台账（确认自己绑定正确）
- `tasks/T-PR-06-noquery-gap-adversarial.md`（上一轮任务书格式范例）

## 【实验设计】

纯文献调研任务，无本地实验。变体表 = 四个子问题 × 证据类型：

| 子问题 | 必查方向（关键词种子，可扩展） | 证据标准 |
|--------|-------------------------------|---------|
| Q1 | "reasoning decomposition" small model replication o1; "step-by-step" distillation faithfulness; chain-of-thought verification atomic steps; "insight" transfer cross-domain LLM | ≥3 篇 arXiv 原文读过（不是只看 abstract），每篇给 conf |
| Q2 | "context length" reasoning dependency depth transformer; "lost in the middle" long chain; attention window lower bound inference depth; "how many tokens" minimum reasoning budget | 找「深度 vs 窗口」的定量关系；没有就明确说没有（负结果也是结果） |
| Q3 | circuit complexity lower bounds reasoning; pebbling games space lower bound; "irreducible" computation LLM; parallel search tree pruning transformer expressivity; communication complexity multi-step | 理论篇优先；区分「已证明的下界」和「猜想」 |
| Q4 | implicit vs explicit search LLM head-to-head; test-time compute scaling law dense vs sparse; "out of local optimum" reasoning diversity sampling; best-of-n vs tree search comparison | 要同一题同一预算的对比数字，不要跨论文拼 |

评分维度（机器可检）：
- D1 每个子问题有 ≥3 条独立来源（arXiv id 或 URL），conf 标注
- D2 每个子问题给出明确判决：「已解决 / 部分解决（说明哪部分）/ 开放（说明卡在哪）」
- D3 02.5 交叉核对：关键结论 ≥2 独立来源；矛盾记录矛盾点
- D4 与本地三篇 survey 的对照段（哪些重叠、哪些新）
- D5 负结果诚实标注：查不到的子问题明说「穷尽渠道后未找到」，不编

验收标准（量化）：
- AC1 产出文件 ≥300 行，四子问题各有一节
- AC2 arXiv id / URL 总数 ≥15，其中 ≥8 篇读了原文（正文引用具体段落/表格/定理编号）
- AC3 每个子问题有 D2 判决句
- AC4 04.5 反方复核 ≥3 个质询 + 防御说明

## 【失败降级】

- arXiv API 不可用 → 直访 arxiv.org 页面（ego-browser 通道，参考 pfb research_hook v2 经验：arXiv API + 站点直访可用，搜索引擎全废）
- 某子问题穷尽检索无果 → 标「开放问题，穷尽渠道：<列出试过的 query>」，conf ≤0.4，不展开猜测
- 时间不够 → 保 Q1+Q3（最核心），Q2/Q4 标 partial

## 【交付物】

- `research/long-insight-decomposability-survey.md`（主产出，≥300 行）
- `research/long-insight-search-log.json`（检索日志：每条 query + 命中数 + 采纳理由，append-only）
- loop 工件：`loop-artifacts/stages/01..04.5/`（按仓库惯例）

完成后回执必须含 repo URL + branch + commit_sha。

## 【给 Lead 的备注】

- 本任务与 pfb T0/T1/T2 措辞梯度实验互补：T0/T1/T2 测「指令剂量对 27b 的影响」，本任务调研「洞察结构本身的性质」。两者合起来才能判断「prompt 范式能逼近权重范式多少」。
- 若 Q3 找到可用的形式化工具（pebbling/circuit complexity），建议后续开一个数学推导 goal（那超出本任务范围，Lead 另行立项）。