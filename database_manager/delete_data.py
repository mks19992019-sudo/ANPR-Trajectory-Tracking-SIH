"""
Database Manager - Data Record Purge Tool.
Deletes all operational ANPR records (observations, alerts, metrics, trajectories)
via the backend deletion endpoint while strictly preserving table columns and schema definitions.
"""
import argparse
import sys
import os
import requests

DEFAULT_BASE = os.getenv("BACKEND_URL", "https://anpr-trajectory-tracking-sih.onrender.com").rstrip("/")
DEFAULT_DELETE_URL = f"{DEFAULT_BASE}/api/v1/system/data"
DEFAULT_STATUS_URL = f"{DEFAULT_BASE}/api/v1/system/status"


def get_current_status(status_url: str = DEFAULT_STATUS_URL) -> dict | None:
    try:
        res = requests.get(status_url, timeout=5)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return None


def delete_all_data(delete_url: str = DEFAULT_DELETE_URL, force: bool = False) -> bool:
    print("=" * 60)
    print(" ANPR DATABASE MANAGER — RECORD PURGE UTILITY")
    print("=" * 60)

    status_url = delete_url.replace("/data", "/status")

    # 1. Fetch current status before deletion
    status_before = get_current_status(status_url)
    if status_before:
        print(f"[*] Current Database State:")
        print(f"    - Observations: {status_before.get('total_observations', 0)}")
        print(f"    - Active Alerts: {status_before.get('total_alerts', 0)}")
        print(f"    - Registered Cameras: {status_before.get('registered_cameras', 0)} (Preserved)")
        print(f"    - Registered Corridors: {status_before.get('registered_corridors', 0)} (Preserved)")
    else:
        print(f"[*] Connecting to backend: {delete_url} ...")

    if not force:
        try:
            confirm = input("\n[?] Delete all traffic observation records and alerts? (y/N): ").strip().lower()
            if confirm not in ("y", "yes"):
                print("[*] Operation cancelled by user.")
                return False
        except (KeyboardInterrupt, EOFError):
            print("\n[*] Aborted.")
            return False

    print(f"\n[*] Sending DELETE request to: {delete_url} ...")
    try:
        response = requests.delete(delete_url, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"[✓] SUCCESS: {result.get('message')}")
            if "tables_cleared" in result:
                print(f"[*] Tables cleared (schema and columns preserved):")
                for tbl in result["tables_cleared"]:
                    print(f"    • {tbl}")

            # Verify after deletion
            status_after = get_current_status(status_url)
            if status_after:
                print(f"\n[*] Verified Post-Purge State:")
                print(f"    - Observations: {status_after.get('total_observations', 0)}")
                print(f"    - Alerts: {status_after.get('total_alerts', 0)}")
                print(f"    - Cameras: {status_after.get('registered_cameras', 0)} (Intact)")
                print(f"    - Roads: {status_after.get('registered_corridors', 0)} (Intact)")
            return True
        else:
            print(f"[x] FAILED (HTTP {response.status_code}): {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"[x] Network error connecting to backend: {e}")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ANPR Database Record Purge Utility")
    parser.add_argument("--url", default=DEFAULT_DELETE_URL, help="Backend deletion endpoint URL")
    parser.add_argument("--force", "-f", action="store_true", help="Skip confirmation prompt")
    args = parser.parse_args()

    success = delete_all_data(delete_url=args.url, force=args.force)
    sys.exit(0 if success else 1)
