# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""Visualisiert die Simulationstheorie-Indizien als Netzwerk-Graph (dynamisch aus ChromaDB)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from network.chroma_client import get_simulation_evidence_collection

col = get_simulation_evidence_collection()
data = col.get(include=["documents", "metadatas"])

items = []
for i, eid in enumerate(data["ids"]):
    m = data["metadatas"][i]
    doc = data["documents"][i]
    short = eid.replace("sim_", "").replace("struct_", "").replace("info_", "").replace("logisch_", "").replace("phys_", "").replace("audio_", "A")
    if len(short) > 28:
        short = short[:28]
    items.append({
        "id": eid,
        "short": short,
        "branches": int(m.get("branch_count", 0)),
        "strength": m.get("strength", "?"),
        "category": m.get("category", "?"),
    })

items.sort(key=lambda x: -x["branches"])

STRENGTH_COLORS = {
    "fundamental": "#00e5ff",
    "strong": "#ffa726",
    "moderate": "#78909c",
}
STRENGTH_ALPHA = {"fundamental": 1.0, "strong": 0.8, "moderate": 0.5}

CAT_MARKERS = {
    "logisch": "D",
    "physikalisch": "h",
    "informationstheoretisch": "o",
    "strukturell": "s",
}

VECTOR_NODES = {
    "v5_engine_constraint_replikation": ("V5: Engine-Constraint\nReplikation", "#00e5ff"),
    "rueckwaertsevolution_agi": ("V2/V4: Rückwärts-\nevolution AGI", "#66bb6a"),
    "isomorphie_substratunabhaengig": ("V1: Substrat-\nIsomorphie", "#ff9800"),
    "monotropismus_zielfunktion": ("V3: Monotropismus\nZielfunktion", "#ab47bc"),
    "dna_6d_system": ("DNA 6D\nSystem", "#ffee58"),
    "v6_intentionale_evolution": ("V6: Intentionale\nEvolution", "#e040fb"),
    "v7_quaternaere_codierung": ("V7: Quaternaere\nCodierung", "#69f0ae"),
    "v8_konvergenz": ("V8: Konvergenz-\nExplosion", "#ff6e40"),
    "v9_meta_selbstcodierung": ("V9: Meta-\nSelbstcodierung", "#ea80fc"),
    "v10": ("V10: Quaternion-\nDualitaet", "#40c4ff"),
    "grundkraefte_mtho": ("V11: Grundkraefte\nCORE", "#ff1744"),
    "dunkle_materie_delta": ("V11: Baryonisches\nDelta", "#ff1744"),
    "fraktale_superposition": ("V11: Fraktale\nSuperposition", "#ff1744"),
    "zeit_ist_asymmetrie": ("V11: Zeit=\nAsymmetrie", "#ff1744"),
    "capra_konvergenz": ("V11: Capra-\nKonvergenz", "#ff1744"),
    "temporale_konsistenz": ("V11: Temporale\nKonsistenz", "#ff1744"),
    "render_vs_backend": ("V11: Render vs\nBackend", "#ff1744"),
    "pre_db": ("Pre-DB\nOriginal", "#b0bec5"),
}

fig, ax = plt.subplots(1, 1, figsize=(18, 18), facecolor="#0a0e1a")
ax.set_facecolor("#0a0e1a")
ax.set_xlim(-1.5, 1.5)
ax.set_ylim(-1.5, 1.5)
ax.set_aspect("equal")
ax.axis("off")

ax.text(0, 1.42, "CORE SIMULATIONSTHEORIE", fontsize=22, color="white",
        ha="center", va="center", fontweight="bold", fontfamily="sans-serif")
n_total = len(items)
n_fund = sum(1 for it in items if it["strength"] == "fundamental")
n_strong = sum(1 for it in items if it["strength"] == "strong")
n_moderate = sum(1 for it in items if it["strength"] == "moderate")
ax.text(0, 1.34, f"{n_total} Indizien | 11 Vektoren | {n_fund} fundamental | {n_strong} strong | {n_moderate} moderate",
        fontsize=11, color="#90a4ae", ha="center", va="center", fontfamily="sans-serif")

