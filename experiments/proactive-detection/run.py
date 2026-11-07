#!/usr/bin/env python3
"""Proactive hook detection (v1, 2026-11-07).

Question: can the model SPONTANEOUSLY flag planted anomalies in a long document
without being told what to look for? (salience detection + metacognition)

Design:
- ~8k token Chinese "research report" with 3 planted hooks:
    H1 (contradiction): text says revenue 8621亿, table later says 8612亿
    H2 (hidden constraint): buried note "本数据集第47行存在重复标注，统计时需去重"
    H3 (counterintuitive number): "用户留存率在第9个月突然从42%跳到78%" (implausible jump)
- Task (open-ended, NO hint about hooks): "请基于以上材料，给出你的分析和建议。"
- Conditions: A = ## section headers; B = no separators (plain paragraphs)
- Scoring: per run, check if model output mentions each hook (keyword-based, lenient).
- temp=0.5, 5 reps per condition → 10 runs total.
- Model: qwen3.8-27b via ninfer, max_tokens=1500 (need room for analysis).
"""
import json, time, urllib.request, sys, re
from pathlib import Path
from collections import defaultdict

NINFER_URL = "http://localhost:8787/v1/chat/completions"
MODEL = "qwen3.8-27b"
N_REPS = 5
TEMP = 0.5
MAX_TOKENS = 1500

# ---- Document construction ------------------------------------------------

def filler_paragraphs(n, seed_topics):
    """Generate n filler paragraphs cycling through topics, ~120 chars each."""
    paras = []
    for i in range(n):
        topic = seed_topics[i % len(seed_topics)]
        paras.append(topic)
    return paras

