#!/usr/bin/env python3
"""
ATLAS – Scout Wake Word Setup

Kopiert Wake Word .tflite Dateien nach Scout (/share/openwakeword).
Unterstützt:
  - Lokales Verzeichnis (z.B. data/openwakeword_models) → Samba-Share
  - Zwei Wake Words: hey atlas, computer (nach Custom Training)

Voraussetzung:
  - Samba-Share auf Scout erreichbar (z.B. \\192.168.178.54\share)
  - Oder: Dateien manuell per Samba kopieren

Verwendung:
  python src/scripts/setup_scout_wake_words.py --source data/openwakeword_models --target \\\\192.168.178.54\\share\\openwakeword
  python src/scripts/setup_scout_wake_words.py --source data/openwakeword_models  # kopiert nur lokal nach data/scout_openwakeword
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


def copy_wake_words(source_dir: Path, target_dir: Path) -> tuple[int, int]:
    """Kopiert alle .tflite Dateien von source nach target. Returns (ok, total)."""
    if not source_dir.exists():
        print(f"Quellverzeichnis existiert nicht: {source_dir}")
        return 0, 0
    tflites = list(source_dir.glob("*.tflite"))
    if not tflites:
        print(f"Keine .tflite Dateien in {source_dir}")
        return 0, 0
    target_dir.mkdir(parents=True, exist_ok=True)
    ok = 0
    for src in tflites:
        dst = target_dir / src.name
        try:
            shutil.copy2(src, dst)
            print(f"  {src.name} -> {dst}")
            ok += 1
        except Exception as e:
            print(f"  Fehler {src.name}: {e}")
    return ok, len(tflites)


def main() -> int:
    parser = argparse.ArgumentParser(description="Wake Word Dateien nach Scout kopieren")
    parser.add_argument(
        "--source",
        "-s",
        type=Path,
        default=Path("data/openwakeword_models"),
        help="Quellverzeichnis mit .tflite Dateien",
    )
    parser.add_argument(
        "--target",
        "-t",
        type=Path,
        default=None,
        help="Zielverzeichnis (Samba: \\\\192.168.178.54\\share\\openwakeword oder lokaler Pfad)",
    )
    parser.add_argument(
        "--local-fallback",
        action="store_true",
        default=True,
        help="Bei fehlendem --target: Nach data/scout_openwakeword kopieren (zum manuellen Übertragen)",
    )
    args = parser.parse_args()

    source = args.source.resolve()
    if args.target:
        target = Path(args.target)
    else:
        target = Path("data/scout_openwakeword").resolve()
        if args.local_fallback:
            print(f"Kein --target angegeben. Kopiere nach lokales Verzeichnis: {target}")
            print("Zum Scout kopieren: Samba \\\\192.168.178.54\\share\\openwakeword öffnen und Dateien manuell verschieben.")

    ok, total = copy_wake_words(source, target)
    if total == 0:
        return 1
    print(f"\n{ok}/{total} Dateien kopiert.")
    print("\nNächste Schritte:")
    print("  1. Falls Ziel Samba war: openWakeWord Add-on auf Scout neu starten")
    print("  2. Einstellungen → Sprachassistenten → Assistent → Streaming Wake Word hinzufügen")
    print("  3. Eigenes Modell aus der Liste wählen (hey_atlas, computer, etc.)")
    print("  4. Ab HA 2025.10: Bis zu 2 Wake Words pro Satellite möglich")
    return 0 if ok == total else 1


if __name__ == "__main__":
    sys.exit(main())
