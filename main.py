from fastapi import FastAPI
from app.routes import user_routes, admin_routes, organization_routes, audit_routes

app = FastAPI()

app.include_router(user_routes.router)
app.include_router(admin_routes.router)
app.include_router(organization_routes.router)
app.include_router(audit_routes.router)

@app.get("/")
def root():
    return {"message": "API working 🚀"}
