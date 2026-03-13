# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Session-Log Ingest: Markdown -> ChromaDB session_logs Collection.

Liest eine Markdown-Session-Datei, chunked nach Turns, extrahiert Metadaten
und schreibt jeden Turn als eigenen Vektor in ChromaDB.

Usage:
    python ingest_session_log.py <markdown_file> [--source gemini_app] [--date 2026-03-01]
"""
import os
import re
import sys
import argparse
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from network.chroma_client import add_session_turn, get_session_logs_collection


def parse_session_markdown(filepath: str) -> dict:
    """Parst eine Session-Log Markdown-Datei in strukturierte Turns."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    header_match = re.search(r"^#\s+(.+)", content, re.MULTILINE)
    title = header_match.group(1).strip() if header_match else os.path.basename(filepath)

    date_match = re.search(r"\*\*Datum:\*\*\s*(\S+)", content)
    session_date = date_match.group(1) if date_match else datetime.now().strftime("%Y-%m-%d")

    source_match = re.search(r"\*\*Quelle:\*\*\s*(.+)", content)
    source = source_match.group(1).strip() if source_match else "unknown"

    turn_pattern = re.compile(
        r"^##\s+Turn\s+(\d+):\s*(.+?)$",
        re.MULTILINE
    )
    matches = list(turn_pattern.finditer(content))

    turns = []
    for i, match in enumerate(matches):
        turn_number = int(match.group(1))
        turn_title = match.group(2).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        turn_content = content[start:end].strip()

        segments = re.split(r"\*\*(?:User|CORE):\*\*", turn_content)
        speakers_raw = re.findall(r"\*\*(User|CORE):\*\*", turn_content)

        sub_turns = []
        for j, speaker in enumerate(speakers_raw):
            text = segments[j + 1].strip() if j + 1 < len(segments) else ""
            if text:
                sub_turns.append({
                    "speaker": "user" if speaker == "User" else "core",
                    "text": text,
                })

        turns.append({
            "turn_number": turn_number,
            "title": turn_title,
            "full_text": turn_content,
            "sub_turns": sub_turns,
        })

    destilled = ""
    destilled_match = re.search(r"^##\s+Destillierte\s+Erkenntnisse.*$", content, re.MULTILINE)
    if destilled_match:
        destilled = content[destilled_match.start():].strip()

    return {
        "title": title,
        "session_date": session_date,
        "source": source,
        "turns": turns,
        "destilled": destilled,
    }


def extract_topics(text: str) -> str:
    """Extrahiert Themen-Tags aus einem Turn-Text (heuristisch)."""
    topic_indicators = {
        "negentropie": ["negentropie", "stagnation", "evolution"],
        "bias_depth": ["bias_depth", "diminishing returns", "circuit breaker", "hyper-fokus"],
        "scaffolding": ["scaffolding", "geruest", "abhaengigkeit", "autonomie"],
        "dissonanz": ["dissonanz", "echokammer", "gegenpositionen"],
        "world_building": ["world-building", "tolkien", "stanton", "burroughs", "pulp"],
        "feedback_loop": ["feedback", "loop", "dopamin", "rekursiv"],
        "chromadb": ["chroma", "vektor", "embedding", "datenbank"],
        "layer0": ["layer-0", "layer 0", "archetypisch", "quellcode"],
    }
    text_lower = text.lower()
    found = []
    for topic, keywords in topic_indicators.items():
        if any(kw in text_lower for kw in keywords):
            found.append(topic)
    return ",".join(found) if found else "general"


def determine_ring_level(text: str) -> int:
    """Bestimmt den Ring-Level eines Turns basierend auf Inhalt."""
    ring0_keywords = [
        "direktive", "grundregel", "circuit breaker", "negentropie",
        "bias_depth", "scaffolding", "ring 0", "ring-0", "kernel",
    ]
    ring1_keywords = [
        "prognose", "vorhersage", "analyse", "auditor", "ring 1", "ring-1",
    ]
    text_lower = text.lower()
    if any(kw in text_lower for kw in ring0_keywords):
        return 0
    if any(kw in text_lower for kw in ring1_keywords):
        return 1
    return 2


def ingest_session(filepath: str, source_override: str = None, date_override: str = None) -> dict:
    """Hauptfunktion: Parst Markdown und schreibt Turns in ChromaDB."""
    session = parse_session_markdown(filepath)

    source = source_override or session["source"]
    session_date = date_override or session["session_date"]
    basename = os.path.splitext(os.path.basename(filepath))[0]

    stats = {"total": 0, "success": 0, "failed": 0}

    for turn in session["turns"]:
        for sub in turn["sub_turns"]:
            turn_id = f"session_{basename}_t{turn['turn_number']:02d}_{sub['speaker']}"
            document = f"[Turn {turn['turn_number']}: {turn['title']}] ({sub['speaker']})\n{sub['text']}"
            topics = extract_topics(sub["text"])
            ring_level = determine_ring_level(sub["text"])

            ok = add_session_turn(
                turn_id=turn_id,
                document=document,
                source=source,
                session_date=session_date,
                turn_number=turn["turn_number"],
                speaker=sub["speaker"],
                topics=topics,
                ring_level=ring_level,
            )
            stats["total"] += 1
            if ok:
                stats["success"] += 1
            else:
                stats["failed"] += 1

    if session["destilled"]:
        dest_id = f"session_{basename}_destilled"
        ok = add_session_turn(
            turn_id=dest_id,
            document=session["destilled"],
            source=source,
            session_date=session_date,
            turn_number=99,
            speaker="core",
            topics="negentropie,bias_depth,scaffolding,dissonanz",
            ring_level=0,
        )
        stats["total"] += 1
        if ok:
            stats["success"] += 1
        else:
            stats["failed"] += 1

    return stats


def main():
    parser = argparse.ArgumentParser(description="Session-Log Markdown -> ChromaDB Ingest")
    parser.add_argument("file", help="Pfad zur Markdown-Session-Datei")
    parser.add_argument("--source", default=None, help="Quelle ueberschreiben (z.B. gemini_app)")
    parser.add_argument("--date", default=None, help="Datum ueberschreiben (ISO-Format)")
    parser.add_argument("--dry-run", action="store_true", help="Nur parsen, nicht in DB schreiben")
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"[FEHLER] Datei nicht gefunden: {args.file}")
        sys.exit(1)

    print(f"[SESSION-INGEST] Parsing: {args.file}")
    session = parse_session_markdown(args.file)
    print(f"  Titel: {session['title']}")
    print(f"  Datum: {session['session_date']}")
    print(f"  Quelle: {session['source']}")
    print(f"  Turns: {len(session['turns'])}")
    print(f"  Destillierte Erkenntnisse: {'Ja' if session['destilled'] else 'Nein'}")

    if args.dry_run:
        print("\n[DRY-RUN] Keine Daten geschrieben.")
        for turn in session["turns"]:
            for sub in turn["sub_turns"]:
                topics = extract_topics(sub["text"])
                ring = determine_ring_level(sub["text"])
                print(f"  Turn {turn['turn_number']:02d} ({sub['speaker']}): "
                      f"topics=[{topics}] ring={ring}")
        return

    stats = ingest_session(args.file, source_override=args.source, date_override=args.date)
    print(f"\n[ERGEBNIS] {stats['success']}/{stats['total']} Turns erfolgreich indiziert.")
    if stats["failed"]:
        print(f"  [WARNUNG] {stats['failed']} Turns fehlgeschlagen.")


if __name__ == "__main__":
    main()
