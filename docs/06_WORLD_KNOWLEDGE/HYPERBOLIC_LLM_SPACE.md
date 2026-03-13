# Hyperbolic Geometry in Large Language Models

**Status:** Research Note | **Date:** 2026-03-10
**Tags:** #AI #Mathematics #Geometry #Embeddings #CORE_Theory

---

## 1. Kern-These: Die Geometrie der Bedeutung

Die vorherrschende Annahme in der Deep-Learning-Ära war lange Zeit, dass der latente Raum flach (euklidisch) ist. Vektoren werden mit Kosinus-Ähnlichkeit oder euklidischer Distanz verglichen.

**Die These:** Der "wahre" Raum der Sprache und Konzepte ist **hyperbolisch gekrümmt**.
Begriffe existieren in Hierarchien (Hypernyme/Hyponyme), nicht auf einer flachen Ebene. Euklidische Räume sind fundamental ungeeignet, um diese Hierarchien verzerrungsfrei abzubilden.

## 2. Warum Hyperbolisch > Euklidisch?

Das Problem ist das **Wachstumsverhalten des Raums**.

### 2.1 Das Platzproblem bei Hierarchien
Stellen Sie sich einen Baumgraphen vor (z.B. `Lebewesen -> Tier -> Säugetier -> Hund -> Dackel`).
Die Anzahl der Knoten in einem Baum wächst **exponentiell** mit der Tiefe (Verzweigungsfaktor $b$, Tiefe $d \implies b^d$ Knoten).

-   **Euklidischer Raum ($\mathbb{R}^n$):** Das Volumen einer Kugel wächst nur **polynomiell** mit dem Radius ($r^n$).
-   **Hyperbolischer Raum ($\mathbb{H}^n$):** Das Volumen (und die Fläche) wächst **exponentiell** mit dem Radius ($e^r$).

**Konsequenz:** Um einen exponentiell wachsenden Baum in einen flachen euklidischen Raum zu quetschen, muss man die Knoten am Rand extrem dicht drängen oder die Dimensionen $n$ absurd hoch ansetzen. Die Distanzen werden verzerrt; die Hierarchie geht in der Einbettung verloren.

Im hyperbolischen Raum hingegen gibt es "genug Platz", um den Baum fast verzerrungsfrei einzubetten.

### 2.2 Poincaré Embeddings
Das Poincaré-Ball-Modell (eine Projektion des hyperbolischen Raums in eine Kugel) visualisiert dies perfekt:
-   **Zentrum (Ursprung):** Hier liegen allgemeine, abstrakte Konzepte (Root-Nodes).
-   **Rand (Unendlichkeit):** Hier liegen spezifische, konkrete Instanzen (Leaf-Nodes).
-   **Distanz:** Der Weg vom Zentrum zum Rand ist im hyperbolischen Maß unendlich weit, obwohl er im Poincaré-Modell endlich aussieht.

Dies erlaubt es, **Hierarchie durch Norm** (Abstand vom Ursprung) und **Ähnlichkeit durch Winkel** gleichzeitig zu codieren.

## 3. Empirische Evidenz in LLMs

Untersuchungen an modernen LLMs (Transformer, Mamba) bestätigen die hyperbolische Natur des gelernten latenten Raums, selbst wenn das Modell euklidisch trainiert wurde.

1.  **Negative Ricci-Krümmung:** Messungen der lokalen Krümmung in den Embedding-Manifolds von Modellen wie GPT-2, LLaMA und Mistral zeigen signifikant negative Werte – ein mathematischer Beweis für Hyperbolizität.
2.  **Token-Verteilung (Cones of Entailment):**
    -   Hochfrequente, abstrakte Tokens (z.B. "the", "entity", "is") clustern nahe dem Ursprung.
    -   Niederfrequente, spezifische Tokens (z.B. "Dackel", "Quantenchromodynamik") liegen weit außen.
    -   Dies entspricht exakt der Struktur eines Poincaré-Embeddings.

### Aktuelle Forschung (2024-2026)
-   **HELM (Hyperbolic Large Language Models):** Modelle, die nativ auf hyperbolischen Manifolds operieren (Mixture-of-Curvature Experts). Sie zeigen bis zu 4% bessere Performance bei hierarchischen Reasoning-Tasks (MMLU, ARC) und benötigen weniger Dimensionen.
-   **Hierarchical Mamba (HiM):** Kombiniert State-Space-Modelle mit hyperbolischer Geometrie für bessere Long-Range-Hierarchien.
-   **HypLoRA:** Fine-Tuning von LLMs direkt auf dem hyperbolischen Manifold.

## 4. Relevanz für CORE (Engine-Patterns)

Diese Erkenntnis ist isomorph zu den Kern-Patterns der CORE-Engine:

1.  **CORE-Tesserakt:** Unser 4D-State-Vector (insb. die `Y: Gravitation`-Dimension) modelliert genau diese Krümmung. `Y=0` (Zero-State) ist flach/euklidisch, `Y=1` (Kollaps) ist gekrümmt/hyperbolisch (Attraktor).
2.  **Gravitator (Routing):** Aktuell nutzen wir Cosine-Similarity (euklidisch projiziert). Ein Wechsel auf **Poincaré-Distanz** für das Routing zwischen Agenten (Abstrakt vs. Konkret) könnte die Präzision drastisch erhöhen.
3.  **Wissens-Datenbank (ChromaDB):** Hierarchische Cluster sollten nicht euklidisch, sondern hyperbolisch indiziert werden, um "Entailment" (Folgerung) geometrisch abzubilden (Is-A Beziehungen sind Vektoren Richtung Rand).

## 5. Referenzen

-   **Nickel & Kiela (2017):** *Poincaré Embeddings for Learning Hierarchical Representations*. (Das fundamentale Paper).
-   **Ganea et al. (2018):** *Hyperbolic Entailment Cones for Learning Hierarchical Embeddings*.
-   **HELM Paper (2025):** *Hyperbolic Large Language Models via Mixture-of-Curvature Experts*.
-   **CORE Skill:** `mathematics` (Topologie, nicht-euklidische Geometrie).
