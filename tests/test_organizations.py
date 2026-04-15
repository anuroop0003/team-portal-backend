import httpx
import uuid

BASE_URL = "http://localhost:8000"

def create_test_org(client, name="Test Corp", initial="TC"):
    payload = {
        "name": name,
        "initial": initial,
        "full_name": f"{name} International"
    }
    resp = client.post("/organizations/", json=payload)
    assert resp.status_code == 200, f"Organization creation failed: {resp.text}"
    return resp.json()

def test_org_crud():
    with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
        # Create
        org = create_test_org(client, "CRUD Corp", f"CR{uuid.uuid4().hex[:4]}")
        org_id = org["id"]
        print(f"   ✅ Created Organization: {org_id}")

        # Get
        resp = client.get(f"/organizations/{org_id}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "CRUD Corp"
        print("   ✅ Fetched Organization details.")

        # List
        resp = client.get("/organizations/")
        assert resp.status_code == 200
        assert any(o["id"] == org_id for o in resp.json())
        print("   ✅ Organization found in global list.")

        # Suspend
        resp = client.patch(f"/organizations/{org_id}/suspend")
        assert resp.status_code == 200
        assert resp.json()["is_active"] is False
        print("   ✅ Organization suspension works.")

        # Cleanup
        client.delete(f"/organizations/{org_id}")
        print("   ✅ Organization cleaned up.")

if __name__ == "__main__":
    print("\n🏢 Running Organization Module Tests...")
    try:
        test_org_crud()
        print("🎉 Organization Tests Passed!")
    except Exception as e:
        print(f"❌ Org Test Failed: {e}")
