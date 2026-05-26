"""
create_chemical_eventhouse.py — Create an Eventhouse, KQL Database, and tables in Fabric.

Creates `eh_chemical` (Eventhouse) and `chemical_db` (KQL Database) in the target
workspace, then executes embedded table DDLs that match the schemas used by
``notebooks/chemical_02_generate_events.ipynb``.
All operations are idempotent — existing resources are detected and skipped.

Tables created:
    - SensorReadingEvent         (センサー定期計測値)
    - ProcessAlarmEvent          (プロセスアラーム)
    - EquipmentStatusEvent       (設備状態変更)
    - BatchPhaseTransitionEvent  (バッチ工程フェーズ遷移)
    - QualityInspectionEvent     (インライン品質検査)

Usage:
    python create_chemical_eventhouse.py \\
        --workspace-id <WORKSPACE_GUID>

    # or via environment variable:
    export FABRIC_WORKSPACE_ID=<WORKSPACE_GUID>
    python create_chemical_eventhouse.py

Requirements:
    pip install sempy-labs requests azure-identity
"""

import argparse
import os
import sys
import time

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

EVENTHOUSE_NAME = "eh_chemical"
KQL_DB_NAME     = "chemical_db"
KUSTO_SCOPE     = "https://kusto.kusto.windows.net/.default"

# ---------------------------------------------------------------------------
# Embedded DDL statements
# Column order MUST match TABLE_COLUMNS in chemical_02_generate_events.ipynb
# ---------------------------------------------------------------------------

