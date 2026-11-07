# origin: ai — 分隔符 recall 实验设计（最小 social 单点）

> 状态：decomp 完成，待执行
> 关系：idea-list §C12 + paradigm-routing Q5.b（arena lit-survey §5）

## 一句话说清

长上下文里加不加"话题分隔符"（如 `---`、`## 主题`），模型回忆前面内容的准确率差多少？中文场景没人测过。

## 为什么值得做

1. **机制已明确**（SepLLM + Attention Sinks + Function Token Hypothesis）：分隔符 token 接收不成比例的 attention，把段内信息压缩后释放到残差流供后续检索。一阶效应 = "有 vs 没有"，字符选择是二阶。
2. **中文空白确认**：所有引用论文都是英文。中文的分隔习惯（空行 vs `---` vs 编号）可能不同。
3. **成本极低**：不需要训练，纯 prompt 对比，本地 27B 几小时跑完。
4. **social 价值**：一个干净的小结果 + 机制解释 = 可发 GitHub issue / 短笔记，不依赖范式路由的大结论。

## 正交子项分解

| # | 子项 | 状态 | 缺口 |
|---|------|------|------|
| 1 | 任务构造：N 段文本 → 问第 k 段的事实 | ❓ 待建 | 需要 ≥5 个段落、每段埋 1 个可验证事实；长度梯度（2k/4k/8k tokens） |
| 2 | 条件设计：无分隔符 vs 显式分隔符 vs 自然分段 | ❓ 待定 | 3 条件 × 3 长度 = 9 cells；中文为主 + 英文对照 |
| 3 | 指标：recall 准确率（精确匹配或 judge 判对） | ✅ 已有 pfb rubric 框架可复用 | 需要定义"正确"的判定标准 |
| 4 | 统计：n per cell ≥ 10 题，报告 mean ± std + 配对检验 | ❓ 待跑 | 总调用量 ≈ 9 × 10 = 90 次推理（temp=0，快） |
| 5 | 机制验证（可选）：attention 热力图看分隔符 token 是否确实吸走更多 attention | ❓ 需 vLLM 开 return_logits 或换 transformers 直接跑 | 如果时间不够可以跳过，只报行为级结果 |
| 6 | 落盘 + social 包装：结果表 + 一段话解释 + 指向 SepLLM 机制 | ❓ 待写 | 放 paradigm-routing/experiments/ 还是独立小 repo？ |

## 条件设计（具体）

### 文本结构
```
[段1: 某个技术事实 A] [段2: 无关填充 B] [段3: 另一个事实 C] [段4: 填充 D] [段5: 事实 E]
```
问题："段 1 提到的 X 是什么？" / "段 5 中 Y 的值是多少？"

### 3 种分隔条件
| 条件 | 段间处理 | 假设 |
|------|---------|------|
| S0: 无分隔 | 段落直接拼接，只有换行 | baseline |
| S1: 显式标记 | 每段前加 `## 主题X` 或 `---` | 一阶效应：有 > 无 |
| S2: 自然分段 | 空行分隔（markdown 默认） | 介于 S0 和 S1 之间？ |

### 长度梯度
- Short: ~2k tokens（5 段各 400）
- Medium: ~4k tokens（5 段各 800）
- Long: ~8k tokens（5 段各 1600）

### 语言
- 主：中文（空白确认）
- 对照：英文（验证 SepLLM 结论可复现）

## 预期结果 & 判决

- **H1 成立**：S1 > S0 在 Long 条件下显著（p < 0.05），且 gap 随长度增大
- **H1 不成立**：S1 ≈ S0（→ 说明 27B 的 attention 分配已经隐式处理了段落边界，分隔符无额外收益）
- **意外发现**：S2 > S1（空行比显式标记更好 → 与 SepLLM 预测矛盾，高价值）

## 执行计划

1. 写脚本 `experiments/separator-recall/run.py`：生成 N 组文本 × 3 条件 × 3 长度，调 vLLM API
2. 跑 90 次推理（temp=0, max_tokens=200）
3. 自动判分（精确匹配 + fallback judge）
4. 出表 + 写 200 字结论
5. commit + push → social 弹药

## 风险

- 27B 在 8k context 上可能本身 recall 就很高（ceiling effect）→ 加长到 16k 或增加干扰段
- 中文 token 化效率低（同样内容 token 数多）→ 长度梯度按 token 数算不按字数
- vLLM 并发限制 → 串行跑，90 次 × ~3s = ~5 分钟，可接受