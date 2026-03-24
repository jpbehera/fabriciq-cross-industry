"""Fetch definition of a working dashboard to compare dataSource format."""
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
WS_ID = "<YOUR_WORKSPACE_ID>"

cred = InteractiveBrowserCredential()
token = cred.get_token("https://api.fabric.microsoft.com/.default").token
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# Working dashboards to compare
dashboards = {
    "MOnitoring_dashboard": "<YOUR_DASHBOARD_ID>",
    "IoT Sensor Real-Time Dashboard": "<YOUR_DASHBOARD_ID>",
    "Healthcare Nursing Dashboard v3": "<YOUR_DASHBOARD_ID>",
}


def get_definition(dash_id, dash_name):
    print(f"\n{'='*60}")
    print(f"Dashboard: {dash_name} ({dash_id})")
    print(f"{'='*60}")
    r = requests.post(
        f"{FABRIC_API}/workspaces/{WS_ID}/items/{dash_id}/getDefinition",
        headers=headers
    )
    print(f"Status: {r.status_code}")

    if r.status_code == 200:
        return decode(r.json())
    elif r.status_code == 202:
        op_id = r.headers.get("x-ms-operation-id", "")
        for _ in range(15):
            time.sleep(2)
            poll = requests.get(f"{FABRIC_API}/operations/{op_id}", headers=headers)
            if poll.status_code == 200:
                status = poll.json().get("status", "")
                if status in ("Succeeded", "Completed"):
                    result = requests.get(
                        f"{FABRIC_API}/operations/{op_id}/result", headers=headers
                    )
                    if result.status_code == 200:
                        return decode(result.json())
                    break
                elif status == "Failed":
                    print(f"  Failed: {poll.json()}")
                    break
    else:
        print(f"  Error: {r.text[:300]}")
    return None


def decode(resp_json):
    parts = resp_json.get("definition", {}).get("parts", [])
    for p in parts:
        if p.get("payloadType") == "InlineBase64":
            return json.loads(base64.b64decode(p["payload"]))
    return None


for name, did in dashboards.items():
    defn = get_definition(did, name)
    if defn:
        # Show dataSources
        print(f"\n  dataSources ({len(defn.get('dataSources', []))}):")
        for ds in defn.get("dataSources", []):
            print(f"    {json.dumps(ds, indent=6)}")

        # Show first tile's properties (especially dataSourceId)
        tiles = defn.get("tiles", [])
        print(f"\n  Tiles: {len(tiles)}")
        if tiles:
            t = tiles[0]
            print(f"  First tile keys: {list(t.keys())}")
            print(f"  First tile dataSourceId: {t.get('dataSourceId')}")
            # Show full first tile for comparison
            print(f"  First tile (abbreviated):")
            for k in ["id", "title", "dataSourceId", "usedParamVariables"]:
                if k in t:
                    print(f"    {k}: {t[k]}")

        # Show schema version
        print(f"\n  schema_version: {defn.get('schema_version')}")
        print(f"  $schema: {defn.get('$schema', 'N/A')}")