_KQL_DDL_STATEMENTS = [
    # ---------- SensorReadingEvent ----------
    """.create-merge table SensorReadingEvent (
    event_id: string,
    event_type: string,
    timestamp: datetime,
    source: string,
    sensor_id: string,
    equipment_id: string,
    production_line_id: string,
    process_order_id: string,
    tag_name: string,
    measurement_type: string,
    value: real,
    unit: string,
    normal_min: real,
    normal_max: real,
    alarm_low: real,
    alarm_high: real,
    is_within_normal: bool
)""",
    """.alter table SensorReadingEvent policy retention ```{ "SoftDeletePeriod": "365.00:00:00", "Recoverability": "Enabled" }```""",

    # ---------- ProcessAlarmEvent ----------
    """.create-merge table ProcessAlarmEvent (
    event_id: string,
    event_type: string,
    timestamp: datetime,
    source: string,
    sensor_id: string,
    equipment_id: string,
    production_line_id: string,
    process_order_id: string,
    tag_name: string,
    alarm_type: string,
    severity: string,
    threshold_value: real,
    actual_value: real,
    deviation_amount: real,
    action_taken: string
)""",
    """.alter table ProcessAlarmEvent policy retention ```{ "SoftDeletePeriod": "365.00:00:00", "Recoverability": "Enabled" }```""",

    # ---------- EquipmentStatusEvent ----------
    """.create-merge table EquipmentStatusEvent (
    event_id: string,
    event_type: string,
    timestamp: datetime,
    source: string,
    equipment_id: string,
    production_line_id: string,
    equipment_name: string,
    equipment_type: string,
    previous_status: string,
    new_status: string,
    reason: string
)""",
    """.alter table EquipmentStatusEvent policy retention ```{ "SoftDeletePeriod": "365.00:00:00", "Recoverability": "Enabled" }```""",

    # ---------- BatchPhaseTransitionEvent ----------
    """.create-merge table BatchPhaseTransitionEvent (
    event_id: string,
    event_type: string,
    timestamp: datetime,
    source: string,
    process_order_id: string,
    batch_number: string,
    product_id: string,
    production_line_id: string,
    previous_phase: string,
    new_phase: string,
    sequence_number: int,
    set_temperature: real,
    set_pressure: real,
    actual_temperature: real,
    actual_pressure: real
)""",
    """.alter table BatchPhaseTransitionEvent policy retention ```{ "SoftDeletePeriod": "365.00:00:00", "Recoverability": "Enabled" }```""",

    # ---------- QualityInspectionEvent ----------
    """.create-merge table QualityInspectionEvent (
    event_id: string,
    event_type: string,
    timestamp: datetime,
    source: string,
    process_order_id: string,
    batch_number: string,
    product_id: string,
    inspection_item: string,
    measured_value: real,
    spec_lower: real,
    spec_upper: real,
    pass_fail: string,
    lot_number: string
)""",
    """.alter table QualityInspectionEvent policy retention ```{ "SoftDeletePeriod": "365.00:00:00", "Recoverability": "Enabled" }```""",
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_client():
    import sempy.fabric as fabric
    return fabric.FabricRestClient()


def _poll_lro(client, resp, label, list_fn=None, timeout=300):
    """Poll a Fabric long-running operation (202 Accepted) until it succeeds.

    Checks all common Fabric LRO headers. If none are present, falls back to
    calling list_fn() (a zero-arg callable) until it returns a non-None value.
    """
    if resp.status_code == 200:
        return resp.json()
    if resp.status_code != 202:
        resp.raise_for_status()

    op_url = (
        resp.headers.get("Operation-Location")
        or resp.headers.get("operation-location")
        or resp.headers.get("Location")
        or resp.headers.get("location")
        or resp.headers.get("x-ms-operation-location")
    )

    print(f"  Provisioning {label}...", end="", flush=True)
    deadline = time.time() + timeout

    if op_url:
        while time.time() < deadline:
            time.sleep(5)
            r = client.get(op_url)
            r.raise_for_status()
            body = r.json()
            status = body.get("status", "").lower()
            if status == "succeeded":
                print(" done.")
                return body
            elif status == "failed":
                raise RuntimeError(f"{label} provisioning failed: {body}")
            print(".", end="", flush=True)
    elif list_fn:
        while time.time() < deadline:
            time.sleep(5)
            result = list_fn()
            if result is not None:
                print(" done.")
                return result
            print(".", end="", flush=True)
    else:
        time.sleep(10)
        print(" done (no operation URL; assumed complete).")
        return None

    raise TimeoutError(f"{label} provisioning timed out after {timeout}s.")


def ensure_eventhouse(workspace_id: str, client=None) -> str:
    """Return EVENTHOUSE_ID, creating the Eventhouse if it does not exist."""
    if client is None:
        client = _get_client()

    resp = client.get(f"v1/workspaces/{workspace_id}/eventhouses")
    resp.raise_for_status()
    existing = next(
        (e for e in resp.json().get("value", []) if e["displayName"] == EVENTHOUSE_NAME),
        None,
    )
    if existing:
        eh_id = existing["id"]
        print(f"  ℹ️  Eventhouse '{EVENTHOUSE_NAME}' already exists — EVENTHOUSE_ID = {eh_id}")
        return eh_id

    print(f"  Creating Eventhouse '{EVENTHOUSE_NAME}'...")
    resp = client.post(
        f"v1/workspaces/{workspace_id}/eventhouses",
        json={"displayName": EVENTHOUSE_NAME},
    )

    def _eh_ready():
        r = client.get(f"v1/workspaces/{workspace_id}/eventhouses")
        r.raise_for_status()
        return next(
            (e for e in r.json().get("value", []) if e["displayName"] == EVENTHOUSE_NAME), None
        )

    _poll_lro(client, resp, EVENTHOUSE_NAME, list_fn=_eh_ready)

    resp2 = client.get(f"v1/workspaces/{workspace_id}/eventhouses")
    resp2.raise_for_status()
    eh = next(e for e in resp2.json()["value"] if e["displayName"] == EVENTHOUSE_NAME)
    eh_id = eh["id"]
    print(f"  ✅ Eventhouse created — EVENTHOUSE_ID = {eh_id}")
    return eh_id


def ensure_kql_database(workspace_id: str, eventhouse_id: str, client=None) -> str:
    """Return KQL_DB_ID, creating the KQL Database inside the Eventhouse if needed."""
    if client is None:
        client = _get_client()

    resp = client.get(f"v1/workspaces/{workspace_id}/kqlDatabases")
    resp.raise_for_status()
    existing = next(
        (d for d in resp.json().get("value", []) if d["displayName"] == KQL_DB_NAME),
        None,
    )
    if existing:
        db_id = existing["id"]
        print(f"  ℹ️  KQL Database '{KQL_DB_NAME}' already exists — KQL_DB_ID = {db_id}")
        return db_id

    print(f"  Creating KQL Database '{KQL_DB_NAME}' inside Eventhouse...")
    resp = client.post(
        f"v1/workspaces/{workspace_id}/kqlDatabases",
        json={
            "displayName": KQL_DB_NAME,
            "creationPayload": {
                "databaseType": "ReadWrite",
                "parentEventhouseItemId": eventhouse_id,
            },
        },
    )

    def _db_ready():
        r = client.get(f"v1/workspaces/{workspace_id}/kqlDatabases")
        r.raise_for_status()
        return next(
            (d for d in r.json().get("value", []) if d["displayName"] == KQL_DB_NAME), None
        )

    _poll_lro(client, resp, KQL_DB_NAME, list_fn=_db_ready)

    resp2 = client.get(f"v1/workspaces/{workspace_id}/kqlDatabases")
    resp2.raise_for_status()
    db = next(d for d in resp2.json()["value"] if d["displayName"] == KQL_DB_NAME)
    db_id = db["id"]
    print(f"  ✅ KQL Database created — KQL_DB_ID = {db_id}")
    return db_id


def create_kql_tables(
    workspace_id: str,
    eventhouse_id: str,
    kql_db_name: str,
    client=None,
) -> list:
    """Execute embedded DDL statements against the KQL database.

    Token acquisition order:
      1. ``notebookutils.credentials.getToken`` — used inside a Fabric notebook.
      2. ``azure.identity.DefaultAzureCredential`` — fallback for CLI / local runs.

    Returns the list of table names that were created or merged.
    """
    import requests as _requests

    if client is None:
        client = _get_client()

    # 1. Resolve queryServiceUri from the Eventhouse item
    resp = client.get(f"v1/workspaces/{workspace_id}/eventhouses/{eventhouse_id}")
    resp.raise_for_status()
    props = resp.json().get("properties", {})
    query_uri = props.get("queryServiceUri") or props.get("queryUri")
    if not query_uri:
        raise RuntimeError(
            f"queryServiceUri not found in Eventhouse properties. "
            f"Available keys: {list(props.keys())}"
        )

    # 2. Acquire a Kusto bearer token
    token = None
    try:
        import notebookutils  # available inside a Fabric notebook
        token = notebookutils.credentials.getToken("https://kusto.kusto.windows.net")
    except Exception:
        from azure.identity import DefaultAzureCredential
        token = DefaultAzureCredential().get_token(KUSTO_SCOPE).token

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    mgmt_url = f"{query_uri.rstrip('/')}/v1/rest/mgmt"

    # 3. Execute each DDL statement
    created_tables: list = []
    total = len(_KQL_DDL_STATEMENTS)
    for i, stmt in enumerate(_KQL_DDL_STATEMENTS, 1):
        first_line = stmt.splitlines()[0][:80]
        try:
            r = _requests.post(
                mgmt_url,
                headers=headers,
                json={"db": kql_db_name, "csl": stmt, "properties": {}},
                timeout=60,
            )
            r.raise_for_status()
            print(f"  ✅ [{i}/{total}] {first_line}")
            tokens = stmt.split()
            if len(tokens) >= 3 and tokens[0] == ".create-merge" and tokens[1] == "table":
                table_name = tokens[2]
                if table_name not in created_tables:
                    created_tables.append(table_name)
        except Exception as exc:
            print(f"  ✗ [{i}/{total}] {first_line}")
            print(f"       Error: {exc}")

    return created_tables


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Create Eventhouse and KQL Database for the Chemical Plant workshop."
    )
    parser.add_argument(
        "--workspace-id",
        default=os.environ.get("FABRIC_WORKSPACE_ID"),
        help="Fabric workspace GUID (or set FABRIC_WORKSPACE_ID env var)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if not args.workspace_id:
        print("ERROR: --workspace-id is required (or set FABRIC_WORKSPACE_ID).")
        sys.exit(1)

    print("=" * 60)
    print(f"  Eventhouse : {EVENTHOUSE_NAME}")
    print(f"  KQL DB     : {KQL_DB_NAME}")
    print(f"  Workspace  : {args.workspace_id}")
    print("=" * 60)

    client = _get_client()

    print("\n[1/3] Eventhouse...")
    eventhouse_id = ensure_eventhouse(args.workspace_id, client)

    print("\n[2/3] KQL Database...")
    kql_db_id = ensure_kql_database(args.workspace_id, eventhouse_id, client)

    print("\n[3/3] KQL Table DDLs (embedded)...")
    created = create_kql_tables(args.workspace_id, eventhouse_id, KQL_DB_NAME, client)
    print(f"  Tables ready: {', '.join(created) if created else '(none)'}")

    print(f"\n✅ Eventhouse  : {EVENTHOUSE_NAME} ({eventhouse_id})")
    print(f"   KQL Database : {KQL_DB_NAME} ({kql_db_id})")
    print("\nDone.")


if __name__ == "__main__":
    main()