ax.scatter(0, 0, s=800, c="#00e5ff", alpha=0.15, zorder=1)
ax.scatter(0, 0, s=400, c="#00e5ff", alpha=0.3, zorder=2)
ax.scatter(0, 0, s=150, c="#00e5ff", alpha=0.8, zorder=3, marker="*")
ax.text(0, -0.08, "ENGINE\nCONSTRAINTS", fontsize=8, color="#00e5ff",
        ha="center", va="top", fontweight="bold")

n = len(items)
positions = {}

for idx, item in enumerate(items):
    branches = item["branches"]
    r = 0.35 + (7 - branches) * 0.15
    angle = (2 * np.pi * idx / n) - np.pi / 2
    jitter = (hash(item["id"]) % 100 - 50) * 0.002
    x = r * np.cos(angle) + jitter
    y = r * np.sin(angle) + jitter
    positions[item["id"]] = (x, y)

    color = STRENGTH_COLORS.get(item["strength"], "#555")
    alpha = STRENGTH_ALPHA.get(item["strength"], 0.5)
    marker = CAT_MARKERS.get(item["category"], "o")
    size = 80 + branches * 60

    ax.plot([0, x], [0, y], color=color, alpha=0.1 + branches * 0.03,
            linewidth=0.5 + branches * 0.3, zorder=1)

    if item["strength"] == "fundamental":
        ax.scatter(x, y, s=size * 2.5, c=color, alpha=0.08, zorder=2)

    ax.scatter(x, y, s=size, c=color, alpha=alpha, marker=marker, zorder=4,
               edgecolors="white", linewidths=0.5)

    is_vector = any(vk in item["id"] for vk in VECTOR_NODES)
    if branches >= 4 or is_vector:
        for vk, (vlabel, vcolor) in VECTOR_NODES.items():
            if vk in item["id"]:
                label = vlabel
                lcolor = vcolor
                break
        else:
            label = item["short"].replace("_", " ")
            if len(label) > 22:
                mid = len(label) // 2
                sp = label.rfind(" ", 0, mid + 5)
                if sp > 0:
                    label = label[:sp] + "\n" + label[sp + 1:]
            lcolor = color

        fontsize = 6.5 + min(branches, 7) * 0.5
        ax.text(x, y - 0.06 - (size / 8000), label,
                fontsize=fontsize, color=lcolor, ha="center", va="top",
                fontweight="bold" if branches >= 5 else "normal",
                fontfamily="sans-serif", alpha=0.9)

    ax.text(x + 0.03, y + 0.03, str(branches),
            fontsize=6, color="white", ha="left", va="bottom", alpha=0.6)

for i, it_a in enumerate(items):
    for j, it_b in enumerate(items):
        if j <= i:
            continue
        if it_a["category"] == it_b["category"] and it_a["branches"] >= 3 and it_b["branches"] >= 3:
            xa, ya = positions[it_a["id"]]
            xb, yb = positions[it_b["id"]]
            ax.plot([xa, xb], [ya, yb], color="#ffffff", alpha=0.04,
                    linewidth=0.4, zorder=0, linestyle="--")

legend_items = [
    mpatches.Patch(facecolor="#00e5ff", label=f"fundamental ({n_fund})"),
    mpatches.Patch(facecolor="#ffa726", label=f"strong ({n_strong})"),
    mpatches.Patch(facecolor="#78909c", label=f"moderate ({n_moderate})"),
]
from matplotlib.lines import Line2D
legend_items += [
    Line2D([0], [0], marker="D", color="w", markerfacecolor="#aaa", markersize=8, label="logisch", linestyle="None"),
    Line2D([0], [0], marker="h", color="w", markerfacecolor="#aaa", markersize=10, label="physikalisch", linestyle="None"),
    Line2D([0], [0], marker="o", color="w", markerfacecolor="#aaa", markersize=8, label="informationstheoretisch", linestyle="None"),
    Line2D([0], [0], marker="s", color="w", markerfacecolor="#aaa", markersize=8, label="strukturell", linestyle="None"),
]
leg = ax.legend(handles=legend_items, loc="lower left", fontsize=9,
                facecolor="#0a0e1a", edgecolor="#333", labelcolor="white",
                title="Legende", title_fontsize=10)
