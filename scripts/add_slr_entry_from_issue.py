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
fault_injection_other = extract_field(
    "If Fault Injection is 'Other', please specify below new fault Injection types separated by commas (new ID will be automatically generated)"
)
raw_threats = extract_field("Targeted Threats")
threats_list = [t.strip() for t in re.split(r"[,\n]", raw_threats) if t.strip()]
threats_codes = [re.match(r"^\w", t).group(0) for t in threats_list]
targeted_threats_str = ", ".join(threats_codes)

# --- Process Fault Injections ---
raw_fi = extract_field("Fault Injection")
fi_list = [t.strip() for t in re.split(r"[,\n]", raw_fi) if t.strip()]

# Extract just the Tx codes (like T1, T2, ...) for selected options
fi_codes = []
for fi in fi_list:
    match = re.match(r"^(T\d+)", fi)
    if match:
        fi_codes.append(match.group(1))

# Handle 'Other' entries
if fault_injection_other:
    # Split by comma if user added multiple new types
    new_fis = [t.strip() for t in fault_injection_other.split(",") if t.strip()]
    # Determine the next Tx number
    existing_numbers = [
        int(re.match(r"T(\d+)", x).group(1))
        for x in fault_injections
        if re.match(r"T\d+", x)
    ]
    next_number = max(existing_numbers, default=0) + 1

    for new_fi in new_fis:
        new_tx = f"T{next_number} ({new_fi})"
        if new_tx not in fault_injections:
            fault_injections.append(new_tx)
            next_number += 1
        fi_codes.append(re.match(r"(T\d+)", new_tx).group(1))

    # Save updated JSON
    fault_injections_path.write_text(json.dumps(fault_injections, indent=2))

# Combine selected Tx codes as comma-separated string
fault_injections_str = ", ".join(fi_codes)


# --- Update JSON lists if 'Other' is specified ---
if domain_other:
    if domain_other not in domains:
        domains.append(domain_other)
        domains_path.write_text(json.dumps(domains, indent=2))
    domain_selected = domain_other

entry = {
    "DOI": extract_field("DOI"),
    "Year": extract_field("Year"),
    "Domain": domain_selected,
    "TRL": extract_field("TRL"),
    "AI": extract_field("AI-based"),
    "Targeted Threats": targeted_threats_str,
    "Attack Scenarios": extract_field("Attack Scenarios"),
    "Fault Injection": fault_injections_str,
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
df.to_csv("slr.csv", index=False, na_rep="NA")

# --- Debug print of updated CSV ---
print("\n--- UPDATED CSV CONTENT ---")
print(tabulate(df, headers="keys", tablefmt="pretty", showindex=False))
print("--------------------------------\n")
