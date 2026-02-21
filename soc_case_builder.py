import requests
import os
print("Running from:", os.getcwd()) # Added this to check the current working directory for debugging purposes.
BASE_DIR = os.path.dirname(__file__)
API_URL = "https://my.api.mockaroo.com/ironclad-soc-case-artifacts"

headers = {
    "X-API-Key": os.environ.get("yAPIk")
}

response = requests.get(API_URL, timeout=10)
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

#Checkpoint time: 2024-21-26 4:27 PM
#Chcekpoint time: 2024-21-26 4:51 PM Failure due to API key issue. Please check the yAPIk
# file and ensure it contains a valid API key.