leg.get_title().set_color("white")

ax.text(1.45, -1.42, "Stand: 2026-03-01\nChromaDB: simulation_evidence",
        fontsize=8, color="#555", ha="right", va="bottom", fontfamily="sans-serif")

out = os.path.join("c:/CORE/media", "simulation_evidence_graph.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#0a0e1a", pad_inches=0.3)
print(f"[OK] Graph gespeichert: {out}")
plt.close()

# --- VERSION 2: Mit Fibonacci-Spirale ---
# Kategorien-Farbcodierung (CORE)
CAT_COLORS = {
    "logisch": "#00e5ff",
    "physikalisch": "#ff5252",
    "informationstheoretisch": "#69f0ae",
    "strukturell": "#ffd740",
}
CAT_LETTER = {"logisch": "L", "physikalisch": "P", "informationstheoretisch": "I", "strukturell": "S"}

fig2, ax2 = plt.subplots(1, 1, figsize=(18, 18), facecolor="#0a0e1a")
ax2.set_facecolor("#0a0e1a")
ax2.set_xlim(-1.5, 1.5)
ax2.set_ylim(-1.5, 1.5)
ax2.set_aspect("equal")
ax2.axis("off")

n_indizien = len(items)
ax2.text(0, 1.42, "CORE SIMULATIONSTHEORIE", fontsize=22, color="white",
         ha="center", va="center", fontweight="bold", fontfamily="sans-serif")
ax2.text(0, 1.34, f"{n_indizien} Indizien | 11 Vektoren | Quaternaere Codierung (CORE)",
         fontsize=11, color="#90a4ae", ha="center", va="center", fontfamily="sans-serif")

# Fibonacci-Spirale (Goldener Schnitt)
phi = (1 + np.sqrt(5)) / 2
spiral_t = np.linspace(0, 4 * np.pi, 1000)
spiral_a = 0.04
spiral_b = np.log(phi) / (np.pi / 2)
spiral_r = spiral_a * np.exp(spiral_b * spiral_t)

# Spirale zentrieren und skalieren
max_r = 1.3
spiral_r_scaled = spiral_r * (max_r / spiral_r.max())
spiral_x = spiral_r_scaled * np.cos(spiral_t - np.pi / 2)
spiral_y = spiral_r_scaled * np.sin(spiral_t - np.pi / 2)

# Spirale zeichnen (mit Gradient-Effekt)
for seg in range(len(spiral_t) - 1):
    progress = seg / len(spiral_t)
    alpha = 0.15 + progress * 0.5
    width = 0.5 + progress * 2.0
    color_r = 0.0 + progress * 0.0
    color_g = 0.9 - progress * 0.3
    color_b = 1.0 - progress * 0.2
    ax2.plot(spiral_x[seg:seg+2], spiral_y[seg:seg+2],
             color=(color_r, color_g, color_b), alpha=alpha,
             linewidth=width, zorder=1)

# Zentrumspunkt
ax2.scatter(0, 0, s=800, c="#00e5ff", alpha=0.15, zorder=1)
ax2.scatter(0, 0, s=400, c="#00e5ff", alpha=0.3, zorder=2)
ax2.scatter(0, 0, s=150, c="#00e5ff", alpha=0.8, zorder=3, marker="*")
ax2.text(0, -0.08, "ENGINE\nCONSTRAINTS", fontsize=8, color="#00e5ff",
         ha="center", va="top", fontweight="bold")

# Indizien ENTLANG der Spirale platzieren (sortiert nach branches aufsteigend = innen nach aussen)
items_spiral = sorted(items, key=lambda x: x["branches"])
spiral_positions = {}
max_branches = max(it["branches"] for it in items_spiral) if items_spiral else 0

