"""
Löst die Abstimmung zum WhatsApp-Plan aus: sendet OC per API eine Nachricht mit der Aufgabe,
Abschnitt 6 (OC-Teil) in WHATSAPP_TRIGGER_UND_ADRESSIERUNG_PLAN.md auszufüllen.

OC erhält die Nachricht im gleichen Kanal wie andere Eingaben (Gateway /v1/responses).
OC soll seine Antwort als rat_submission ablegen (topic z. B. "WhatsApp-Plan Abschnitt 6");
ATLAS holt sie später mit fetch_oc_submissions ab.

Kein SSH nötig – nur OPENCLAW_GATEWAY_TOKEN und VPS_HOST in .env.

Aufruf (aus Projekt-Root):
  python -m src.scripts.trigger_whatsapp_plan_oc
"""
from __future__ import annotations

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

PLAN_DOC = os.path.join(PROJECT_ROOT, "docs", "WHATSAPP_TRIGGER_UND_ADRESSIERUNG_PLAN.md")

# Aufgabe für OC (inkl. Auszug aus dem Plan, damit OC den Kontext hat)
TASK_MESSAGE = """Abstimmung WhatsApp-Plan (Trigger & Adressierung): Bitte fülle deinen Teil in Abschnitt 6 aus.

Kontext: Es geht darum, dass nur bei Trigger (@Atlas/@OC) systemisch geantwortet wird und Nachrichten für Marc privat nicht von Systemen beantwortet werden. ATLAS und Dev-Agent stimmen sich mit dir ab.

Deine Aufgabe (für Abschnitt 6 im Plan-Dokument):
1. Empfohlenes Procedere für „nur richtige Absender / unterschiedliche Nummern“ (z. B. allowFrom, getrennte Nummer, Kombination mit @OC).
2. Ob du aktuell nur Nachrichten „von Marc an Marc“ siehst und wie das mit der Trigger-Regel zusammenspielt.

Bitte lege deine Antwort als Einreichung in rat_submissions/ ab:
- type: "info" oder "rat_submission"
- payload.topic: "WhatsApp-Plan Abschnitt 6"
- payload.body: dein Text (Vorschläge, Procedere, wie du Nachrichten siehst).

ATLAS holt die Einreichungen mit fetch_oc_submissions ab und trägt sie in den Plan ein."""


def main() -> int:
    from src.network.openclaw_client import send_message_to_agent, is_configured

    if not is_configured():
        print("Nicht konfiguriert (VPS_HOST, OPENCLAW_GATEWAY_TOKEN in .env).")
        return 1

    # Optional: Plan-Auszug mitsenden (Abschnitt 6), damit OC die genaue Stelle kennt
    plan_excerpt = ""
    if os.path.isfile(PLAN_DOC):
        with open(PLAN_DOC, "r", encoding="utf-8") as f:
            full = f.read()
        if "## 6. Abstimmung" in full:
            start = full.index("## 6. Abstimmung")
            plan_excerpt = full[start : start + 1200]
            if len(full) > start + 1200:
                plan_excerpt += "\n\n[...]"
        if plan_excerpt:
            TASK_FULL = TASK_MESSAGE + "\n\n--- Auszug aus dem Plan (Abschnitt 6) ---\n\n" + plan_excerpt
        else:
            TASK_FULL = TASK_MESSAGE
    else:
        TASK_FULL = TASK_MESSAGE

    if len(TASK_FULL) > 14000:
        TASK_FULL = TASK_FULL[:14000] + "\n\n[... gekürzt ...]"

    print("Sende Aufgabe an OC (Agent 'main') ...")
    ok, response = send_message_to_agent(TASK_FULL, agent_id="main", timeout=180.0)
    print(f"Erfolg: {ok}")
    print(f"Antwort: {response[:600] if response else '(leer)'}")
    if ok:
        print("Nächster Schritt: OC-Antwort aus rat_submissions holen (python -m src.scripts.fetch_oc_submissions) und in Abschnitt 6 des Plans eintragen.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
