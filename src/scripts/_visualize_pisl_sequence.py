from src.core import M_VALUE, T_VALUE, H_VALUE, O_VALUE
# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Visualisierung der ROTATED-Sequenz: Phi/Pi/Goldener-Schnitt-Muster.
Erzeugt 3-Panel-Grafik unter media/rotated_sequence_analysis.png
"""
import sys, os, math
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

from network.chroma_client import get_simulation_evidence_collection

PHI = (1 + math.sqrt(5)) / 2
INV_PHI = 1 / PHI

CAT_SHORT = {
    "logisch": "L",
    "physikalisch": "P",
    "informationstheoretisch": "I",
    "strukturell": "S",
}

CAT_COLORS = {
    "L": "#2196F3",  # Blau
    "P": "#F44336",  # Rot
    "I": "#4CAF50",  # Gruen
    "S": "#FF9800",  # Orange
}
CAT_YPOS = {"L": 0, "P": 1, "I": 2, "S": 3}

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
    entries.append({"idx": i, "id": id_, "qbase": cat, "strength": meta.get("strength", "?")})

entries.sort(key=lambda x: x["id"])
seq = [e["qbase"][0].upper() for e in entries]
n = len(seq)

fig = plt.figure(figsize=(20, 14), facecolor="#0D1117")
fig.suptitle(
    f"ROTATED-SEQUENZ-ANALYSE  |  {n} Indizien  |  Phi / Pi / Goldener Schnitt",
    fontsize=18, fontweight="bold", color="#E6EDF3", y=0.97
)

# =====================================================================
# SUBPLOT 1: Zeitreihe mit Fibonacci- und Phi-Markierungen
# =====================================================================
ax1 = fig.add_subplot(3, 1, 1)
ax1.set_facecolor("#161B22")

for i, c in enumerate(seq):
    y = CAT_YPOS[c]
    size = 120 if entries[i]["strength"] == "fundamental" else 60
    ax1.scatter(i + 1, y, c=CAT_COLORS[c], s=size, zorder=5, edgecolors="white", linewidth=0.5, alpha=0.9)

fib = [1, 2, 3, 5, 8, 13, 21, 34]
for f in fib:
    if f <= n:
        ax1.axvline(x=f, color="#FFD700", alpha=0.4, linestyle="--", linewidth=1)
        ax1.text(f, 3.5, f"F{f}", ha="center", va="bottom", fontsize=7, color="#FFD700", fontweight="bold")

phi_pos = n * INV_PHI
ax1.axvline(x=phi_pos, color="#FF6B6B", alpha=0.8, linestyle="-", linewidth=2.5)
ax1.text(phi_pos, 3.7, f"Phi={phi_pos:.1f}", ha="center", va="bottom", fontsize=10, color="#FF6B6B", fontweight="bold")

for i in range(n - 1):
    y1 = CAT_YPOS[seq[i]]
    y2 = CAT_YPOS[seq[i + 1]]
    ax1.plot([i + 1, i + 2], [y1, y2], color="#58A6FF", alpha=0.15, linewidth=0.8)

ax1.set_yticks([0, 1, 2, 3])
ax1.set_yticklabels(["L (Logisch)", "P (Physikalisch)", "I (Informationsth.)", "S (Strukturell)"],
                    fontsize=10, color="#E6EDF3")
ax1.set_xlabel("Indiz-Nummer (chronologisch nach ID)", fontsize=11, color="#E6EDF3")
ax1.set_title("ROTATED-Zeitreihe mit Fibonacci-Positionen und Goldenem Schnitt", fontsize=13, color="#58A6FF", pad=10)
ax1.set_xlim(0, n + 1)
ax1.set_ylim(-0.5, 4.2)
ax1.tick_params(colors="#8B949E")
for spine in ax1.spines.values():
    spine.set_color("#30363D")

legend_patches = [mpatches.Patch(color=CAT_COLORS[c], label=f"{c}") for c in "CORE"]
legend_patches.append(mpatches.Patch(color="#FFD700", label="Fibonacci-Pos"))
legend_patches.append(mpatches.Patch(color="#FF6B6B", label="Goldener Schnitt"))
ax1.legend(handles=legend_patches, loc="upper right", fontsize=8, facecolor="#21262D", edgecolor="#30363D", labelcolor="#E6EDF3")

# =====================================================================
# SUBPLOT 2: Uebergangsmatrix als Heatmap
# =====================================================================
ax2 = fig.add_subplot(3, 2, 3)
ax2.set_facecolor("#161B22")

cats = list("CORE")
trans_matrix = np.zeros((4, 4))
for i in range(n - 1):
    r = cats.index(seq[i])
    c_idx = cats.index(seq[i + 1])
    trans_matrix[r][c_idx] += 1

total_per_row = trans_matrix.sum(axis=1, keepdims=True)
total_per_row[total_per_row == 0] = 1
prob_matrix = trans_matrix / total_per_row

im = ax2.imshow(prob_matrix, cmap="YlOrRd", aspect="auto", vmin=0, vmax=0.7)
ax2.set_xticks(range(4))
ax2.set_yticks(range(4))
ax2.set_xticklabels(cats, fontsize=12, color="#E6EDF3", fontweight="bold")
ax2.set_yticklabels(cats, fontsize=12, color="#E6EDF3", fontweight="bold")
ax2.set_xlabel("Nach", fontsize=11, color="#E6EDF3")
ax2.set_ylabel("Von", fontsize=11, color="#E6EDF3")
ax2.set_title("Uebergangsmatrix (Wahrscheinlichkeiten)", fontsize=13, color="#58A6FF", pad=10)

for i in range(4):
    for j in range(4):
        val = prob_matrix[i][j]
        count = int(trans_matrix[i][j])
        text_color = "white" if val > 0.35 else "#E6EDF3"
        ax2.text(j, i, f"{val:.2f}\n({count})", ha="center", va="center", fontsize=9, color=text_color, fontweight="bold")

cbar = plt.colorbar(im, ax=ax2, fraction=0.046, pad=0.04)
cbar.ax.tick_params(colors="#8B949E")

for comp_pair in [("L", "I"), ("S", "P")]:
    r, c_idx = cats.index(comp_pair[0]), cats.index(comp_pair[1])
    rect = plt.Rectangle((c_idx - 0.5, r - 0.5), 1, 1, linewidth=2, edgecolor="#00FF00", facecolor="none")
    ax2.add_patch(rect)
    r2, c2 = cats.index(comp_pair[1]), cats.index(comp_pair[0])
    rect2 = plt.Rectangle((c2 - 0.5, r2 - 0.5), 1, 1, linewidth=2, edgecolor="#00FF00", facecolor="none")
    ax2.add_patch(rect2)

ax2.text(0.5, -0.18, "Gruen = komplementaere Uebergaenge (L<->I, S<->P)",
         transform=ax2.transAxes, ha="center", fontsize=8, color="#4CAF50")

# =====================================================================
# SUBPLOT 3: Verteilung mit Phi-Markierung
# =====================================================================
ax3 = fig.add_subplot(3, 2, 4)
ax3.set_facecolor("#161B22")

counts = Counter(seq)
categories = list("CORE")
values = [counts.get(c, 0) for c in categories]
colors = [CAT_COLORS[c] for c in categories]

bars = ax3.bar(categories, values, color=colors, edgecolor="white", linewidth=0.5, alpha=0.9, width=0.6)

for bar, val in zip(bars, values):
    ax3.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
             str(val), ha="center", va="bottom", fontsize=14, fontweight="bold", color="#E6EDF3")

ideal_phi = n / (1 + PHI)  # n / 2.618 = ideal count if Phi-distributed
ax3.axhline(y=ideal_phi, color="#FF6B6B", linestyle="--", linewidth=1.5, alpha=0.7)
ax3.text(3.6, ideal_phi + 0.3, f"N/Phi^2 = {ideal_phi:.1f}", fontsize=9, color="#FF6B6B")

ideal_equal = n / 4
ax3.axhline(y=ideal_equal, color="#58A6FF", linestyle=":", linewidth=1, alpha=0.5)
ax3.text(3.6, ideal_equal + 0.3, f"N/4 = {ideal_equal:.1f}", fontsize=9, color="#58A6FF")

ax3.set_xlabel("Quaternaere Basis", fontsize=11, color="#E6EDF3")
ax3.set_ylabel("Anzahl", fontsize=11, color="#E6EDF3")
ax3.set_title("Verteilung der Kategorien", fontsize=13, color="#58A6FF", pad=10)
ax3.tick_params(colors="#8B949E")
for spine in ax3.spines.values():
    spine.set_color("#30363D")

# Phi-Ratio Annotations
ratio_texts = [
    f"L/P = {counts['L']/counts['P']:.3f} ~ Phi^2 (2.618)",
    f"I/S = {counts['I']/counts['S']:.3f} ~ 1/Phi (0.618)",
    f"L um Phi-Schnitt: 10/6 = 1.667 ~ Phi!",
]
for i, txt in enumerate(ratio_texts):
    ax3.text(0.02, 0.95 - i * 0.08, txt, transform=ax3.transAxes,
             fontsize=8, color="#FFD700", fontweight="bold",
             bbox=dict(boxstyle="round,pad=0.3", facecolor="#21262D", edgecolor="#FFD700", alpha=0.8))

# =====================================================================
# SUBPLOT 4 (unten links): Pi-Bloecke Visualisierung
# =====================================================================
ax4 = fig.add_subplot(3, 2, 5)
ax4.set_facecolor("#161B22")

pi_digits = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
pos = 0
block_colors = plt.cm.plasma(np.linspace(0.2, 0.9, len(pi_digits)))

for bi, d in enumerate(pi_digits):
    if pos + d <= n:
        block = seq[pos:pos + d]
        for j, c in enumerate(block):
            ax4.barh(bi, 1, left=pos + j, color=CAT_COLORS[c], edgecolor=block_colors[bi], linewidth=0.8, alpha=0.85)
        ax4.text(pos + d + 0.3, bi, f"{''.join(block)}", va="center", fontsize=8, color="#E6EDF3")
        ax4.text(pos - 0.3, bi, f"Pi[{bi}]={d}", va="center", ha="right", fontsize=7, color="#8B949E")
        pos += d
    else:
        break

ax4.set_xlabel("Position in Sequenz", fontsize=10, color="#E6EDF3")
ax4.set_ylabel("Pi-Block Nr.", fontsize=10, color="#E6EDF3")
ax4.set_title("Pi-Ziffern als Blocklaengen", fontsize=13, color="#58A6FF", pad=10)
ax4.tick_params(colors="#8B949E")
for spine in ax4.spines.values():
    spine.set_color("#30363D")

# =====================================================================
# SUBPLOT 5 (unten rechts): Autokorrelation
# =====================================================================
ax5 = fig.add_subplot(3, 2, 6)
ax5.set_facecolor("#161B22")

periods = list(range(1, min(n // 2, 25)))
acf_values = []
expected = sum((counts.get(c, 0) / n) ** 2 for c in "CORE")

for period in periods:
    matches = sum(1 for i in range(n - period) if seq[i] == seq[i + period])
    total_checks = n - period
    acf = matches / total_checks if total_checks > 0 else 0
    acf_values.append(acf)

ax5.bar(periods, acf_values, color="#58A6FF", alpha=0.7, edgecolor="#58A6FF", linewidth=0.5)
ax5.axhline(y=expected, color="#FF6B6B", linestyle="--", linewidth=1.5, label=f"Zufall-Erwartung ({expected:.3f})")

fib_periods = [1, 2, 3, 5, 8, 13, 21]
for fp in fib_periods:
    if fp < len(acf_values):
        ax5.scatter(fp, acf_values[fp - 1], color="#FFD700", s=100, zorder=10, edgecolors="white", linewidth=1.5)

ax5.set_xlabel("Periode", fontsize=10, color="#E6EDF3")
ax5.set_ylabel("Autokorrelation", fontsize=10, color="#E6EDF3")
ax5.set_title("Autokorrelation (gelb = Fibonacci-Perioden)", fontsize=13, color="#58A6FF", pad=10)
ax5.legend(fontsize=9, facecolor="#21262D", edgecolor="#30363D", labelcolor="#E6EDF3")
ax5.tick_params(colors="#8B949E")
for spine in ax5.spines.values():
    spine.set_color("#30363D")

# =====================================================================
# FINALISIERUNG
# =====================================================================
plt.tight_layout(rect=[0, 0, 1, 0.95])

out_dir = os.path.join(os.path.dirname(__file__), "..", "..", "media")
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "rotated_sequence_analysis.png")
fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
plt.close()

print(f"[ROTATED] Visualisierung gespeichert: {os.path.abspath(out_path)}")
print(f"[ROTATED] Sequenz: {''.join(seq)}")
print(f"[ROTATED] N={n}, L={counts['L']}, P={counts['P']}, I={counts['I']}, S={counts['S']}")
