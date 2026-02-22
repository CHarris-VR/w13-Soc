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
