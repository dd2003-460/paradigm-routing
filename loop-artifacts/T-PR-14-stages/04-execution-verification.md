# 04 · 执行与验证（T-PR-14）

## 产物
| 文件 | 规模 | 状态 |
|---|---|---|
| `research/reasoning-as-search-survey.md` | 327 行 | ✅（≥200 要求） |
| `research/search-log-reasoning-as-search.json` | 7 queries / 5 self_corrections / 6 negative / 5 verification_gaps | ✅ `json.load` 通过 |
| `loop-artifacts/T-PR-14-stages/{01,02,02.5,03,04,04.5}.md` | 6 文件 | ✅ |

## 逐条 AC 自验
| AC | 要求 | 实现 | 证据位置 |
|---|---|---|---|
| **AC1** | 逐条违反清单，每条带文献或推导 | **6 条**（A1–A6），三态判定 + 后果列 | §2 表 |
| **AC2** | ≥2 策略 + 定理陈述 + 条件 | **5 个**：Hajek SA（充要条件+3 条致命限制）、UCT（regret 界+3 条前提）、覆盖-选择（6 公式）、compute-optimal（>4×）、**beam 样本复杂度（3 定理）** | §3.1–3.5 |
| **AC3** | ≥5 篇（标题+ID+一句话+覆盖标注） | **15 篇**，直接 9 / 部分 4 | §4 表 |
| **AC4** | 推荐抽象 + 理由 + 能解释/预测什么 | (b) 主 + (c) 预算层 + 第一性修正；3 条理由；**3/3 判据**；5 条现象解释表 | §5.1–5.3 |
| **AC5** | ≥12 来源，≥5 到定理/公式级 | **19 条**外部；**14 条**定理/公式级；**4 条有明确定理编号**；含 URL/访问日/阅读级别列 | §7 表 |
| **AC6** | ≥3 反方质询 | **4 条**（含 1 条自查） | §6 |
| 约束 | 不重复 G1–G4 | 全部引用而非重检，日志 `upstream_not_rechecked` 显式列出 | JSON |
| 约束 | 要定理/条件/反例 | 定理 6 处、条件逐条列、**反例 3 个**（BLEU 30.3→2.1；Beam-100 只降 4 点；覆盖 1.00 vs 自一致 0.87） | §2, §3.5, §3.3 |
| 降级 | 穷尽无果 → 明说空白 + 最小实验 | §8 六条负结果 + §8.1 完整实验设计（臂/扫描/主指标/可否证预测/成本） | §8 |

## 数字一致性核查（写完后回扫）
- "51.8%" 只出现在 exact 行 ✅
- "57.7% / 53.62% / 73.58%" 三处出现且口径一致 ✅
- "30.3 → 2.1" 出现 3 次（§0、§2、§9），数值一致 ✅
- "1.00 vs 0.87" 出现 3 次（§0、§3.3、§9），均标 GSM8K/10⁴/Llama-3-8B ✅
- 来源计数"19 条 / 14 条定理级"与 §7 表实际行数一致 ✅

## 校验命令
```
wc -l research/reasoning-as-search-survey.md          # 327
python3 -c "import json;json.load(open('research/search-log-reasoning-as-search.json'))"   # pass
ls loop-artifacts/T-PR-14-stages/                      # 6 files
```
