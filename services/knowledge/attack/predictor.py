from collections import defaultdict

# simple co-occurrence counts (toy)
CO_OCC = defaultdict(lambda: defaultdict(int))

# seed some relations
CO_OCC["T1110"]["T1078"] += 5   # brute force → valid accounts
CO_OCC["T1110"]["T1021"] += 3   # brute force → lateral movement
CO_OCC["T1490"]["T1486"] += 6   # inhibit recovery → ransomware

def predict_next(ttps: list[str], k: int = 3):
    scores = defaultdict(int)
    for t in ttps:
        for nxt, c in CO_OCC[t].items():
            scores[nxt] += c

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:k]

    out = []
    for t, s in ranked:
        out.append({
            "technique_id": t,
            "confidence": float(s),
            "reasoning": f"Often co-occurs with {','.join(ttps)}"
        })
    return out