"""Delete old dashboard and create a fresh one with the fixed JSON."""
import base64
import json
import sys
import time

try:
    import requests
    from azure.identity import InteractiveBrowserCredential
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install",
                           "azure-identity", "requests", "--quiet"])
    import requests
    from azure.identity import InteractiveBrowserCredential

FABRIC_API = "https://api.fabric.microsoft.com/v1"
SCOPE = "https://api.fabric.microsoft.com/.default"
WS_ID = "<YOUR_WORKSPACE_ID>"
OLD_DASH_ID = "<YOUR_DASHBOARD_ID>"
DASHBOARD_JSON_FILE = "Healthcare_Nursing_Dashboard.json"
DASHBOARD_NAME = "Healthcare Nursing Dashboard v4"

print("Authenticating...")
credential = InteractiveBrowserCredential()
token = credential.get_token(SCOPE).token
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
print("Authenticated\n")

# Step 1: Delete old dashboard
print(f"Deleting old dashboard {OLD_DASH_ID}...")
del_resp = requests.delete(
    f"{FABRIC_API}/workspaces/{WS_ID}/items/{OLD_DASH_ID}",
    headers=headers
)
print(f"  Delete status: {del_resp.status_code}")
if del_resp.status_code not in (200, 204):
    print(f"  Warning: {del_resp.text[:300]}")
print("Waiting 10s for cleanup...")
time.sleep(10)

# Step 2: Load fresh JSON
print(f"\nLoading {DASHBOARD_JSON_FILE}...")
with open(DASHBOARD_JSON_FILE, "r") as f:
    dashboard_json = f.read()

# Verify dataSource
d = json.loads(dashboard_json)
ds = d["dataSources"][0]
print(f"  dataSource: {json.dumps(ds)}")

payload_b64 = base64.b64encode(dashboard_json.encode("utf-8")).decode("utf-8")

# Step 3: Create new dashboard
print(f"\nCreating fresh dashboard: '{DASHBOARD_NAME}'...")
create_body = {
    "displayName": DASHBOARD_NAME,
    "type": "KQLDashboard",
    "description": "Real-time monitoring of healthcare nursing operations",
    "definition": {
        "parts": [
            {
                "path": "RealTimeDashboard.json",
                "payload": payload_b64,
                "payloadType": "InlineBase64"
            }
        ]
    }
}

resp = requests.post(
    f"{FABRIC_API}/workspaces/{WS_ID}/items",
    headers=headers,
    json=create_body
)

if resp.status_code == 201:
    result = resp.json()
    print(f"Dashboard created!")
    print(f"  ID   : {result['id']}")
    print(f"  Name : {result['displayName']}")
    print(f"  URL  : https://app.fabric.microsoft.com/groups/{WS_ID}/dashboards/{result['id']}")

elif resp.status_code == 202:
    op_id = resp.headers.get("x-ms-operation-id", "")
    print(f"  Provisioning... (operation: {op_id})")
    for _ in range(30):
        time.sleep(2)
        poll = requests.get(f"{FABRIC_API}/operations/{op_id}", headers=headers)
        if poll.status_code == 200:
            status = poll.json().get("status", "")
            print(f"  Status: {status}")
            if status in ("Succeeded", "Completed"):
                result_resp = requests.get(f"{FABRIC_API}/operations/{op_id}/result", headers=headers)
                if result_resp.status_code == 200:
                    result = result_resp.json()
                    print(f"  Dashboard ID: {result.get('id', 'N/A')}")
                break
            elif status == "Failed":
                print(f"  Failed: {poll.json()}")
                sys.exit(1)
    print("Dashboard provisioned!")

else:
    print(f"Failed (HTTP {resp.status_code})")
    print(f"  {resp.text[:500]}")
