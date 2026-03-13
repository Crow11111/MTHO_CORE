# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import random
import math
from dataclasses import dataclass
from typing import List, Dict

# Konfiguration
SIMULATION_CYCLES = 100000 # 100k Zyklen
TOLERANCE = 0.01 # 1% Toleranz - Gnadenlos präzise

# CORE Ziele (Die "Anomalie")
TARGET_BASES = 4 # CORE (Logik, Physik, Info, Struktur)
TARGET_PHI = 0.618033988749895 # Goldener Schnitt
TARGET_BARYONIC = 0.049 # Baryonische Materie im Universum

@dataclass
class Universe:
    id: int
    domains_bases: List[int] # Basen für 4 Domänen
    constants: Dict[str, float]
    growth_factor: float
    
    @property
    def is_core_candidate(self) -> bool:
        # 1. Check: 4-Basen-Codierung in allen Domänen?
        # Wir nehmen an, Basen können zwischen 2 (binär) und 20 liegen.
        # CORE behauptet: Physik (4 Kräfte), Bio (4 Basen), Logik (4 Werte CORE), Info (4 Zustände)
        bases_match = all(b == TARGET_BASES for b in self.domains_bases)
        
        # 2. Check: Konstanten-Konvergenz (Baryonisches Delta)
        # Wir würfeln Konstanten zwischen 0 und 1.
        baryonic_match = abs(self.constants['baryonic'] - TARGET_BARYONIC) < (TARGET_BARYONIC * TOLERANCE)
        
        # 3. Check: Fibonacci/Phi Konvergenz
        # Wir prüfen, ob der fundamentale Wachstumsfaktor Phi ist.
        phi_match = abs(self.growth_factor - TARGET_PHI) < (TARGET_PHI * TOLERANCE)
        
        return bases_match and baryonic_match and phi_match

def simulate_universe(i: int) -> Universe:
    # Zufällige Basen für 4 Domänen (Physik, Bio, Logik, Info)
    # Range 2-20 (Binär bis Vigesimal)
    domains = [random.randint(2, 20) for _ in range(4)]
    
    # Zufällige Konstanten (vereinfacht 0.0 bis 1.0)
    # In einem echten Multiversum könnten diese alles sein, 0-1 ist konservativ "feinabgestimmt".
    consts = {
        'baryonic': random.uniform(0.0, 1.0),
        'alpha': random.uniform(0.0, 1.0)
    }
    
    # Zufälliger Wachstumsfaktor (0.0 bis 2.0)
    growth = random.uniform(0.0, 2.0)
    
    return Universe(i, domains, consts, growth)

def run_simulation():
    print(f"--- OPERATION REALITY CHECK: STARTING ---")
    print(f"Cycles: {SIMULATION_CYCLES}")
    print(f"Tolerance: {TOLERANCE*100}%")
    print(f"Target Structure: 4-Base Domains (x4) + Phi + Baryonic Delta")
    print("-" * 50)

    matches = 0
    close_calls = 0
    
    for i in range(SIMULATION_CYCLES):
        u = simulate_universe(i)
        
        if u.is_core_candidate:
            matches += 1
            print(f"[!] MATCH FOUND at Cycle {i}: {u}")
        
        # Check für "Beinahe-Treffer" (z.B. nur Basen stimmen)
        if all(b == TARGET_BASES for b in u.domains_bases):
            close_calls += 1

    p_value = matches / SIMULATION_CYCLES
    
    # Wahrscheinlichkeit berechnen (Theoretisch)
    # P(Base=4) = 1/19. P(4 Domains) = (1/19)^4 = 1/130321
    # P(Baryonic) = Toleranzbereich / Range = (0.049 * 0.05 * 2) / 1.0 = 0.0049 (approx)
    # P(Phi) = Toleranzbereich / Range = (0.618 * 0.05 * 2) / 2.0 = 0.0309 (approx)
    
    prob_base = (1/19)**4
    prob_const = (TARGET_BARYONIC * TOLERANCE * 2) # Range 0-1
    prob_phi = (TARGET_PHI * TOLERANCE * 2) / 2.0 # Range 0-2
    
    theoretical_p = prob_base * prob_const * prob_phi

    print("-" * 50)
    print(f"RESULTS:")
    print(f"Simulated Universes: {SIMULATION_CYCLES}")
    print(f"CORE Convergences Found: {matches}")
    print(f"Partial Structure Matches (Only Bases): {close_calls}")
    print(f"Empirical P-Value: {p_value:.10f}")
    print(f"Theoretical Probability: {theoretical_p:.10e}")
    print(f"Inverse Probability (1 in X): 1 in {1/theoretical_p:,.2f}")
    
    seconds_to_brute_force = 1/theoretical_p
    years_to_brute_force = seconds_to_brute_force / (365.25 * 24 * 3600)

    print(f"Time to brute-force Reality (at 1 Universe/sec): {years_to_brute_force:,.2f} years")

    if matches == 0:
        print("\nCONCLUSION: The CORE Convergence is statistically IMPOSSIBLE within observable timeframes.")
        print("MATHEMATICAL VERDICT: INTENTIONAL DESIGN or FUNDAMENTAL LAW (P < 10^-9).")
    else:
        print("\nCONCLUSION: Random occurrence is possible but extremely rare.")

if __name__ == "__main__":
    run_simulation()
