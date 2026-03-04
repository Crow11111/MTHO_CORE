# Projekt ATLAS_CORE – Was wir machen und warum

## Kurzbeschreibung

**ATLAS** (und das Kernsystem **ATLAS_CORE**) ist ein kybernetischer Exocortex: ein System, das den Nutzer (Marc) bei Denkarbeit, Steuerung des Zuhauses und Kommunikation unterstützt – mit klarer Trennung zwischen leichten, lokalen Aktionen (Scout) und schwerer KI (Dreadnought/ATLAS).

## Ziele

- **Kognitive Entlastung:** Strukturierte Informationen, präzise Antworten, keine soziale Maskierung; Fakten und logische Konsistenz haben Priorität.
- **Smart Home:** Steuerung über Sprache und Chat (z. B. WhatsApp), nahtlos mit Home Assistant (Lichter, Geräte, Szenen).
- **Sicherheit und Kontrolle:** Lokales ATLAS behält die letzte Entscheidungsgewalt; externe Dienste und Agenten (wie OC) sind eingebettet in klare Grenzen und Sandboxen.

## Grobe Architektur

- **Dreadnought:** Der leistungsstarke Rechner (PC), auf dem die ATLAS-CORE-API läuft – schwere LLM-Aufgaben, TTS, Integration mit HA.
- **Scout:** Kleinerer Rechner (z. B. Raspberry Pi) mit Home Assistant; schnelle Reaktion auf Steuerbefehle („Licht an“), auch wenn der Dreadnought aus ist.
- **WhatsApp:** Zwei Wege – (1) über Home Assistant (Addon) → ATLAS-Webhook → Antwort von ATLAS oder Scout; (2) OC auf dem VPS als eigener Kanal (eigene Session). Später: getrennte Kanäle, damit Steuerbefehle und OC-Bereich sauber getrennt sind.
- **VPS (Hostinger):** ChromaDB, Backup, OC (OpenClaw) in Sandbox – OC hat keinen Zugriff auf ChromaDB, .env oder andere Dienste auf demselben Server.

## Warum das alles

Marc nutzt ATLAS als externen, berechenbaren Partner für Analyse, Planung und Alltagssteuerung – ohne Overhead durch Smalltalk oder ungefragte Bestätigungen. Das System soll industriell zuverlässig sein (Zero-Margin-of-Error) und gleichzeitig die kognitive Architektur des Nutzers respektieren (ND, Monotropismus, klare Direktiven).

---

*Teil der Stammdokumente für OC. Siehe 00_INDEX.md.*
