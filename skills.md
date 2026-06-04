# Codebase Architecture and Standards: Modular Domain-Driven FastAPI

This project follows a structured, modular, domain-driven architecture under the `src/` folder. Each feature or business domain is packaged self-sufficiently with its own routers, schemas, models, services, constants, and utilities.

## Directory Structure

```text
fastapi-project/
├── src/
│   ├── <domain>/
│   │   ├── router.py        # Module core containing all endpoints
│   │   ├── schemas.py       # Pydantic models for request/response serialization
│   │   ├── models.py        # SQLAlchemy database models
│   │   ├── dependencies.py  # Route/Router specific dependency injection (e.g. get_current_user)
│   │   ├── service.py       # Business logic (merges old service & controller layer)
│   │   ├── config.py        # Domain-specific local configurations
│   │   ├── constants.py     # Domain-specific constants & custom error codes
│   │   ├── exceptions.py    # Domain-specific exceptions (e.g. UserNotFoundError)
│   │   └── utils.py         # Helper functions (e.g. hashing, local formatters)
│   │
│   ├── config.py            # Global application settings and environment variables
│   ├── database.py          # SQLAlchemy database engine and local session get_db utility
│   ├── models.py            # Unified models registry for migration auto-discovery
│   ├── exceptions.py        # Global application exception definitions
│   ├── pagination.py        # Global pagination schemas & helpers
│   └── main.py              # Root bootstrapping of the FastAPI instance
```

---

## Key Core Architectural Principles

### 1. Unified Domain Packaging
- Keep code corresponding to a specific functional block (e.g., `auth`, `users`, `organizations`) strictly inside its respective domain directory.
- Avoid exposing database models or core logic inside controller/service layers that span across domains unless using explicit module imports.

### 2. Service and Controller Layer Unification
- To maintain a lean, high-velocity codebase, the redundant `controllers` and `services` layers are unified into a single `service.py` file per domain package.
- `service.py` performs database queries, handles transactional logic, and applies business rules.

### 3. Absolute & Explicit Multi-Domain Imports
When one domain requires models, services, or constants from another domain, they must be imported explicitly with the module name to ensure clarity:
```python
from src.auth import service as auth_service
from src.audit.service import log_audit
from src.users.models import User
```
To avoid circular imports between domains, perform runtime/lazy imports inside specific functions when necessary.

### 4. Global Alembic Registry
All database models must be imported in `src/models.py` so that Alembic's `alembic/env.py` can discover them cleanly through `Base.metadata` auto-generation.

---

## Detailed Coding Structure: The `src/auth` Pattern

The `src/auth` module serves as the reference implementation for all domain modules in the project. Developers should replicate its layered responsibilities:

### 1. Router Layer (`router.py`)
- **Responsibility**: Endpoint definitions, route mapping, request/response validation (using Pydantic models), and injection of dependencies (like database sessions `get_db` or current user dependencies).
- **Behavior**:
  - Keep logic extremely lean. **Do not handle database actions, database transactions, or raw exceptions directly within routers.**
  - Delegate workflow logic directly to functions in the domain's service layer.
  - Return the results of the service layer functions or appropriate status representations.
  - **Include clean docstrings** on every route endpoint function to serve as OpenAPI/Swagger documentation.
- **Example Pattern**:
  ```python
  from fastapi import APIRouter, Depends, Request
  from sqlalchemy.orm import Session
  from src.database import get_db
  from src.auth import service as auth_service
  from src.auth.schemas import SignInRequest, Token

  router = APIRouter(prefix="/auth", tags=["Authentication"])

  @router.post("/sign-in", response_model=Token)
  def sign_in(request: Request, credentials: SignInRequest, db: Session = Depends(get_db)):
      """
      Authenticate user credentials and return an access token.
      """
      return auth_service.authenticate_user(db, credentials, ip_address=request.client.host)
  ```

### 2. Service Layer (`service.py`)
- **Responsibility**: Houses all business logic, manages unit of work/transactions (`db.commit()`, `db.rollback()`), triggers emails or external service workflows, and handles model instantiation or updates.
- **Behavior**:
  - Implements operations such as user registration workflows, authentication, token decoding, and password resets.
  - Manages database transaction control within try/except blocks, ensuring `db.rollback()` is invoked if an exception arises.
  - Throws custom, domain-specific errors defined in `exceptions.py` (which derive from `APIException`) instead of generic `HTTPException`.
  - Imports services of other domains using absolute modular-level aliases (e.g. `from src.users import service as user_service`) to avoid circular imports.
