"""
Healthcare Streaming Data Simulator
====================================
Sends real-time nursing events to Microsoft Fabric Eventstream
via Event Hub–compatible protocol.

Setup:
    1. Open your Eventstream "medical_data_stream" in Fabric
    2. Click the Custom Endpoint source node → "Keys"
    3. Copy the connection string and Event Hub name
    4. Create a .env file (see .env.example) or export the variables

    RECOMMENDED (Zero Trust): Use Azure Key Vault instead of .env files:
        pip install azure-keyvault-secrets azure-identity
        export AZURE_KEYVAULT_URL=https://<your-vault>.vault.azure.net/
        Store secrets as: event-hub-connection-string, event-hub-name

Usage:
    pip install -r requirements.txt
    python stream_simulator.py
    python stream_simulator.py --interval 0.3 --loops 5
"""

import argparse
import csv
import json
import os
import random
import time
from datetime import datetime, timedelta
from pathlib import Path

from azure.eventhub import EventHubProducerClient, EventData
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

STREAM_FILES = {
    "rtls_location": "stream_rtls_location.csv",
    "ehr_clickstream": "stream_ehr_clickstream.csv",
    "nurse_call_events": "stream_nurse_call_events.csv",
    "bcma_scans": "stream_bcma_scans.csv",
    "clinical_alerts": "stream_clinical_alerts.csv",
}


def load_csv_rows(filename: str) -> list[dict]:
    """Load a CSV and return a list of row dicts."""
    filepath = DATA_DIR / filename
    with open(filepath, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def rebase_timestamp(value: str, now: datetime) -> str:
    """Replace the date portion of a timestamp with today, keep the time."""
    try:
        original = datetime.fromisoformat(value)
        rebased = now.replace(
            hour=original.hour,
            minute=original.minute,
            second=original.second,
            microsecond=original.microsecond,
        )
        return rebased.isoformat()
    except (ValueError, TypeError):
        return value


def prepare_event(row: dict, stream_type: str, now: datetime) -> dict:
    """Build a JSON-serialisable event envelope."""
    # Rebase any timestamp columns to "now"
    for key in row:
        if "timestamp" in key.lower():
            row[key] = rebase_timestamp(row[key], now)
    return {
        "stream_type": stream_type,
        "ingestion_time": datetime.utcnow().isoformat() + "Z",
        "data": row,
    }


def run_simulation(
    connection_string: str,
    event_hub_name: str,
    interval: float,
    loops: int,
):
    """Main simulation loop."""
    # ── Load all rows ────────────────────────────────────────────────
    all_events: list[tuple[str, dict]] = []
    for stream_type, filename in STREAM_FILES.items():
        rows = load_csv_rows(filename)
        for row in rows:
            all_events.append((stream_type, row))
        print(f"  Loaded {len(rows):>4} rows  ←  {filename}")

    print(f"\n  Total events per loop : {len(all_events)}")
    print(f"  Loops                 : {loops}")
    print(f"  Interval between sends: {interval}s\n")

    # ── Connect to Eventstream ───────────────────────────────────────
    producer = EventHubProducerClient.from_connection_string(
        conn_str=connection_string,
        eventhub_name=event_hub_name,
    )

    total_sent = 0
    try:
        for loop_num in range(1, loops + 1):
            random.shuffle(all_events)
            now = datetime.now()
            i = 0

            print(f"── Loop {loop_num}/{loops} "
                  f"(base time: {now.strftime('%H:%M:%S')}) ──")

            while i < len(all_events):
                batch = producer.create_batch()
                batch_count = 0
                batch_size = random.randint(1, 8)

                for j in range(i, min(i + batch_size, len(all_events))):
                    stream_type, row = all_events[j]
                    event = prepare_event(
                        dict(row), stream_type,
                        now + timedelta(seconds=total_sent * 0.1),
                    )
                    try:
                        batch.add(EventData(json.dumps(event)))
                        batch_count += 1
                    except ValueError:
                        break

                producer.send_batch(batch)
                total_sent += batch_count
                i += batch_count

                last_type = all_events[min(i - 1, len(all_events) - 1)][0]
                print(
                    f"    Sent {batch_count} events  "
                    f"({total_sent} total)  "
                    f"last_type={last_type}"
                )
                time.sleep(interval)

            print(f"  ✓ Loop {loop_num} complete — {len(all_events)} events\n")

    except KeyboardInterrupt:
        print(f"\n  ⚠ Interrupted after {total_sent} events.")
    finally:
        producer.close()

    print(f"✅  Simulation finished — {total_sent} events sent to Eventstream.")


def main():
    parser = argparse.ArgumentParser(
        description="Stream healthcare events to Fabric Eventstream"
    )
    parser.add_argument(
        "--interval", type=float, default=0.5,
        help="Seconds between batches (default: 0.5)",
    )
    parser.add_argument(
        "--loops", type=int, default=1,
        help="Number of times to replay the full dataset (default: 1)",
    )
    args = parser.parse_args()

    connection_string = os.environ.get("EVENT_HUB_CONNECTION_STRING", "")
    event_hub_name = os.environ.get("EVENT_HUB_NAME", "")

    # ZT: Attempt to load secrets from Azure Key Vault if configured
    keyvault_url = os.environ.get("AZURE_KEYVAULT_URL", "")
    if keyvault_url and not connection_string:
        try:
            from azure.identity import DefaultAzureCredential
            from azure.keyvault.secrets import SecretClient
            print("🔐 ZT: Loading credentials from Azure Key Vault...")
            kv_client = SecretClient(vault_url=keyvault_url, credential=DefaultAzureCredential())
            connection_string = kv_client.get_secret("event-hub-connection-string").value
            event_hub_name = kv_client.get_secret("event-hub-name").value
            print("✅ ZT: Credentials loaded from Key Vault")
        except Exception as e:
            print(f"⚠ ZT: Key Vault load failed ({e}), falling back to environment variables")

    if not connection_string or not event_hub_name:
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║  Missing Eventstream connection details                     ║")
        print("╠══════════════════════════════════════════════════════════════╣")
        print("║  Set these environment variables (or create a .env file):   ║")
        print("║                                                             ║")
        print("║  EVENT_HUB_CONNECTION_STRING=Endpoint=sb://...              ║")
        print("║  EVENT_HUB_NAME=es_xxxxxxxx                                ║")
        print("║                                                             ║")
        print("║  To find them in Fabric:                                    ║")
        print("║    1. Open Eventstream 'medical_data_stream'                ║")
        print("║    2. Click the Custom Endpoint source → Keys               ║")
        print("║    3. Copy 'Connection string–primary key'                  ║")
        print("║       and 'Event hub name'                                  ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        return

    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  Healthcare Streaming Simulator → Fabric Eventstream        ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")

    run_simulation(connection_string, event_hub_name, args.interval, args.loops)


if __name__ == "__main__":
    main()
