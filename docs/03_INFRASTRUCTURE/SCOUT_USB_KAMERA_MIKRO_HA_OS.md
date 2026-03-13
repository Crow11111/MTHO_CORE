<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# Scout (Raspi 5 + HA OS): USB-Kamera mit Mikro

**Frage:** Kamera (z. B. 4K mit Mikro) per USB am Scout (Raspi 5, Home Assistant OS) – geht das? Scout soll sehen und hören können.

---

## Antwort: Ja, unter Bedingungen

### Kamera (Video)
- **HA OS** erkennt UVC-USB-Kameras typisch als `/dev/video0`.
- **In HA nutzbar über:**
  - **FFmpeg:** Kamera-Integration mit Eingabe `/dev/video0` (oder passendem Device).
  - **MotionEye-Add-on:** USB-Kamera als „Local V4L2 Camera“ wählen, Stream dann in HA z. B. über Generic Camera.
- Raspi 5 reicht für 4K, ggf. Auflösung/Framerate reduzieren wenn Last hoch ist.

### Mikro (Audio)
- **HA OS** unterstützt USB-Audio (Mikros) z. B. für **Assist**, **Whisper**, **Piper** (Add-ons).
- **Wichtig:** Ob die **Kamera** Audio liefert, hängt vom Gerät ab:
  - Viele USB-Kameras liefern nur Video (UVC), **kein** Audio.
  - Liefert die Kamera Audio (UAC), erscheint unter Linux ein separates Sound-Device (z. B. in `arecord -l`). Dann kann ein Add-on oder Skript es nutzen.
- Wenn die Kamera **kein** USB-Audio hat: separates USB-Mikro am Raspi (mit Adapter falls nur USB-C) oder Kamera mit Mikro wählen, die UAC unterstützt.

### Praktisch
1. **Stecker umstecken** (Kamera an Raspi 5).
2. In HA: unter **Einstellungen → System → Hardware** prüfen, ob ein neues Gerät (Video/Audio) erscheint.
3. **Kamera:** Integration hinzufügen (FFmpeg mit `/dev/video0` oder MotionEye).
4. **Mikro:** Wenn ein Audio-Gerät sichtbar ist → z. B. Assist/Whisper konfigurieren oder eigenes Skript; wenn nicht → Kamera liefert kein Audio, dann separates Mikro nötig.

---

## Referenz
- HA OS 12+: Raspi 5 offiziell unterstützt.
- USB-Mikro: z. B. [Community: How to check microphone locally on Rpi5](https://community.home-assistant.io/t/how-to-check-microphone-localy-on-rpi5/697467).
- USB-Kamera: FFmpeg-Integration, MotionEye-Add-on (z. B. `issacg/motioneye-addon`).
