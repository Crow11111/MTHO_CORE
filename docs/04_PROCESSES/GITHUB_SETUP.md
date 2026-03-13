<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

﻿# GitHub Repository Setup für CORE

> Anleitung zur Verbindung des lokalen CORE Repos mit GitHub für Cloud Agents und Push-Funktionalität.

## Voraussetzungen

- GitHub Account: `Crow11111`
- Lokales Repo: `c:\CORE` (existiert bereits)
- Aktueller Branch: `2026-02-25-cjle`

## Schritt 1: GitHub Repository erstellen

1. Öffne [github.com/new](https://github.com/new)
2. Repository name: `CORE`
3. Description: `CORE Orchestration Core - Private Infrastructure`
4. Visibility: **Private** (wichtig!)
5. **KEIN** README, .gitignore oder License hinzufügen (Repo existiert lokal bereits)
6. Klicke **Create repository**

## Schritt 2: Cursor mit GitHub verbinden (OAuth)

1. Öffne Cursor
2. Gehe zu **Settings** (Ctrl+,) oder über das Zahnrad-Icon
3. Suche nach **GitHub** oder gehe zu **Accounts**
4. Klicke **Sign in with GitHub**
5. Autorisiere Cursor in deinem Browser
6. Bestätige die Verbindung

## Schritt 3: Remote hinzufügen

Führe im Terminal (in `c:\CORE`) aus:

```powershell
git remote add origin https://github.com/Crow11111/CORE.git
```

Prüfe mit:

```powershell
git remote -v
```

Erwartete Ausgabe:
```
origin  https://github.com/Crow11111/CORE.git (fetch)
origin  https://github.com/Crow11111/CORE.git (push)
```

## Schritt 4: Initial Push

Push den aktuellen Branch:

```powershell
git push -u origin 2026-02-25-cjle
```

Optional auch den master-Branch pushen:

```powershell
git push -u origin main
```

Bei Authentifizierungsprompt:
- Nutze **GitHub Personal Access Token** (nicht dein Passwort)
- Oder Cursor's integrierte GitHub-Auth nutzt automatisch OAuth

## Schritt 5: Cloud Agents aktivieren

1. In Cursor: Öffne **Cloud Agents** Tab (Sidebar oder Ctrl+Shift+P -> Cloud Agents)
2. Klicke **Manage Settings** oder **Configure**
3. Wähle Repository: `Crow11111/CORE`
4. Aktiviere Cloud Agents für das Repo

## Troubleshooting

### Remote existiert bereits
```powershell
git remote remove origin
git remote add origin https://github.com/Crow11111/CORE.git
```

### Authentication failed
1. Erstelle Personal Access Token: [github.com/settings/tokens](https://github.com/settings/tokens/new)
2. Scope: `repo` (Full control of private repositories)
3. Nutze Token als Passwort beim Push

### Push rejected (non-fast-forward)
Falls GitHub-Repo bereits Commits hat:
```powershell
git pull origin 2026-02-25-cjle --rebase
git push -u origin 2026-02-25-cjle
```

## Sicherheitshinweise

Die `.gitignore` schützt bereits:
- `.env` - Umgebungsvariablen/Secrets
- `*.pem`, `*.key` - SSH/TLS Schlüssel
- `.secrets.mth` - CORE Secrets

**NIEMALS** folgende Dateien committen:
- API-Keys
- Passwörter
- Private SSH Keys
- `.env` Dateien

---

*Erstellt: 2026-03-04 | Infrastruktur-Spezialist*
