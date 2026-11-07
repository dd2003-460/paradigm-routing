# 03 · 判决（T-PR-11）
## AC3
合成目标**不存在**；伪合成 4 例（SSPO 嵌套 / UnifiedPlayers 加权和最强 / SearchGym 环境替代 / —— 注：GroundedPRM 实为单侧，C1 修正后剔除）；纯单侧 2 例（MARCH、Proof-Carrying）。
最终计数：**伪合成 2 例（SSPO、UnifiedPlayers）+ 单侧 4 例（SearchGym、GroundedPRM、MARCH、Proof-Carrying）**。

## AC5
- A reward 污染：**成立 0.85**（SearchGym "corrupted reward signals…"；PCC N^(1/ρ²)、0.94→0.32、+0.53 hacking gap、90% 崩塌）
- B credit assignment：**成立 0.85**（SSPO "single outcome reward… far too sparse"；GroundedPRM "credit misattribution"；UnifiedPlayers coordination challenge = 非平稳性）
- C 试过失败：**证据不足 0.45**（只见规避，不见失败）

## AC6
优势：能测出负贡献（M1 +0.237 与 M4 −0.240 并存），RL 的一维 reward 做不到。
劣势：组件级、非端到端、Δ 只在固定配置下成立（换配置即失效，与 on-policy 漂移同源）。
