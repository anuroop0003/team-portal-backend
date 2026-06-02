import asyncio
from src.database import SessionLocal
from src.auth import service as auth_service
from src.users import service as user_service
from src.audit import service as audit_service
from src.organizations import service as org_service
from src.auth.schemas import OrganizationRegisterRequest, OrganizationRegister, AdminRegister
from src.users.schemas import CreateUser
from src.users.models import User, Membership
from src.organizations.models import Organization
from src.audit.models import AuditLog

async def main():
    print("--- Starting Database Verification and Population Script ---")
    db = SessionLocal()
    try:
        # 1. Clean up existing data if it exists (for a clean run)
        print("Cleaning up old test data (if any)...")
        db.query(AuditLog).delete()
        db.query(Membership).delete()
        db.query(User).delete()
        db.query(Organization).delete()
        db.commit()

        # 2. Register Organization and Owner
        print("\n1. Registering Organization 'TechCorp Ltd' (Code: TC)...")
        payload = OrganizationRegisterRequest(
            organization=OrganizationRegister(
                name="TechCorp Ltd",
                code="TC",
                website_url="https://techcorp.com",
                industry="Technology",
                company_size="10-50"
            ),
            admin=AdminRegister(
                name="Admin Owner",
                email="owner@techcorp.com",
                password="OwnerPassword123!",
                phone="+1234567890",
                job_title="Chief Executive Officer"
            )
        )
        
        owner_user = await auth_service.register_organization_workflow(db, payload, ip_address="127.0.0.1")
        
        # Verify and activate the owner
        owner_user.is_verified = True
        owner_user.is_active = True
        db.commit()
        db.refresh(owner_user)
        
        org_id = owner_user.organization_id
        org = org_service.get_organization_by_id(db, org_id)
        
        print(f"Organization registered: {org.name} (ID: {org.id})")
        print(f"Owner created: {owner_user.name} ({owner_user.email})")

        # Log audit for organization registration
        audit_service.log_audit(
            db=db,
            organization_id=org_id,
            action="REGISTER_ORGANIZATION",
            target_id=org_id,
            actor_id=owner_user.id,
            ip_address="127.0.0.1",
            changes={"organization": {"name": org.name, "code": org.code}}
        )

        # 3. Create 20 Users under the Organization
        print("\n2. Creating 20 users under the organization...")
        users_credentials = []
        for i in range(1, 21):
            email = f"user{i}@techcorp.com"
            password = f"UserPassword{i:02d}!"
            user_data = CreateUser(
                name=f"Test User {i}",
                email=email,
                password=password,
                phone=f"+155500000{i:02d}",
                designation="Software Engineer",
                department="Engineering",
                organization_id=org_id
            )
            
            user = await user_service.create_user(db, user_data, role="EMPLOYEE", ip_address="127.0.0.1")
            user.is_verified = True
            user.is_active = True
            db.commit()
            db.refresh(user)
            
            # Log audit for user creation
            audit_service.log_audit(
                db=db,
                organization_id=org_id,
                action="CREATE_USER",
                target_id=user.id,
                actor_id=owner_user.id,
                ip_address="127.0.0.1",
                changes={"email": {"old": None, "new": email}, "name": {"old": None, "new": user.name}}
            )
            
            users_credentials.append({
                "index": i,
                "name": user.name,
                "email": email,
                "password": password,
                "employee_id": user.employee_id
            })
            print(f"   Created User {i}: {user.name} ({email}) - Emp ID: {user.employee_id}")

        # 4. Check the Audit Logs
        print("\n3. Retrieving Audit Logs...")
        logs = audit_service.get_audit_logs(db, organization_id=org_id, limit=100)
        print(f"Total audit logs retrieved: {len(logs)}")
        for idx, log in enumerate(logs[:5], 1):
            print(f"   [{idx}] Action: {log.action} | Target ID: {log.target_id} | Timestamp: {log.timestamp}")
        if len(logs) > 5:
            print(f"   ... and {len(logs) - 5} more log entries.")

        # 5. Output All Credentials Formatted
        print("\n" + "="*60)
        print("CREDENTIALS SUMMARY")
        print("="*60)
        print("Organization details:")
        print(f"  Name: {org.name}")
        print(f"  Code: {org.code}")
        print(f"  ID:   {org.id}")
        print("\nOwner credentials:")
        print(f"  Email:    owner@techcorp.com")
        print(f"  Password: OwnerPassword123!")
        print("\nUser credentials:")
        for uc in users_credentials:
            print(f"  User {uc['index']:02d}: Name: {uc['name']:<15} | EmpID: {uc['employee_id']:<10} | Email: {uc['email']:<22} | Password: {uc['password']}")
        print("="*60)

    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
