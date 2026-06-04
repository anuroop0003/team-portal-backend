from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from src.auth.router import router as auth_router
from src.users.router import user_router, admin_router
from src.organizations.router import router as organization_router
from src.audit.router import router as audit_router
from src.storage.router import router as storage_router
from src.config import settings
from src.exceptions import APIException

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL] if settings.FRONTEND_URL else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(APIException)
async def api_exception_handler(request, exc: APIException):
    content = {"detail": exc.detail}
    if exc.error_code:
        content["code"] = exc.error_code
    return JSONResponse(
        status_code=exc.status_code, content=content, headers=exc.headers
    )


app.include_router(auth_router)
app.include_router(user_router)
app.include_router(admin_router)
app.include_router(organization_router)
app.include_router(audit_router)
app.include_router(storage_router)


@app.get("/")
def root():
    return {"message": "API working 🚀"}
