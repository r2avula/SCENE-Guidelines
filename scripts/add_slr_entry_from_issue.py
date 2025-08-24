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


def extract_field(field_label):
    pattern = rf"(?:^|\n)###\s+{re.escape(field_label)}\s*\n\n([^\n]+)"
    match = re.search(pattern, body)
    if match:
        value = match.group(1).strip().strip("_")
        if value.lower() == "no response":
            return ""
        return value
    return ""


# --- Load config files ---
domains_path = Path("./config/domains.json")
fault_injections_path = Path("./config/fault_injections.json")

domains = json.loads(domains_path.read_text())
fault_injections = json.loads(fault_injections_path.read_text())

# --- Extract fields from issue ---
domain_selected = extract_field("Domain")
domain_other = extract_field("If Domain is 'Other', please specify below")
fault_injections_selected = extract_field("Fault Injection")
fault_injection_other = extract_field(
    "If Fault Injection is 'Other', please specify below"
)
raw_threats = extract_field("Targeted Threats")
targeted_threats_list = [
    t.strip() for t in re.split(r"[,\n]", raw_threats) if t.strip()
]
targeted_threats_str = ",".join(targeted_threats_list)

# --- Update JSON lists if 'Other' is specified ---
if domain_other:
    if domain_other not in domains:
        domains.insert(-2, domain_other)
        domains_path.write_text(json.dumps(domains, indent=2))
    domain_selected = domain_other

if fault_injection_other:
    if fault_injection_other not in fault_injections:
        fault_injections.insert(-2, fault_injection_other)
        fault_injections_path.write_text(json.dumps(fault_injections, indent=2))
    fault_injections_selected = fault_injection_other

entry = {
    "DOI": extract_field("DOI"),
    "Year": extract_field("Year"),
    "Domain": domain_selected,
    "TRL": extract_field("TRL"),
    "AI": extract_field("AI-based"),
    "Targeted Threats": targeted_threats_str,
    "Attack Scenarios": extract_field("Attack Scenarios"),
    "Fault Injection": fault_injections_selected,
    "Evaluation Method": extract_field("Evaluation Method"),
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

# --- Debug print of updated CSV ---
print("\n--- UPDATED CSV CONTENT ---")
print(tabulate(df, headers="keys", tablefmt="pretty", showindex=False))
print("--------------------------------\n")
