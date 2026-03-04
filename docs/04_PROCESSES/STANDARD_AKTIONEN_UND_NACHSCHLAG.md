# Standard-Aktionen: Wo nachschauen, wie es gemacht wird

**Zweck:** Etablierte Wege zentral nachschlagbar. Kein Ad-hoc-Umbau (z. B. SSH/VPS), wenn ein Versuch fehlschlägt – zuerst Nachschlagen, ggf. erneuter Versuch (Takt 0).

---

## 1. VPS / SSH / Tunnel

| Aktion | Wo nachschauen | Skript / Befehl |
|--------|----------------|------------------|
| VPS erreichen (Ping/Port) | `docs/03_INFRASTRUCTURE/VPS_FULL_STACK_SETUP.md`, `docs/03_INFRASTRUCTURE/VPS_IP_MONITORING.md` | `Test-NetConnection -ComputerName $VPS_HOST -Port 22` |
| **IP-Wechsel prüfen** | `docs/03_INFRASTRUCTURE/VPS_IP_MONITORING.md` | **Bei Timeout: Hostinger Panel → VPS → IP prüfen.** IP kann sich ändern. |
| SSH-Tunnel zu VPS (Chroma/Sync) | `docs/04_PROCESSES/VPS_SYNC_CORE_DIRECTIVES.md` | Tunnel: `ssh -L 8001:127.0.0.1:8000 root@<VPS_HOST> -N`. Sync: `python -m src.scripts.run_vps_sync_with_tunnel` |
| Sync core_directives (manuell) | `docs/04_PROCESSES/VPS_SYNC_CORE_DIRECTIVES.md` | CHROMA_VPS_HOST=127.0.0.1, CHROMA_VPS_PORT=8001 → `sync_core_directives_to_vps.py` |
| VPS-Deploy (Container) | `docs/03_INFRASTRUCTURE/VPS_FULL_STACK_SETUP.md` | `python -m src.scripts.deploy_vps_full_stack` (--dry-run zuerst) |
| .env für VPS/SSH | `.env.template`, `docs/03_INFRASTRUCTURE/` | VPS_HOST, VPS_USER, VPS_PASSWORD oder VPS_SSH_KEY; CHROMA_* für Sync |

**Regel:** Bei "Connection refused" oder Timeout: Nicht sofort SSH/Tunnel/Netz umbauen. Erst: Takt 0 (erneuter Test, 1–2 s Wartezeit, **IP-Wechsel prüfen**, Port/Service auf Zielseite prüfen). Siehe `docs/04_PROCESSES/TAKT_0_VOR_DELEGATION.md`.

---

## 2. Home Assistant / TTS / Minis

| Aktion | Wo nachschauen | Skript / Hinweis |
|--------|----------------|------------------|
| TTS auf Media-Player (z. B. Mini) | `src/scripts/play_sound_schreibtisch.py`, `src/connectors/home_assistant.py` | HA: `tts.google_translate_say` oder `tts.cloud_say`, entity_id aus .env (z. B. media_player.schreibtisch) |
| Audio-Bestätigung "Fertig" (Minis) | `src/scripts/play_tts_confirmation.py` | `python -m src.scripts.play_tts_confirmation`. Entity: TTS_CONFIRMATION_ENTITY (Default: media_player.schreibtisch). Für mehrere Minis: in HA Gruppe anlegen (z. B. group.minis) und als Entity setzen. |
| HA-URL/Token | `.env` | HASS_URL/HA_URL, HASS_TOKEN/HA_TOKEN |
| Zertifikat/IP/AdGuard (Fritzbox, HA) | `docs/03_INFRASTRUCTURE/FRITZBOX_ADGUARD_ZERTIFIKAT.md` | Fritzbox 192.168.178.1; IP-Wechsel prüfen; AdGuard-Clients; Zertifikat nach IP-Änderung |
| Media-Player-Liste | `src/scripts/list_media_players.py` | Zum Finden der richtigen Entity für Minis/Gruppen |

---

## 3. ChromaDB / Abgleich

| Aktion | Wo nachschauen | Skript / Hinweis |
|--------|----------------|------------------|
| Lokale ChromaDB (core_directives) | `src/network/chroma_client.py`, `docs/04_PROCESSES/VPS_SYNC_CORE_DIRECTIVES.md` | CHROMA_LOCAL_PATH; CHROMA_HOST leer = lokal |
| Abgleich VPS vs. Dreadnought | `docs/05_AUDIT_PLANNING/VERGLEICHSDOKUMENT_OC_BRAIN_VS_DREADNOUGHT.md` | `check_oc_brain_chroma_abgleich.py` (mit Tunnel/CHROMA_HOST) |
| Gravitations-Axiome hinzufügen | `src/scripts/add_gravitational_axioms_to_chroma.py` | Lokal ausführen; für VPS danach Sync nutzen |

---

## 4. Backend / Dienste starten

| Aktion | Wo nachschauen | Skript / Hinweis |
|--------|----------------|------------------|
| ATLAS-Dienste starten | Projektroot: `START_ATLAS_DIENSTE.bat` | Backend 8000, Dashboard 8501, Voice-Info 8502; bei Fehler: Fenster bleibt mit Pause offen (Fehlermeldung lesen) |
| Komplett (inkl. MX-Snapshot) | `START_ATLAS_KOMPLETT.bat` | Ruft START_ATLAS_DIENSTE.bat auf |

---

## 5. Kritische Änderungen (Umbau)

Änderungen an **geschützten Modulen** (SSH, Auth, Chroma-Client, HA-Connector, VPS-Skripte, .env-Handling, Core-API) erfordern **interne Freigabe** durch den Code-Sicherheitsrat. Siehe `docs/04_PROCESSES/CODE_SICHERHEITSRAT.md` und `.cursor/rules/code_sicherheitsrat.mdc`.

---

**Stand:** 2026-03. Bei neuen Standard-Aktionen: Eintrag hier ergänzen, Verweis in .cursorrules oder Takt-0-Regel setzen.
