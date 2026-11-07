# 02 · 检索计划（T-PR-09）

## 三类检索目标（按任务书的三个子问题拆）
| 目标 | query 骨架 | 期望证据形态 |
|---|---|---|
| Q1 MDL/最简描述 | MDL + in-context + demonstration selection | 有算法 + 实验数字；等价性定理 |
| Q2 参数 vs 压缩 | compression ratio + parameter count + phase transition | N vs K(data) 测量 |
| Q3 Bayesian/统计/信息论 | PAC-Bayes ICL / generalization bounds / mutual information | 定理编号 + 假设条件 |
| Q3(d) 断裂 | labels random demonstrations | 同任务对照数字 |
| AC6 可操作准则 | information gain demonstration selection | 可直接跑的准则 |

## 预期落空点（先写下，防事后合理化）
- 预计"互信息界"查不到 → 实际确认（N4）
- 预计"posterior 信息增益 demo 选择"查不到 → 实际确认（N6）
- 预计 PAC-Bayes×ICL 有少量结果 → 实际**没有 ICL 专用**（N1），意外落空

## 措辞切换预案（前两任务的教训）
若 "MDL" 返回噪声 → 切 "information compression"、"description length"、"minimum description"
若 "PAC-Bayes ICL" 空 → 切 "generalization bound few-shot prompt"
