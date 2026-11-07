#!/usr/bin/env python3
"""Separator recall experiment v3: real token counting + distractor facts.

Fixes from v2 (which produced identical results across all conditions):
1. Token counting via tiktoken (gpt-4o encoding as proxy) instead of char-based estimate
   → v2 "long" was only ~570 tok; SepLLM effects need 4k+ context
2. Distractor facts: 15 similar-valued facts per domain to force real retrieval
   → v2 had 5 unique easy-to-spot facts, zero variance (std=0 everywhere)
3. More fillers cycled to reach true 2k/4k/8k token targets

Design:
- 5 target facts (the ones we ask about)
- 15 distractors (similar numbers, same domains — model must find the RIGHT one)
- Filler paragraphs padded to hit token target
- Conditions: S0 (no separator), S1 (## headers + ---), S2 (blank lines only)
- 3 lengths × 2 langs × 3 reps = 54 inferences (5 questions each)
"""
import json, time, urllib.request, sys
from pathlib import Path
from collections import defaultdict
import tiktoken

NINFER_URL = "http://localhost:8787/v1/chat/completions"
MODEL = "qwen3.8-27b"
N_REPS = 3
ENC = tiktoken.encoding_for_model("gpt-4o")

def count_tokens(text):
    return len(ENC.encode(text))

def call_ninfer(messages, max_tokens=60):
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0,
        "max_tokens": max_tokens,
    }
    req = urllib.request.Request(
        NINFER_URL,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read())
    return data["choices"][0]["message"]["content"].strip()

# ============================================================
# TARGET FACTS (we ask about these 5)
# ============================================================
TARGETS_ZH = [
    ("超导量子比特", "超导量子比特的相干时间在 2024 年已突破 300 微秒。",
     "文中提到的超导量子比特相干时间突破了多少微秒？", "300"),
    ("AlphaFold2", "AlphaFold2 的 GDT-TS 评分在 CASP14 中达到 92.4。",
     "AlphaFold2 在 CASP14 的 GDT-TS 是多少？", "92.4"),
    ("台积电 N3", "台积电 N3 制程的晶体管密度约为 1.1 亿个每平方毫米。",
     "台积电 N3 晶体管密度约为多少？", "1.1亿"),
    ("M87* 黑洞", "事件视界望远镜拍摄的 M87* 黑洞阴影直径约为 42 微角秒。",
     "M87* 黑洞阴影直径约为多少微角秒？", "42"),
    ("CRISPR-Cas9", "CRISPR-Cas9 的脱靶率在第三代高保真变体中已降至百万分之一以下。",
     "第三代 CRISPR 脱靶率降至多少以下？", "百万分之一"),
]

DISTRACTORS_ZH = [
    # Quantum computing — similar numbers
    ("超导量子比特", "IBM 的超导量子处理器在 2023 年的相干时间记录为 245 微秒，使用了新型铝铌界面工艺。"),
    ("超导量子比特", "谷歌 Willow 芯片的 5 量子比特纠缠态相干时间达到 312 微秒，但尚未实现纠错。"),
    ("超导量子比特", "清华大学团队报道的稀土离子量子比特相干时间为 38 分钟，远超超导体系。"),
    # Protein folding — similar scores
    ("蛋白质折叠", "RoseTTAFold2 在 CASP14 的 GDT-TS 平均分为 89.1，略低于 AlphaFold2。"),
    ("蛋白质折叠", "ESMFold 在无模板条件下对单链蛋白的 GDT-TS 中位数为 91.2。"),
    ("蛋白质折叠", "CASP13 中 AlphaFold2 的 GDT-TS 为 90.7，首次超过实验方法。"),
    # Chip fabrication — similar densities
    ("芯片制程", "三星 3nm GAA 工艺的晶体管密度约为 0.9 亿个每平方毫米，良率仍在爬坡。"),
    ("芯片制程", "台积电 N5 制程的晶体管密度约为 0.72 亿个每平方毫米，是 N3 的前代。"),
    ("芯片制程", "Intel 18A 节点预计晶体管密度达到 1.3 亿个每平方毫米，采用 RISC-V 设计验证。"),
    # Black hole — similar angular sizes
    ("黑洞物理", "Sgr A* 黑洞阴影直径约为 51 微角秒，由于距离更近显得更大。"),
    ("黑洞物理", "M87* 的吸积盘外环直径约为 120 微角秒，由 EHT 2023 数据解析得到。"),
    ("黑洞物理", "TON 618 的质量约为太阳的 660 亿倍，其史瓦西半径对应的角直径仅约 0.001 微角秒。"),
    # Gene editing — similar rates
    ("基因编辑", "第二代 CRISPR-Cas9 高保真变体 eSpCas9 的脱靶率约为十万分之一。"),
    ("基因编辑", "Base Editor BE4max 在肝脏中的脱靶编辑率为 0.3%，主要发生在 DMD 基因座。"),
    ("基因编辑", "Prime Editor PE2 的脱靶率低于百万分之五，但仍高于第三代 Cas9 变体。"),
]

