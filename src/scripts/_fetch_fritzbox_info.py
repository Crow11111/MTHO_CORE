#!/usr/bin/env python3
"""
Fritzbox-Einstellungen auslesen via TR-064 (UPnP/SOAP).
Nutzt FRITZBOX_USERNAME und FRITZBOX_PASSWORD aus .env.
Gibt Netzwerk-Geräte, DNS-Einstellungen, DHCP-Konfiguration aus.
"""
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT, ".env"))

FRITZBOX_IP = "192.168.178.1"
USERNAME = os.getenv("FRITZBOX_USERNAME", "")
PASSWORD = os.getenv("FRITZBOX_PASSWORD", "")

try:
    from fritzconnection import FritzConnection
    from fritzconnection.lib.fritzhosts import FritzHosts
    from fritzconnection.lib.fritzstatus import FritzStatus
except ImportError:
    print("fritzconnection nicht installiert. Installiere mit: pip install fritzconnection")
    sys.exit(1)

def main():
    print(f"Verbinde mit Fritzbox {FRITZBOX_IP} als {USERNAME}...")
    try:
        fc = FritzConnection(address=FRITZBOX_IP, user=USERNAME, password=PASSWORD)
    except Exception as e:
        print(f"Verbindungsfehler: {e}")
        return

    print(f"\n=== Fritzbox Modell: {fc.modelname} ===")
    print(f"Firmware: {fc.system_version}")

    # Status
    try:
        fs = FritzStatus(fc=fc)
        print(f"\n--- WAN ---")
        print(f"Externe IP: {fs.external_ip}")
        print(f"Externe IPv6: {fs.external_ipv6}")
        print(f"Verbindungsstatus: {'Online' if fs.is_connected else 'Offline'}")
        print(f"Uptime: {fs.uptime} Sekunden")
    except Exception as e:
        print(f"Status-Fehler: {e}")

    # Hosts / Geräte
    try:
        fh = FritzHosts(fc=fc)
        hosts = fh.get_hosts_info()
        print(f"\n--- Netzwerkgeräte ({len(hosts)} gesamt) ---")
        print(f"{'Name':<25} {'IP':<18} {'MAC':<20} {'Status'}")
        print("-" * 75)
        for h in sorted(hosts, key=lambda x: x.get('ip') or ''):
            name = (h.get('name') or '-')[:24]
            ip = h.get('ip') or '-'
            mac = h.get('mac') or '-'
            status = 'aktiv' if h.get('status') else 'inaktiv'
            print(f"{name:<25} {ip:<18} {mac:<20} {status}")
    except Exception as e:
        print(f"Hosts-Fehler: {e}")

    # DNS-Einstellungen (soweit abrufbar)
    print("\n--- DNS-/DHCP-Einstellungen (TR-064 limitiert) ---")
    try:
        # Versuche LANHostConfigManagement
        result = fc.call_action("LANHostConfigManagement1", "GetInfo")
        for k, v in result.items():
            print(f"  {k}: {v}")
    except Exception as e:
        print(f"  LANHostConfigManagement nicht verfügbar: {e}")

    try:
        # DHCPv4 Range
        result = fc.call_action("LANHostConfigManagement1", "GetAddressRange")
        print(f"  DHCP Range: {result}")
    except Exception:
        pass

    try:
        # DNS Server
        result = fc.call_action("LANHostConfigManagement1", "GetDNSServers")
        print(f"  DNS Server: {result}")
    except Exception:
        pass

    print("\n--- Fertig ---")


if __name__ == "__main__":
    main()
