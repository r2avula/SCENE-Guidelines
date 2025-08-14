import pandas as pd
import re
from tabulate import tabulate

# Load the issue body
with open("issue_body.txt", "r", encoding="utf-8") as f:
    body = f.read()


def extract(field):
    """Extract field values from GitHub issue form text."""
    match = re.search(rf"{field}\n\n(.*)", body)
    return match.group(1).strip() if match else ""


entry = {
    "Study": extract("Study ID"),
    "Year": extract("Year"),
    "Domain": extract("Domain"),
    "TRL": extract("TRL"),
    "AI": extract("AI-based"),
    "Targeted Threats": extract("Targeted Threats"),
    "Attack Scenarios": extract("Attack Scenarios"),
    "Evaluation Method": extract("Evaluation Method"),
}

# Append entry to CSV
df = pd.read_csv("slr.csv")
df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
df.to_csv("slr.csv", index=False)

# Update README table between markers
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
