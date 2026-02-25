import requests
import os
print("Running from:", os.getcwd()) # Added this to check the current working directory for debugging purposes.
BASE_DIR = os.path.dirname(__file__)
API_URL = "https://my.api.mockaroo.com/ironclad-soc-case-artifacts"

headers = {
    "X-API-Key": os.environ.get("MOCKAROO_API_KEY")  
}

response = requests.get(API_URL, headers=headers, timeout=10)
print("Status:", response.status_code) 

if response.status_code != 200:
    print("Request failed:", response.text[:200])
    raise SystemExit

data = response.json()
print("JSON type:", type(data))
print("Records:", len(data) if isinstance(data, list) else "N/A")

# Preview first record
if isinstance(data, list) and data:
    print("First record preview:")
    print(data[0])
else:
    print("Unexpected JSON structure. Expected a list of records.")
    raise SystemExit

# Checkpoint time: 2026-02-21 4:27 PM
# Chcekpoint time: 2026-02-21 4:51 PM Failure due to API key issue. Please check the yAPIk
# File and ensure it contains a valid API key.
# Success time: 2026-02-21 8:12 PM - API key issue resolved, data successfully retrieved and printed.

if isinstance(data[0], dict):
    print("\nFields in record:")
    for k in data[0].keys():
        print("-", k)

# Checkpoint time: 2026-02-22 5:06 PM 
# Success time: 2026-02-22 5:08 PM - Verified fields in the first record.

from enum import Enum

class Severity(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class CaseStatus(Enum):
    NEW = "NEW"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"
    FALSE_POSITIVE = "FALSE_POSITIVE"

# Checkpoint time: 2026-02-22 5:09 PM

class Artifact:
    def __init__(self, raw: dict):
        self.raw = raw

        # TODO: Replace these keys with the actual JSON field names
        self.case_id = raw.get("case_id", "UNKNOWN_CASE")
        self.indicator_type = raw.get("indicator_type", "unknown")
        
        # Map the indicator_type to the correct field in the JSON.
        field_mapping = {
            "ip": "ip",
            "domain": "domain",
            "file_hash": "file_hash",
        }
        # Use the mapping to get the correct value based on the indicator_type.
        key = field_mapping.get(self.indicator_type)
        self.value = raw.get(key, "") if key else ""

        self.comment = raw.get("comment", "")

    def is_internal_ip(self) -> bool:
        # only relevant if indicator_type indicates an IP
        if self.indicator_type != "ip":
            return False
        return self.value.startswith(("10.", "192.168."))

    def __str__(self) -> str:
        extra = f" ({self.comment})" if self.comment else ""
        return f"{self.indicator_type}: {self.value}{extra}"
    

# Checkpoint time: 2026-02-22 6:11 PM - Implemented the Artifact class with basic fields and methods.
# Checkpoint time: 2026-02-22 6:21 PM - Fixed things with the Artifact. Trying to solve for line 65 at the moment. 
# Success time: 2026-02-22 6:40 PM - Successfully created an Artifact instance and printed it.

# print()
# test_artifact = Artifact(data[0])
# print(test_artifact)

class Case:
    def __init__(self, case_id: str):
        self.case_id = case_id
        self.status = CaseStatus.NEW
        self.severity = Severity.LOW
        self.artifacts: list[Artifact] = []
        self.notes: list[str] = []

    def add_artifact(self, artifact: Artifact):
        self.artifacts.append(artifact)
        self.recalculate_severity()

    def add_note(self, note: str):
        self.notes.append(note)

    def recalculate_severity(self):
        # Simple rules (you may adjust based on your data):
        # HIGH if any file hash present
        # MEDIUM if any external IP or suspicious domain keyword
        # LOW otherwise


        #Testing to see if has_hash is working. 2026-02-23 5:24 PM.
        # Success time: 2026-02-24 PM - Successfully implemented severity calculation based on artifacts. Cases with file hashes are now marked as HIGH severity. 
        has_hash = any(
            a.indicator_type in ["file_hash", "hash", "sha256"] and a.value.strip() != ""
            for a in self.artifacts
        )
        if has_hash:
            self.severity = Severity.HIGH
        return
        
        
        # Since that artifact_type was changed to indicator_type, I updated the code to reflect that change.
        has_external_ip = any(
            a.indicator_type == "ip" and not a.is_internal_ip()
            for a in self.artifacts
        )
        has_suspicious_domain = any(
            a.indicator_type == "domain" and any(word in a.value.lower() for word in ["login", "verify", "secure"])
            for a in self.artifacts
        )

        if has_external_ip or has_suspicious_domain:
            self.severity = Severity.MEDIUM
        else:
            self.severity = Severity.LOW

    def summary(self) -> str:
        return f"{self.case_id} | {self.status.value} | {self.severity.value} | artifacts={len(self.artifacts)}"

    def __str__(self) -> str:
        lines = [self.summary(), "-" * 48, "Artifacts:"]
        for a in self.artifacts:
            lines.append(f"  - {a}")
        if self.notes:
            lines.append("Notes:")
            for n in self.notes:
                lines.append(f"  * {n}")
        return "\n".join(lines)
    
cases_by_id = {}

for record in data:
    artifact = Artifact(record)

    if artifact.case_id not in cases_by_id:
        cases_by_id[artifact.case_id] = Case(artifact.case_id)

    cases_by_id[artifact.case_id].add_artifact(artifact)

# Checkpoint time: 2026-02-23 4:31 PM - Implemented the Case class and logic to group artifacts into cases.
# Success time: 2026-02-23 4:44 PM - Successfully created cases and printed summaries for each case.
print("\n=== Case Summaries ===")
severity_rank = {Severity.HIGH: 3,
                 Severity.MEDIUM: 2,
                 Severity.LOW: 1
}

sorted_cases = sorted(
    cases_by_id.values(),
    key=lambda c: severity_rank[c.severity],
    reverse=True # Sort by severity descending
)
# Testing to see if the cases are being sorted by severity correctly. 2026-02-23 5:25 PM.
from collections import Counter

severity_counts = Counter(c.severity for c in cases_by_id.values())

print("\n=== Severity Totals ===")
print("HIGH:", severity_counts.get(Severity.HIGH, 0))
print("MEDIUM:", severity_counts.get(Severity.MEDIUM, 0))
print("LOW:", severity_counts.get(Severity.LOW, 0))
for c in sorted_cases:
    print(c.summary())

with open("case_report.txt", "w", encoding="utf-8") as out:
    for c in cases_by_id.values():
        out.write(str(c))
        out.write("\n\n")

print("\nWrote report to case_report.txt")

# Checkpoint time: 2026-02-23 4:45 PM - Added code to write detailed case reports to a text file.
# Success time: 2026-02-23 4:55 PM - Successfully wrote detailed case reports to case_report.txt.