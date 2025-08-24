import pandas as pd
import re
import json
import os
from pathlib import Path
from tabulate import tabulate

# Load the issue body from environment variable (preferred) or file
body = os.environ.get("ISSUE_BODY", "")
if not body:
    with open("issue_body.txt", "r", encoding="utf-8") as f:
        body = f.read()

print("\n--- RAW ISSUE BODY ---")
print(body)
print("----------------------\n")


def extract_single(field_label):
    pattern = rf"(?:^|\n)###\s+{re.escape(field_label)}\s*\n\n([^\n]+)"
    match = re.search(pattern, body)
    if match:
        value = match.group(1).strip().strip("_")
        if value.lower() == "no response":
            return ""
        return value
    return ""


def extract_multi(field_label):
    pattern = rf"(?:^|\n)###\s+{re.escape(field_label)}\s*\n\n((?:- .*\n?)+)"
    match = re.search(pattern, body)
    if match:
        items = [
            line.strip("- ").strip()
            for line in match.group(1).splitlines()
            if line.strip()
        ]
        return ", ".join(items)
    return ""


# --- Load config files ---
domains_path = Path("./config/domains.json")
attack_scenarios_path = Path("./config/attack_scenarios.json")

domains = json.loads(domains_path.read_text())
attack_scenarios = json.loads(attack_scenarios_path.read_text())

# --- Extract fields from issue ---
domain_selected = extract_single("Domain")
domain_other = extract_single("If Domain is 'Other', please specify below")
attack_selected = extract_single("Attack Scenarios")
attack_other = extract_single("If Attack Scenarios is 'Other', please specify below")

# --- Update JSON lists if 'Other' is specified ---
if domain_other:
    if domain_other not in domains:
        domains.insert(-2, domain_other)
        domains_path.write_text(json.dumps(domains, indent=2))
    domain_selected = domain_other

if attack_other:
    if attack_other not in attack_scenarios:
        attack_scenarios.insert(-2, attack_other)
        attack_scenarios_path.write_text(json.dumps(attack_scenarios, indent=2))
    attack_selected = attack_selected.replace(
        "Other (please specify below)", attack_other
    )

entry = {
    "DOI": extract_single("DOI"),
    "Year": extract_single("Year"),
    "Domain": domain_selected,
    "TRL": extract_single("TRL"),
    "AI-based": extract_single("AI-based"),
    "Targeted Threats": extract_single("Targeted Threats"),
    "Attack Scenarios": attack_selected,
    "Evaluation Method": extract_single("Evaluation Method"),
}

# --- Debug print ---
print("\n--- EXTRACTED VALUES ---")
for k, v in entry.items():
    print(f"{k}: {v}")
print("------------------------\n")

# --- Append to CSV ---
df = pd.read_csv("slr.csv")
df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
df.to_csv("slr.csv", index=False)

# --- Update README table ---
table_md = tabulate(df, headers="keys", tablefmt="github")
start_marker = "<!-- SLR_TABLE_START -->"
end_marker = "<!-- SLR_TABLE_END -->"

with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

readme = re.sub(
    f"{start_marker}.*?{end_marker}",
    f"{start_marker}\n\n{table_md}\n\n{end_marker}",
    readme,
    flags=re.S,
)

with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme)
