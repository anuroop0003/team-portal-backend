import httpx
import uuid

BASE_URL = "http://localhost:8000"

def test_audit_logging():
    with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
        # 1. Setup Org and User
        org_resp = client.post("/organizations/", json={
            "name": "Audit Test Corp", 
            "initial": f"AU{uuid.uuid4().hex[:4]}",
            "full_name": "Audit Testing"
        })
        org_id = org_resp.json()["id"]

        try:
            user_resp = client.post("/users/", json={
                "name": "Audit Target",
                "email": f"audit_{uuid.uuid4().hex[:6]}@test.com",
                "password": "password123",
                "organization_id": org_id
            })
            user_id = user_resp.json()["id"]

            # 2. Trigger an update with a UNIQUE phone to avoid collision
            unique_phone = f"+99 {uuid.uuid4().hex[:8]}"
            resp_put = client.put(f"/admins/{user_id}?organization_id={org_id}", json={"phone": unique_phone})
            assert resp_put.status_code == 200, f"Update failed: {resp_put.text}"

            # 3. Verify Logs
            resp = client.get(f"/audit-logs/?organization_id={org_id}")
            assert resp.status_code == 200
            logs = resp.json()
            print(f"   DEBUG: Logs found: {[l['action'] for l in logs]}")
            assert len(logs) >= 2 # CREATE_USER and UPDATE_USER
            
            # Check if UPDATE_USER is present
            update_log = next((l for l in logs if l["action"] == "UPDATE_USER"), None)
            assert update_log is not None
            print("   ✅ Audit Log captured update correctly.")

        finally:
            # Cleanup
            client.delete(f"/organizations/{org_id}")
            print("   ✅ Audit environment cleaned up.")

if __name__ == "__main__":
    print("\n🔍 Running Audit Module Tests...")

    try:
        test_audit_logging()
        print("🎉 Audit Tests Passed!")
    except Exception as e:
        print(f"❌ Audit Test Failed: {e}")
        import traceback
        traceback.print_exc()