# ============================================================
# ENGLISH VERSIONS
# ============================================================
TARGETS_EN = [
    ("Superconducting Qubit", "Superconducting qubit coherence times have surpassed 300 microseconds as of 2024.",
     "What superconducting qubit coherence time breakthrough (in microseconds) is mentioned?", "300"),
    ("AlphaFold2", "AlphaFold2 achieved a GDT-TS score of 92.4 at CASP14.",
     "What was AlphaFold2's GDT-TS at CASP14?", "92.4"),
    ("TSMC N3", "TSMC's N3 process achieves approximately 110 million transistors per square millimeter.",
     "What is TSMC N3 transistor density (in millions per mm²)?", "110"),
    ("M87* Black Hole", "The EHT image of M87* shows a shadow diameter of approximately 42 microarcseconds.",
     "What is the M87* shadow diameter in microarcseconds?", "42"),
    ("CRISPR-Cas9", "Third-generation high-fidelity CRISPR-Cas9 variants reduced off-target rates below one in a million.",
     "What is the off-target rate threshold of third-gen CRISPR?", "one in a million"),
]

DISTRACTORS_EN = [
    ("Superconducting Qubit", "IBM's superconducting processor reached 245 microseconds coherence in 2023 using novel Al-Nb interface processing."),
    ("Superconducting Qubit", "Google's Willow chip achieved 312 microseconds coherence for a 5-qubit entangled state, though error correction remains unimplemented."),
    ("Superconducting Qubit", "Tsinghua University reported 38-minute coherence for rare-earth ion qubits, far exceeding superconducting systems."),
    ("Protein Folding", "RoseTTAFold2 scored 89.1 mean GDT-TS at CASP14, slightly below AlphaFold2."),
    ("Protein Folding", "ESMFold achieved a median GDT-TS of 91.2 for single-chain proteins without templates."),
    ("Protein Folding", "At CASP13, AlphaFold2 scored 90.7 GDT-TS, the first time it exceeded experimental methods."),
    ("Chip Fabrication", "Samsung's 3nm GAA process achieves roughly 90 million transistors per square millimeter, with yields still climbing."),
    ("Chip Fabrication", "TSMC's N5 process has a transistor density of about 72 million per square millimeter, the predecessor to N3."),
    ("Chip Fabrication", "Intel 18A is projected to reach 130 million transistors per square millimeter, validated on RISC-V designs."),
    ("Black Hole Physics", "Sgr A*'s shadow diameter measures about 51 microarcseconds, appearing larger due to closer distance."),
    ("Black Hole Physics", "M87*'s outer accretion disk ring spans roughly 120 microarcseconds, resolved from 2023 EHT data."),
    ("Black Hole Physics", "TON 618, at 66 billion solar masses, has a Schwarzschild-radius angular diameter of only about 0.001 microarcseconds."),
    ("Gene Editing", "Second-generation eSpCas9 high-fidelity variant shows off-target rates around one in a hundred thousand."),
    ("Gene Editing", "Base editor BE4max exhibits 0.3% off-target editing in liver, primarily at the DMD locus."),
    ("Gene Editing", "Prime editor PE2 shows off-target rates below five in a million, still higher than third-gen Cas9 variants."),
]

