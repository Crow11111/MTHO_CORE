# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import os
import glob
import re
from datetime import datetime
import sys

def generate_anchor(text):
    """Generates a GitHub-style anchor for a given header text."""
    anchor = text.lower()
    anchor = re.sub(r'[^a-z0-9\s-]', '', anchor)
    anchor = re.sub(r'\s+', '-', anchor)
    return anchor

def compile_master(source_dir, output_filename, title, image_path=None):
    output_file = os.path.join(source_dir, output_filename)
    print(f"[CORE] Starte Kompilierung: {title} in {source_dir}...")

    # Get all markdown files except the output file itself
    all_files = sorted(glob.glob(os.path.join(source_dir, "*.md")))
    files_to_process = [f for f in all_files if os.path.basename(f) != output_filename]

    if not files_to_process:
        print(f"[ERROR] Keine Dokumente in {source_dir} gefunden.")
        return

    # 1. Header & Image
    master_content = []
    master_content.append(f"# {title}\n")
    master_content.append(f"**Generiert am:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    if image_path:
        master_content.append(f"![CORE Visual Context]({image_path})\n\n---\n")
    else:
        master_content.append("\n---\n")

    # 2. Table of Contents (TOC)
    toc = ["## Inhaltsverzeichnis\n"]
    sections = []

    print(f"[CORE] Verarbeite {len(files_to_process)} Dateien in {source_dir}...")

    for file_path in files_to_process:
        file_name = os.path.basename(file_path)
        display_name = file_name.replace(".md", "").replace("_", " ")
        anchor = generate_anchor(display_name)

        toc.append(f"- [{display_name}](#{anchor})")

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

            # Adjust headers: Shift all headers down by one level if they start with #
            content = re.sub(r'^(#+)', r'#\1', content, flags=re.MULTILINE)

            sections.append(f"\n<a name=\"{anchor}\"></a>\n# {display_name}\n\n{content}\n\n---\n")

    # Merge everything
    master_content.extend(toc)
    master_content.append("\n---\n")
    master_content.extend(sections)

    # Write output
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(master_content))
        print(f"[SUCCESS] Master-Dokument erstellt: {output_file}")
    except Exception as e:
        print(f"[ERROR] Fehler beim Schreiben des Master-Dokuments: {e}")

if __name__ == "__main__":
    # Standard targets for CORE
    targets = [
        ("docs/02_ARCHITECTURE", "00_CORE_ARCHITECTURE_MASTER.md", "CORE ARCHITECTURE MASTER PLAN", "../../CORE.png"),
        ("docs/03_INFRASTRUCTURE", "00_CORE_INFRASTRUCTURE_MASTER.md", "CORE INFRASTRUCTURE MASTER PLAN", "../../CORE.png"),
        ("docs/04_PROCESSES", "00_CORE_PROCESSES_MASTER.md", "CORE PROCESSES MASTER PLAN", "../../CORE.png")
    ]

    for src, out, title, img in targets:
        compile_master(src, out, title, img)
