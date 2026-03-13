"""
Scout -> OC Brain: Event an OpenClaw senden (Webhook-Kanal).

Nutzt openclaw_client.send_event_to_oc_brain. Für Scout/HA: Event als JSON
von stdin oder als Argumente. .env: OPENCLAW_ADMIN_VPS_HOST, OPENCLAW_GATEWAY_TOKEN.

Beispiele:
  echo '{"source":"scout","node_id":"raspi5-ha-master","event_type":"motion_detected_prefiltered","timestamp":"2026-02-28T15:00:00Z","priority":"medium","data":{"device":"tapo_c52a"}}' | python -m src.scripts.scout_send_event_to_oc
  python -m src.scripts.scout_send_event_to_oc --type motion_detected_prefiltered --node raspi5-ha-master --device tapo_c52a
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from dotenv import load_dotenv
load_dotenv("c:/CORE/.env")

from src.network.openclaw_client import send_event_to_oc_brain, is_configured


def _event_from_args(args) -> dict:
    from datetime import datetime, timezone
    ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return {
        "source": "scout",
        "node_id": getattr(args, "node_id", None) or "raspi5-ha-master",
        "event_type": getattr(args, "event_type", None) or "sensor_event",
        "timestamp": ts,
        "priority": getattr(args, "priority", None) or "medium",
        "data": {
            "device": getattr(args, "device", None) or "unknown",
            **(getattr(args, "extra", None) or {}),
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Scout-Event an OC Brain senden")
    parser.add_argument("--type", dest="event_type", default="sensor_event", help="event_type")
    parser.add_argument("--node", dest="node_id", default="raspi5-ha-master", help="node_id")
    parser.add_argument("--device", default="unknown", help="data.device")
    parser.add_argument("--priority", default="medium", help="priority")
    parser.add_argument("--agent", default="main", help="OpenClaw agent_id")
    args = parser.parse_args()

    if not is_configured():
        print("FEHLER: OPENCLAW_ADMIN_VPS_HOST und OPENCLAW_GATEWAY_TOKEN in .env fehlen.")
        return 1

    event = None
    if not sys.stdin.isatty():
        raw = sys.stdin.read().strip()
        if raw:
            try:
                event = json.loads(raw)
            except json.JSONDecodeError:
                print("FEHLER: Ungültiges JSON von stdin.")
                return 1
    if event is None:
        event = _event_from_args(args)

    ok, out = send_event_to_oc_brain(event, agent_id=args.agent, timeout=25.0)
    if ok:
        print("OK:", (out[:200] + "..." if len(out) > 200 else out))
        return 0
    print("FEHLER:", out)
    return 1


if __name__ == "__main__":
    sys.exit(main())
