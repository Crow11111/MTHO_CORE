"""
Sendet Kontext (was/warum/wer/wie) und die offenen Punkte an OC über den direkten Kanal.

- Mit --with-context (Standard): Zuerst eine Nachricht mit dem Stammdokumente-Kontext
  (Projekt, Marc, Team, deine Rolle), dann die offenen Punkte. So hat OC das Material,
  auch wenn die Stammdokumente noch nicht auf dem VPS liegen.
- Ohne --with-context: Nur die offenen Punkte (wie bisher).

Voraussetzung: OpenClaw Gateway mit gateway.http.endpoints.responses.enabled: true
(siehe setup_vps_hostinger.py). Bei 405: Config auf VPS anpassen, Container neu starten.

Aufruf:
  python -m src.scripts.send_offene_punkte_to_oc
  python -m src.scripts.send_offene_punkte_to_oc --no-context
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from src.network.openclaw_client import send_message_to_agent, is_configured

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DOC_OFFENE = os.path.join(PROJECT_ROOT, "docs", "oc_diskussion_offene_punkte.md")
STAMM_DIR = os.path.join(PROJECT_ROOT, "docs", "stammdokumente_oc")


def _read_stammdokumente_compact() -> str:
    """Kompakte Version von was/warum/wer/wie aus den Stammdokumenten."""
    parts = []
    for name in ["01_PROJEKT_ATLAS.md", "02_MARC_UND_TEAM.md", "03_OC_ROLLE_UND_GRENZEN.md"]:
        path = os.path.join(STAMM_DIR, name)
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                parts.append(f.read())
    return "\n\n---\n\n".join(parts) if parts else ""


def main() -> int:
    with_context = "--no-context" not in sys.argv

    if not is_configured():
        print("Nicht konfiguriert (VPS_HOST, OPENCLAW_GATEWAY_TOKEN in .env).")
        return 1

    if with_context:
        context = _read_stammdokumente_compact()
        if context:
            msg1 = (
                "Kontext für dich (was / warum / wer / wie):\n\n"
                "Du hast diese Infos, damit du das Projekt und deine Rolle kennst. "
                "Falls die Stammdokumente schon auf dem Server unter workspace/stammdokumente/ liegen, "
                "dort findest du die gleichen Inhalte ausführlicher.\n\n" + context
            )
            if len(msg1) > 10000:
                msg1 = msg1[:10000] + "\n\n[... gekürzt ...]"
            print("Sende Kontext (was/warum/wer/wie) an OC ...")
            ok1, r1 = send_message_to_agent(msg1, agent_id="main", timeout=180.0)
            print(f"  Kontext: {'OK' if ok1 else 'Fehler'} – {r1[:200] if r1 else ''}")
            if not ok1:
                print("Warnung: Kontext konnte nicht gesendet werden. Sende trotzdem offene Punkte.")
                print("Hinweis: Bei 405 Gateway-Config pruefen responses.enabled; bei Timeout evtl. erneut versuchen.")

    if not os.path.isfile(DOC_OFFENE):
        print(f"Datei nicht gefunden: {DOC_OFFENE}")
        return 1

    with open(DOC_OFFENE, "r", encoding="utf-8") as f:
        text = f.read()
    max_chars = 12000
    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n[... gekürzt ...]"

    prompt = (
        "Das ist die aktuelle Liste offener Punkte aus der ATLAS-Implementierungsplanung, "
        "die wir mit dir besprechen möchten. Bitte lies sie und lege bei Bedarf eine Einreichung "
        "in rat_submissions/ ab (type rat_submission oder info, payload mit topic und body), "
        "mit deinen Vorschlägen oder Priorisierungen. ATLAS holt die Einreichungen ab und bringt sie in den Rat ein.\n\n"
        + text
    )

    print("Sende offene Punkte an OC (Agent 'main') ...")
    ok, response = send_message_to_agent(prompt, agent_id="main", timeout=180.0)
    print(f"Erfolg: {ok}")
    print(f"Antwort: {response[:800] if response else '(leer)'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
