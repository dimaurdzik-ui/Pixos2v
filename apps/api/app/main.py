from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apps.api.app.core.config import settings
from apps.api.app.api.endpoints import workflows, approvals

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(workflows.router, prefix=settings.API_V1_STR + "/workflows", tags=["workflows"])
app.include_router(approvals.router, prefix=settings.API_V1_STR + "/approvals", tags=["approvals"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Pixos v2 API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