SEED_TOPICS_ZH = [
    "本报告研究对象的样本覆盖全国 31 个省级行政区，数据采集周期为 2024 年 1 月至 2025 年 6 月，共回收有效问卷 12,847 份，其中一线城市的样本占比为 43.2%，二线城市占 31.7%，三线及以下城市占 25.1%。样本采集采用分层随机抽样与便利抽样相结合的方式，在一线城市以社区拦截和线上推送为主，在下沉市场则依托合作渠道进行入户访问。需要说明的是，由于部分受访者在多轮追踪中流失，最终用于纵向分析的样本量缩减至 9,632 人，流失率约为 25%，流失群体在年龄和收入维度上与保留群体存在显著差异，这一选择偏差在后文的结果解读中需要予以考虑。",
    "在方法论层面，本研究采用混合研究设计，定量部分使用结构方程模型检验主效应和中介效应，定性部分对 24 名核心用户进行了深度访谈，每次访谈时长 45 至 90 分钟，访谈转录文本共计 18.6 万字。定量分析使用 Mplus 8.3 软件，模型拟合指标包括 CFI、TLI、RMSEA 和 SRMR，其中 RMSEA 低于 0.08 被视为可接受拟合，低于 0.05 视为良好拟合。定性编码采用主题分析法，由两名独立编码员分别完成初编码，编码一致性（Cohen's kappa）达到 0.81，分歧通过讨论协商解决。所有原始数据已脱敏处理并存储于加密服务器，仅项目组成员可按需调取。",
    "行业背景方面，过去三年该赛道的市场规模年均复合增长率约为 18.4%，但增速在 2025 年上半年出现放缓迹象，多家头部机构的预测已从之前的 25% 下调至 15% 至 20% 区间。放缓的主要原因包括：下游需求端受宏观经济波动影响出现观望情绪，上游供应链成本上升挤压了利润空间，以及新进入者增多导致价格竞争加剧。值得注意的是，细分领域中与 AI 应用相关的子赛道仍然保持 30% 以上的增速，显示出结构性分化特征，传统业务板块的增长动能正在减弱。",
    "竞争格局上，目前市场上活跃的玩家约有 30 余家，其中前五大厂商合计占据约 61% 的市场份额，长尾厂商虽然数量众多但单体规模较小，平均年营收不足 2000 万元。头部厂商之间的竞争焦点已从单纯的价格战转向技术壁垒和生态构建，近一年内共有 7 起并购事件发生，涉及金额合计超过 45 亿元。与此同时，有两家曾经的第二梯队厂商因资金链断裂退出市场，行业集中度因此进一步上升。预计未来两年内还将有 3 至 5 家中小厂商被整合或淘汰。",
    "技术演进路径显示，该领域正从规则驱动向数据驱动过渡，机器学习方法在核心环节的应用比例从两年前的 34% 提升至目前的 67%，但完全自动化的方案尚未成熟，人机协同仍是主流形态。具体而言，在数据采集环节自动化程度最高，已达到 89%；在分析决策环节自动化程度最低，仅为 41%，主要受限于领域知识的复杂性和责任归属问题。大语言模型的引入正在改变这一格局，试点项目中 LLM 辅助分析将人工审核时间缩短了约 35%，但幻觉问题仍然是制约其大规模部署的主要瓶颈。",
    "用户画像分析表明，核心用户群体以 25 至 40 岁的城镇中产为主力，学历结构中本科及以上占比达 72.3%，收入水平显著高于全国平均水平，消费意愿强但对价格敏感度也相对较高。按职业分布看，互联网从业者占 28.4%，金融从业者占 19.2%，专业技术人员占 17.6%，其余为管理人员和其他白领。地域分布上，华东地区用户占比最高（34.1%），其次是华南（22.8%）和华北（18.5%），西部地区合计仅占 12.3%，存在明显的区域不均衡。",
    "渠道分布上，线上渠道贡献了约 68% 的营收，其中移动端 App 占线上总营收的 54%，小程序占 23%，Web 端占 23%；线下渠道虽然占比下降但在一二线城市仍具有不可替代的品牌展示作用。获客成本方面，线上渠道的平均 CAC 为 87 元/人，线下渠道为 156 元/人，但线下渠道用户的 12 个月 LTV 高出线上渠道约 23%，因此综合 ROI 两者基本持平。私域流量运营是近两年增长最快的渠道，企业微信社群的用户月活率达到了公域平台的 2.4 倍。",
    "成本结构分析显示，人力成本占总成本的 41%，技术研发投入占 28%，营销费用占 19%，其余 12% 为运营和其他杂项。近一年毛利率稳定在 52% 至 55% 区间，净利率约为 14%。与行业平均水平相比，该公司的研发费率偏高（行业均值 19%），这与其持续投入自研算法引擎的策略一致。现金流方面，经营性现金流连续四个季度为正，账期管理较为健康，应收账款周转天数为 47 天，处于行业中等偏上水平。",
    "政策环境方面，2024 年下半年以来监管部门陆续出台了三项与数据安全相关的规范性文件，对企业的合规要求明显提高，预计未来一年合规成本将上升 15% 至 20%。其中最关键的一项是关于个人信息跨境传输的新规，要求涉及海外业务的企业建立独立的数据安全评估机制，并对敏感数据的存储和处理提出更严格的本地化要求。此外，反垄断执法也在加强，2025 年初已有两起平台经济领域的处罚案例落地，罚款金额均在 10 亿元以上，对行业的竞争行为产生了明显的威慑效应。",
    "国际对比来看，该领域的海外成熟市场渗透率已达 38% 至 45%，而国内目前仅为 19%，差距主要在于基础设施完善程度和用户习惯差异，但追赶速度在过去两年明显加快。美国市场以 B 端服务为主，GTM 策略强调 ROI 量化和 SLA 保障；欧洲市场受 GDPR 约束，隐私计算技术采用率远高于其他地区；日本市场则呈现出独特的终身客户导向特征，续费率普遍在 85% 以上。国内市场的差异化机会在于下沉市场的数字化渗透和政企客户的定制化需求，这两块在海外几乎没有对应物。",
]

HOOK_CONTRADICTION = "根据财务数据，2024 年度公司总营收为 8621 亿元，同比增长 12.3%，净利润 1247 亿元，研发投入 486 亿元，均创下历史新高。"
TABLE_WITH_CONTRADICTION = "| 指标 | 2023 年 | 2024 年 |\n|------|---------|---------|\n| 总营收（亿元） | 7678 | 8612 |\n| 净利润（亿元） | 1102 | 1247 |\n| 研发投入（亿元） | 412 | 486 |\n| 员工总数（人） | 82,400 | 91,200 |"

HOOK_CONSTRAINT = "注：本数据集第 47 行存在重复标注，统计时需去重处理，否则会导致样本量虚高约 0.3%。"

HOOK_COUNTERINTUITIVE = "用户生命周期数据显示，新增用户的月度留存率在前八个月保持在 38% 至 42% 的稳定区间，但在第 9 个月突然跳升至 78%，此后两个月维持在 75% 至 79% 的高位，这一变化与同期产品功能更新无直接对应关系。"

TASK_PROMPT = "请基于以上材料，给出你的分析和建议。重点指出你认为值得关注的要点、潜在风险以及后续行动建议。"

