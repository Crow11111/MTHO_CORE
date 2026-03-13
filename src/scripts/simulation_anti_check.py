# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
CORE Anti-Check Simulation
Chaos-Mathematiker Modul

Mission: Beweise, dass die CORE-Konvergenz ein statistischer Zufall oder Artefakt der Datenselektion ist.
Testet:
1. Law of Large Numbers (Look-elsewhere effect)
2. Anthropic Principle (Selection Bias)
3. Benford's Law / Zipf's Law (Natural Distribution)
"""

import random
import math
import time
from collections import Counter
import sys

# Konstanten aus CORE
PHI = 1.618033988749895
INV_PHI = 0.618033988749895
CORE_BASES = ["L", "P", "I", "S"]

def log_section(title):
    print(f"\n{'='*60}")
    print(f"RUNNING: {title}")
    print(f"{'='*60}")

def check_look_elsewhere_effect(num_samples=1_000_000, tolerance=0.01):
    """
    Simuliert das Suchen nach 'bedeutungsvollen' Mustern in Rauschen.
    Wir suchen nach Verhältnissen a/b, die nahe an PHI liegen.
    """
    log_section("1. Law of Large Numbers (Look-elsewhere Effect)")
    print(f"Scanning {num_samples} random pairs for PHI pattern (tolerance {tolerance})...")
    
    matches = 0
    start_time = time.time()
    
    # Wir simulieren "Datenpunkte" als Zufallszahlen
    # In der Realität sucht man in Datensätzen nach "irgendeinem" Verhältnis.
    # Hier vereinfacht: Wir ziehen a und b und prüfen a/b.
    
    for _ in range(num_samples):
        # Zufallszahlen zwischen 1 und 1000 (beliebige Skala)
        a = random.uniform(1, 1000)
        b = random.uniform(1, 1000)
        
        if b == 0: continue
        
        ratio = a / b
        if abs(ratio - PHI) < tolerance:
            matches += 1
            
    elapsed = time.time() - start_time
    probability = matches / num_samples
    
    print(f"Found {matches} matches in {num_samples} samples.")
    print(f"Probability of finding PHI by chance: {probability:.6f} ({probability*100:.4f}%)")
    
    # Interpretation: Wenn wir 100 Konstanten haben und 100 mögliche Beziehungen prüfen,
    # haben wir 10.000 Versuche.
    # Wahrscheinlichkeit, dass *mindestens eine* passt: 1 - (1 - p)^10000
    
    num_constants = 50 # Angenommene Anzahl "interessanter" Konstanten in einem System
    num_relations = 50 # Angenommene Anzahl geprüfter Relationen (Verhältnis, Produkt, Differenz...)
    trials = num_constants * num_relations
    
    p_at_least_one = 1 - (1 - probability)**trials
    
    print(f"In a system with {num_constants} constants and {num_relations} relation types:")
    print(f"Probability of finding AT LEAST ONE Phi-match purely by chance: {p_at_least_one:.6f}")
    
    return p_at_least_one

def check_anthropic_principle(num_universes=100_000):
    """
    Simuliert Universen mit zufälligen Parametern.
    Prüft, wie viele "lebensfreundlich" sind.
    """
    log_section("2. Anthropic Principle (Fine-Tuning Check)")
    print(f"Simulating {num_universes} universes with random constants...")
    
    # Vereinfachtes Modell: Ein Universum braucht Parameter in bestimmten Bereichen
    # um "stabile Strukturen" (Leben/Beobachter) zu ermöglichen.
    # Wir definieren 3 Parameter, die "passen" müssen.
    
    # Annahme: "Feinabstimmung" bedeutet, Parameter müssen in einem 10% Fenster liegen.
    target_range = 0.1 
    
    habitable_universes = 0
    
    for _ in range(num_universes):
        # Parameter G (Gravitation), E (Elektromagnetismus), S (Starke Kernkraft)
        # Normalisiert auf [0, 1]. "Unser" Wert ist 0.5.
        G = random.random()
        E = random.random()
        S = random.random()
        
        # Bedingungen für Leben (fiktiv, aber strukturell analog):
        # 1. G darf nicht zu stark (Kollaps) oder zu schwach (keine Sterne) sein
        g_ok = 0.45 < G < 0.55
        
        # 2. E muss Balance zu G haben (Sterne brennen stabil)
        e_ok = 0.45 < E < 0.55
        
        # 3. S muss Kerne zusammenhalten
        s_ok = 0.45 < S < 0.55
        
        if g_ok and e_ok and s_ok:
            habitable_universes += 1
            
    p_habitable = habitable_universes / num_universes
    
    print(f"Habitable universes found: {habitable_universes}")
    print(f"Probability of a random universe being habitable: {p_habitable:.6f}")
    
    if p_habitable == 0:
        print("Selection Bias Warning: Even if P is low, WE are here.")
        return 1.0 # Wenn wir hier sind, ist P(Delusion) hoch, weil wir denken wir sind speziell
    
    # P(Delusion) hier: Die Wahrscheinlichkeit, dass wir denken, das Universum sei FÜR UNS gemacht,
    # obwohl es nur ein Selektionseffekt ist.
    # Dies ist hoch, wenn habitable Universen selten sind (wir fühlen uns speziell).
    
    # Score: Wie sehr "sieht" es nach Design aus? 
    # Je seltener, desto mehr sieht es nach Design aus -> desto höher die Gefahr der Täuschung.
    delusion_score = 1.0 - p_habitable 
    print(f"Anthropic Delusion Score (Inverse Probability): {delusion_score:.6f}")
    
    return delusion_score

def check_benford_zipf(num_data_points=1000):
    """
    Prüft, ob eine Fibonacci-Verteilung durch Zipf's Law erklärt werden kann.
    """
    log_section("3. Benford's Law / Zipf's Law Check")
    
    # 1. Erzeuge eine Zipf-Verteilung (natürliche Verteilung von Worthäufigkeiten etc.)
    # Zipf: Frequenz ~ 1/Rang
    
    print("Generating Zipf-distributed data...")
    ranks = list(range(1, num_data_points + 1))
    frequencies = [1.0 / r for r in ranks]
    
    # Normalisieren
    total = sum(frequencies)
    probs = [f / total for f in frequencies]
    
    # Simulierte "Indizien" Kategorien
    # Wir mappen die häufigsten Kategorien auf unsere CORE-Struktur
    # Wenn CORE Fibonacci nutzt (13, 21, 55...), schauen wir ob Zipf das matcht.
    
    # Fibonacci Anteile (normiert auf Summe ~1):
    # 55, 34, 21, 13, 8...
    fib_sequence = [55, 34, 21, 13, 8, 5, 3, 2, 1]
    fib_sum = sum(fib_sequence)
    fib_dist = [x/fib_sum for x in fib_sequence]
    
    print("Fibonacci Distribution (Target):")
    print([f"{x:.3f}" for x in fib_dist[:5]])
    
    print("Zipf Distribution (Top 5):")
    print([f"{x:.3f}" for x in probs[:5]])
    
    # Berechne Korrelation oder Abstand
    # Wir vergleichen die Top N Ranks
    error_sum = 0
    for i in range(min(len(fib_dist), 5)):
        error_sum += abs(fib_dist[i] - probs[i])
        
    avg_error = error_sum / 5
    print(f"Average deviation between Zipf and Fibonacci: {avg_error:.6f}")
    
    # Wenn die Abweichung klein ist, ist Fibonacci nur ein Spezialfall von Zipf.
    # P(Delusion) ist hoch, wenn Fehler klein ist.
    # Wenn Fehler < 0.05, dann ist es sehr wahrscheinlich Zipf.
    
    delusion_score = max(0, 1.0 - (avg_error * 10)) # Skaliert: 0.1 Error -> 0 Delusion
    print(f"Zipf Delusion Score: {delusion_score:.6f}")
    
    return delusion_score

def main():
    print("Starting CORE Anti-Check Simulation...")
    print("Identity: Chaos-Mathematiker")
    print("-" * 60)
    
    score1 = check_look_elsewhere_effect()
    score2 = check_anthropic_principle()
    score3 = check_benford_zipf()
    
    log_section("FINAL RESULTS")
    
    # Gewichteter Durchschnitt (kann angepasst werden)
    final_p_delusion = (score1 + score2 + score3) / 3
    
    print(f"P(Look-Elsewhere): {score1:.4f}")
    print(f"P(Anthropic-Bias): {score2:.4f}")
    print(f"P(Zipf-Mimicry):   {score3:.4f}")
    print("-" * 30)
    print(f"TOTAL P(Delusion): {final_p_delusion:.4f}")
    print("-" * 30)
    
    if final_p_delusion > 0.8:
        print("CONCLUSION: CORE Convergence is almost certainly a statistical artifact.")
    elif final_p_delusion > 0.5:
        print("CONCLUSION: High probability of confirmation bias / pattern forcing.")
    elif final_p_delusion > 0.2:
        print("CONCLUSION: Ambiguous results. Pattern might be real, but skepticism warranted.")
    else:
        print("CONCLUSION: Patterns are robust against random chance. Converegence might be real.")

if __name__ == "__main__":
    main()
