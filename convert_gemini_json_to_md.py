#!/usr/bin/env python3
"""
Konvertiert MeineAktivitäten.json (Google Takeout Gemini) in lesbares Markdown.
"""

import json
import re
import html
from pathlib import Path
from datetime import datetime


def html_to_markdown(html_str: str) -> str:
    """Konvertiert HTML-String in Markdown."""
    if not html_str or not html_str.strip():
        return ""
    # HTML-Entities dekodieren
    text = html.unescape(html_str)
    # Block-Elemente zu Markdown
    text = re.sub(r"<h1[^>]*>", "\n\n# ", text)
    text = re.sub(r"<h2[^>]*>", "\n\n## ", text)
    text = re.sub(r"<h3[^>]*>", "\n\n### ", text)
    text = re.sub(r"</h[1-3]>", "\n\n", text)
    text = re.sub(r"<p>", "\n\n", text)
    text = re.sub(r"</p>", "\n\n", text)
    text = re.sub(r"<li>", "\n- ", text)
    text = re.sub(r"</li>", "", text)
    text = re.sub(r"<ul[^>]*>", "\n", text)
    text = re.sub(r"</ul>", "\n", text)
    text = re.sub(r"<ol[^>]*>", "\n", text)
    text = re.sub(r"</ol>", "\n", text)
    text = re.sub(r"<strong>", "**", text)
    text = re.sub(r"</strong>", "**", text)
    text = re.sub(r"<em>", "*", text)
    text = re.sub(r"</em>", "*", text)
    text = re.sub(r"<blockquote>", "\n\n> ", text)
    text = re.sub(r"</blockquote>", "\n\n", text)
    text = re.sub(r"<hr\s*/?>", "\n\n---\n\n", text)
    text = re.sub(r"<br\s*/?>", "\n", text)
    # Links: <a href="url">text</a> -> [text](url)
    text = re.sub(r'<a\s+href="([^"]+)"[^>]*>([^<]*)</a>', r"[\2](\1)", text)
    # href= ohne Anführungszeichen (selten)
    text = re.sub(r"<a\s+href=([^\s>]+)[^>]*>([^<]*)</a>", r"[\2](\1)", text)
    # Verbleibende Tags entfernen
    text = re.sub(r"<[^>]+>", "", text)
    # Mehrfache Leerzeilen reduzieren
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def format_timestamp(ts: str) -> str:
    """ISO-Timestamp in lesbares Format."""
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return ts


def main():
    input_path = Path(r"c:\Users\MtH\Downloads\MeineAktivitäten.json")
    output_path = Path(r"c:\MTHO_CORE\gemini.md")

    if not input_path.exists():
        print(f"Fehler: {input_path} nicht gefunden.")
        return 1

    print(f"Lade {input_path}...")
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        data = [data]

    lines = [
        "# Gemini-Aktivitäten (Meine Aktivitäten)",
        "",
        f"Exportiert aus Google Takeout. {len(data)} Einträge.",
        "",
        "---",
        "",
    ]

    for i, item in enumerate(data):
        title = item.get("title", "(Ohne Titel)")
        time_str = format_timestamp(item.get("time", ""))
        header = item.get("header", "Gemini-Apps")

        # Prompt-Titel bereinigen (z.B. "Eingegebener Prompt: ..." -> nur Inhalt)
        if title.startswith("Eingegebener Prompt: "):
            prompt = title[len("Eingegebener Prompt: ") :].strip()
        else:
            prompt = title

        lines.append(f"## Eintrag {i + 1}")
        lines.append("")
        lines.append(f"**Datum:** {time_str} | **Quelle:** {header}")
        lines.append("")
        lines.append("### Prompt")
        lines.append("")
        lines.append(prompt)
        lines.append("")

        # Antwort(en) aus safeHtmlItem
        safe_items = item.get("safeHtmlItem") or []
        if safe_items:
            lines.append("### Antwort")
            lines.append("")
            for block in safe_items:
                html_content = block.get("html", "")
                if html_content:
                    md = html_to_markdown(html_content)
                    if md:
                        lines.append(md)
                        lines.append("")

        # Optionale Hinweise
        if item.get("subtitles"):
            lines.append("*Audio enthalten.*")
            lines.append("")
        if item.get("attachedFiles"):
            lines.append(f"*Anhänge: {', '.join(item['attachedFiles'])}*")
            lines.append("")

        lines.append("---")
        lines.append("")

    out_text = "\n".join(lines)
    output_path.write_text(out_text, encoding="utf-8")
    print(f"Gespeichert: {output_path} ({len(out_text):,} Zeichen)")
    return 0


if __name__ == "__main__":
    exit(main())
