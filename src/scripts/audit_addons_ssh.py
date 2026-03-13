# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import os
import json
import paramiko
from dotenv import load_dotenv

# Lade Umgebungsvariablen
load_dotenv()

# Konfiguration
HOST = "192.168.178.54"
USER = "dreadnought"
PASS_PREFIX = "USsxrqqg"
TARGET_FILE = "docs/05_AUDIT_PLANNING/CORE_HASS_OPTIMAL_PLAN.md"

def get_password():
    """Findet das Passwort in den Umgebungsvariablen, das mit dem Prefix beginnt."""
    for key, value in os.environ.items():
        if value and value.startswith(PASS_PREFIX):
            return value
    return None

def connect_and_execute():
    password = get_password()
    if not password:
        print(f"FEHLER: Kein Passwort gefunden, das mit '{PASS_PREFIX}' beginnt.")
        return None

    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOST, username=USER, password=password)
        
        # Befehl ausführen: Docker Container Listen
        # Versuche mit und ohne sudo
        commands = [
            "docker ps -a --format '{{.Names}}|{{.Status}}|{{.Image}}'",
            "sudo docker ps -a --format '{{.Names}}|{{.Status}}|{{.Image}}'"
        ]
        
        for cmd in commands:
            stdin, stdout, stderr = client.exec_command(cmd)
            output = stdout.read().decode('utf-8', errors='ignore').strip()
            error = stderr.read().decode('utf-8', errors='ignore').strip()
            
            # Auch Fehleroutput kann nützlich sein (z.B. Protection Mode Warning)
            if output:
                client.close()
                return output
            
            # Manchmal kommt Output auf Stderr bei Warnungen
            if "PROTECTION MODE" in error:
                client.close()
                return error

        client.close()
        return None
    except Exception as e:
        print(f"SSH Fehler: {e}")
        return None

def analyze_docker_output(output):
    if not output:
        return "FEHLER: Keine Docker-Daten empfangen."
    
    report = []
    report.append("## 3. ADD-ON AUDIT (HOST LEVEL - DOCKER)\n")
    report.append(f"> **Quelle:** SSH Host {HOST} ({USER}) | **Methode:** `docker ps`\n")
    
    if "PROTECTION MODE" in output:
        report.append("### ⛔ BLOCKED: PROTECTION MODE ACTIVE\n")
        report.append("**Das SSH Add-on läuft im 'Protection Mode'. Zugriff auf Docker und HA CLI ist blockiert.**\n")
        report.append("#### Lösungsschritte:\n")
        report.append("1. Gehe im Home Assistant zu **Einstellungen -> Add-ons -> Advanced SSH & Web Terminal**.\n")
        report.append("2. Deaktiviere den Schalter **Protection mode**.\n")
        report.append("3. Starte das Add-on neu.\n")
        report.append("4. Führe dieses Audit erneut aus.\n")
        return "\n".join(report)

    lines = output.split('\n')
    report.append("| Container Name | Status | Image | Action |")
    report.append("|----------------|--------|-------|--------|")
    
    zombies = []
    found_addons = False
    
    for line in lines:
        parts = line.split('|')
        if len(parts) < 3:
            continue
            
        name = parts[0]
        status = parts[1]
        image = parts[2]
        
        # Filter: Nur Addons (addon_) oder Hassio Core Container
        if not (name.startswith("addon_") or name.startswith("hassio_")):
            continue
            
        found_addons = True
        action = ""
        if "Exited" in status:
            action = "**DELETE (Zombie)**"
            zombies.append(f"{name} ({status})")
        elif "Up" in status:
            action = "KEEP"
        else:
            action = f"CHECK ({status})"
            
        report.append(f"| {name} | {status} | {image} | {action} |")
    
    if not found_addons:
        report.append(f"| FEHLER | Keine Addons gefunden | Raw Output: {output[:100]}... | CHECK |")
    
    report.append("\n")
    
    if zombies:
        report.append("### 💀 ZOMBIE ALERT (Sofort löschen)\n")
        for z in zombies:
            report.append(f"- [ ] `docker rm {z.split(' ')[0]}`")
    elif found_addons:
        report.append("### ✅ Keine Zombies gefunden.\n")
        
    return "\n".join(report)

def update_file(content):
    if not os.path.exists(TARGET_FILE):
        print(f"Datei {TARGET_FILE} nicht gefunden.")
        return

    with open(TARGET_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    # Suche Einfügeposition (nach Abschnitt 2, vor Abschnitt 3)
    insert_idx = -1
    section_3_idx = -1
    section_4_idx = -1
    
    # Finde Abschnitt 3 (egal wie er heißt) oder 4 (falls schon umbenannt)
    for i, line in enumerate(lines):
        if line.strip().startswith("## 3. ADD-ON AUDIT"):
            # Bereits vorhanden -> Update
            section_3_idx = i
            # Suche Ende des Abschnitts (nächstes ##)
            end_idx = len(lines)
            for j in range(i+1, len(lines)):
                if lines[j].strip().startswith("## "):
                    end_idx = j
                    break
            # Lösche alten Abschnitt
            lines = lines[:section_3_idx] + lines[end_idx:]
            insert_idx = section_3_idx
            break
        elif line.strip().startswith("## 4. Masterplan"):
             section_4_idx = i
             break
        elif line.strip().startswith("## 3. Masterplan"):
             section_3_idx = i
             break
            
    if insert_idx == -1:
        if section_4_idx != -1:
            insert_idx = section_4_idx
        elif section_3_idx != -1:
            # Ersetze die Überschrift von Abschnitt 3 zu 4
            lines[section_3_idx] = lines[section_3_idx].replace("## 3.", "## 4.")
            insert_idx = section_3_idx
        else:
            # Fallback
            insert_idx = len(lines)
    
    # Einfügen
    new_lines = lines[:insert_idx] + ["\n" + content + "\n\n"] + lines[insert_idx:]
    
    with open(TARGET_FILE, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    print(f"Bericht in {TARGET_FILE} eingefügt/aktualisiert.")

if __name__ == "__main__":
    print("Starte Docker Audit via SSH...")
    output = connect_and_execute()
    if output:
        print("Daten empfangen. Analysiere...")
        report = analyze_docker_output(output)
        # print(report)
        update_file(report)
        print("Fertig.")
    else:
        print("Keine Daten empfangen.")
