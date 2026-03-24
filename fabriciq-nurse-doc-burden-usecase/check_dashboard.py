"""Check real database ID and current dashboard definition in Fabric."""
import requests
import json
import base64
import time
import sys

try:
    from azure.identity import InteractiveBrowserCredential
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "azure-identity", "requests", "--quiet"])
    from azure.identity import InteractiveBrowserCredential

FABRIC_API = "https://api.fabric.microsoft.com/v1"
SCOPE = "https://api.fabric.microsoft.com/.default"
WS_ID = "<YOUR_WORKSPACE_ID>"
DASH_ID = "<YOUR_DASHBOARD_ID>"

cred = InteractiveBrowserCredential()
token = cred.get_token(SCOPE).token
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# 1. List KQL Databases
print("=== KQL Databases in workspace ===")
r = requests.get(f"{FABRIC_API}/workspaces/{WS_ID}/items?type=KQLDatabase", headers=headers)
r.raise_for_status()
for item in r.json().get("value", []):
    print(f"  {item['displayName']}  id={item['id']}")

# 2. List Eventhouses
print("\n=== Eventhouses in workspace ===")
r2 = requests.get(f"{FABRIC_API}/workspaces/{WS_ID}/items?type=Eventhouse", headers=headers)
r2.raise_for_status()
for item in r2.json().get("value", []):
    print(f"  {item['displayName']}  id={item['id']}")

# 3. Get current dashboard definition
print("\n=== Dashboard definition (from Fabric) ===")
r3 = requests.post(f"{FABRIC_API}/workspaces/{WS_ID}/items/{DASH_ID}/getDefinition", headers=headers)
print(f"Status: {r3.status_code}")

def show_definition(resp_json):
    parts = resp_json.get("definition", {}).get("parts", [])
    for p in parts:
        print(f"  Part: {p['path']}, payloadType: {p.get('payloadType')}")
        if p.get("payloadType") == "InlineBase64":
            decoded = json.loads(base64.b64decode(p["payload"]))
            ds = decoded.get("dataSources", [{}])[0]
            print("  Current dataSource in Fabric:")
            print(f"    {json.dumps(ds, indent=4)}")

if r3.status_code == 200:
    show_definition(r3.json())
elif r3.status_code == 202:
    op_id = r3.headers.get("x-ms-operation-id", "")
    print(f"  Long-running op: {op_id}")
    for _ in range(15):
        time.sleep(2)
        poll = requests.get(f"{FABRIC_API}/operations/{op_id}", headers=headers)
        if poll.status_code == 200:
            status = poll.json().get("status", "")
            print(f"  Status: {status}")
            if status in ("Succeeded", "Completed"):
                result = requests.get(f"{FABRIC_API}/operations/{op_id}/result", headers=headers)
                if result.status_code == 200:
                    show_definition(result.json())
                break
            elif status == "Failed":
                print(f"  Failed: {poll.json()}")
                break
else:
    print(f"  Response: {r3.text[:500]}")
