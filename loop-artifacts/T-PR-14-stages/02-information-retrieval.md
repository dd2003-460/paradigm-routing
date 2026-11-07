# 02 · 信息调研（T-PR-14）

## 检索策略
本主题是**双重热门词**（搜索算法 × LLM 推理），泛词返回大量百科/博客 → 沿用 T-PR-13 的**精确数字/定理编号定位法**：
- "c ≥ d*"、"weak reversibility" → 锁 Hajek 1988
- "search errors"、"51.8%"、"BLEU 2.1" → 锁 `1908.10090`
- "modulo beam size"、"optimality certificate" → 锁 `D17-1227`
- "n_eff → 1/ρ"、"selection ceiling" → 锁 `2606.28661`
- "provable test-time scaling" + "beam search" → **锁 `2609.38672`（本轮最关键命中）**

## 七轮 query 与命中
| 轮 | query 主题 | 关键命中 |
|---|---|---|
| S01 | beam search 最优性/完备性 | `1908.10090`、`D17-1227`、`2010.02650` |
| S02 | SA 收敛充要条件 | Hajek 1988、`2208.11444`、Ohlmann & Bean |
| S03 | ToT / RAP / MCTS-for-LLM | `2305.10601`、`2305.14992`、`2509.25835` |
| S04 | self-consistency / Snell | `2203.11171`、`2408.03314` |
| S05 | 覆盖-选择缺口 | `2606.28661`（全部关键公式） |
| S06 | **TTC × complexity（追加）** | **`2609.38672`**、`2602.02909`、`2502.02393`、`2605.19944` |
| S07 | **latent vs token（追加）** | `2505.13308`、`2601.17275`、`2604.02029` |

## 为什么追加 S06/S07
- S01–S05 后自评：**定理级来源不足**（1908.10090 与 D17-1227 是二手摘要+PDF 片段），且任务书 Q3 明确要求"任何把 TTC 接 complexity 的工作"、Q2 明确要求"latent vs token"的区分。**两条都没覆盖 ⇒ 不能收工。**
- S06 的收益超出预期：`2609.38672` 直接改写了 Q1 的判决措辞（见 `02.5` C-01）。

## 通道
- `fetch_page` 本轮 **0 次**：S06/S07 的 web_search 已返回目标论文 HTML 正文片段（含定理编号、公式、结果表），信息密度够用。代价写入 `verification_gaps`（只引陈述、不引证明）。
- 未访问 `arxiv.org/pdf/`（历史四次失败）。

## 追加检索（成璐 2026-11-08 追加 Q5「动态适配」后）
| 轮 | query 主题 | 关键命中 |
|---|---|---|
| S08 | overthinking / 自适应思考预算 | `2412.21187`（1,953%）、`2506.18237` AdapThink、NoWait（ID 未核）、SelfBudgeter（ID 未核）、`2026.findings-acl.1285`（"models lack adaptive computation"） |
| S09 | SOP 归纳 / 策略选择的 prompt 可激发性 | `2510.04618` ACE、`2504.07952` Dynamic Cheatsheet、`2409.07429` AWM、`2402.03620` Self-Discover、`2505.13379` Thinkless、`2510.07364`（91%/12%）、`2507.11423`（依从率 32–99%） |

**为什么必须追加**：远端在 `c879af4` 给任务书加了 Q5（四个子问题 + 整理/写SOP/研究推进的映射）。**这不是可选项**——任务书新增内容属于交付范围。本地先 `git pull --rebase`（1 local / 1 remote 分叉，文件不相交，rebase 干净），再补检索与 §9。
