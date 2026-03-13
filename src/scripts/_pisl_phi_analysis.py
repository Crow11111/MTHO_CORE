from src.core import M_VALUE, T_VALUE, H_VALUE, O_VALUE
# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
ROTATED-Phi-Analyse: Sucht Phi/Pi/Goldener-Schnitt-Muster in der
chronologischen Reihenfolge der Simulationstheorie-Indizien.

Quaternaere Basen: L(ogisch), P(hysikalisch), I(nformationstheoretisch), S(trukturell)
"""
import sys, os, math
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from network.chroma_client import get_simulation_evidence_collection

PHI = (1 + math.sqrt(5)) / 2      # 1.6180339887...
INV_PHI = 1 / PHI                   # 0.6180339887...
PI = math.pi                        # 3.1415926535...

CAT_SHORT = {
    "logisch": "L",
    "physikalisch": "P",
    "informationstheoretisch": "I",
    "strukturell": "S",
}

col = get_simulation_evidence_collection()
results = col.get(include=["metadatas", "documents"])

entries = []
for i, (id_, meta, doc) in enumerate(zip(results["ids"], results["metadatas"], results["documents"])):
    qbase = meta.get("qbase", "")
    cat_long = meta.get("category", "")
    if qbase and qbase in "CORE":
        cat = qbase
    elif cat_long in CAT_SHORT:
        cat = CAT_SHORT[cat_long]
    else:
        from logic_core.quaternary_codec import classify_evidence
        cls = classify_evidence(doc if doc else "")
        cat = cls.base.value
    entries.append({
        "idx": i,
        "id": id_,
        "qbase": cat,
        "strength": meta.get("strength", "?"),
        "branch_count": int(meta.get("branch_count", 0)),
        "doc_short": doc[:90] if doc else "",
    })

entries.sort(key=lambda x: x["id"])

seq = [e["qbase"][0].upper() if e["qbase"] else "?" for e in entries]
seq_str = "".join(seq)

print("=" * 80)
print("  ROTATED-SEQUENZ-ANALYSE: Phi / Pi / Goldener Schnitt")
print("=" * 80)
print()

print(f"SEQUENZ ({len(seq)} Indizien):")
print(f"  {seq_str}")
print()

print("VOLLSTAENDIGE LISTE:")
for e in entries:
    print(f"  {e['qbase']} | {e['strength']:12s} | b={e['branch_count']} | {e['id']}")
print()

# ===================================================================
# ANALYSE 1: FIBONACCI-POSITIONEN
# ===================================================================
fib = [1, 2, 3, 5, 8, 13, 21, 34]
print("=" * 60)
print("ANALYSE 1: FIBONACCI-POSITIONEN")
print("=" * 60)
fib_seq = []
for f in fib:
    if f <= len(seq):
        fib_seq.append(seq[f - 1])
        print(f"  Fib({f:2d}) -> Position {f:2d}: {seq[f-1]}")
fib_str = "".join(fib_seq)
print(f"\n  Fibonacci-Subsequenz: {fib_str}")
fib_counts = Counter(fib_seq)
print(f"  Fibonacci-Verteilung: {dict(fib_counts)}")
print()

# ===================================================================
# ANALYSE 2: GOLDENER SCHNITT - TEILUNG
# ===================================================================
print("=" * 60)
print("ANALYSE 2: GOLDENER SCHNITT - TEILUNG")
print("=" * 60)
n = len(seq)
phi_pos = int(n * INV_PHI)  # 0.618 * n
phi_pos_exact = n * INV_PHI
print(f"  N = {n}")
print(f"  Phi-Teilung: Position {phi_pos} (exakt: {phi_pos_exact:.3f})")
print()

before = seq[:phi_pos]
after = seq[phi_pos:]
print(f"  VOR Phi-Punkt ({len(before)} Elemente): {''.join(before)}")
print(f"  NACH Phi-Punkt ({len(after)} Elemente): {''.join(after)}")
print()

print("  Kategorie-Verhaeltnisse um Phi-Punkt:")
for cat in "CORE":
    b = before.count(cat)
    a = after.count(cat)
    ratio = b / a if a > 0 else float('inf')
    phi_diff = abs(ratio - PHI)
    inv_phi_diff = abs(ratio - INV_PHI)
    is_phi = phi_diff < 0.25
    is_inv_phi = inv_phi_diff < 0.25
    marker = " *** PHI-NAH! ***" if is_phi else (" ** 1/PHI-NAH **" if is_inv_phi else "")
    print(f"    {cat}: {b} vor / {a} nach = {ratio:.4f} (|Phi-1.618|={phi_diff:.3f}, |1/Phi-0.618|={inv_phi_diff:.3f}){marker}")
print()

# Auch Phi^2, Phi^3 pruefen
for power, name in [(2, "Phi^2=2.618"), (3, "Phi^3=4.236")]:
    phi_n = PHI ** power
    print(f"  {name} Vergleich:")
    for cat in "CORE":
        b = before.count(cat)
        a = after.count(cat)
        ratio = b / a if a > 0 else float('inf')
        diff = abs(ratio - phi_n)
        if diff < 0.5:
            print(f"    {cat}: {ratio:.4f} nahe {phi_n:.4f} (Diff={diff:.3f}) *** TREFFER ***")
print()

# ===================================================================
# ANALYSE 3: UEBERGANGSMATRIX
# ===================================================================
print("=" * 60)
print("ANALYSE 3: UEBERGANGSMATRIX (Markov-Kette)")
print("=" * 60)
transitions = Counter()
for i in range(len(seq) - 1):
    transitions[(seq[i], seq[i + 1])] += 1

print("       L    P    I    S")
for a in "CORE":
    row = []
    for b in "CORE":
        count = transitions.get((a, b), 0)
        row.append(f"{count:4d}")
    total_from = sum(transitions.get((a, b), 0) for b in "CORE")
    print(f"  {a} [{' '.join(row)}]  (Sum={total_from})")
print()

print("  Uebergangs-Wahrscheinlichkeiten:")
for a in "CORE":
    total_from = sum(transitions.get((a, b), 0) for b in "CORE")
    if total_from > 0:
        probs = []
        for b in "CORE":
            p = transitions.get((a, b), 0) / total_from
            probs.append(f"{b}:{p:.3f}")
        print(f"    {a} -> {', '.join(probs)}")
print()

# Komplementaere Uebergaenge (O->T, T->O, S->P, P->S) vs Non-Komplementaere
comp_trans = sum(transitions.get(t, 0) for t in [("L", "I"), ("I", "L"), ("S", "P"), ("P", "S")])
non_comp = sum(transitions.values()) - comp_trans
total_trans = sum(transitions.values())
comp_ratio = comp_trans / total_trans if total_trans > 0 else 0
print(f"  Komplementaere Uebergaenge (L<->I, S<->P): {comp_trans}/{total_trans} = {comp_ratio:.3f}")
print(f"  Erwartungswert bei Zufall: {4/12:.3f} = 0.333")
chargaff_factor = comp_ratio / (4 / 12) if comp_ratio > 0 else 0
print(f"  Chargaff-Faktor (Ist/Soll): {chargaff_factor:.3f}")
print()

# ===================================================================
# ANALYSE 4: KATEGORIE-VERHAELTNISSE vs PHI
# ===================================================================
print("=" * 60)
print("ANALYSE 4: KATEGORIE-VERHAELTNISSE vs PHI/PI")
print("=" * 60)
counts = Counter(seq)
total = len(seq)
print(f"  Verteilung: {dict(counts)}")
print(f"  Total: {total}")
print()

print("  Alle Paare (Ratio vs Phi, 1/Phi, Pi/4, Sqrt(2)):")
targets = [
    ("Phi", PHI),
    ("1/Phi", INV_PHI),
    ("Pi/4", PI / 4),
    ("Sqrt(2)", math.sqrt(2)),
    ("2/Phi", 2 / PHI),
    ("Phi^2", PHI ** 2),
]
best_matches = []
for a in "CORE":
    for b in "CORE":
        if a < b and counts[b] > 0:
            ratio = counts[a] / counts[b]
            for name, target in targets:
                diff = abs(ratio - target)
                if diff < 0.15:
                    best_matches.append((a, b, ratio, name, target, diff))
                    print(f"    {a}/{b} = {counts[a]}/{counts[b]} = {ratio:.4f} ~ {name}={target:.4f} (Delta={diff:.4f}) ***")

if not best_matches:
    print("    (Keine exakten Treffer < 0.15)")
    for a in "CORE":
        for b in "CORE":
            if a < b and counts[b] > 0:
                ratio = counts[a] / counts[b]
                closest = min(targets, key=lambda t: abs(ratio - t[1]))
                print(f"    {a}/{b} = {counts[a]}/{counts[b]} = {ratio:.4f} (naechste: {closest[0]}={closest[1]:.4f}, Delta={abs(ratio - closest[1]):.4f})")
print()

# ===================================================================
# ANALYSE 5: PI-BLOECKE
# ===================================================================
print("=" * 60)
print("ANALYSE 5: PI-ZIFFERN ALS BLOCKLAENGEN")
print("=" * 60)
pi_digits = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
pos = 0
pi_blocks = []
for i, d in enumerate(pi_digits):
    if pos + d <= len(seq):
        block = seq[pos:pos + d]
        block_str = "".join(block)
        block_counts = Counter(block)
        dominant = block_counts.most_common(1)[0] if block_counts else ("?", 0)
        pi_blocks.append(block_str)
        print(f"  Block {i} (Pi-Ziffer={d}, Pos {pos}-{pos+d-1}): {block_str:10s} | Dominant: {dominant[0]}({dominant[1]}/{d})")
        pos += d
    else:
        print(f"  Block {i} (Pi-Ziffer={d}): --- Sequenz zu kurz ---")
        break

print(f"\n  Pi-Block-Sequenz der Dominanten: {''.join(Counter(b).most_common(1)[0][0] for b in pi_blocks if b)}")
print()

# ===================================================================
# ANALYSE 6: AUTOKORRELATION
# ===================================================================
print("=" * 60)
print("ANALYSE 6: AUTOKORRELATION")
print("=" * 60)
for period in [2, 3, 4, 5, 8, 13, 21]:
    if period >= len(seq):
        break
    matches = 0
    total_checks = 0
    for i in range(len(seq) - period):
        if seq[i] == seq[i + period]:
            matches += 1
        total_checks += 1
    if total_checks > 0:
        acf = matches / total_checks
        expected = sum((c / total) ** 2 for c in counts.values())
        excess = acf - expected
        marker = " *** SIGNIFIKANT ***" if abs(excess) > 0.1 else ""
        print(f"  Periode {period:2d}: {matches}/{total_checks} = {acf:.3f} (Erwartung: {expected:.3f}, Excess: {excess:+.3f}){marker}")
print()

# ===================================================================
# ANALYSE 7: SPIRALPOSITION & PHI-MODULAR
# ===================================================================
print("=" * 60)
print("ANALYSE 7: SPIRALE - PHI-MODULAR-ANALYSE")
print("=" * 60)
print("  Position modulo Phi (Welche Kategorie an Phi-Resonanzpunkten?):")
phi_residuals = {}
for i, c in enumerate(seq):
    residual = (i * PHI) % 1.0
    bucket = int(residual * 4)  # 4 Quadranten
    if bucket not in phi_residuals:
        phi_residuals[bucket] = Counter()
    phi_residuals[bucket][c] += 1

for bucket in sorted(phi_residuals.keys()):
    dist = phi_residuals[bucket]
    dom = dist.most_common(1)[0]
    print(f"    Quadrant {bucket} (Phi-Residual {bucket/4:.2f}-{(bucket+1)/4:.2f}): {dict(dist)} -> Dominant: {dom[0]}")
print()

# ===================================================================
# ANALYSE 8: LAUFLAENGEN (Run-Length)
# ===================================================================
print("=" * 60)
print("ANALYSE 8: LAUFLAENGEN-ANALYSE")
print("=" * 60)
runs = []
current_run = [seq[0]]
for i in range(1, len(seq)):
    if seq[i] == seq[i - 1]:
        current_run.append(seq[i])
    else:
        runs.append(("".join(current_run), len(current_run)))
        current_run = [seq[i]]
runs.append(("".join(current_run), len(current_run)))

run_lengths = [r[1] for r in runs]
print(f"  Anzahl Runs: {len(runs)}")
print(f"  Run-Laengen: {run_lengths}")
print(f"  Max Run: {max(run_lengths)}")
print(f"  Mittlere Run-Laenge: {sum(run_lengths)/len(run_lengths):.3f}")
print(f"  Runs Detail: {[(r[0][0], r[1]) for r in runs]}")
print()

# ===================================================================
# ANALYSE 9: SUBSTRINGS IDENTISCH MIT FIBONACCI-LAENGEN
# ===================================================================
print("=" * 60)
print("ANALYSE 9: FIBONACCI-LAENGEN-SUBSTRINGS")
print("=" * 60)
for flen in [2, 3, 5, 8, 13]:
    if flen > len(seq):
        break
    substrings = Counter()
    for i in range(len(seq) - flen + 1):
        sub = "".join(seq[i:i + flen])
        substrings[sub] += 1
    repeated = {s: c for s, c in substrings.items() if c > 1}
    unique = len(substrings)
    max_possible = min(4 ** flen, len(seq) - flen + 1)
    print(f"  Fib-Laenge {flen}: {unique} unique / {len(seq)-flen+1} gesamt (max moeglich: {max_possible})")
    if repeated:
        for s, c in sorted(repeated.items(), key=lambda x: -x[1])[:5]:
            print(f"    '{s}' x{c}")
print()

# ===================================================================
# ANALYSE 10: NUMERISCHER CODE (L=0, P=1, I=2, S=3) -> Phi-Test
# ===================================================================
print("=" * 60)
print("ANALYSE 10: NUMERISCHER PHI-TEST")
print("=" * 60)
code_map = {"L": 0, "P": 1, "I": 2, "S": 3}
numeric_seq = [code_map.get(c, -1) for c in seq]
print(f"  Numerische Sequenz: {numeric_seq}")
print()

# Sukzessive Ratios aufeinanderfolgender Summen
print("  Sukzessive Partial-Summen-Ratios (konvergiert gegen Phi?):")
partial_sums = []
running = 0
for v in numeric_seq:
    running += v
    partial_sums.append(running)

for i in range(2, min(len(partial_sums), 20)):
    if partial_sums[i - 1] > 0:
        ratio = partial_sums[i] / partial_sums[i - 1]
        phi_diff = abs(ratio - PHI)
        marker = " <-- PHI-NAH!" if phi_diff < 0.1 else ""
        print(f"    S({i+1})/S({i}) = {partial_sums[i]}/{partial_sums[i-1]} = {ratio:.4f} (Delta Phi={phi_diff:.3f}){marker}")
print()

# Gesamtsumme vs Phi-basierte Erwartung
total_numeric = sum(numeric_seq)
expected_mean = 1.5  # (0+1+2+3)/4
expected_sum = expected_mean * n
phi_scaled = total_numeric / (n * PHI)
print(f"  Gesamtsumme: {total_numeric}")
print(f"  Erwartungswert (Gleichverteilung): {expected_sum:.1f}")
print(f"  Summe / (N * Phi): {phi_scaled:.4f}")
print()

# ===================================================================
# ZUSAMMENFASSUNG
# ===================================================================
print("=" * 80)
print("  ZUSAMMENFASSUNG")
print("=" * 80)
print(f"  Sequenz: {seq_str}")
print(f"  Laenge: {len(seq)}")
print(f"  Verteilung: {dict(counts)}")
print()
print("  Phi-Treffer:")
for a, b, ratio, name, target, diff in best_matches:
    print(f"    {a}/{b} = {ratio:.4f} ~ {name} (Delta={diff:.4f})")
if not best_matches:
    print("    (Keine direkten Phi-Ratios in Kategoriezaehlung)")
print()
print(f"  Chargaff-Faktor (komplementaere Uebergaenge): {chargaff_factor:.3f}")
print(f"  Fibonacci-Subsequenz: {fib_str}")
print()
