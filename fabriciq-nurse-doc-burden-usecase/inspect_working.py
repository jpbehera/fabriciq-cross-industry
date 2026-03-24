"""Get full tile structure from a working dashboard."""
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
# Use the IoT dashboard as reference (smaller, simpler)
DASH_ID = "<YOUR_DASHBOARD_ID>"

cred = InteractiveBrowserCredential()
token = cred.get_token("https://api.fabric.microsoft.com/.default").token
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

r = requests.post(f"{FABRIC_API}/workspaces/{WS_ID}/items/{DASH_ID}/getDefinition", headers=headers)
parts = r.json().get("definition", {}).get("parts", [])

for p in parts:
    if p.get("payloadType") == "InlineBase64":
        defn = json.loads(base64.b64decode(p["payload"]))
        
        # Print full structure overview
        print("Top-level keys:", list(defn.keys()))
        print()
        
        # Print full dataSource
        print("=== dataSources ===")
        print(json.dumps(defn["dataSources"], indent=2))
        
        # Print pages
        print("\n=== pages ===")
        print(json.dumps(defn.get("pages", []), indent=2))
        
        # Print first 2 tiles fully
        tiles = defn.get("tiles", [])
        print(f"\n=== First 2 of {len(tiles)} tiles ===")
        for t in tiles[:2]:
            print(json.dumps(t, indent=2))
            print("---")
        
        # Print queries if they exist as separate section
        if "queries" in defn:
            queries = defn["queries"]
            print(f"\n=== First 2 of {len(queries)} queries ===")
            for q in queries[:2]:
                print(json.dumps(q, indent=2))
                print("---")
        
        # Print parameters if any
        if "parameters" in defn:
            print(f"\n=== parameters ===")
            print(json.dumps(defn["parameters"], indent=2))
        
        # Print auto-refresh
        if "autoRefresh" in defn:
            print(f"\n=== autoRefresh ===")
            print(json.dumps(defn["autoRefresh"], indent=2))
