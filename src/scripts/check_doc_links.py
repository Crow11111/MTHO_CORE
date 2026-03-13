# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Prüft Markdown-Dokumente im Projekt auf kaputte interne Links.

- Scannt `docs/` rekursiv.
- Unterstützt zwei Link-Formate:
  1. Normale Markdown-Links: [Text](relativer/pfad.md)
  2. CORE-Core-Referenzen: @docs/...

Aufruf (aus Projekt-Root):
  python -m src.scripts.check_doc_links
"""
from __future__ import annotations

import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DOCS_ROOT = PROJECT_ROOT / "docs"

MD_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
AT_REF_RE = re.compile(r"@docs/[\w\-/\.]+")


def iter_markdown_files():
    for path in DOCS_ROOT.rglob("*.md"):
        yield path


def check_links() -> int:
    missing = []

    for md_path in iter_markdown_files():
        text = md_path.read_text(encoding="utf-8", errors="ignore")
        rel_dir = md_path.parent

        # 1) Normale Markdown-Links
        for match in MD_LINK_RE.finditer(text):
            target = match.group(1).strip()
            if not target or target.startswith(("http://", "https://", "#")):
                continue
            # nur .md und relative Pfade prüfen
            if not target.endswith(".md"):
                continue
            target_path = (rel_dir / target).resolve()
            if not target_path.exists():
                missing.append((md_path, target))

        # 2) @docs/ Referenzen
        for match in AT_REF_RE.finditer(text):
            ref = match.group(0)  # z.B. @docs/02_ARCHITECTURE/DEV_AGENT_UND_SCHNITTSTELLEN.md
            rel = ref[len("@") :]  # docs/...
            target_path = (PROJECT_ROOT / rel).resolve()
            if not target_path.exists():
                missing.append((md_path, ref))

    if not missing:
        print("OK: Keine fehlenden Link-Ziele gefunden.")
        return 0

    print("Fehlende Link-Ziele:")
    for src, tgt in missing:
        rel_src = src.relative_to(PROJECT_ROOT)
        print(f"- {rel_src} -> {tgt}")
    return 1


def main() -> int:
    if not DOCS_ROOT.exists():
        print(f"FEHLER: docs-Ordner nicht gefunden: {DOCS_ROOT}")
        return 1
    return check_links()


if __name__ == "__main__":
    raise SystemExit(main())

