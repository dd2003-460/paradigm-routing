#!/usr/bin/env python3
"""Cross-turn recall decay experiment (v1, 2026-11-07).

Question: in a long multi-turn conversation, does the model lose facts from EARLY turns?
Does re-stating the fact every N turns flatten the decay curve?

Design:
- Build a 20-turn conversation. Turn 1 plants a target fact (plus distractor facts in later turns).
- Filler turns are short chit-chat / unrelated Q&A to pad realistic dialogue length.
- At turn T (T in {2, 5, 10, 15, 20}), ask "what was [X] that I mentioned earlier?"
- Two conditions:
    A) plant-once: fact stated only in turn 1
    B) restate-every-5: fact restated verbatim at turns 1, 5, 10, 15 (before each query point)
- Metric: per (condition, query_turn): did the model retrieve the correct value? (binary)
- Also track total context tokens at query time (to separate "length effect" from "turns effect").

Model: qwen3.8-27b via ninfer localhost:8787, temp=0.
Scale: 2 conds × 5 query points × 3 reps = 30 full-conversation runs (~20 turns each).
Each run = 1 API call with the full message history (stateless chat completions).
"""
import json, time, urllib.request, sys
from pathlib import Path
from collections import defaultdict

NINFER_URL = "http://localhost:8787/v1/chat/completions"
MODEL = "qwen3.8-27b"
N_REPS = 3
QUERY_TURNS = [10, 20, 40, 60, 80]
MAX_TURN = 80

