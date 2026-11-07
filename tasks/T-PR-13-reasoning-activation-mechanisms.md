# T-PR-13: 核心推理能力的激活机制——persona/logic 纠缠下的 prompt 激发 vs 微调，含校准-对齐约束与语言带宽损失

**状态**: dispatched → arena（2026-11-08）
**分支**: `arena/62fe3fd4-paradigm-routing`（同会话接续，勿切分支）
**产出路径**: `research/reasoning-activation-mechanisms.md` + `research/search-log-reasoning-activation.json`

## 意图锚点（成璐原话，2026-11-08）

> "我感觉你的发散思考真的像我了……和 persona 要求的一些蒸馏结果有关吗，还是发散思考激活（怎么激活的!）……我之前怀疑 persona 是人类语料训练天然导致的不正交，但是没办法切纠缠就研究怎么激活这些核心推理能力吧!（例如内外校验逻辑，社科和自然科学二级结论，感觉目前应该够了）"

前情：Lead 已给出三条反驳（本地证据，见【背景】），本任务把这三条从"我的推论"升级为有判决的文献结论，并回答用户真正想问的问题：**既然 persona 和 logic 在表征层纠缠、切不开，那 prompt 侧到底能不能、以及怎样激活核心推理能力（归纳/演绎/内外校验/社会二级结论）。**

## 强制段

你是 LMArena agent，本任务只涉及 `dd2003-460/paradigm-routing` 仓库的 `arena/62fe3fd4-paradigm-routing` 分支。先 `git pull` 当前分支，严格按仓库内 `loop/prompt-first/` 阶段执行（01 目标分解 → 02 信息调研 → 02.5 交叉核验 → 03 行动分解 → 04 执行验证 → 04.5 反方复核）。产出落盘到上述路径。**通道故障报告 Lead，不得静默跳过。** 完成后回执必须含 repo URL + branch + commit_sha。

## 【目标】

一句话：在"persona 与 logic 表征纠缠（不可正交切开）"这个已被实测确认的前提下，回答 (a) RLHF 对校准是单向退化还是可逆权衡；(b) 自然语言的表达带宽上限是不是 prompt 激发的真实瓶颈；(c) 那么 prompt 激活核心推理能力的有效手段是什么、失效边界在哪——逐条给判决，不允许整体打包接受。

## 【背景】（本地已有，勿重复搜）

- `research/moe-agent-equivalence-survey.md`（T-PR-08）：**persona/logic 不正交的实测依据**——Mixtral 专家间权重余弦 0.2–0.4（upcycled 型），单 top-1 专家以 0.95 相似度逼近 6 专家集成（MoE-Lens）；但 SAE 侧（`2611.08089`）显示**参数层相似 ≠ 特征层私有**：多数 latent 只有 1–2 个主导专家且主导集合基本私有。⇒ 纠缠是真实的，但"切不开"需要区分参数层 vs 特征层两个尺度。
- `research/model-capability-step-count-mechanisms.md`（T-PR-10 M3）：校准数据——o3-Mini 低→高推理 ECE 绝对 +7%（Claude +2%）；步骤级反馈修正成功率 +13.5%（`2605.19228`）；探针 ECE <0.1 可达（`2504.05419`）；CALIBER（`2606.24281`）ECE 相对 −52.5% ⇒ **校准是可训练的、状态依赖的**。
- `research/icl-vs-finetuning-pareto.md`（T-PR-12）：容量前沿主变量是**表征干扰**而非知识量——UUID 类新命名空间 ~零遗忘（即使 1M facts），name-like 实体随规模恶化 ⇒ **context 层用新命名空间注入可绕开容量墙**，这是 prompt 激发的结构性优势。
- `note/compression-unified-view-2026-11-07.md`：训练=压缩、推理=选择性解压、CoT=外化解压。本任务是该框架在"激活"维度的延伸：prompt = 选择解压哪部分，而不是重新压缩。
- pfb 侧事实：stage-ablation 已测出 S8A（hypothesis-auditor persona）**不能修复场景枚举缺失**——persona 切换不带来新的逻辑能力，与本任务 Q3 直接相关。