# ============================================================
# FILLERS (cycled to pad to target length)
# ============================================================
FILLERS_ZH = [
    "近年来，人工智能在自然语言处理领域取得了显著进展。大语言模型的参数量从数亿增长到数千亿，训练数据规模也相应扩大。然而，模型的可解释性仍然是开放问题，注意力权重的含义至今没有统一的物理解释。研究者们提出了多种方法试图可视化模型的内部表征，但结果往往依赖于具体的实现细节。Transformer 架构自 2017 年提出以来，已成为几乎所有现代 NLP 系统的基础。其核心创新——自注意力机制——允许序列中的每个位置直接关注其他所有位置，从而捕获长距离依赖关系。",
    "气候变化是当前全球面临的最重大挑战之一。根据政府间气候变化专门委员会的报告，如果不采取激进减排措施，本世纪末全球平均温度将上升 2.7 至 4.8 摄氏度。海平面上升、极端天气事件频率增加、生物多样性丧失等问题将严重影响人类社会的可持续发展。各国正在加速推进能源转型，可再生能源装机容量持续增长。太阳能和风能的发电成本在过去十年中分别下降了近 90% 和 70%，使得它们在越来越多的地区成为最经济的电力来源。",
    "城市交通拥堵已成为大城市的普遍问题。研究表明，通勤时间的增加不仅降低了生产效率，还对居民心理健康产生负面影响。智能交通系统通过实时数据分析和信号优化，可以在不新建道路的情况下提升路网通行能力 15-20%。自动驾驶技术的成熟有望从根本上改变城市交通格局。共享出行模式的兴起也在改变人们的出行习惯，网约车和共享单车的渗透率在一二线城市已超过 30%。",
    "睡眠科学的研究表明，成人每晚需要 7-9 小时的高质量睡眠以维持认知功能和免疫功能。睡眠周期分为浅睡、深睡和快速眼动三个阶段，每个阶段对记忆巩固的作用不同。深度睡眠期间生长激素分泌达到峰值，而快速眼动期则与情绪调节和创造性思维密切相关。长期睡眠不足与心血管疾病、肥胖症和抑郁症的风险增加显著相关。",
    "量子信息理论的发展为密码学带来了革命性变化。Shor 算法证明了大整数分解在量子计算机上是多项式时间可解的，这直接威胁到当前广泛使用的 RSA 加密体系。作为回应，后量子密码学标准正在制定中，基于格的密码方案被认为是最有前景的候选者之一。量子密钥分发则利用量子力学的基本原理实现了信息论安全的通信。",
    "材料科学的进步不断推动着电子器件的性能边界。二维材料如石墨烯和过渡金属硫化物因其独特的电子结构而受到广泛关注。石墨烯的理论载流子迁移率高达 200,000 平方厘米每伏特秒，远超硅的 1,400。然而，带隙工程仍是将其应用于数字逻辑器件的主要障碍。碳纳米管场效应管的最新进展显示，在亚 5 纳米尺度下仍保持优异的开关特性。",
    "神经科学与人工智能的交叉领域——类脑计算——正在探索新的计算范式。脉冲神经网络使用离散的脉冲信号而非连续值进行信息传递，其能耗可以比传统人工神经网络低一到两个数量级。忆阻器作为模拟突触的非易失性存储元件，是实现大规模脉冲神经网络硬件的关键。IBM 的 TrueNorth 芯片和 Intel 的 Loihi 平台已经展示了数百万神经元规模的类脑处理器。",
    "统计学中的贝叶斯方法在机器学习时代重新获得了关注。与频率学派不同，贝叶斯推断将参数视为随机变量，通过先验分布和似然函数得到后验分布。这一框架自然地提供了预测不确定性量化，在小数据场景下具有显著优势。变分推断和马尔可夫链蒙特卡洛方法是两种主要的近似后验计算技术，前者速度快但精度有限，后者精度高但计算成本大。",
    "基因组学的大规模测序项目正在揭示人类遗传多样性的全貌。千人基因组计划已完成 2,504 个个体的全基因组测序，发现了超过 8,800 万个变异位点。这些发现为精准医疗奠定了基础，但也引发了关于数据隐私和种族本质主义的伦理讨论。表观基因组学进一步揭示了环境因素如何在不改变 DNA 序列的情况下影响基因表达。",
    "太空探索进入商业时代。SpaceX 的星链计划已部署超过 5,000 颗低轨道卫星，提供全球互联网覆盖。NASA 的阿尔忒弥斯计划旨在 2027 年前将宇航员送回月球表面。中国的天问一号成功着陆火星乌托邦平原，祝融号火星车完成了 92 天的地表探测任务。小行星采样返回任务（OSIRIS-REx）于 2023 年将胶囊送回地球，携带约 12 克样本。",
]

