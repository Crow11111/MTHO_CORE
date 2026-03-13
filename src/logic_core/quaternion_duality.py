# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
CORE Rotation Phasenverschiebungs-Modul (V12+)

Implementiert die zyklische Rotation zwischen CORE- und rotierter Codierung.
CORE -> ROTATED: Jede Base rotiert um +1 Position im Zyklus O->M->T->H->O.
ROTATED -> CORE: Inverse Rotation (-1).

Die Dualitaet entspricht dem Verhaeltnis von Sense-Strang und Antisense-Strang
in der DNS – derselbe Informationsgehalt, aber phasenverschoben gelesen.
"""
from __future__ import annotations
from src.core import M_VALUE, T_VALUE, H_VALUE, O_VALUE


#  legacy removed
ROT_FORWARD: dict[str, str] = {"O": "M", "M": "T", "T": "H", "H": "O"}

ROT_BACKWARD: dict[str, str] = {"M": "O", "T": "M", "H": "T", "O": "H"}

_VALID_BASES = frozenset("CORE")


def _validate_sequence(sequence: str) -> str:
    seq = sequence.upper().replace(" ", "")
    invalid = [c for c in seq if c not in _VALID_BASES]
    if invalid:
        raise ValueError(f"Ungueltiges Zeichen in Sequenz: {invalid}. Nur M/T/H/O erlaubt.")
    return seq


def rotate_forward(sequence: str) -> str:
    """Konvertiert eine CORE-Sequenz in rotierter Codierung (zyklische Rotation +1).

    >>> rotate_forward("CORE")
    'ROTATED'
    >>> rotate_forward("LLLL")
    'PPPP'
    """
    seq = _validate_sequence(sequence)
    return "".join(ROT_FORWARD[c] for c in seq)


def rotate_backward(sequence: str) -> str:
    """Konvertiert eine rotierte Sequenz zurueck in CORE-Codierung (inverse Rotation).

    >>> rotate_backward("ROTATED")
    'CORE'
    >>> rotate_backward(rotate_forward("LSIP"))
    'LSIP'
    """
    seq = _validate_sequence(sequence)
    return "".join(ROT_BACKWARD[c] for c in seq)


def compute_phase_shift(seq_a: str, seq_b: str) -> int:
    """Berechnet die minimale zyklische Phasenverschiebung zwischen zwei Sequenzen.

    Probiert 0-3 Rotationen durch und gibt die Anzahl der Rotationen zurueck,
    bei der seq_a in seq_b transformiert wird. -1 falls keine Rotation passt.

    >>> compute_phase_shift("CORE", "ROTATED")
    1
    >>> compute_phase_shift("CORE", "CORE")
    0
    >>> compute_phase_shift("CORE", "ISLP")
    2
    """
    a = _validate_sequence(seq_a)
    b = _validate_sequence(seq_b)

    if len(a) != len(b):
        return -1

    current = a
    for shift in range(4):
        if current == b:
            return shift
        current = "".join(ROT_FORWARD[c] for c in current)

    return -1


def hm_stability_check(sequence: str) -> dict:
    """Prueft H-M Abstaende in der Sequenz auf Stabilitaet.

    In einer stabilen Erkenntnisspirale sollte der Abstand zwischen
    H- und M-Basen (Komplementpaare) moeglichst konstant sein.

    Returns:
        {"h_positions": list, "m_positions": list, "hm_distances": list,
         "mean_distance": float, "variance": float, "stable": bool}
    """
    seq = _validate_sequence(sequence)

    h_pos = [i for i, c in enumerate(seq) if c == "H"]
    m_pos = [i for i, c in enumerate(seq) if c == "M"]

    if not h_pos or not m_pos:
        return {
            "h_positions": h_pos,
            "m_positions": m_pos,
            "hm_distances": [],
            "mean_distance": 0.0,
            "variance": 0.0,
            "stable": len(seq) < 2,
        }

    distances = []
    for s in h_pos:
        nearest_p = min(m_pos, key=lambda p: abs(p - s))
        distances.append(abs(nearest_p - s))

    mean_dist = sum(distances) / len(distances) if distances else 0.0
    variance = (
        sum((d - mean_dist) ** 2 for d in distances) / len(distances)
        if distances
        else 0.0
    )

    return {
        "h_positions": h_pos,
        "m_positions": m_pos,
        "hm_distances": distances,
        "mean_distance": round(mean_dist, 4),
        "variance": round(variance, 4),
        "stable": variance < 2.0,
    }


def ot_direction_analysis(sequence: str) -> dict:
    """Analysiert O-T Richtungswechsel in der Sequenz.

    Zaehlt wie oft die Sequenz zwischen L und I wechselt. Haeufige Wechsel
    deuten auf starke Logik-Information-Interaktion hin (analoog zu
    Transkriptionsfaktor-Bindungsstellen in der DNS).

    Returns:
        {"o_count": int, "t_count": int, "transitions_o_to_t": int,
         "transitions_t_to_o": int, "total_transitions": int,
         "transition_density": float}
    """
    seq = _validate_sequence(sequence)

    o_count = seq.count("L")
    t_count = seq.count("I")

    o_to_t = 0
    t_to_o = 0

    for idx in range(len(seq) - 1):
        if seq[idx] == "L" and seq[idx + 1] == "I":
            o_to_t += 1
        elif seq[idx] == "I" and seq[idx + 1] == "L":
            t_to_o += 1

    total = o_to_t + t_to_o
    density = total / (len(seq) - 1) if len(seq) > 1 else 0.0

    return {
        "o_count": o_count,
        "t_count": t_count,
        "transitions_o_to_t": o_to_t,
        "transitions_t_to_o": t_to_o,
        "total_transitions": total,
        "transition_density": round(density, 4),
    }


if __name__ == "__main__":
    print("=" * 60)
    print("[CORE] CORE Rotation Phasenverschiebungs-Modul – Selbsttest")
    print("=" * 60)

    print("\n--- rotate_forward ---")
    for seq in ["CORE", "LLLL", "SIPL", "LSIPL"]:
        print(f"  {seq} -> {rotate_forward(seq)}")

    print("\n--- rotate_backward ---")
    for seq in ["ROTATED", "PPPP", "LISP"]:
        print(f"  {seq} -> {rotate_backward(seq)}")

    print("\n--- Roundtrip ---")
    test = "LSIPLLISPS"
    converted = rotate_forward(test)
    back = rotate_backward(converted)
    print(f"  Original:  {test}")
    print(f"  ROTATED:      {converted}")
    print(f"  Zurueck:   {back}")
    print(f"  Roundtrip: {'OK' if back == test else 'FEHLER'}")

    print("\n--- compute_phase_shift ---")
    for a, b in [("CORE", "ROTATED"), ("CORE", "CORE"), ("CORE", "ISLP"), ("CORE", "SLPI")]:
        print(f"  {a} -> {b}: Shift = {compute_phase_shift(a, b)}")

    print("\n--- hm_stability_check ---")
    sp = hm_stability_check("LSIPLLISPS")
    print(f"  Sequenz: LSIPLLISPS")
    print(f"  S-P Distanzen: {sp['hm_distances']}")
    print(f"  Mittel: {sp['mean_distance']}, Varianz: {sp['variance']}")
    print(f"  Stabil: {sp['stable']}")

    print("\n--- ot_direction_analysis ---")
    li = ot_direction_analysis("LSIPL LISPS")
    print(f"  O->T: {li['transitions_o_to_t']}, T->O: {li['transitions_t_to_o']}")
    print(f"  Dichte: {li['transition_density']}")

    print("\n" + "=" * 60)
    print("[CORE] Phasenverschiebungs-Modul operativ.")
    print("=" * 60)