- **Example Pattern**:
  ```python
  from sqlalchemy.orm import Session
  from src.users import service as user_service
  from src.auth import exceptions as auth_exceptions
  from src.exceptions import APIException

  async def register_organization_workflow(db: Session, payload, ip_address: str):
      if user_service.get_user_by_email(db, payload.admin.email):
          raise auth_exceptions.EmailAlreadyRegisteredError()
      try:
          # Business logic & db modifications
          # ...
          db.commit()
          return user
      except APIException:
          db.rollback()
          raise
      except Exception as e:
          db.rollback()
          raise auth_exceptions.RegistrationFailedError(str(e))
  ```

### 3. Dependencies Layer (`dependencies.py`)
- **Responsibility**: Contains FastAPI security dependencies or route guards that validate tokens and extract authenticated contexts.
- **Behavior**:
  - Decodes and validates tokens (e.g. JWTs) using global configuration settings.
  - Resolves models from the database to yield items like `current_user` or roles.
  - Raises standard `HTTPException` directly if credentials or security context cannot be validated (since dependencies run as part of the FastAPI router request-lifecycle filter).

### 4. Exception Layer (`exceptions.py`)
- **Responsibility**: Houses all custom domain exceptions.
- **Behavior**:
  - Each domain exception inherits from the global base `APIException` (`src/exceptions.py`).
  - It specifies an HTTP status code, a client-friendly detail message, and optional error code headers or payloads.
  - Keeps HTTP status code logic decoupled from the routing layer.
- **Example Pattern**:
  ```python
  from fastapi import status
  from src.exceptions import APIException
  from src.auth import constants

  class EmailAlreadyRegisteredError(APIException):
      def __init__(self):
          super().__init__(
              status_code=status.HTTP_400_BAD_REQUEST,
              detail=constants.ERR_EMAIL_ALREADY_REGISTERED,
          )
  ```

### 5. Constants, Schemas, and Utils
- **`constants.py`**: Local config values, string keys for actions/audit records, and error messages to avoid hardcoded strings.
- **`schemas.py`**: Pydantic schemas specifying the exact shape of data for requests and responses.
- **`utils.py`**: Internal helpers like hashing or specific validation routines.

---

## Additional Coding Patterns & Standards

### 1. Post-Request Audit Logging (`audit_logger` & `set_audit_event`)
To keep audit log writes clean and decouple them from business logic:
- **Dependency**: Apply `dependencies=[Depends(audit_logger)]` to your route decorators.
- **Payload Definition**: Call `set_audit_event(request, organization_id, action, target_id, changes)` inside the router endpoint function. This binds metadata to the `request.state`.
- **Deferred Execution**: The dependency will yield the response to the client first, and then execute the audit log insertion into the database after the response is completed.

### 2. Dynamic Audit Change Tracking (`audit_changes`)
To log exact field changes during resource updates:
- In `service.py`, track changes as a dictionary: `audit_changes[field] = {"old": str(old_val), "new": str(new_val)}`.
- Attach it to the returned object as a dynamic runtime attribute: `user.audit_changes = audit_changes`.
- In the router layer, pass this dynamically: `set_audit_event(..., changes=getattr(res, "audit_changes", None))`.

### 3. Pydantic V2 Standardization
- Always utilize Pydantic V2 `.model_dump(exclude_unset=True)` or `.model_dump()` instead of the legacy Pydantic V1 `.dict()` method.

### 4. Function Docstring Standards
All functions (including endpoints, services, helpers, and dependencies) must have detailed, clear docstrings that document:
- The purpose of the function.
- Parameters and their types.
- Return values and types.
- Exceptions raised.

Example Pattern:
```python
def process_data(data: dict, flag: bool = False) -> dict:
    """
    Processes the raw input data and returns a cleaned dictionary.

    Args:
        data (dict): The raw key-value pairs to process.
        flag (bool, optional): A flag to enable advanced parsing. Defaults to False.

    Returns:
        dict: The parsed and formatted dictionary.

    Raises:
        ValueError: If key data fields are missing.
    """
    # implementation...
```