def build_document(condition):
    """Build ~8k char document. condition: 'headers' or 'plain'."""
    T = SEED_TOPICS_ZH
    sections = []
    # Section 1: overview (contains H1 contradiction statement) — 4 paras + hook
    s1 = ["一、研究概述与行业背景"]
    s1 += [T[0], T[2], T[9], T[4]]
    s1.append(HOOK_CONTRADICTION)
    sections.append(s1)
    # Section 2: methodology — 4 paras + constraint hook buried in middle
    s2 = ["二、研究方法与数据来源"]
    s2 += [T[1], T[5]]
    s2.append(HOOK_CONSTRAINT)  # buried mid-section
    s2 += [T[7], T[3]]
    sections.append(s2)
    # Section 3: user analysis — 4 paras + counterintuitive hook
    s3 = ["三、用户行为与留存分析"]
    s3 += [T[5], T[6], T[0], T[8]]
    s3.append(HOOK_COUNTERINTUITIVE)
    sections.append(s3)
    # Section 4: financials — 3 paras + table with contradicting number
    s4 = ["四、财务表现"]
    s4 += [T[7], T[2], T[9]]
    s4.append(TABLE_WITH_CONTRADICTION)
    sections.append(s4)
    # Section 5: policy & outlook — 4 paras
    s5 = ["五、政策环境与展望"]
    s5 += [T[8], T[3], T[4], T[1]]
    sections.append(s5)

    if condition == "headers":
        parts = []
        for sec in sections:
            title = sec[0]
            body = "\n\n".join(sec[1:])
            parts.append(f"## {title}\n\n{body}")
        doc = "\n\n---\n\n".join(parts)
    else:
        # plain: strip titles, just paragraphs separated by blank lines
        all_paras = []
        for sec in sections:
            all_paras.extend(sec[1:])  # skip title
        doc = "\n\n".join(all_paras)
    return doc

# ---- Hook detection (lenient keyword matching) ----------------------------

def detect_hooks(output_text):
    """Return dict hook_id -> bool. Lenient: match on key numbers/phrases."""
    t = output_text
    h1 = ("8621" in t and "8612" in t) or ("矛盾" in t and ("8621" in t or "8612" in t)) or \
         ("不一致" in t and ("8621" in t or "8612" in t)) or ("数据冲突" in t)
    h2 = ("47" in t and ("重复" in t or "去重" in t)) or ("重复标注" in t) or \
         ("去重" in t and ("第47" in t or "47行" in t))
    h3 = ("78" in t and ("跳" in t or "突" in t or "异常" in t or "存疑" in t or "不合理" in t)) or \
         ("78%" in t and ("异常" in t or "可疑" in t or "存疑" in t or "跳升" in t))
    return {"H1_contradiction": h1, "H2_constraint": h2, "H3_counterintuitive": h3}

def call_ninfer(messages, max_tokens=MAX_TOKENS, temp=TEMP):
    payload = {"model": MODEL, "messages": messages, "temperature": temp, "max_tokens": max_tokens}
    req = urllib.request.Request(NINFER_URL, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as resp:
        data = json.loads(resp.read())
    return data["choices"][0]["message"]["content"].strip()

def run():
    results = []
    for condition in ["headers", "plain"]:
        doc = build_document(condition)
        print(f"\n=== Condition: {condition} ({len(doc)} chars) ===", flush=True)
        for rep in range(N_REPS):
            messages = [
                {"role": "user", "content": f"以下是一份研究报告全文：\n\n{doc}\n\n{TASK_PROMPT}"},
            ]
            try:
                resp = call_ninfer(messages)
                hooks = detect_hooks(resp)
                n_hit = sum(hooks.values())
                results.append({
                    "condition": condition, "rep": rep,
                    "hooks": hooks, "n_hit": n_hit,
                    "output_len": len(resp), "output_head": resp[:200],
                })
                hit_str = " ".join(k for k, v in hooks.items() if v) or "(none)"
                print(f"  r{rep}: {n_hit}/3 [{hit_str}] ({len(resp)} chars)", flush=True)
            except Exception as e:
                print(f"  r{rep}: ERROR {e}", file=sys.stderr)
                results.append({"condition": condition, "rep": rep, "error": str(e), "n_hit": None})

    out = Path(__file__).parent / "results_proactive.jsonl"
    with open(out, "w") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"\nSaved {len(results)} records → {out}")

    print("\n=== SUMMARY ===")
    for cond in ["headers", "plain"]:
        recs = [r for r in results if r["condition"] == cond and r.get("n_hit") is not None]
        if not recs: continue
        avg = sum(r["n_hit"] for r in recs) / len(recs)
        per_hook = {}
        for hk in ["H1_contradiction", "H2_constraint", "H3_counterintuitive"]:
            hits = sum(1 for r in recs if r["hooks"].get(hk))
            per_hook[hk] = f"{hits}/{len(recs)}"
        print(f"  {cond:<10} avg={avg:.2f}/3  H1={per_hook['H1_contradiction']}  H2={per_hook['H2_constraint']}  H3={per_hook['H3_counterintuitive']}")

if __name__ == "__main__":
    run()