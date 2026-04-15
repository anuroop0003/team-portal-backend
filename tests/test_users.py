import httpx
import uuid

BASE_URL = "http://localhost:8000"

def create_test_user(client, org_id, name="Test User", email=None):
    if not email:
        email = f"user_{uuid.uuid4().hex[:6]}@example.com"
    
    payload = {
        "name": name,
        "email": email,
        "password": "password123",
        "organization_id": org_id,
        "designation": "Software Engineer",
        "department": "Engineering"
    }
    resp = client.post("/users/", json=payload)
    assert resp.status_code == 200, f"User creation failed: {resp.text}"
    return resp.json()

def test_user_management():
    with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
        # 1. Need an Org first
        org_resp = client.post("/organizations/", json={
            "name": "User Test Corp", 
            "initial": f"UT{uuid.uuid4().hex[:4]}",
            "full_name": "User Testing Corporation"
        })
        org = org_resp.json()
        org_id = org["id"]

        # 2. Create User
        user = create_test_user(client, org_id, "Alice Smith")
        user_id = user["id"]
        print(f"   ✅ Created User: {user_id}")
        assert user["employee_id"].startswith(org["initial"])
        print(f"   ✅ Employee ID Prefix verified: {user['employee_id']}")

        # 3. Search & Pagination
        resp = client.get(f"/users/?organization_id={org_id}&search=Alice")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1
        print("   ✅ User Search (Admin Directory) verified.")

        # 4. Profile Detail (Statutory Check)
        resp = client.get(f"/users/{user_id}?organization_id={org_id}")
        assert resp.status_code == 200
        detail = resp.json()
        assert "statutory_details" in detail
        print("   ✅ User Detail + Automated Statutory record verified.")

        # Cleanup
        client.delete(f"/organizations/{org_id}")
        print("   ✅ Organization and Users wiped.")

if __name__ == "__main__":
    print("\n👤 Running User Module Tests...")
    try:
        test_user_management()
        print("🎉 User Tests Passed!")
    except Exception as e:
        print(f"❌ User Test Failed: {e}")
