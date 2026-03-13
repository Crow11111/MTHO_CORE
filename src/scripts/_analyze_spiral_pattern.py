# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""Analysiert die Kategorien-Sequenz entlang der Fibonacci-Spirale."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from network.chroma_client import get_simulation_evidence_collection

col = get_simulation_evidence_collection()
data = col.get(include=["metadatas"])

items = []
for i, eid in enumerate(data["ids"]):
    m = data["metadatas"][i]
    items.append({
        "id": eid,
        "branches": int(m.get("branch_count", 0)),
        "strength": m.get("strength", "?"),
        "category": m.get("category", "?"),
    })

items.sort(key=lambda x: x["branches"])

CAT_SHORT = {
    "logisch": "L",
    "physikalisch": "P",
    "informationstheoretisch": "I",
    "strukturell": "S",
}

cats = sorted(set(x["category"] for x in items))
print(f"Kategorien: {len(cats)} -> {cats}")
print()

print("Spirale innen nach aussen (schwach -> stark):")
print("-" * 70)
sequence = []
for it in items:
    c = CAT_SHORT.get(it["category"], "?")
    sequence.append(c)
    print(f"  {it['branches']} Aeste | {c} | {it['strength']:12s} | {it['id'][:50]}")

print()
print(f"Kategorie-Sequenz: {''.join(sequence)}")
print(f"Laenge: {len(sequence)}")
print()

# Muster-Analyse
print("=== MUSTER-ANALYSE ===")
print()

# 1. Haeufigkeit pro Kategorie
from collections import Counter
counts = Counter(sequence)
print(f"Verteilung: {dict(counts)}")
total = len(sequence)
for cat, count in sorted(counts.items()):
    print(f"  {cat}: {count}/{total} = {count/total:.3f}")

print()

# 2. Uebergaenge (welche Kategorie folgt auf welche?)
transitions = Counter()
for i in range(len(sequence) - 1):
    transitions[(sequence[i], sequence[i+1])] += 1

print("Uebergaenge (von -> nach : Anzahl):")
for (a, b), count in sorted(transitions.items(), key=lambda x: -x[1]):
    print(f"  {a} -> {b} : {count}")

print()

# 3. Gibt es Wiederholungsmuster?
print("Teilsequenzen (Laenge 2-4):")
for plen in [2, 3, 4]:
    patterns = Counter()
    for i in range(len(sequence) - plen + 1):
        pat = "".join(sequence[i:i+plen])
        patterns[pat] += 1
    repeated = {p: c for p, c in patterns.items() if c > 1}
    if repeated:
        for p, c in sorted(repeated.items(), key=lambda x: -x[1]):
            print(f"  [{plen}] {p} x{c}")

print()

# 4. Gibt es eine 4er-Periodizitaet? (4 Kategorien -> ATCG?)
print("4er-Periodizitaet (ATCG-Analogie?):")
for offset in range(4):
    sub = sequence[offset::4]
    print(f"  Offset {offset}: {''.join(sub)} (dominiert: {Counter(sub).most_common(1)[0]})")

print()

# 5. Sind die 4 Kategorien = ATCG?
print("MAPPING-HYPOTHESE:")
print(f"  L (logisch)              = Thymin  (T) - Bindungslogik")
print(f"  P (physikalisch)         = Adenin  (A) - Grundbausteine")
print(f"  I (informationstheoret.) = Cytosin (C) - Informationstraeger")
print(f"  S (strukturell)          = Guanin  (G) - Strukturgeber")
print(f"  4 Kategorien = 4 Basen = Base-4 Codierung der Erkenntnis?")