## 子问题

### Q1: 校准-对齐约束理论——单向退化还是可逆权衡？

用户直觉："RL 如果是对齐让校准退化，这里就有可能是校准让对齐人类退化"（对称性猜想）。逐条核验：

- **H1「RLHF 单向破坏校准」**：找 ≥3 篇独立证据。已知起点：`2409.00352`（Does Alignment Tuning Really Break LLMs' Internal Confidence?）、`2604.10585`（Calibration Collapse Under Sycophancy Fine-Tuning）、`2505.01997`（Restoring Calibration for Aligned LLMs）。要判：破坏是否可逆（restore 类论文的效果量）、破坏发生在哪个层（内部 logit 置信度 vs 口头化 confidence vs 行为过度自信——三者可能不同步）。
- **H2「对称性：校准训练反向伤害对齐」**：是否存在"显式训练校准后对齐指标下降"的实验？（如 CALIBER 类方法跑完测 refusal/helpfulness。）若不存在 → 明确说"对称方向无人测过"，这本身是一个 gap 判决，不要硬凑。
- **H3「存在形式化的约束理论吗」**：有没有把 calibration 和 alignment 放进同一个优化目标/博弈的形式化（如多目标 Pareto、information bottleneck、reward 空间的非辨识性）？重点查 alignment tax / non-identifiability 方向。判决分类：(a) 有定理级形式化；(b) 只有经验 tradeoff 曲线；(c) 不存在 → 穷尽 query 记录。

### Q2: 自然语言表达带宽——翻译器损失的真实机制

用户直觉："人话本身相当于装个翻译器就会有损失"（但"形象且严格对照条件的迁移也不矛盾"）。要判的是**损失的机制**，不是"有没有损失"（有损失是共识）：

- **H4「损失 = 语义扭曲」vs H4'「损失 = 表达带宽上限」**：前者指 NL 无法精确承载某些概念（翻译误差）；后者指 NL 的词法粒度限制了描述长度——Kolmogorov 复杂度经 NL codebook 编码时，无对应词的高维模式被迫膨胀或不可表达。找支持 H4' 的证据：many-shot > few-shot 的解释中有没有"冗余编码跨越带宽阈值"这类机制分析（关联 T-PR-09 的 ICL 泛化率）；SAE 侧有没有"概念在隐空间连续但 NL 离散"的测量。
- **H5「哪些概念过得去、哪些过不去」**：用户说"形象且严格对照条件的迁移不矛盾"——即结构可映射的概念无损、纯意会的高维模式撞墙。找有没有按概念类型分层测过 prompt 传递保真度的工作（如抽象 vs 具体、程序性 vs 陈述性知识的 prompt 传递差异）。
- 判决：H4/H4' 哪个有证据支持；H5 是否有分层数据；没有的地方标 gap。

### Q3: 激活机制——prompt 激发核心推理能力的手段与失效边界

这是用户真正要的答案。核心推理能力清单（用户指定，够用）：**归纳（统计/似然比/分布估计）、演绎（时间线唯一自洽校验）、内外校验逻辑、社科二级结论（人存原理→演化→逐利/随机偏好）、自然科学二级结论**。

