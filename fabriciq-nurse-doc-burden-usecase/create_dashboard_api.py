"""
Create a Fabric Real-Time Dashboard via the Fabric REST API.

Authenticates via DefaultAzureCredential (browser login / Azure CLI),
finds the workspace containing medical_data_rt_store, and creates
a KQLDashboard item with all 21 tiles.

Usage:
    python create_dashboard_api.py
"""

import base64
import json
import sys
import time

try:
    import requests
    from azure.identity import InteractiveBrowserCredential
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install",
                           "azure-identity", "requests", "--quiet"])
    import requests
    from azure.identity import InteractiveBrowserCredential

# ─── Configuration ───────────────────────────────────────────────────────────
FABRIC_API = "https://api.fabric.microsoft.com/v1"
SCOPE = "https://api.fabric.microsoft.com/.default"
DASHBOARD_JSON_FILE = "Healthcare_Nursing_Dashboard.json"
DASHBOARD_NAME = "Healthcare Nursing Operations"
TARGET_DB = "medical_data_rt_store"   # find workspace containing this DB

# ─── Auth ────────────────────────────────────────────────────────────────────
print("🔐 Authenticating via browser...")
credential = InteractiveBrowserCredential()
token = credential.get_token(SCOPE).token
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
print("✅ Authenticated\n")

# ─── Find workspace ─────────────────────────────────────────────────────────
print("🔍 Finding workspace containing database:", TARGET_DB)
resp = requests.get(f"{FABRIC_API}/workspaces", headers=headers)
resp.raise_for_status()
workspaces = resp.json().get("value", [])

workspace_id = None
for ws in workspaces:
    ws_id = ws["id"]
    items_resp = requests.get(f"{FABRIC_API}/workspaces/{ws_id}/items?type=KQLDatabase", headers=headers)
    if items_resp.status_code == 200:
        for item in items_resp.json().get("value", []):
            if item["displayName"] == TARGET_DB:
                workspace_id = ws_id
                print(f"   Found in workspace: {ws['displayName']} ({ws_id})")
                break
    if workspace_id:
        break

if not workspace_id:
    print("❌ Could not find a workspace containing database:", TARGET_DB)
    print("   Available workspaces:")
    for ws in workspaces:
        print(f"     - {ws['displayName']} ({ws['id']})")
    sys.exit(1)

# ─── Load dashboard JSON ────────────────────────────────────────────────────
print(f"\n📄 Loading dashboard definition from {DASHBOARD_JSON_FILE}...")
with open(DASHBOARD_JSON_FILE, "r") as f:
    dashboard_json = f.read()

payload_b64 = base64.b64encode(dashboard_json.encode("utf-8")).decode("utf-8")
print(f"   Payload size: {len(dashboard_json)} bytes → {len(payload_b64)} base64 chars")

# ─── Check for existing dashboard ───────────────────────────────────────────
print(f"\n🔍 Checking for existing dashboard: '{DASHBOARD_NAME}'...")
existing_id = None
items_resp = requests.get(f"{FABRIC_API}/workspaces/{workspace_id}/items?type=KQLDashboard", headers=headers)
if items_resp.status_code == 200:
    for item in items_resp.json().get("value", []):
        if item["displayName"] == DASHBOARD_NAME:
            existing_id = item["id"]
            print(f"   Found existing dashboard: {existing_id}")
            break

definition_body = {
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

if existing_id:
    print(f"\n🔄 Updating existing dashboard definition...")
    resp = requests.post(
        f"{FABRIC_API}/workspaces/{workspace_id}/items/{existing_id}/updateDefinition",
        headers=headers,
        json=definition_body
    )
else:
    print(f"\n🚀 Creating Real-Time Dashboard: '{DASHBOARD_NAME}'...")
    create_body = {
        "displayName": DASHBOARD_NAME,
        "type": "KQLDashboard",
        "description": "Real-time monitoring of healthcare nursing operations across 5 data streams",
        **definition_body
    }
    resp = requests.post(
        f"{FABRIC_API}/workspaces/{workspace_id}/items",
        headers=headers,
        json=create_body
    )

action = "Updated" if existing_id else "Created"
dashboard_id = existing_id

if resp.status_code in (200, 201):
    result = resp.json() if resp.text else {}
    dashboard_id = result.get("id", existing_id)
    print(f"✅ Dashboard {action.lower()} successfully!")
    if dashboard_id:
        print(f"   ID   : {dashboard_id}")
    print(f"   Name : {DASHBOARD_NAME}")
    dashboard_url = f"https://app.fabric.microsoft.com/groups/{workspace_id}/dashboards/{dashboard_id}"
    print(f"\n🔗 Open dashboard: {dashboard_url}")

elif resp.status_code == 202:
    # Long-running operation
    op_url = resp.headers.get("Location", "")
    op_id = resp.headers.get("x-ms-operation-id", "")
    print(f"   Provisioning in progress (operation: {op_id})...")

    # Poll for completion
    for _ in range(30):
        time.sleep(2)
        poll = requests.get(f"{FABRIC_API}/operations/{op_id}", headers=headers)
        if poll.status_code == 200:
            status = poll.json().get("status", "")
            print(f"   Status: {status}")
            if status in ("Succeeded", "Completed"):
                # Get the result
                result_resp = requests.get(f"{FABRIC_API}/operations/{op_id}/result", headers=headers)
                if result_resp.status_code == 200:
                    result = result_resp.json()
                    print(f"\n✅ Dashboard created!")
                    print(f"   ID: {result.get('id', 'N/A')}")
                break
            elif status == "Failed":
                print(f"❌ Dashboard creation failed")
                print(f"   {poll.json()}")
                sys.exit(1)

    print("\n✅ Dashboard provisioned!")

else:
    print(f"❌ Failed to create dashboard (HTTP {resp.status_code})")
    print(f"   Response: {resp.text}")
    print("\n💡 Fallback: Import the JSON manually:")
    print(f"   1. Create a new Real-Time Dashboard in Fabric")
    print(f"   2. Switch to Edit mode")
    print(f"   3. Manage tab → 'Replace with file'")
    print(f"   4. Select '{DASHBOARD_JSON_FILE}'")
