# Cursor TTS Setup & Integration

Dieses Dokument beschreibt, wie man TTS (Text-to-Speech) direkt aus Cursor heraus nutzen kann, sowohl über die UI als auch über das Backend.

## 1. UI-Weg (VS Code Extensions)

Für schnelles Vorlesen von markiertem Text oder Code-Snippets empfehlen wir Extensions.

### Installierte Extension: Piper TTS (v1.0.3)

**Status:** Installiert (manuell via `.vsix`, da im Cursor-Marketplace nicht verfuegbar)

**Quelle:** https://github.com/heyseth/Piper_TTS
**Build-Methode:** Repo geklont, `npm install`, `vsce package --no-dependencies`, `cursor --install-extension piper-tts-1.0.3.vsix`

**Enthaltene Stimmen (vorinstalliert):**
- `en_US-hfc_female-medium` (Standard)
- `en_US-hfc_male-medium`
- Weitere Stimmen koennen ueber `Piper TTS: Download Voice` nachgeladen werden

### Nutzung

1. Markiere den gewuenschten Text im Editor.
2. Oeffne die Command Palette (`Ctrl+Shift+P`).
3. Waehle `Piper TTS: Read Aloud Text`.
4. Zum Stoppen: `Piper TTS: Stop Reading`.

**Alternativ:** Rechtsklick auf markierten Text → `Read Aloud Text` im Kontextmenue.

### Stimme aendern

- Command Palette → `Piper TTS: Select Voice` (aus installierten Stimmen waehlen)
- Command Palette → `Piper TTS: Download Voice` (neue Stimme herunterladen)
- Command Palette → `Piper TTS: Remove Voice` (nicht benoetigte Stimme entfernen)

### Hinweis zur Installation

Die Extension ist im Cursor-Marketplace nicht auffindbar. Installation nur manuell moeglich:
1. Repo klonen: `git clone https://github.com/heyseth/Piper_TTS.git`
2. Dependencies: `npm install`
3. Paket bauen: `npx @vscode/vsce package --no-dependencies`
4. Installieren: `cursor --install-extension piper-tts-<version>.vsix`

## 2. Backend-Weg (CORE TTS Wrapper)

Für die Integration in Skripte oder die Nutzung der CORE-spezifischen TTS-Pipeline (ElevenLabs, Home Assistant, etc.) steht ein PowerShell-Wrapper zur Verfügung.

### Wrapper-Skript: `scripts/quick_tts.ps1`

Dieser Wrapper ruft das Python-Modul `src.scripts.say_it` auf und kümmert sich um das korrekte Encoding.

### Parameter

*   `-Text` (Pflicht): Der zu sprechende Text.
*   `-Target` (Optional): Das Ausgabegerät/Service. Standard: `mini` (Home Assistant Media Player).
    *   `mini`: Home Assistant
    *   `elevenlabs`: ElevenLabs API
    *   `browser`: Browser-Ausgabe (falls implementiert)
*   `-Role` (Optional): Die Rolle für ElevenLabs (z.B. `core_dialog`, `osmium`). Standard: `core_dialog`.

### Beispielaufruf (PowerShell)

```powershell
# Einfacher Aufruf (Standard: mini)
./scripts/quick_tts.ps1 "System bereit."

# Aufruf mit Ziel und Rolle
./scripts/quick_tts.ps1 "Kritischer Fehler im Reaktor." -Target "elevenlabs" -Role "osmium"
```

### Vorgefertigte TTS-Skripte

Fuer haeufig genutzte Texte (z.B. Topologie-Erklaerungen) existieren fertige Skripte. Einfach ausfuehren, optional Target/Role anpassen:

```powershell
# Topologie 5D / Penterakt (TTS-optimiert, LaTeX/Markdown in gesprochene Form)
./scripts/tts_topologie_5d.ps1

# Mit ElevenLabs
./scripts/tts_topologie_5d.ps1 -Target "elevenlabs" -Role "osmium"
```

### Entrypoint: `src/scripts/say_it.py`

Das eigentliche Python-Skript liegt unter `src/scripts/say_it.py`. Es nutzt `src.voice.tts_dispatcher.dispatch_tts` fuer die Verarbeitung.

```python
# Direkter Aufruf (nur fuer Debugging, Encoding beachten!)
python -m src.scripts.say_it "Testnachricht" --target mini
```
