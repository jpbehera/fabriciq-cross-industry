"""Check current dashboard definition and re-push corrected version."""
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
JSON_FILE = "Healthcare_Nursing_Dashboard.json"

cred = InteractiveBrowserCredential()
token = cred.get_token(SCOPE).token
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def wait_for_operation(op_id):
    """Poll a long-running operation until it completes."""
    for _ in range(30):
        time.sleep(2)
        poll = requests.get(f"{FABRIC_API}/operations/{op_id}", headers=headers)
        if poll.status_code == 200:
            status = poll.json().get("status", "")
            print(f"  Poll status: {status}")
            if status in ("Succeeded", "Completed"):
                result = requests.get(f"{FABRIC_API}/operations/{op_id}/result", headers=headers)
                return result
            elif status == "Failed":
                print(f"  FAILED: {poll.json()}")
                return None
    print("  Timed out waiting for operation")
    return None


def decode_definition(resp_json):
    """Extract and decode the dashboard JSON from API response."""
    parts = resp_json.get("definition", {}).get("parts", [])
    for p in parts:
        if p.get("payloadType") == "InlineBase64":
            return json.loads(base64.b64decode(p["payload"]))
    return None


# === Step 1: List databases to confirm real IDs ===
print("=== KQL Databases in workspace ===")
r = requests.get(f"{FABRIC_API}/workspaces/{WS_ID}/items?type=KQLDatabase", headers=headers)
r.raise_for_status()
db_map = {}
for item in r.json().get("value", []):
    print(f"  {item['displayName']}  id={item['id']}")
    db_map[item['displayName']] = item['id']

real_db_id = db_map.get("medical_data_rt_store", "")
print(f"\nReal database ID for medical_data_rt_store: {real_db_id}")

# === Step 2: Get current dashboard definition ===
print("\n=== Getting current dashboard definition ===")
r3 = requests.post(f"{FABRIC_API}/workspaces/{WS_ID}/items/{DASH_ID}/getDefinition", headers=headers)
print(f"Status: {r3.status_code}")

current_def = None
if r3.status_code == 200:
    current_def = decode_definition(r3.json())
elif r3.status_code == 202:
    op_id = r3.headers.get("x-ms-operation-id", "")
    result = wait_for_operation(op_id)
    if result and result.status_code == 200:
        current_def = decode_definition(result.json())

if current_def:
    ds = current_def.get("dataSources", [{}])[0]
    print(f"Current dataSource in Fabric:")
    print(f"  {json.dumps(ds, indent=2)}")
else:
    print("Could not retrieve current definition")

# === Step 3: Load local corrected JSON and verify ===
print(f"\n=== Loading local {JSON_FILE} ===")
with open(JSON_FILE, "r") as f:
    local_json = json.load(f)

local_ds = local_json["dataSources"][0]
print(f"Local dataSource:")
print(f"  {json.dumps(local_ds, indent=2)}")

# Fix if needed: ensure scopeId = real database ID and kind = kusto-trident
needs_fix = False
if local_ds.get("scopeId") != real_db_id:
    print(f"\n  FIX: scopeId {local_ds.get('scopeId')} -> {real_db_id}")
    local_ds["scopeId"] = real_db_id
    needs_fix = True
if local_ds.get("kind") != "kusto-trident":
    print(f"  FIX: kind {local_ds.get('kind')} -> kusto-trident")
    local_ds["kind"] = "kusto-trident"
    needs_fix = True

if needs_fix:
    # Save the fixed JSON locally too
    with open(JSON_FILE, "w") as f:
        json.dump(local_json, f, indent=2)
    print(f"  Saved fixed JSON to {JSON_FILE}")

# === Step 4: Push updated definition ===
print("\n=== Pushing updated definition to Fabric ===")
payload_b64 = base64.b64encode(json.dumps(local_json).encode("utf-8")).decode("utf-8")

update_body = {
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

r4 = requests.post(
    f"{FABRIC_API}/workspaces/{WS_ID}/items/{DASH_ID}/updateDefinition",
    headers=headers,
    json=update_body
)

print(f"Update status: {r4.status_code}")
if r4.status_code == 200:
    print("Definition updated successfully!")
elif r4.status_code == 202:
    op_id = r4.headers.get("x-ms-operation-id", "")
    print(f"Long-running update, polling...")
    result = wait_for_operation(op_id)
    if result:
        print("Definition updated successfully!")
    else:
        print("Update may have failed")
else:
    print(f"Error: {r4.text[:500]}")

# === Step 5: Verify ===
print("\n=== Verifying updated definition ===")
time.sleep(3)
r5 = requests.post(f"{FABRIC_API}/workspaces/{WS_ID}/items/{DASH_ID}/getDefinition", headers=headers)
verified_def = None
if r5.status_code == 200:
    verified_def = decode_definition(r5.json())
elif r5.status_code == 202:
    op_id = r5.headers.get("x-ms-operation-id", "")
    result = wait_for_operation(op_id)
    if result and result.status_code == 200:
        verified_def = decode_definition(result.json())

if verified_def:
    ds = verified_def.get("dataSources", [{}])[0]
    print(f"Verified dataSource:")
    print(f"  {json.dumps(ds, indent=2)}")
    print(f"\nDone! Refresh your dashboard at:")
    print(f"  https://app.fabric.microsoft.com/groups/{WS_ID}/dashboards/{DASH_ID}")
else:
    print("Could not verify - try opening the dashboard anyway")