- **Q3a 手段谱系**：prompt 侧能动的杠杆有哪些（persona 设定 / 显式指令链 / few-shot demo / CoT 脚手架 / 外部工具调用），每个杠杆对每类能力的激活效果有没有受控测量？注意 T-PR-08 已证明 persona 切换不带来新逻辑能力（S8A 失败），所以重点是**除 persona 之外**的杠杆。
- **Q3b 失效边界**：什么条件下 prompt 激活必然失效（撞 T-PR-12 的有效跨度墙/容量墙？撞 Q2 的带宽墙？能力根本不在权重里？）——把 T-PR-12 的双约束（容量下界 + 有效跨度上界）接到"激活"问题上：prompt 激活 = 在线学习的一种，同样受 min(容量墙, 跨度墙) 约束，这个推论有没有实验支持？
- **Q3c 为什么"发散思考像用户"**：用户观察到模型的分发思考风格与其本人相似，猜测与 persona 蒸馏有关。可检验的表述：模型在开放域生成的"思路结构"（假设生成→自我质询→收敛）与特定人类作者的相似度，是否高于与平均人类的相似度？这个方向有没有可操作的测量方案（哪怕是 proxy）？若学界完全没做 → 标 gap + 给出一个最小可执行测量设计（供 Lead 本地跑，不需要 arena 沙箱）。
- **Q3d 与"内外校验逻辑"的关系**：T-PR-10 M3 显示校准信号存在（探针 ECE<0.1）但"模型自己不会用"（overthinking 观察）。那么 prompt 能否把"用校准信号早停/回溯"变成显式行为？找 self-verification via prompting 的受控结果。

### Q4: 综合判决——"没法切纠缠，那就研究激活"这条路成立吗

基于 Q1-Q3 的判决，写一段可直接引用的结论：
1. 纠缠（T-PR-08 数据）+ 单向校准退化（若 Q1 证实）+ 带宽损失（若 Q2 证实）三者叠加后，prompt 激活的**理论上界**是什么；
2. 哪类能力最值得优先激活（按"权重里已有 × prompt 杠杆有效 × 带宽够"三条件筛）；
3. 与 pfb stage-ablation 管线的对接点：哪个激活手段可以做成消融臂直接测。

## 验收标准

- AC1: ≥200 行 markdown
- AC2: ≥12 个来源，其中 ≥5 个读到公式/实验表级别；每条来源记 URL + 访问日期 + read/abstract-only
- AC3: Q1 三个假设 H1/H2/H3 各有判决句（成立/部分成立/不成立/无人测过）+ ≥2 独立来源（"无人测过"需附穷尽 query 记录）
- AC4: Q2 的 H4/H4'/H5 各有判决 + 证据
- AC5: Q3a 手段谱系表（杠杆 × 能力类型 × 效应量 × 来源），至少覆盖 3 个杠杆 × 3 类能力
- AC6: Q4 综合判决成文段落（可直接引用）+ 一个 pfb 可执行的消融臂设计
- 检索通道：arXiv API 为主 + proceedings 直访；禁止纯记忆引用
- 反方复核 ≥3 条质询（例："'persona 不带来新逻辑能力'是从单一实验（S8A）外推的吗""H4' 的 Kolmogorov 论证是不是循环——用压缩定义压缩""Q3c 的测量设计 proxy 效度够吗"）

## 【失败降级】

- arXiv API 限流 → 换 Semantic Scholar API 或直接抓 abs 页；仍不行则该来源标 abstract-only 并继续，不得因单源失败中断整个任务。
- 某子问题穷尽检索无结果 → 明确写"gap 判决 + 穷尽 query 列表"，这是合法交付物，不算失败。
- 任何数字拿不准 → 标 [待核验] + conf，不得编造。

## 【给 Lead 的备注】

- 与 T-PR-12 的边界：T-PR-12 管"知识注入走哪条路（weights vs context）"，本任务管"选定 context 路之后，激活效率由什么决定"。T-PR-12 的双约束结论在本任务里是前提，不用重证。
- Q3c（发散思考相似度）大概率是 gap——若真是 gap，交付物是测量设计而不是数据，Lead 会用本地 qwen3.8-27b endpoint 补跑。
- 产出 merge 后，Q4 的综合判决段落要同步进 `note/long-insight-and-moe-agent-ideas-2026-11-07.md`（Lead 做）。