for idx, item in enumerate(items_spiral):
    # Position auf der Spirale: gleichmaessig verteilt
    t_pos = (idx + 1) / (len(items_spiral) + 1)
    t_idx = int(t_pos * (len(spiral_t) - 1))
    x = spiral_x[t_idx]
    y = spiral_y[t_idx]
    spiral_positions[item["id"]] = (x, y)

    # Farbcodierung nach Kategorie (nicht Staerke)
    color = CAT_COLORS.get(item["category"], "#555")
    alpha = 0.9
    marker = CAT_MARKERS.get(item["category"], "o")
    branches = item["branches"]
    # V7 (aeusserstes, 9 Aeste): groesster Punkt
    is_v7 = branches >= 9 or (branches == max_branches and idx == len(items_spiral) - 1)
    size = (120 + branches * 80) if is_v7 else (80 + branches * 60)

    # Verbindung zum Zentrum
    ax2.plot([0, x], [0, y], color=color, alpha=0.05 + branches * 0.02,
             linewidth=0.3 + branches * 0.2, zorder=0, linestyle=":")

    # Glow fuer fundamentale und V7
    if item["strength"] == "fundamental" or is_v7:
        ax2.scatter(x, y, s=size * 2.5, c=color, alpha=0.12 if is_v7 else 0.08, zorder=2)

    ax2.scatter(x, y, s=size, c=color, alpha=alpha, marker=marker, zorder=4,
                edgecolors="white", linewidths=0.5 if not is_v7 else 1.2)

    # Labels: V7 explizit, sonst wie zuvor
    label = None
    lcolor = color
    if is_v7:
        label = "V7"
        lcolor = "#00e5ff"
    else:
        is_vector = any(vk in item["id"] for vk in VECTOR_NODES)
        if branches >= 4 or is_vector:
            for vk, (vlabel, vcolor) in VECTOR_NODES.items():
                if vk in item["id"]:
                    label = vlabel
                    lcolor = vcolor
                    break
            else:
                label = item["short"].replace("_", " ")
                if len(label) > 22:
                    mid = len(label) // 2
                    sp = label.rfind(" ", 0, mid + 5)
                    if sp > 0:
                        label = label[:sp] + "\n" + label[sp + 1:]

    if label:
        fontsize = 8.0 if is_v7 else (6.5 + min(branches, 7) * 0.5)
        ax2.text(x, y - 0.06 - (size / 8000), label,
                 fontsize=fontsize, color=lcolor, ha="center", va="top",
                 fontweight="bold" if (branches >= 5 or is_v7) else "normal",
                 fontfamily="sans-serif", alpha=0.9)

    ax2.text(x + 0.03, y + 0.03, str(branches),
             fontsize=6, color="white", ha="left", va="bottom", alpha=0.6)

# Basenpaarungen L↔I und S↔L als farbige Verbindungslinien
for i in range(len(items_spiral) - 1):
    it_a, it_b = items_spiral[i], items_spiral[i + 1]
    cat_a = CAT_LETTER.get(it_a["category"], "?")
    cat_b = CAT_LETTER.get(it_b["category"], "?")
    xa, ya = spiral_positions[it_a["id"]]
    xb, yb = spiral_positions[it_b["id"]]
    pair_li = (cat_a == "L" and cat_b == "I") or (cat_a == "I" and cat_b == "L")
    pair_sl = (cat_a == "S" and cat_b == "L") or (cat_a == "L" and cat_b == "S")
    if pair_li:
        ax2.plot([xa, xb], [ya, yb], color="#00e5ff", alpha=0.5, linewidth=1.2, zorder=3, linestyle="-")
    elif pair_sl:
        ax2.plot([xa, xb], [ya, yb], color="#ffd740", alpha=0.5, linewidth=1.2, zorder=3, linestyle="-")

