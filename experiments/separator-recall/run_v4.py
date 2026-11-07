#!/usr/bin/env python3
"""Separator recall experiment v4: multi-character head-to-head (second-order test).

Question: is character choice second-order vs presence?
- Δ_presence = acc(best separator) - acc(no separator)   → first-order
- Δ_character = max_acc(separators) - min_acc(separators) → second-order
- If Δ_character / Δ_presence < 0.1 across langs → "character doesn't matter" confirmed empirically

Conditions (all with the SAME 20 facts + same fillers, only formatting differs):
  S0: no separator (single newline between segments)
  S1: ## Topic headers + --- between segments        (v3's "good" condition)
  S2: blank lines only (double newline)
  S3: [SEP] token between segments (no header)
  S4: ### Topic headers (deeper markdown level)
  S5: numbered list (1. 2. 3. ...)

Length: 4k tokens only (where v3 showed the effect). 2 langs × 6 conds × 3 reps = 36 cells.
"""
import json, time, urllib.request, sys
from pathlib import Path
from collections import defaultdict
import tiktoken

NINFER_URL = "http://localhost:8787/v1/chat/completions"
MODEL = "qwen3.8-27b"
N_REPS = 3
ENC = tiktoken.encoding_for_model("gpt-4o")
TARGET_TOK = 4000

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

# Reuse v3 fact sets (exec the data section of run.py to avoid duplication drift)
_v3 = Path(__file__).parent / "run.py"
_ns = {}
exec(_v3.read_text().split("def build_context")[0], _ns)  # grabs TARGETS/DISTRACTORS/FILLERS
TARGETS_ZH = _ns["TARGETS_ZH"]; DISTRACTORS_ZH = _ns["DISTRACTORS_ZH"]
TARGETS_EN = _ns["TARGETS_EN"]; DISTRACTORS_EN = _ns["DISTRACTORS_EN"]
FILLERS_ZH = _ns["FILLERS_ZH"]; FILLERS_EN = _ns["FILLERS_EN"]

CONDITIONS = ["S0", "S1", "S2", "S3", "S4", "S5"]

def format_segment(topic, text, cond, lang, idx):
    zh = lang == "zh"
    if cond == "S0":
        return text
    elif cond == "S1":
        return f"{'## '}{topic}\n{text}"
    elif cond == "S2":
        return text
    elif cond == "S3":
        return text  # [SEP] added as joiner
    elif cond == "S4":
        return f"### {topic}\n{text}"
    elif cond == "S5":
        num = str(idx + 1) + "."
        return f"{num} {text}"

JOINERS = {
    "S0": "\n",
    "S1": "\n\n---\n\n",
    "S2": "\n\n\n",
    "S3": "\n[SEP]\n",
    "S4": "\n\n",
    "S5": "\n",
}

def build_context(targets, distractors, condition, lang, target_tokens):
    fillers = FILLERS_ZH if lang == "zh" else FILLERS_EN
    # Same interleave pattern as v3
    fact_items = []
    d_idx = 0
    for i, (topic, text, _, _) in enumerate(targets):
        fact_items.append((topic, text, "target"))
        for _ in range(3):
            if d_idx < len(distractors):
                fact_items.append((distractors[d_idx][0], distractors[d_idx][1], "distractor"))
                d_idx += 1

    joiner = JOINERS[condition]
    segments = [format_segment(t, x, condition, lang, i) for i, (t, x, _) in enumerate(fact_items)]
    base = joiner.join(segments)
    current = count_tokens(base)

    filler_idx = 0
    while current < target_tokens:
        filler = fillers[filler_idx % len(fillers)]
        seg = format_segment(("补充" if lang == "zh" else "Note"), filler, condition, lang, len(segments) + filler_idx)
        test = base + joiner + seg
        if count_tokens(test) > target_tokens * 1.15:
            break
        base = test
        current = count_tokens(base)
        filler_idx += 1
    return base, current


def run_experiment():
    results = []
    for lang, targets, distractors in [
        ("zh", TARGETS_ZH, DISTRACTORS_ZH),
        ("en", TARGETS_EN, DISTRACTORS_EN),
    ]:
        for cond in CONDITIONS:
            context, actual_tok = build_context(targets, distractors, cond, lang, TARGET_TOK)
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
                        print(f"  [{lang}/{cond}/r{rep}/f{i}] {status} '{answer}' ← '{response[:40]}'", flush=True)
                    except Exception as e:
                        print(f"  ERROR [{lang}/{cond}/r{rep}/f{i}]: {e}", file=sys.stderr)
                        continue
                acc = correct_count / total
                results.append({
                    "lang": lang, "condition": cond, "length": "4k",
                    "rep": rep, "correct": correct_count, "n_facts": total,
                    "accuracy": acc, "actual_tokens": actual_tok,
                })
                print(f"[{lang}/{cond}/r{rep}] {correct_count}/{total} = {acc:.2f} ({actual_tok} tok)", flush=True)

    out_path = Path(__file__).parent / "results_v4.jsonl"
    with open(out_path, "w") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"\nSaved {len(results)} records to {out_path}")

    # Summary + order-ratio analysis
    print("\n=== SUMMARY ===")
    grouped = defaultdict(list)
    tok_map = {}
    for r in results:
        key = (r["lang"], r["condition"])
        grouped[key].append(r["accuracy"])
        tok_map[key] = r["actual_tokens"]
    print(f"{'Lang':<5} {'Cond':<5} {'Tok':<7} {'Mean Acc':<10}")
    cell_mean = {}
    for (lang, cond), accs in sorted(grouped.items()):
        mean = sum(accs) / len(accs)
        cell_mean[(lang, cond)] = mean
        print(f"{lang:<5} {cond:<5} {tok_map[(lang, cond)]:<7} {mean:<10.3f}")

    print("\n=== ORDER ANALYSIS (per language) ===")
    for lang in ["en", "zh"]:
        s0 = cell_mean.get((lang, "S0"), float("nan"))
        seps = {c: cell_mean[(lang, c)] for c in ["S1", "S2", "S3", "S4", "S5"] if (lang, c) in cell_mean}
        best_c = max(seps, key=seps.get); worst_c = min(seps, key=seps.get)
        delta_presence = seps[best_c] - s0
        delta_char = seps[best_c] - seps[worst_c]
        ratio = (delta_char / delta_presence) if delta_presence != 0 else float("inf")
        print(f"{lang}: S0={s0:.2f} | best={best_c}@{seps[best_c]:.2f} worst={worst_c}@{seps[worst_c]:.2f}")
        print(f"     Δ_presence={delta_presence:+.2f}  Δ_character={delta_char:+.2f}  ratio={ratio:.2f}")
        if abs(ratio) < 0.1 and delta_presence > 0.05:
            print("     → second-order CONFIRMED (char effect < 10% of presence effect)")
        elif delta_presence <= 0.05:
            print("     → no first-order effect in this lang; ratio not interpretable")
        else:
            print("     → char effect NOT negligible here")

if __name__ == "__main__":
    run_experiment()