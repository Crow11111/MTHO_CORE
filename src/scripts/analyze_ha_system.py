import json
import os
from collections import Counter
from datetime import datetime

class HomeAssistantAnalyzer:
    def __init__(self, data_dir="data/home_assistant"):
        self.data_dir = data_dir
        self.states = self._load_json("states.json")
        self.config = self._load_json("config.json")
        self.services = self._load_json("services.json")
        self.automations = self._load_json("automations_derived.json")
        self.scripts = self._load_json("scripts_derived.json")

    def _load_json(self, filename):
        path = os.path.join(self.data_dir, filename)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return [] if "json" in filename else {}

    def analyze_entities(self):
        domains = [s["entity_id"].split(".")[0] for s in self.states]
        return Counter(domains)

    def analyze_integrations(self):
        # Infer integrations from entity naming conventions or attributes (heuristic)
        # This is a basic estimation.
        integrations = set()
        if isinstance(self.config, dict) and "components" in self.config:
             return self.config["components"]
        return list(integrations)

    def generate_report(self, output_file="docs/system_analysis.md"):
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        domain_counts = self.analyze_entities()
        integrations = self.analyze_integrations()
        
        report = []
        report.append("# Home Assistant System Analysis")
        report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Version:** {self.config.get('version', 'Unknown')}")
        report.append(f"**Location:** {self.config.get('location_name', 'Unknown')}")
        report.append("")

        report.append("## 1. System Overview")
        report.append(f"- **Total Entities:** {len(self.states)}")
        report.append(f"- **Automations:** {len(self.automations)}")
        report.append(f"- **Scripts:** {len(self.scripts)}")
        report.append(f"- **Integrations/Components:** {len(integrations)}")
        report.append("")

        report.append("## 2. Entity Breakdown by Domain")
        report.append("| Domain | Count |")
        report.append("| :--- | :--- |")
        for domain, count in domain_counts.most_common():
             report.append(f"| `{domain}` | {count} |")
        report.append("")

        report.append("## 3. Notable Integrations")
        report.append("Based on installed components:")
        # List top 20 components for brevity if too many
        for component in sorted(integrations)[:50]: 
            report.append(f"- {component}")
        if len(integrations) > 50:
            report.append(f"... and {len(integrations) - 50} more.")
        report.append("")

        report.append("## 4. Automation Summary")
        report.append(f"Found {len(self.automations)} automations.")
        if self.automations:
             report.append("| Automation Name | State | Last Triggered |")
             report.append("| :--- | :--- | :--- |")
             for auto in self.automations:
                 attrs = auto.get("attributes", {})
                 name = attrs.get("friendly_name", auto["entity_id"])
                 state = auto.get("state", "unknown")
                 last_triggered = attrs.get("last_triggered")
                 report.append(f"| {name} | {state} | {last_triggered} |")
        report.append("")

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(report))
        
        print(f"Report generated at: {output_file}")

if __name__ == "__main__":
    analyzer = HomeAssistantAnalyzer()
    analyzer.generate_report()