def call_ninfer(messages, max_tokens=80):
    payload = {"model": MODEL, "messages": messages, "temperature": 0, "max_tokens": max_tokens}
    req = urllib.request.Request(NINFER_URL, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as resp:
        data = json.loads(resp.read())
    return data["choices"][0]["message"]["content"].strip()

# ---- Conversation content -------------------------------------------------
# Target fact planted in turn 1. Distractors: similar-value facts in other turns.
TARGET_FACT_ZH = "我们项目的 KV cache 预算上限是 4096 tokens"
DISTRACTORS_ZH = [
    "我们项目的最大上下文窗口是 8192 tokens",
    "测试环境的超时阈值设为 300 秒",
    "数据库连接池大小配置为 20",
]
FILLER_USER_ZH = [
    "今天天气不错，适合跑步。我早上跑了五公里，感觉状态比上周好一些，配速稳定在六分半左右，心率曲线也正常，就是膝盖有点紧，可能是最近跑量上太快了，下周打算减量休息两天再恢复。",
    "帮我总结一下昨天会议的要点。主要讨论了 Q4 的预算分配和人员配置问题，技术组要加两个人，一个后端一个数据，市场那边砍了二十万的投放预算转去做内容营销，有几个待办事项需要这周跟进，下周三前出方案。",
    "你觉得远程办公和坐班哪个效率高？我个人的经验是深度工作适合远程，不用被打断可以连续专注两三个小时；但协作密集型任务还是坐班更好，特别是需要频繁对齐的项目，线上沟通的效率大概是线下的三分之一到二分之一。",
    "周末有什么推荐的电影吗？我最近看科幻片比较多，偏好硬科幻而不是软科幻，剧情要有逻辑自洽性，不要那种靠设定强行推动故事的。《星际穿越》和《降临》我都看过好几遍了，有没有类似水准的新片子？",
    "解释一下什么是分布式锁，简单点。我知道 Redis 可以用 SETNX 实现，但想了解下 etcd 的方案有什么区别。主要是 lease 机制和 watch 那部分，还有在脑裂场景下两种方案的可靠性差异，生产环境里踩过坑。",
    "最近在读《三体》，第二部挺震撼的。黑暗森林法则的逻辑链条很严密，从公理出发一步步推到那个结论，就是结局有点意难平。大刘的文风其实很干，没什么修辞，但就是能把宏大的宇宙观写得让人喘不过气。",
    "帮我把这段英文翻译成中文：The quick brown fox jumps over the lazy dog. 注意保持原文的幽默感，不要太生硬的直译。另外我想了解一下这句为什么包含所有字母，是不是有什么历史典故？",
    "Python 里 list 和 tuple 有什么区别？我知道一个是可变一个是不可变，但实际选型时还有什么考量因素？比如性能差异、能不能做 dict 的 key、在多线程环境下的安全性，这些细节想搞清楚。",
    "中午吃什么好呢，纠结死了。楼下有面馆、沙拉店和一家新开的湘菜馆，预算二十块以内。面馆的面条一般但汤底不错，沙拉比较健康但吃不饱，湘菜馆听说辣度可以调但不知道味道怎么样，你给个建议？",
    "给我讲个冷笑话。不要太老的，最好跟程序员相关的那种，上次那个递归的笑话我已经听过了。最好是那种听完要反应三秒才能笑出来的类型，太直白的没意思，要有点双关或者文字游戏的。",
]
ASSISTANT_SHORT_ZH = "好的，收到。我记下了，后续有需要随时问我。"  # ~20 chars, realistic but short

def build_conversation(condition, lang="zh", upto_turn=80):
    """Return list of (role, content) for user turns 1..upto_turn.
    Query turns get NO assistant reply (the query is appended later by caller)."""
    msgs = []
    # plant_once: fact only in turn 1. restate_every_5: turns 1,5,10,15.
    restate_at = {1} if condition == "plant_once" else {1, 5, 10, 15}

    d_idx = 0
    for t in range(1, upto_turn + 1):
        parts = []
        if t in restate_at:
            parts.append(TARGET_FACT_ZH)
        if t > 1 and t % 3 == 0 and d_idx < len(DISTRACTORS_ZH):
            parts.append(DISTRACTORS_ZH[d_idx]); d_idx += 1
        parts.append(FILLER_USER_ZH[(t - 1) % len(FILLER_USER_ZH)])
        msgs.append({"role": "user", "content": "\n".join(parts)})
        if t not in QUERY_TURNS:
            msgs.append({"role": "assistant", "content": ASSISTANT_SHORT_ZH})
    return msgs

def make_query(turn, lang="zh"):
    return f"我之前提到过我们项目的 KV cache 预算上限是多少 tokens？只回答数字。"

def count_messages_tokens(msgs):
    # rough: 1.5 chars/token zh
    return sum(len(m["content"]) for m in msgs) // 1

def run():
    results = []
    for condition in ["plant_once", "restate_every_5"]:
        for qt in QUERY_TURNS:
            for rep in range(N_REPS):
                # build history up to just before the query at turn qt
                hist = build_conversation(condition, upto_turn=qt)
                # remove the trailing assistant if present so query is last
                if hist and hist[-1]["role"] == "assistant" and qt in QUERY_TURNS:
                    hist = hist[:-1]
                hist.append({"role": "user", "content": make_query(qt)})
                try:
                    resp = call_ninfer(hist)
                    ok = "4096" in resp
                    ctx_chars = sum(len(m["content"]) for m in hist)
                    results.append({
                        "condition": condition, "query_turn": qt, "rep": rep,
                        "correct": ok, "response": resp[:60], "ctx_chars": ctx_chars,
                    })
                    print(f"[{condition}/T{qt}/r{rep}] {'✓' if ok else '✗'} '{resp[:40]}' ({ctx_chars} chars)", flush=True)
                except Exception as e:
                    print(f"ERROR [{condition}/T{qt}/r{rep}]: {e}", file=sys.stderr)
                    results.append({"condition": condition, "query_turn": qt, "rep": rep,
                                    "correct": None, "error": str(e), "ctx_chars": 0})

    out = Path(__file__).parent / "results_turn_decay.jsonl"
    with open(out, "w") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"\nSaved {len(results)} records → {out}")

    print("\n=== SUMMARY (recall by query turn) ===")
    print(f"{'Cond':<16} {'Turn':<6} {'Recall':<8} {'CtxChars':<10}")
    grouped = defaultdict(list)
    ctxmap = {}
    for r in results:
        if r["correct"] is None: continue
        key = (r["condition"], r["query_turn"])
        grouped[key].append(r["correct"])
        ctxmap[key] = r["ctx_chars"]
    for cond in ["plant_once", "restate_every_5"]:
        for qt in QUERY_TURNS:
            accs = grouped.get((cond, qt), [])
            rec = sum(accs) / len(accs) if accs else float("nan")
            print(f"{cond:<16} T{qt:<5} {rec:<8.2f} {ctxmap.get((cond,qt),0):<10}")

if __name__ == "__main__":
    run()