"""Search for mystery entity ID in workspace."""
import requests
import json
import sys

try:
    from azure.identity import InteractiveBrowserCredential
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "azure-identity", "requests", "--quiet"])
    from azure.identity import InteractiveBrowserCredential

FABRIC_API = "https://api.fabric.microsoft.com/v1"
WS_ID = "<YOUR_WORKSPACE_ID>"
TARGET = "<YOUR_ENTITY_ID>"

cred = InteractiveBrowserCredential()
token = cred.get_token("https://api.fabric.microsoft.com/.default").token
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

print(f"Searching for entity: {TARGET}\n")

r = requests.get(f"{FABRIC_API}/workspaces/{WS_ID}/items", headers=headers)
r.raise_for_status()
items = r.json().get("value", [])
print(f"Total items in workspace: {len(items)}\n")

found = False
for item in items:
    if item["id"] == TARGET:
        print(f"FOUND: {item['displayName']}  type={item['type']}  id={item['id']}")
        found = True
    if item["type"] in ("KQLDatabase", "Eventhouse", "KQLDashboard"):
        print(f"  [{item['type']}] {item['displayName']}  id={item['id']}")

if not found:
    print(f"\nEntity {TARGET} NOT found in workspace items")

# Also try to directly GET the entity
print(f"\nTrying direct GET for {TARGET}...")
r2 = requests.get(f"{FABRIC_API}/workspaces/{WS_ID}/items/{TARGET}", headers=headers)
print(f"  Status: {r2.status_code}")
if r2.status_code == 200:
    print(f"  Found: {r2.json()}")
else:
    print(f"  Response: {r2.text[:300]}")
