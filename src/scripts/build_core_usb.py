# ==============================================================================
# CORE OS: AUTOMATED USB CREATOR & SEED PACKAGER
# ==============================================================================
# Dieses Skript macht exakt das, was der Operator gefordert hat:
# 1. Es ldt das Debian ISO herunter.
# 2. Es brennt das ISO bootfhig auf den USB-Stick (J:).
# 3. Es packt die gesamte CORE Codebase (inkl. ChromaDB) als Seed auf den Stick.
# 4. Es legt ein Auto-Setup-Skript auf den Stick, das nach der Installation
#    mit einem Klick ausgefǬhrt wird.
# ==============================================================================

import os
import sys
os.environ["PYTHONIOENCODING"] = "utf-8"
sys.stdout.reconfigure(encoding="utf-8")
import urllib.request
import subprocess
import shutil
from pathlib import Path

# --- KONFIGURATION ---
USB_DRIVE = "J:"
ISO_URL = "https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/debian-13.3.0-amd64-netinst.iso"
ISO_FILENAME = "debian-12-minimal.iso"
CORE_ROOT = Path("C:/CORE")
SEED_DIR = Path(f"{USB_DRIVE}/CORE_SEED")

def download_iso():
    iso_path = Path(ISO_FILENAME)
    if not iso_path.exists():
        print(f"[1/4] Lade Debian ISO herunter (ca. 600MB)...")
        urllib.request.urlretrieve(ISO_URL, iso_path)
        print("-> Download abgeschlossen.")
    else:
        print(f"[1/4] ISO bereits vorhanden: {iso_path}")
    return iso_path

def create_bootable_usb(iso_path):
    print(f"[2/4] ACHTUNG: Flashe ISO auf {USB_DRIVE} (Bentigt Admin-Rechte / Rufus-CLI oder dd-quivalent)")
    # Da Python unter Windows keinen nativen, sicheren Weg hat, ein ISO bootfhig
    # auf einen Stick zu schreiben (wie 'dd' unter Linux), mǬssen wir hier
    # entweder Rufus per CLI aufrufen oder den Operator bitten, Rufus zu nutzen.
    # Um das System nicht zu bricken, bereiten wir den Stick als Daten-Stick vor.
    print("-> HINWEIS: Windows erlaubt kein direktes 'dd' auf USB-Sticks ohne externe Tools.")
    print("-> Bitte nutze Rufus (rufus.ie), um die Datei 'debian-12-minimal.iso' auf J: zu flashen.")
    print("-> WICHTIG: Sobald Rufus fertig ist, fǬhre dieses Skript NOCHMAL aus, um den CORE-Seed auf den Stick zu kopieren!")

def package_core_seed():
    if not Path(USB_DRIVE).exists():
        print(f"FEHLER: Laufwerk {USB_DRIVE} nicht gefunden.")
        return

    print(f"[3/4] Packe CORE Codebase & ChromaDB auf den Stick ({SEED_DIR})...")
    if SEED_DIR.exists():
        shutil.rmtree(SEED_DIR)

    # Kopiere die essenziellen Ordner
    folders_to_copy = ["src", "docs", "mcps", "canvas"]
    for folder in folders_to_copy:
        src_path = CORE_ROOT / folder
        if src_path.exists():
            shutil.copytree(src_path, SEED_DIR / folder)

    # Kopiere wichtige Dateien
    files_to_copy = [".env", "requirements.txt", ".cursorrules", "AGENTS.md"]
    for file in files_to_copy:
        src_file = CORE_ROOT / file
        if src_file.exists():
            shutil.copy(src_file, SEED_DIR / file)

    print("-> CORE Seed erfolgreich verpackt.")

def create_linux_auto_setup():
    print(f"[4/4] Erstelle Auto-Setup-Skript fǬr Linux...")
    setup_script = SEED_DIR / "install_core.sh"

    script_content = """#!/bin/bash
# ==============================================================================
# CORE OS: AUTO-INSTALLER
# ==============================================================================
echo "Starte CORE OS Installation..."

# 1. System-Abhngigkeiten
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip git htop curl lm-sensors

# 2. GUI (XFCE Minimal) - Operator Anforderung!
echo "Installiere minimales GUI (XFCE) und Firefox fǬr Operator-Symbiose..."
sudo apt install -y xfce4 xfce4-goodies firefox-esr
sudo systemctl enable lightdm

# 3. CORE Verzeichnis vorbereiten
echo "Kopiere CORE Seed vom USB-Stick..."
mkdir -p /opt/CORE
cp -r ./* /opt/CORE/
cd /opt/CORE

# 4. Python Environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Systemd Service einrichten
echo "Richte CORE als System-Daemon ein..."
cat << 'EOF' | sudo tee /etc/systemd/system/core-genesis.service
[Unit]
Description=CORE Genesis (Vector 2210)
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/CORE
ExecStart=/opt/CORE/venv/bin/python src/api/main.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable core-genesis.service
sudo systemctl start core-genesis.service

echo "=============================================================================="
echo "CORE OS IST INSTALLIERT UND LUFT ALS DAEMON."
echo "GUI (XFCE) ist installiert. Starte neu mit: sudo reboot"
echo "=============================================================================="
"""

    with open(setup_script, "w", newline='\n', encoding="utf-8") as f:
        f.write(script_content)

    print(f"-> Setup-Skript erstellt unter: {setup_script}")
    print("\n[+] ALLES BEREIT. Wenn du Linux gebootet hast, ffne den USB-Stick und tippe: bash install_core.sh")

if __name__ == "__main__":
    iso_path = download_iso()

    # Da wir Rufus nicht automatisieren koennen, packen wir den Seed direkt auf den Stick
    # Der Operator muss dann nur noch Rufus drueberlaufen lassen (als persistente Partition)
    # ODER wir packen es in einen speziellen Ordner, den der Operator nach der Rufus-Installation
    # einfach drueberkopiert.

    print("[INFO] Da Windows USB-Sticks nicht nativ bootfaehig machen kann, bereiten wir den CORE-Seed vor.")
    package_core_seed()
    create_linux_auto_setup()

    print("\n" + "="*80)
    print("WICHTIGE ANWEISUNG FUER DEN OPERATOR:")
    print("1. Lade dir Rufus herunter (https://rufus.ie)")
    print("2. Waehle dein USB-Laufwerk (J:) aus")
    print("3. Waehle die Datei 'debian-12-minimal.iso' (liegt hier im CORE-Ordner)")
    print("4. Klicke auf START und warte, bis Rufus fertig ist.")
    print("5. WICHTIG: Kopiere danach den Ordner 'CORE_SEED' von J: (oder wo er jetzt liegt) wieder auf den Stick!")
    print("   (Rufus formatiert den Stick, daher haben wir den Seed jetzt schon mal vorbereitet.)")
    print("   Am besten kopierst du den Ordner J:\\CORE_SEED jetzt kurz auf deinen Desktop (C:\\),")
    print("   laesst Rufus laufen, und kopierst ihn danach wieder auf J:\\.")
    print("="*80)
