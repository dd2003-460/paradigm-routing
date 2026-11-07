# 02 · 检索计划（T-PR-12）
| 目标 | 主 query | 备用措辞 | 预期 |
|---|---|---|---|
| Q1 受控对照 | fair comparison ICL vs fine-tuning same model | matched knowledge quantity curve | 有 1–2 篇，大概率缺 D4 |
| Q2-C1 固化 | catastrophic forgetting new knowledge hallucination | persistence vs context override | 有机制文献 |
| Q2-C3 成本 | cost crossover token cost | break-even samples | 预计只有样本数，无美元 |
| Q3 前沿 | ICL saturates with number of examples | scaling curve | 预计只有 K 单侧曲线 |
| Q4.3 有效跨度 | effective vs nominal window ICL | （复用 T-PR-10 RULER） | 预计无直接测量 |

## 预登记落空点
- 预计"双曲线同图 + 函数拟合"不存在 → 实际确认（N2）
- 预计"美元交叉点"不存在 → 实际确认（N3）
- 预计"ICL vs 有效跨度直接测量"不存在 → 实际确认（N5）
