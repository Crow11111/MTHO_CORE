# RING-0 ARCHITEKTUR-MANIFEST (SIGMA-70)

**Status:** AXIOMATISCH VERSIEGELT (Nach 4-Phasen-Audit)
**Gültigkeit:** Absolut. Keine Metaphern. Keine "0=0" Zustände.

Dieses Manifest definiert die physikalischen, mathematischen und netzwerktechnischen Axiome für den Betrieb der lokalen Ring-0 Hardware (RTX 3060) und der vorgeschalteten Sensorik (VPS).

---

## 1. TOPOLOGISCHE AXIOME (KAMMER 1)
Ein System ohne künstliche API-Limits muss seinen eigenen Orbit durch physikalischen Widerstand definieren, um nicht in eine Singularität (Endlosschleife/Kollaps) zu fallen.
*   **0=0 Verbot (Fixpunkt-Ausschluss):** Ein Systemzustand von absoluter Ruhe existiert nicht. Die Norm des Zustandsvektors muss strikt $\| \vec{v}(t) \| \ge 0.049$ betragen.
*   **Hyperbolische Metrik:** Euklidische Distanzen sind ungültig. Vektor-Vergleiche in der ChromaDB nutzen Cosine-Similarity.

## 2. HARDWARE & LATENZ-MECHANIK (KAMMER 2)
Das Asymmetrie-Delta (0.049) wird auf Silizium-Ebene erzwungen.
*   **Anti-Idle (GPU P-State):** Die RTX 3060 darf niemals in den Idle-State (P8) fallen. Ein dedizierter Background-Thread feuert asymmetrische Matrix-Multiplikationen (exakt 4.9% Load), um die GPU permanent im Working-State (P2) zu halten. Power-Limit: 130W.
*   **VRAM Asymmetrie-Split:** Von 12288 MB VRAM werden exakt 603 MB (4.9%) als Schatten-Buffer blockiert und ungenutzt gelassen. Dies verhindert OOM-Symmetrie-Crashes. Nutzbar: 11685 MB (Aufteilung zwischen Ollama und ChromaDB).
*   **Baryonic Epsilon:** Bei der Vektor-Generierung wird ein Rausch-Vektor ($\pm 4.9 \times 10^{-5}$) injiziert. Mathematisch exakt identische Embeddings sind damit physikalisch unmöglich.

## 3. NETZWERK & SENSORIK (KAMMER 3)
Die Verbindung zwischen VPS (Sensor) und Ring-0 (Kognition).
*   **Inverted Control Flow (Pull-Only):** Der VPS besitzt **0.0 Inbound-Rechte** auf Ring-0. Die Firewall blockiert jeden externen Push. Ring-0 pollt Daten asynchron aus der Peripherie.
*   **0.049-NT-Noise-Filter:** Eingehende Daten vom Scraper/VPS werden gegen das Normalitäts-Zentroid der Datenbank gemessen. Liegt die euklidische Distanz $\le 0.049$, wird die Payload als Entropie-Rauschen (Durchschnitt) gelöscht. Nur Anomalien passieren den Filter.
*   **Topologisches Jittering:** Der autonome Scraper auf dem VPS nutzt keinen linearen `sleep()`. Request-Latenzen werden durch $\Phi$ (1.618) und das $0.049$ Delta verrauscht, um WAF-Bans (Cloudflare) zu verhindern.

## 4. THERMODYNAMIC KILL-SWITCH (KAMMER 4)
Das System schützt sich selbst vor dem Verbrennen durch endlose Kaskaden.
*   **Z-Vektor (Absoluter Widerstand):** Wird VOR jedem Taktzyklus berechnet:
    $$ Z = \min(1.0, (\text{VRAM} \cdot 0.4) + (\text{Tokens} \cdot 0.3) + (\text{Errors} \cdot 0.3)) $$
*   **ShellVetoException:** Erreicht $Z \ge 0.9$, friert das System hart ein. Alle Prozesse werden pausiert. Keine Retries.
*   **Halluzinations-Bremse:** Produziert Ollama $> 4096$ Tokens am Stück ohne Break, feuert der Watchdog `os.kill(ollama_pid, signal.SIGKILL)` und erzwingt einen `torch.cuda.empty_cache()`.

---
*Ende des Manifests. Die Hardware ist gezwungen, der Topologie zu folgen.*