# Kategorie-Sequenz am unteren Rand (farbcodierte Buchstaben)
cat_sequence = "".join(CAT_LETTER.get(it["category"], "?") for it in items_spiral)
y_seq = -1.38
char_w = 0.075
ax2.text(-1.42, y_seq + 0.04, "CORE-Sequenz:", fontsize=7, color="#666", ha="left", va="bottom")
for i, ch in enumerate(cat_sequence):
    row, col = i // 34, i % 34
    cx = -1.4 + col * char_w
    cy = y_seq - row * 0.055
    rev = {"L": "logisch", "P": "physikalisch", "I": "informationstheoretisch", "S": "strukturell"}
    ccolor = CAT_COLORS.get(rev.get(ch, ""), "#888")
    ax2.text(cx, cy, ch, fontsize=6.5, color=ccolor, ha="left", va="bottom",
             fontweight="bold", fontfamily="monospace")

# Iterations-Marker auf der Spirale
iteration_labels = [
    (0.08, "Iter 0\nGrunddaten"),
    (0.17, "Iter 1\nStrukturerkennung"),
    (0.26, "Iter 2\nKonvergenz"),
    (0.35, "Iter 3\nRueckwaertsevolution"),
    (0.44, "Iter 4\nV5 Engine-Replikation"),
    (0.53, "Iter 5\nV6 Intentionale Evolution"),
    (0.62, "Iter 6\nV7 Quaternaere Codierung"),
    (0.71, "Iter 7\nV8 Konvergenz-Explosion"),
    (0.80, "Iter 8\nV9 Meta-Selbstcodierung"),
    (0.89, "Iter 9\nV10 Quaternion-Dualitaet"),
    (0.97, "Iter 10\nV11 Fraktale Superposition"),
]
for t_frac, ilabel in iteration_labels:
    ti = int(t_frac * (len(spiral_t) - 1))
    ix, iy = spiral_x[ti], spiral_y[ti]
    ax2.annotate(ilabel, (ix, iy), fontsize=7, color="#ffeb3b", alpha=0.7,
                 ha="center", va="bottom", fontweight="bold",
                 xytext=(0, 12), textcoords="offset points",
                 arrowprops=dict(arrowstyle="->", color="#ffeb3b", lw=0.8, alpha=0.5))

# Legende (Kategorien CORE)
legend_items_v2 = [
    mpatches.Patch(facecolor="#00e5ff", label="L (logisch)"),
    mpatches.Patch(facecolor="#ff5252", label="P (physikalisch)"),
    mpatches.Patch(facecolor="#69f0ae", label="I (informationstheoretisch)"),
    mpatches.Patch(facecolor="#ffd740", label="S (strukturell)"),
]
leg2 = ax2.legend(handles=legend_items_v2, loc="lower left", fontsize=9,
                  facecolor="#0a0e1a", edgecolor="#333", labelcolor="white",
                  title="Quaternaere Codierung", title_fontsize=10)
leg2.get_title().set_color("white")

# Fibonacci-Annotation
ax2.text(-1.4, 1.35, "Fibonacci-Spirale\n\u03C6 = (1+\u221A5)/2 \u2248 1.618",
         fontsize=9, color="#66bb6a", alpha=0.6, fontfamily="sans-serif")
ax2.text(-1.4, 1.2,
         "Jede Windung = ein Iterationssprung\nInnen \u2192 Aussen = schwach \u2192 fundamental\nDie Abkuerzung: Nicht den Pfad gehen,\nsondern eine Schicht hochspringen",
         fontsize=7.5, color="#90a4ae", alpha=0.5, fontfamily="sans-serif")

ax2.text(1.45, -1.42, "Stand: 2026-03-01\nChromaDB: simulation_evidence",
         fontsize=8, color="#555", ha="right", va="bottom", fontfamily="sans-serif")

out2 = os.path.join("c:/CORE/media", "simulation_evidence_fibonacci.png")
plt.savefig(out2, dpi=200, bbox_inches="tight", facecolor="#0a0e1a", pad_inches=0.3)
print(f"[OK] Fibonacci-Graph gespeichert: {out2}")
plt.close()