FILLERS_EN = [
    "Artificial intelligence has made remarkable progress in natural language processing in recent years. Large language model parameters have grown from hundreds of millions to trillions, with training data scales expanding accordingly. However, model interpretability remains an open problem; the meaning of attention weights still lacks a unified physical explanation. Researchers have proposed various methods to visualize internal representations, but results often depend on implementation specifics. The Transformer architecture, introduced in 2017, has become the foundation of virtually all modern NLP systems.",
    "Climate change represents one of the most significant challenges facing humanity. According to IPCC reports, without aggressive mitigation, global average temperatures will rise 2.7 to 4.8 degrees Celsius by century's end. Sea level rise, increased extreme weather events, and biodiversity loss will profoundly impact sustainable development. Nations are accelerating energy transitions as renewable capacity continues to grow. Solar and wind power costs have dropped nearly 90% and 70% respectively over the past decade.",
    "Urban traffic congestion has become ubiquitous in major cities. Research shows that increased commute times reduce both productivity and mental well-being. Intelligent transportation systems leveraging real-time analytics can improve network throughput by 15-20% without new infrastructure. Autonomous vehicle maturity may fundamentally reshape urban mobility patterns. Ride-sharing and bike-share penetration exceeds 30% in first and second tier cities.",
    "Sleep science indicates adults require 7-9 hours of quality sleep nightly for cognitive function and immune health. Sleep cycles through light, deep, and REM stages, each contributing differently to memory consolidation. Growth hormone peaks during deep sleep while REM correlates with emotional regulation and creative thinking. Chronic sleep deprivation is significantly associated with increased risk of cardiovascular disease, obesity, and depression.",
    "Advances in quantum information theory have revolutionized cryptography. Shor's algorithm demonstrated that large integer factorization is solvable in polynomial time on quantum computers, directly threatening the widely-used RSA cryptosystem. In response, post-quantum cryptographic standards are being developed, with lattice-based schemes considered among the most promising candidates. Quantum key distribution leverages fundamental principles of quantum mechanics for information-theoretically secure communication.",
    "Materials science advances continue to push the performance boundaries of electronic devices. Two-dimensional materials such as graphene and transition metal dichalcogenides attract widespread attention due to their unique electronic structures. Graphene's theoretical carrier mobility reaches 200,000 square centimeters per volt-second, far exceeding silicon's 1,400. However, bandgap engineering remains the primary obstacle for digital logic applications.",
    "The intersection of neuroscience and artificial intelligence—neuromorphic computing—is exploring new computational paradigms. Spiking neural networks use discrete spike signals rather than continuous values, with energy consumption potentially one to two orders of magnitude lower than conventional ANN. Memristors as non-volatile synapse analogs are critical for large-scale SNN hardware. IBM's TrueNorth and Intel's Loihi platforms demonstrate neuromorphic processors at million-neuron scale.",
    "Bayesian methods in statistics have regained attention in the machine learning era. Unlike frequentist approaches, Bayesian inference treats parameters as random variables, obtaining posterior distributions through prior and likelihood. This framework naturally provides predictive uncertainty quantification, offering significant advantages in small-data scenarios. Variational inference and Markov Chain Monte Carlo are two main approximate posterior computation techniques.",
    "Large-scale genomic sequencing projects are revealing the full scope of human genetic diversity. The 1000 Genomes Project completed whole-genome sequencing of 2,504 individuals, discovering over 88 million variant sites. These findings laid the groundwork for precision medicine but also raised ethical discussions about data privacy and racial essentialism. Epigenomics further revealed how environmental factors influence gene expression without altering DNA sequences.",
    "Space exploration has entered a commercial era. SpaceX's Starlink constellation has deployed over 5,000 low-Earth-orbit satellites providing global internet coverage. NASA's Artemis program aims to return astronauts to the lunar surface by 2027. China's Tianwen-1 successfully landed in Utopia Planitia, with the Zhurong rover completing 92 days of surface operations. The OSIRIS-REx asteroid sample return mission delivered a capsule to Earth in 2023 carrying approximately 12 grams of material.",
]

