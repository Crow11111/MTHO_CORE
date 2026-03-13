# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Gemini App Bridge: Extrahiert Session-Daten aus der Gemini App und fuehrt sie
ueber ingest_session_log.py in ChromaDB ein.

Drei Pfade (nach Machbarkeit):
  1. Manual: Markdown-Datei aus Copy-Paste -> ingest_session_log.py
  2. Google Takeout: JSON-Export -> Markdown -> ingest_session_log.py
  3. Gemini API (experimentell): google-genai SDK Chat-History -> Markdown -> ingest

Usage:
    python gemini_app_bridge.py manual <markdown_file>
    python gemini_app_bridge.py takeout <takeout_json_dir>
    python gemini_app_bridge.py api [--list] [--chat-id <id>]
"""
import os
import re
import sys
import json
import glob
import argparse
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

SESSION_LOGS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "session_logs")


def ensure_session_logs_dir():
    os.makedirs(SESSION_LOGS_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# Pfad 1: Manual (Markdown direkt einlesen)
# ---------------------------------------------------------------------------

def bridge_manual(filepath: str, dry_run: bool = False) -> dict:
    """Nimmt eine manuell erstellte Markdown-Session und ingestet sie."""
    from scripts.ingest_session_log import ingest_session, parse_session_markdown

    if not os.path.exists(filepath):
        return {"error": f"Datei nicht gefunden: {filepath}"}

    session = parse_session_markdown(filepath)
    print(f"[BRIDGE:MANUAL] Session: {session['title']}")
    print(f"  Datum: {session['session_date']}, Turns: {len(session['turns'])}")

    if dry_run:
        return {"mode": "manual", "dry_run": True, "turns": len(session["turns"])}

    stats = ingest_session(filepath, source_override="gemini_app")
    return {"mode": "manual", **stats}


# ---------------------------------------------------------------------------
# Pfad 2: Google Takeout JSON -> Markdown -> Ingest
# ---------------------------------------------------------------------------

def _takeout_json_to_markdown(json_path: str) -> str:
    """Konvertiert eine Google Takeout Gemini-Konversation (JSON) in Markdown."""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    title = data.get("title", Path(json_path).stem)
    create_time = data.get("create_time", "")
    if create_time:
        try:
            dt = datetime.fromisoformat(create_time.replace("Z", "+00:00"))
            session_date = dt.strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            session_date = datetime.now().strftime("%Y-%m-%d")
    else:
        session_date = datetime.now().strftime("%Y-%m-%d")

    lines = [
        f"# Session Log: {title}",
        "",
        f"- **Datum:** {session_date}",
        f"- **Quelle:** Gemini App (Google Takeout Import)",
        "",
        "---",
        "",
    ]

    messages = data.get("messages", data.get("mapping", []))
    if isinstance(messages, dict):
        messages = list(messages.values())

    turn_num = 0
    for msg in messages:
        if isinstance(msg, dict):
            role = msg.get("role", msg.get("author", {}).get("role", "unknown"))
            content = ""
            if "content" in msg:
                if isinstance(msg["content"], str):
                    content = msg["content"]
                elif isinstance(msg["content"], dict):
                    parts = msg["content"].get("parts", [])
                    content = "\n".join(
                        p if isinstance(p, str) else p.get("text", "")
                        for p in parts
                    )
                elif isinstance(msg["content"], list):
                    content = "\n".join(
                        p if isinstance(p, str) else p.get("text", "")
                        for p in msg["content"]
                    )
            elif "parts" in msg:
                content = "\n".join(
                    p.get("text", p) if isinstance(p, dict) else str(p)
                    for p in msg["parts"]
                )

            if not content.strip():
                continue

            if role in ("user", "human"):
                turn_num += 1
                speaker_label = "User"
                turn_title = content[:60].replace("\n", " ").strip()
                if turn_title.endswith("..."):
                    pass
                elif len(content) > 60:
                    turn_title += "..."
                lines.append(f"## Turn {turn_num:02d}: {turn_title}")
                lines.append("")
            else:
                speaker_label = "CORE"

            lines.append(f"**{speaker_label}:**")
            lines.append(content.strip())
            lines.append("")

    return "\n".join(lines)


def bridge_takeout(takeout_dir: str, dry_run: bool = False) -> dict:
    """Verarbeitet Google Takeout Gemini-Exports (JSON-Dateien)."""
    ensure_session_logs_dir()

    json_files = glob.glob(os.path.join(takeout_dir, "**", "*.json"), recursive=True)
    if not json_files:
        return {"error": f"Keine JSON-Dateien in {takeout_dir} gefunden"}

    results = []
    for jf in json_files:
        try:
            md_content = _takeout_json_to_markdown(jf)
            basename = Path(jf).stem
            safe_name = re.sub(r'[^\w\-]', '_', basename)[:80]
            md_path = os.path.join(SESSION_LOGS_DIR, f"takeout_{safe_name}.md")

            with open(md_path, "w", encoding="utf-8") as f:
                f.write(md_content)

            print(f"[BRIDGE:TAKEOUT] Konvertiert: {jf} -> {md_path}")

            if not dry_run:
                stats = bridge_manual(md_path)
                results.append({"file": jf, **stats})
            else:
                results.append({"file": jf, "dry_run": True, "md_path": md_path})

        except Exception as e:
            print(f"[BRIDGE:TAKEOUT] Fehler bei {jf}: {e}")
            results.append({"file": jf, "error": str(e)})

    return {"mode": "takeout", "processed": len(results), "results": results}


# ---------------------------------------------------------------------------
# Pfad 3: Gemini API (experimentell)
# ---------------------------------------------------------------------------

def bridge_api(list_chats: bool = False, chat_id: str = None, dry_run: bool = False) -> dict:
    """
    Experimentell: Versucht Chat-History ueber die google-genai SDK zu lesen.
    Die Gemini App selbst nutzt intern eine andere API als das SDK,
    daher ist dieser Pfad moeglicherweise nicht funktional.
    """
    try:
        from google import genai
    except ImportError:
        return {"error": "google-genai nicht installiert: pip install google-genai"}

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return {"error": "GEMINI_API_KEY nicht gesetzt"}

    client = genai.Client(api_key=api_key)

    if list_chats:
        try:
            chats = client.chats.list()
            chat_list = []
            for chat in chats:
                chat_list.append({
                    "id": getattr(chat, "id", "?"),
                    "title": getattr(chat, "title", getattr(chat, "display_name", "?")),
                })
            return {"mode": "api", "action": "list", "chats": chat_list}
        except AttributeError:
            return {
                "mode": "api",
                "action": "list",
                "error": "client.chats.list() nicht verfuegbar in dieser SDK-Version. "
                         "Die Gemini App Sessions sind ueber die Public API nicht abrufbar. "
                         "Nutze Pfad 1 (manual) oder Pfad 2 (takeout)."
            }
        except Exception as e:
            return {"mode": "api", "action": "list", "error": str(e)}

    if chat_id:
        try:
            chat = client.chats.get(chat_id)
            messages = getattr(chat, "messages", getattr(chat, "history", []))
            return {
                "mode": "api",
                "action": "get",
                "chat_id": chat_id,
                "message_count": len(messages) if messages else 0,
            }
        except Exception as e:
            return {"mode": "api", "action": "get", "error": str(e)}

    return {"mode": "api", "error": "Kein --list oder --chat-id angegeben"}


# ---------------------------------------------------------------------------
# Empfehlungs-Engine: Welcher Pfad ist der beste?
# ---------------------------------------------------------------------------

def recommend_path() -> str:
    """Gibt eine Empfehlung, welcher Bridge-Pfad genutzt werden sollte."""
    has_api_key = bool(os.getenv("GEMINI_API_KEY", "").strip())
    takeout_hints = glob.glob(os.path.join(os.path.expanduser("~"), "Downloads", "Takeout", "**", "*.json"), recursive=True)

    if takeout_hints:
        return (
            f"[EMPFEHLUNG] Google Takeout gefunden ({len(takeout_hints)} JSON-Dateien). "
            f"Nutze: python gemini_app_bridge.py takeout ~/Downloads/Takeout/"
        )
    if has_api_key:
        return (
            "[EMPFEHLUNG] GEMINI_API_KEY vorhanden. API-Pfad verfuegbar (experimentell). "
            "Fuer zuverlaessige Extraktion: Gemini App -> Copy-Paste -> Markdown."
        )
    return (
        "[EMPFEHLUNG] Manueller Pfad: Gespraech in der Gemini App kopieren, "
        "als Markdown in data/session_logs/ speichern, dann:\n"
        "  python gemini_app_bridge.py manual data/session_logs/<datei>.md"
    )


def main():
    parser = argparse.ArgumentParser(
        description="Gemini App Bridge: Session-Daten extrahieren und in ChromaDB indizieren"
    )
    sub = parser.add_subparsers(dest="mode")

    p_manual = sub.add_parser("manual", help="Markdown-Datei direkt einlesen")
    p_manual.add_argument("file", help="Pfad zur Markdown-Session-Datei")
    p_manual.add_argument("--dry-run", action="store_true")

    p_takeout = sub.add_parser("takeout", help="Google Takeout JSON-Verzeichnis verarbeiten")
    p_takeout.add_argument("dir", help="Pfad zum Takeout-Verzeichnis")
    p_takeout.add_argument("--dry-run", action="store_true")

    p_api = sub.add_parser("api", help="Gemini API (experimentell)")
    p_api.add_argument("--list", action="store_true", help="Verfuegbare Chats auflisten")
    p_api.add_argument("--chat-id", help="Bestimmten Chat abrufen")
    p_api.add_argument("--dry-run", action="store_true")

    p_recommend = sub.add_parser("recommend", help="Besten Pfad empfehlen")

    args = parser.parse_args()

    if not args.mode:
        print(recommend_path())
        parser.print_help()
        return

    if args.mode == "recommend":
        print(recommend_path())
        return

    if args.mode == "manual":
        result = bridge_manual(args.file, dry_run=args.dry_run)
    elif args.mode == "takeout":
        result = bridge_takeout(args.dir, dry_run=args.dry_run)
    elif args.mode == "api":
        result = bridge_api(list_chats=args.list, chat_id=args.chat_id, dry_run=args.dry_run)
    else:
        parser.print_help()
        return

    print(f"\n[ERGEBNIS] {json.dumps(result, indent=2, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
