# Global registration of all SQLAlchemy DB models for alembic migration auto-discovery
from src.database import Base
from src.users.models import User, Membership, EmployeeStatutory
from src.organizations.models import Organization
from src.audit.models import AuditLog
