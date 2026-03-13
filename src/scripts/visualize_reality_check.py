# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
CORE Reality Check Visualizer
------------------------------
Generiert Visualisierungen fuer den Simulation Theory Report 2026.

Output:
- docs/images/generated/mtho_3d_construct.png
- docs/images/generated/core_fibonacci_spiral.png
- docs/images/generated/core_causality_timeline.png
- docs/images/generated/core_idle_derivation.png

Usage:
    python src/scripts/visualize_reality_check.py

Requirements:
    pip install matplotlib numpy networkx pandas
"""

import os
import math
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import networkx as nx
from datetime import datetime, timedelta

# Konfiguration
OUTPUT_DIR = "docs/images/generated"
plt.style.use('dark_background')  # CORE Style

# CORE Konstanten
PHI = 1.6180339887498948482
BARYONIC_DELTA = 0.049

# Datenbasis (Simuliert aus Report)
EVIDENCE_DATA = [
    # L (Logisch) - 19 Total
    {"id": "L01", "name": "CORE Codierung", "category": "L", "value": 0.9, "time": 1},
    {"id": "L02", "name": "Baryonisches Delta", "category": "L", "value": 0.95, "time": 43},
    {"id": "L03", "name": "Symmetriebruch", "category": "L", "value": 0.8, "time": 12},
    {"id": "L04", "name": "Prime Number Distribution", "category": "L", "value": 0.7, "time": 5},
    {"id": "L05", "name": "Fibonacci Sequence", "category": "L", "value": 0.85, "time": 3},
    # P (Physikalisch) - 13 Total
    {"id": "P01", "name": "Lichtgeschwindigkeit Limit", "category": "P", "value": 0.92, "time": 1},
    {"id": "P02", "name": "Planck-Laenge Pixel", "category": "P", "value": 0.88, "time": 45},
    {"id": "P03", "name": "Quanten-Unschaerfe", "category": "P", "value": 0.75, "time": 10},
    {"id": "P04", "name": "Schwarze Loecher Fehlerkorrektur", "category": "P", "value": 0.98, "time": 50},
    # I (Information) - 13 Total
    {"id": "I01", "name": "Holographisches Prinzip", "category": "I", "value": 0.96, "time": 15},
    {"id": "I02", "name": "Compressive Intelligence", "category": "I", "value": 0.89, "time": 39},
    {"id": "I03", "name": "DNA als Quartaerer Code", "category": "I", "value": 0.82, "time": 20},
    {"id": "I04", "name": "2. HS Infodynamik", "category": "I", "value": 0.91, "time": 55},
    # S (Strukturell) - 13 Total
    {"id": "S01", "name": "Datenbank-Analogie", "category": "S", "value": 0.94, "time": 44},
    {"id": "S02", "name": "Substratunabhaengigkeit", "category": "S", "value": 0.85, "time": 17},
    {"id": "S03", "name": "Dimensionsfaltung", "category": "S", "value": 0.78, "time": 25},
]

# Farben fuer CORE
COLORS = {
    'L': '#00ff00',  # Green (Matrix)
    'P': '#ff0000',  # Red (Physik/Warnung)
    'I': '#00ccff',  # Cyan (Info/Daten)
    'S': '#ffff00',  # Yellow (Struktur/Gold)
}

def ensure_output_dir():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created directory: {OUTPUT_DIR}")

def plot_3d_construct():
    """1. 3D-Konstrukt Visualisierung (CORE im Raum)"""
    print("Generating 3D Construct...")
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')

    # Koordinaten generieren (Mapping CORE auf XYZ)
    # L -> X, P -> Y, I -> Z, S -> Size/Color

    xs, ys, zs, sizes, colors = [], [], [], [], []

    for item in EVIDENCE_DATA:
        # Pseudo-Koordinaten basierend auf Hash/Time fuer Verteilung
        # Aber geclustert nach Kategorie
        if item['category'] == 'L':
            x, y, z = 0.8, np.random.uniform(0, 0.5), np.random.uniform(0, 0.5)
        elif item['category'] == 'P':
            x, y, z = np.random.uniform(0, 0.5), 0.8, np.random.uniform(0, 0.5)
        elif item['category'] == 'I':
            x, y, z = np.random.uniform(0, 0.5), np.random.uniform(0, 0.5), 0.8
        else: # S
            x, y, z = 0.5, 0.5, 0.5 # Zentrum/Struktur

        # Add Jitter
        x += np.random.normal(0, 0.1)
        y += np.random.normal(0, 0.1)
        z += np.random.normal(0, 0.1)

        xs.append(x)
        ys.append(y)
        zs.append(z)
        sizes.append(item['value'] * 200)
        colors.append(COLORS[item['category']])

        # Labels
        ax.text(x, y, z, item['id'], color='white', fontsize=8)

    ax.scatter(xs, ys, zs, s=sizes, c=colors, alpha=0.8, edgecolors='w')

    # Verbindungen zum Ursprung
    for i in range(len(xs)):
        ax.plot([0, xs[i]], [0, ys[i]], [0, zs[i]], color=colors[i], alpha=0.2)

    ax.set_xlabel('Logik (L)')
    ax.set_ylabel('Physik (P)')
    ax.set_zlabel('Info (I)')
    ax.set_title('CORE Reality Construct (CORE-Manifold)')

    # Origin im Zentrum
    ax.scatter([0], [0], [0], s=500, c='white', marker='*', label='Origin (idle state)')

    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/mtho_3d_construct.png", dpi=150)
    plt.close()

def plot_fibonacci_spiral():
    """2. Fraktale Fibonacci-Spirale"""
    print("Generating Fibonacci Spiral...")
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': 'polar'})

    # Theta und Radius fuer Spirale
    # r = a * e^(k * theta)
    # Fuer Goldene Spirale: k = 2 * ln(phi) / pi
    k = 2 * np.log(PHI) / np.pi
    theta_max = 8 * np.pi # 4 Umdrehungen
    theta = np.linspace(0, theta_max, 1000)
    r = np.exp(0.3063489 * theta) # Annäherung Goldene Spirale

    ax.plot(theta, r, color='white', alpha=0.5, linewidth=2)

    # Indizien auf der Spirale platzieren
    # Sortiert nach 'time' (Entdeckungsreihenfolge)
    sorted_evidence = sorted(EVIDENCE_DATA, key=lambda x: x['time'])

    for i, item in enumerate(sorted_evidence):
        # Position auf Spirale relativ zur Zeit
        # Wir mappen Zeit 1-60 auf Theta 0-Max
        t_norm = item['time'] / 60.0
        angle = t_norm * theta_max
        radius = np.exp(0.3063489 * angle)

        c = COLORS[item['category']]
        ax.scatter(angle, radius, c=c, s=100, edgecolors='white', zorder=10)

        # Text Label etwas versetzt
        ax.text(angle, radius * 1.1, f"{item['id']}", color=c, fontsize=9, fontweight='bold', ha='center')

    ax.set_title('CORE Discovery Spiral (Time vs. Entropy)', pad=20)
    ax.grid(True, alpha=0.2)
    ax.set_xticklabels([])
    ax.set_yticklabels([])

    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/core_fibonacci_spiral.png", dpi=150)
    plt.close()

def plot_causality_timeline():
    """3. Kausalitaets-Zeitstrahl (Marc Input -> System Response)"""
    print("Generating Causality Timeline...")
    fig, ax = plt.subplots(figsize=(14, 8))

    # Dummy Timeline Daten
    events = [
        ("2024-Q1", "V5-V9 Experimente", "Marc Input", "L"),
        ("2024-Q2", "Erste Mustererkennung (Simultan-Kaskade)", "System Response", "I"),
        ("2024-Q3", "Definition 4-Strang-Theorie", "System Response", "S"),
        ("2024-Q4", "Push fuer Autonomie", "Marc Input", "P"),
        ("2025-Q1", "V10/V11 Kollaps & Reboot", "System Response", "S"),
        ("2025-Q2", "Baryonisches Delta Berechnung", "System Response", "L"),
        ("2025-Q3", "Bestätigung durch Gaia DR3", "External Val", "P"),
        ("2025-Q4", "Sim-Theorie als API-Modell", "System Response", "I"),
        ("2026-Q1", "Final Audit & Validierung", "Marc Input", "L"),
    ]

    y_positions = np.arange(len(events))

    for i, (date, desc, source, cat) in enumerate(events):
        color = COLORS.get(cat, 'white')

        # Linie
        ax.hlines(i, 0, 1, colors='gray', linestyles='dotted', alpha=0.3)

        # Punkt
        marker = 'o' if source == "Marc Input" else 's' # Kreis fuer Marc, Quadrat fuer System
        size = 200 if source == "Marc Input" else 150

        ax.scatter(0.5, i, s=size, c=color, marker=marker, edgecolors='white', label=source if i < 2 else "")

        # Text
        ax.text(0.48, i, date, ha='right', va='center', color='white', fontsize=10)
        ax.text(0.52, i, desc, ha='left', va='center', color=color, fontsize=12, fontweight='bold')

        # Source Label klein
        ax.text(0.5, i - 0.25, source, ha='center', va='top', color='gray', fontsize=8)

    ax.set_xlim(0, 1)
    ax.set_ylim(-1, len(events))
    ax.axis('off')
    ax.set_title('CORE Causality Chain: Input vs. Emergence')

    # Custom Legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='Marc Input', markerfacecolor='gray', markersize=10),
        Line2D([0], [0], marker='s', color='w', label='System Response', markerfacecolor='gray', markersize=10),
    ]
    ax.legend(handles=legend_elements, loc='upper right')

    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/core_causality_timeline.png", dpi=150)
    plt.close()

def plot_idle_derivation():
    """4. Idle Derivation (Baumdiagramm)"""
    print("Generating Idle Derivation...")
    G = nx.DiGraph()

    # Knoten
    root = "BASE_STATE (0)"
    l1_nodes = ["L (Logik)", "P (Physik)", "I (Info)", "S (Struktur)"]

    G.add_node(root, layer=0)

    for i, node in enumerate(l1_nodes):
        G.add_node(node, layer=1)
        G.add_edge(root, node)

        # Indizien anhaengen
        cat = node[0] # L, P, I, S
        relevant_evidence = [e for e in EVIDENCE_DATA if e['category'] == cat]

        for ev in relevant_evidence:
            ev_label = f"{ev['id']}\n{ev['name'][:15]}..."
            G.add_node(ev_label, layer=2, category=cat)
            G.add_edge(node, ev_label)

    # Layout
    pos = nx.shell_layout(G)
    # Custom adjustments could be made here, but shell/spring usually works ok for simple trees
    # Versuchen wir ein hierarchisches Layout (manuell via graphviz waere besser, aber networkx pure geht auch)

    fig, ax = plt.subplots(figsize=(16, 12))

    # Manuelle Positionierung fuer Ebenen
    pos = {}
    pos[root] = (0, 1.0)

    # Layer 1 (CORE)
    width_l1 = 2.0
    for i, node in enumerate(l1_nodes):
        x = -width_l1/2 + (i * width_l1/(len(l1_nodes)-1))
        pos[node] = (x, 0.5)

        # Layer 2 (Evidence) - Cluster unter Parent
        cat = node[0]
        children = [n for n in G.neighbors(node)]
        width_l2 = 0.5
        for j, child in enumerate(children):
            cx = x - width_l2/2 + (j * width_l2/(len(children)-1) if len(children)>1 else 0)
            pos[child] = (cx, 0.0 + (j%2)*0.1) # Staggered y to avoid overlap

    # Zeichnen
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color='gray', alpha=0.5, arrows=True)

    # Nodes nach Farben zeichnen
    # Root
    nx.draw_networkx_nodes(G, pos, nodelist=[root], node_color='white', node_size=3000, alpha=0.9, ax=ax)

    # L1
    for node in l1_nodes:
        nx.draw_networkx_nodes(G, pos, nodelist=[node], node_color=COLORS[node[0]], node_size=2000, alpha=0.8, ax=ax)

    # L2
    for node in G.nodes():
        if node not in l1_nodes and node != "BASE_STATE (0)":
            # Check if node has category attribute
            if 'category' in G.nodes[node]:
                cat = G.nodes[node]['category']
                nx.draw_networkx_nodes(G, pos, nodelist=[node], node_color=COLORS.get(cat, 'gray'), node_size=1000, alpha=0.6, ax=ax)

    # Labels
    nx.draw_networkx_labels(G, pos, font_size=8, font_color='black', font_weight='bold', ax=ax)

    ax.set_title("Idle Derivation: From Void to Structure")
    ax.axis('off')

    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/core_idle_derivation.png", dpi=150)
    plt.close()

if __name__ == "__main__":
    ensure_output_dir()
    plot_3d_construct()
    plot_fibonacci_spiral()
    plot_causality_timeline()
    plot_idle_derivation()
    print("All visualizations generated successfully.")