def build_context(targets, distractors, condition, lang, target_tokens):
    """Build context: interleave targets + distractors + fillers to hit target_tokens.
    
    All 20 facts (5 targets + 15 distractors) are always present.
    Fillers are cycled until we reach the token target.
    """
    fillers = FILLERS_ZH if lang == "zh" else FILLERS_EN
    sep_header_zh = "## "
    sep_header_en = "## "
    
    # Create fact list: interleave targets and distractors
    # Pattern: T1, D1, D2, T2, D3, D4, T3, D5, D6, T4, D7, D8, T5, D9, D10...D15
    fact_items = []
    d_idx = 0
    for i, (topic, text, _, _) in enumerate(targets):
        fact_items.append((topic, text, "target"))
        # Add 3 distractors after each target (last target gets remaining)
        for _ in range(3):
            if d_idx < len(distractors):
                fact_items.append((distractors[d_idx][0], distractors[d_idx][1], "distractor"))
                d_idx += 1
    
    segments = []
    for i, (topic, text, kind) in enumerate(fact_items):
        if condition == "S1":
            header = f"{sep_header_zh}{topic}" if lang == "zh" else f"{sep_header_en}{topic}"
            segments.append(f"{header}\n{text}")
        elif condition == "S2":
            segments.append(text)
        else:  # S0
            segments.append(text)
    
    # Build base context
    if condition == "S0":
        base_join = "\n"
    elif condition == "S1":
        base_join = "\n\n---\n\n"
    else:
        base_join = "\n\n\n"
    
    base = base_join.join(segments)
    current_tokens = count_tokens(base)
    
    # Pad with fillers until we hit target
    filler_idx = 0
    while current_tokens < target_tokens:
        filler = fillers[filler_idx % len(fillers)]
        if condition == "S1":
            seg = f"{'## 补充' if lang == 'zh' else '## Note'}\n{filler}"
        else:
            seg = filler
        joiner = base_join if segments else ""
        test = base + joiner + seg
        if count_tokens(test) > target_tokens * 1.15:  # don't overshoot by >15%
            break
        base = test
        current_tokens = count_tokens(base)
        filler_idx += 1
    
    return base, current_tokens


def run_experiment():
    results = []
    conditions = ["S0", "S1", "S2"]
    # Real token targets: 2k, 4k, 8k
    lengths = [("short", 2000), ("medium", 4000), ("long", 8000)]
    
    for lang, targets, distractors in [
        ("zh", TARGETS_ZH, DISTRACTORS_ZH),
        ("en", TARGETS_EN, DISTRACTORS_EN),
    ]:
        for cond in conditions:
            for len_name, target_tok in lengths:
                context, actual_tok = build_context(targets, distractors, cond, lang, target_tok)
                
                for rep in range(N_REPS):
                    correct_count = 0
                    total = len(targets)
                    
                    for i, (topic, fact_text, question, answer) in enumerate(targets):
                        if lang == "zh":
                            prompt = f"请根据以下文本回答问题。只回答具体数值或短语，不要解释。\n\n{context}\n\n问题：{question}"
                        else:
                            prompt = f"Answer the question based ONLY on the text below. Give only the specific value or phrase, no explanation.\n\n{context}\n\nQuestion: {question}"
                        
                        try:
                            response = call_ninfer([{"role": "user", "content": prompt}])
                            matched = answer.lower() in response.lower()
                            correct_count += 1 if matched else 0
                            status = "✓" if matched else "✗"
                            print(f"  [{lang}/{cond}/{len_name}/r{rep}/f{i}] {status} '{answer}' ← '{response[:40]}'", flush=True)
                        except Exception as e:
                            print(f"  ERROR [{lang}/{cond}/{len_name}/r{rep}/f{i}]: {e}", file=sys.stderr)
                            continue
                    
                    acc = correct_count / total if total > 0 else 0
                    record = {
                        "lang": lang, "condition": cond, "length": len_name,
                        "rep": rep, "n_facts": total, "correct": correct_count,
                        "accuracy": acc, "context_len_chars": len(context),
                        "actual_tokens": actual_tok, "target_tokens": target_tok,
                    }
                    results.append(record)
                    print(f"[{lang}/{cond}/{len_name}/r{rep}] {correct_count}/{total} = {acc:.2f} ({actual_tok} tok)", flush=True)
    
    # Save
    out_path = Path(__file__).parent / "results_v3.jsonl"
    with open(out_path, "w") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"\nSaved {len(results)} records to {out_path}")
    
    # Summary table
    print("\n=== SUMMARY ===")
    print(f"{'Lang':<5} {'Cond':<5} {'Len':<8} {'Tok':<7} {'Mean Acc':<10} {'Std':<8}")
    grouped = defaultdict(list)
    tok_map = {}
    for r in results:
        key = (r["lang"], r["condition"], r["length"])
        grouped[key].append(r["accuracy"])
        tok_map[key] = r["actual_tokens"]
    for (lang, cond, ln), accs in sorted(grouped.items()):
        mean = sum(accs) / len(accs)
        std = (sum((a-mean)**2 for a in accs) / max(1, len(accs)-1))**0.5
        tok = tok_map[(lang, cond, ln)]
        print(f"{lang:<5} {cond:<5} {ln:<8} {tok:<7} {mean:<10.3f} {std:<8.3f}")

if __name__ == "__main__":
    run_experiment()