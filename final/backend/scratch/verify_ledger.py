import os
import sys

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app.services.audit_ledger import verify_ledger

print("=" * 60)
print("AUDIT LEDGER VERIFICATION")
print("=" * 60)

results = verify_ledger()
if not results:
    print("Ledger is empty or does not exist.")
    sys.exit(0)

tampered_count = 0
for r in results:
    status = "VALID" if r['is_valid'] else "TAMPERED"
    print(f"[{status}] Entry {r['index']} (Alert {r['alert_id']})")
    if not r['is_valid']:
        tampered_count += 1
        print(f"    Expected Hash: {r['stored_hash']}")
        print(f"    Actual Hash:   {r['actual_hash']}")

print("-" * 60)
print(f"Total Entries: {len(results)}")
print(f"Tampered Entries: {tampered_count}")

if tampered_count > 0:
    print("\nWARNING: Ledger integrity compromised. Cryptographic verification failed.")
    sys.exit(1)
else:
    print("\nSUCCESS: Ledger integrity verified. Cryptographic verification passed.")
    sys.exit(0)
