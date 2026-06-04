import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
import urllib.parse
from src.main import app
from src.database import SessionLocal
from src.users.models import User, Membership
from src.organizations.models import Organization
from src.audit.models import AuditLog

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def clean_database():
    # Clean up test users / organizations before starting
    db = SessionLocal()
    try:
        # We can clean up existing test organization and user emails
        test_email = "test-owner-flow@example.com"
        db.query(AuditLog).filter(
            AuditLog.actor_id.in_(
                db.query(User.id).filter(User.email == test_email)
            )
        ).delete(synchronize_session=False)
        
        db.query(Membership).filter(
            Membership.user_id.in_(
                db.query(User.id).filter(User.email == test_email)
            )
        ).delete(synchronize_session=False)
        
        db.query(User).filter(User.email == test_email).delete(synchronize_session=False)
        db.query(Organization).filter(Organization.code == "TFLOW").delete(synchronize_session=False)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

    yield

    # Clean up again after test run
    db = SessionLocal()
    try:
        test_email = "test-owner-flow@example.com"
        db.query(AuditLog).filter(
            AuditLog.actor_id.in_(
                db.query(User.id).filter(User.email == test_email)
            )
        ).delete(synchronize_session=False)
        
        db.query(Membership).filter(
            Membership.user_id.in_(
                db.query(User.id).filter(User.email == test_email)
            )
        ).delete(synchronize_session=False)
        
        db.query(User).filter(User.email == test_email).delete(synchronize_session=False)
        db.query(Organization).filter(Organization.code == "TFLOW").delete(synchronize_session=False)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


@patch("src.mail.service.send_email")
def test_full_onboarding_and_auth_workflow(mock_send_email):
    """
    Test the entire onboarding and authentication workflow:
    1. Register Organization & Owner
    2. Try to Sign In (Should fail because not verified)
    3. Decode/Verify Token Info
    4. Verify Email
    5. Sign In (Should succeed)
    6. Access /auth/me
    7. Forgot Password
    8. Reset Password
    9. Sign In with new password
    """
    mock_send_email.return_value = None

    # --- 1. Register Organization & Owner ---
    reg_payload = {
        "organization": {
            "name": "Flow Test Corp",
            "code": "TFLOW",
            "website_url": "https://flowtest.com",
            "industry": "Testing",
            "company_size": "1-10"
        },
        "admin": {
            "name": "Flow Owner",
            "email": "test-owner-flow@example.com",
            "password": "InitialPassword123!",
            "phone": "+19998887777",
            "job_title": "Quality Engineer"
        }
    }

    response = client.post("/auth/register-organization", json=reg_payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == "test-owner-flow@example.com"
    assert data["is_verified"] is False

    # Capture the verification email call
    mock_send_email.assert_called_once()
    args, kwargs = mock_send_email.call_args
    recipient = args[0]
    subject = args[1]
    html_content = args[2]

    assert recipient == "test-owner-flow@example.com"
    assert "Verify your email address" in subject
    
    # Extract the verification link from the email HTML content
    # Look for href="http://localhost:5173/auth/verify-email?token=..."
    assert "token=" in html_content
    # Find token
    parts = html_content.split("token=")
    token_part = parts[1].split('"')[0]
    # In case there are html escapes or other structures:
    verification_token = token_part.split('&')[0].strip()

    # Reset mock for future calls
    mock_send_email.reset_mock()

    # --- 2. Try to Sign In (Should fail because not verified) ---
    login_data = {
        "username": "test-owner-flow@example.com",
        "password": "InitialPassword123!"
    }
    response = client.post("/auth/sign-in", data=login_data)
    assert response.status_code == 403
    assert "Email not verified" in response.json()["detail"]

    # --- 3. Verify Token Info ---
    response = client.get(f"/auth/verify-token-info?token={verification_token}")
    assert response.status_code == 200, response.text
    info = response.json()
    assert info["email"] == "test-owner-flow@example.com"
    assert info["is_valid"] is True

    # --- 4. Verify Email ---
    response = client.get(f"/auth/verify-email?token={verification_token}")
    assert response.status_code == 200, response.text
    assert response.json()["message"] == "Email verified successfully"

    # --- 5. Sign In (Should succeed now) ---
    response = client.post("/auth/sign-in", data=login_data)
    assert response.status_code == 200, response.text
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    access_token = token_data["access_token"]

    # --- 6. Access /auth/me ---
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200, response.text
    me_data = response.json()
    assert me_data["email"] == "test-owner-flow@example.com"
    assert me_data["is_verified"] is True

    # --- 7. Forgot Password ---
    forgot_payload = {
        "email": "test-owner-flow@example.com"
    }
    response = client.post("/auth/forgot-password", json=forgot_payload)
    assert response.status_code == 200, response.text
    assert "reset link" in response.json()["message"].lower()

    # Capture the password reset email
    mock_send_email.assert_called_once()
    args, kwargs = mock_send_email.call_args
    assert args[0] == "test-owner-flow@example.com"
    assert "Reset your password" in args[1]
    
    # Extract reset token from URL
    reset_html = args[2]
    assert "token=" in reset_html
    reset_token = reset_html.split("token=")[1].split('"')[0].split('&')[0].strip()

    # Reset mock
    mock_send_email.reset_mock()

    # --- 8. Reset Password ---
    reset_payload = {
        "token": reset_token,
        "new_password": "NewSecurePassword999!"
    }
    response = client.post("/auth/reset-password", json=reset_payload)
    assert response.status_code == 200, response.text
    assert "Password reset successfully" in response.json()["message"]

    # --- 9. Sign In with new password ---
    # Old password should fail
    response = client.post("/auth/sign-in", data=login_data)
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]

    # New password should succeed
    new_login_data = {
        "username": "test-owner-flow@example.com",
        "password": "NewSecurePassword999!"
    }
    response = client.post("/auth/sign-in", data=new_login_data)
    assert response.status_code == 200, response.text
    new_token_data = response.json()
    assert "access_token" in new_token_data
