from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.organization_schema import OrganizationCreate, OrganizationResponse
from app.controllers import organization_controller

router = APIRouter(prefix="/organizations", tags=["Organizations"])


@router.post("/", response_model=OrganizationResponse)
def create_organization(org: OrganizationCreate, db: Session = Depends(get_db)):
    try:
        return organization_controller.create_organization(db, org)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[OrganizationResponse])
def get_organizations(db: Session = Depends(get_db)):
    return organization_controller.get_organizations(db)


@router.get("/{org_id}", response_model=OrganizationResponse)
def get_organization(org_id: UUID, db: Session = Depends(get_db)):
    org = organization_controller.get_organization_by_id(db, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org


@router.patch("/{org_id}/suspend", response_model=OrganizationResponse)
def suspend_organization(org_id: UUID, db: Session = Depends(get_db)):
    try:
        return organization_controller.suspend_organization(db, org_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{org_id}/unsuspend", response_model=OrganizationResponse)
def unsuspend_organization(org_id: UUID, db: Session = Depends(get_db)):
    try:
        return organization_controller.unsuspend_organization(db, org_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{org_id}")
def delete_organization(org_id: UUID, db: Session = Depends(get_db)):
    try:
        organization_controller.delete_organization(db, org_id)
        return {
            "message": f"Organization {org_id} and all associated users deleted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
