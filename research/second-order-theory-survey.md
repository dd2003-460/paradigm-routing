# 二阶效应的理论路径 — 文献调研 (2026-11-07)

> 问题：能不能从数学上严格区分"分隔符存在性（一阶）"和"字符选择（二阶）"？有没有已有路径，别民科。

## 结论（先说人话）

**没有人做过严格的阶数分解。** 现有工作分三类，每类都只覆盖了问题的一部分：

1. **几何/机制解释**（attention sink 为什么存在）→ 解释了"为什么有分隔符比没有好"，但没量化"换一种分隔符差多少"
2. **消融/干预实验**（去掉标点看掉几个点）→ 给了一阶效应的下界，但没做字符间的控制变量对比
3. **信息论/形式化框架**（tokenizer 的信息代价、图论位置偏差）→ 有数学工具，但没人套到"分隔符字符选择"这个具体问题上

所以"一阶 vs 二阶的准确数学表达"**目前没有现成定理**。但有三条可走的路径，不需要民科：

## 路径 A：几何参考系框架（最接近理论）

**来源**：*What are you sinking? A geometric approach on attention sink* (arXiv:2508.02546, 2025)

核心论点：attention sink 不是架构 bug，是高维表示空间建立**参考系**（reference frame）的几何必然。三种类型：centralized / distributed / bidirectional，在训练最早期就涌现。

**怎么用**：
- 一阶效应 = "有没有参考系锚点"（separator presence → 建立/不建立 reference frame）
- 二阶效应 = "参考系的形状/方向"（不同 separator token 激活不同的 key/query 子空间 → 参考系旋转）
- 可测量的量：sink token 处 key vector 的 norm 和方向余弦。如果 `##` 和 `---` 产生的 key vector 方向差 < ε，那二阶效应在这个模型上确实可以忽略
- **需要的工具**：hook 进 attention 层，提取 sink position 的 K/V matrix，算 cosine similarity between different separator conditions
- **成本**：需要白盒访问（qwen 权重本地有吗？ninfer 是黑盒 API → 这条路走不通，除非用开源 qwen 权重本地跑）

## 路径 B：线性度/上下文化度量（实验可落地）

**来源**：*LLM-Microscope* (arXiv:2502.15007, 2025)

核心发现：punctuation/stopwords 的 removal 对 MMLU/BABILong-4k 有持续负面影响；且这种影响与**线性度**（linearity）强相关——layer-to-layer embedding transformation 越接近线性，filler token 的作用越大。

**怎么用**：
- 定义 Δ_presence = perf(with any separator) − perf(no separator) → 一阶
- 定义 Δ_character = perf(separator A) − perf(separator B) → 二阶
- 如果 Δ_character / Δ_presence < 0.1 跨多个任务 → 经验性地确认"二阶可忽略"
- 进一步：用 LLM-Microscope toolkit 量化 separator token 的 contextualization score，看不同字符的分数差异是否显著小于"有 vs 无"的差异
- **成本**：纯黑盒 API 就能跑（我们 v3 的 pipeline 直接复用），加 3-4 个 separator 变体（`##` / `---` / `[SEP]` / `1.` / 空行）× 3 lengths × 2 langs
- **这是最现实的路径**，跟我们的 social 单点直接衔接

## 路径 C：图论位置偏差框架（最形式化但最远）

**来源**：*On the Emergence of Position Bias in Transformers* (arXiv:2502.01951, 2025) + *Frayed RoPE* (arXiv:2603.18017, 2026)

核心工具：把 attention mask 建模为 directed graph，量化每个 token 对 context 的可达性；RoPE 的几何分析给出 sink 功能的数学条件。

**怎么用**：
- 理论上可以证明：separator token 在 graph 中是 articulation point（割点），它的存在改变了 segment 内 token 的 reachability
- 一阶 = 图的连通性变化（有/无割点 → 不同连通分量）
- 二阶 = 割点的 degree/weight 变化（不同 separator 被 attend 的频率不同 → 割点强度不同）
- **问题**：这个框架是为 position bias 设计的，套到 separator character choice 上需要额外假设（比如"所有 separator 都是完美割点，只是强度不同"），推导链长且每一步都有近似
- **判断**：能出结果但性价比低，适合当论文的理论 section，不适合当快速 social 验证

## 推荐行动

| 优先级 | 动作 | 产投比 | 理由 |
|--------|------|--------|------|
| 1 | 路径 B 扩展实验（v4-multi-char） | 高 | 黑盒可跑、复用 v3 pipeline、直接回答"二阶是否可忽略"、产出可发 |
| 2 | 路径 A 的简化版：如果 ninfer 暴露 logits/hidden states，提取 sink 位置统计 | 中 | 一个数字（cosine sim）就能定性回答，但依赖 API 能力 |
| 3 | 路径 C 的形式化 | 低（短期） | 留作论文 theoretical motivation，不急 |

## 关键引用（已验证标题+摘要）

| Paper | arXiv | 贡献 | 与本问题的关系 |
|-------|-------|------|--------------|
| SepLLM | 2412.12094 | separator 压缩段信息，plug-and-play | 一阶效应的功能解释 |
| Geometric AS | 2508.02546 | sink = reference frame，三类型 | 一阶的几何根源；二阶 = 参考系方向 |
| LLM-Microscope | 2502.15007 | filler token contextualization + linearity | 可操作的度量工具 |
| Punctuation & Predicates | 2508.14067 | punctuation necessity/sufficiency 跨模型 | 模型依赖性证据（GPT-2 yes, Gemma no） |
| Frayed RoPE | 2603.18017 | RoPE 几何 → sink 功能条件 | 架构依赖性的数学基础 |
| Position Bias Graph | 2502.01951 | 图论框架，causal mask + RPE 交互 | 形式化工具（远） |
| Token Boundaries | 2609.35869 | compression certificates for boundaries | 信息论角度（待细读） |

## 缺口（诚实标注）

- [ ] 没有任何一篇做过 `##` vs `---` vs `[SEP]` vs `1.` 的控制变量 head-to-head
- [ ] "二阶" 这个词本身在 transformer 文献里没有标准定义——我这里是借用 perturbation theory 的直觉（一阶 = 拓扑变化，二阶 = 参数变化），不是引自某篇论文的定理
- [ ] 路径 A 需要白盒，ninfer 黑盒 API 大概率不支持 hidden state 提取 [待核验：ninfer 是否有 /v1/completions 带 logprobs 或 hidden_states 选项]
- [ ] 模型依赖性很强（Punctuation & Predicates 显示 GPT-2 ≠ Gemma），所以任何"二阶可忽略"的结论都要限定模型
