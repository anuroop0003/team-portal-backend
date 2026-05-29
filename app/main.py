from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import (
    user_routes,
    admin_routes,
    organization_routes,
    audit_routes,
    auth_routes,
    storage_routes,
)
from app.core.config import settings

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL] if settings.FRONTEND_URL else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(admin_routes.router)
app.include_router(organization_routes.router)
app.include_router(audit_routes.router)
app.include_router(storage_routes.router)


@app.get("/")
def root():
    return {"message": "API working 🚀"}
