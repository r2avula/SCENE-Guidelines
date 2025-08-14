import json
from pathlib import Path
import yaml

# Load JSON lists
domains = json.loads(Path("./config/domains.json").read_text())
attack_scenarios = json.loads(Path("./config/attack_scenarios.json").read_text())

# Append an 'Other' and 'NA' option
domains.extend(["Other (please specify below)", "NA"])
attack_scenarios.append("NA")

# Define YAML template
form = {
    "name": "Add SLR Entry",
    "description": "Submit a new study for inclusion in the SLR",
    "title": "[SLR Entry] ",
    "labels": ["slr-entry"],
    "body": [
        {
            "type": "input",
            "id": "doi",
            "attributes": {"label": "DOI", "placeholder": "10.5281/zenodo.XXXXXXX"},
            "validations": {"required": True},
        },
        {
            "type": "input",
            "id": "year",
            "attributes": {"label": "Year"},
            "validations": {"required": True},
        },
        {
            "type": "dropdown",
            "id": "domain",
            "attributes": {"label": "Domain", "options": domains},
            "validations": {"required": True},
        },
        {
            "type": "dropdown",
            "id": "trl",
            "attributes": {"label": "TRL", "options": ["1-3", "4-6", "7-9", "NA"]},
            "validations": {"required": True},
        },
        {
            "type": "dropdown",
            "id": "ai",
            "attributes": {"label": "AI-based", "options": ["Yes", "No"]},
            "validations": {"required": True},
        },
        {
            "type": "dropdown",
            "id": "targeted_threats",
            "attributes": {
                "label": "Targeted Threats",
                "multiple": True,
                "options": [
                    "S (Spoofing)",
                    "T (Tampering)",
                    "R (Repudiation)",
                    "I (Information Disclosure)",
                    "D (Denial of Service)",
                    "E (Elevation of Privilege)",
                    "NA",
                ],
            },
            "validations": {"required": True},
        },
        {
            "type": "dropdown",
            "id": "attack_scenarios",
            "attributes": {
                "label": "Attack Scenarios",
                "multiple": True,
                "options": attack_scenarios,
            },
            "validations": {"required": True},
        },
        {
            "type": "dropdown",
            "id": "evaluation_method",
            "attributes": {
                "label": "Evaluation Method",
                "multiple": True,
                "options": ["Empirical", "Analytical", "Simulation", "NA"],
            },
            "validations": {"required": True},
        },
        {
            "type": "input",
            "id": "other_specify",
            "attributes": {"label": "If 'Other', please specify here"},
            "validations": {"required": False},
        },
    ],
}

# Save YAML into .github/ISSUE_TEMPLATE/
output_path = Path(".github/ISSUE_TEMPLATE/add_slr_entry.yml")
output_path.parent.mkdir(parents=True, exist_ok=True)

with output_path.open("w") as f:
    yaml.dump(form, f, sort_keys=False)

print(f"Issue form generated: {output_path}")
