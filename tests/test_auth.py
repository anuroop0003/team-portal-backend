import httpx
import uuid
import time

BASE_URL = "http://localhost:8000"

def test_auth_flow():
    with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
        print("\n🚀 Starting Auth Flow Test...")

        # 1. Register Organization and Admin
        org_name = f"AuthCorp_{uuid.uuid4().hex[:4]}"
        admin_email = f"admin_{uuid.uuid4().hex[:4]}@example.com"
        
        payload = {
            "organization": {
                "name": org_name,
                "initial": f"AC{uuid.uuid4().hex[:2].upper()}"
            },
            "admin": {
                "name": "Super Admin",
                "email": admin_email,
                "password": "securepassword123"
            }
        }
        
        print(f"   Registering Org: {org_name} with Admin: {admin_email}...")
        resp = client.post("/auth/register-organization", json=payload)
        assert resp.status_code == 200, f"Registration failed: {resp.text}"
        user_data = resp.json()
        print(f"   ✅ Registration successful. User ID: {user_data['id']}")

        # 2. Login (Should work even if not verified yet, or we can check verification)
        login_payload = {
            "email": admin_email,
            "password": "securepassword123"
        }
        print("   Attempting Login...")
        resp = client.post("/auth/login", json=login_payload)
        assert resp.status_code == 200, f"Login failed: {resp.text}"
        token_data = resp.json()
        access_token = token_data["access_token"]
        print("   ✅ Login successful. Token received.")

        # 3. Get /me
        print("   Fetching /auth/me...")
        headers = {"Authorization": f"Bearer {access_token}"}
        resp = client.get("/auth/me", headers=headers)
        assert resp.status_code == 200, f"Get /me failed: {resp.text}"
        me_data = resp.json()
        assert me_data["email"] == admin_email
        print(f"   ✅ /auth/me verified for {me_data['email']}")

        # 4. Forgot Password
        print("   Requesting password reset...")
        resp = client.post("/auth/forgot-password", json={"email": admin_email})
        assert resp.status_code == 200
        print("   ✅ Forgot password request processed.")

        # Note: We can't easily test reset/verify without direct DB access here 
        # but we've verified the main API endpoints are up and responding.

        # Cleanup Org (optional but good)
        org_id = user_data["organization_id"]
        client.delete(f"/organizations/{org_id}")
        print("   ✅ Cleanup complete.")

if __name__ == "__main__":
    try:
        test_auth_flow()
        print("\n🎉 Auth Flow Tests Passed!")
    except Exception as e:
        print(f"\n❌ Auth Flow Test Failed: {e}")
