import logging
import uuid
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apps.api.app.core.config import settings
from apps.api.app.api.endpoints import agents, workflows, chat, teams, billing, policies, approvals, artifacts, admin, integrations, stripe_webhooks, oauth, users

# Configure Structured Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [req_id=%(request_id)s] - %(message)s'
)
# Provide default request_id for logs outside request context
old_factory = logging.getLogRecordFactory()
def record_factory(*args, **kwargs):
    record = old_factory(*args, **kwargs)
    record.request_id = getattr(record, 'request_id', 'N/A')
    return record
logging.setLogRecordFactory(record_factory)

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        # Set request_id in context or attach to request
        request.state.request_id = request_id
        
        # Log request start
        logger = logging.getLogger("api")
        extra = {"request_id": request_id}
        logger.info(f"Incoming Request: {request.method} {request.url.path}", extra=extra)
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        
        logger.info(f"Outgoing Response: {response.status_code}", extra=extra)
        return response

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize LangGraph Checkpointer tables
    from apps.api.app.workflows.coordinator import checkpointer
    await checkpointer.setup()
    
    yield
    
    # Cleanup connection pool
    from apps.api.app.workflows.coordinator import pool
    await pool.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Add Middleware
app.add_middleware(RequestIDMiddleware)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(workflows.router, prefix=settings.API_V1_STR + "/workflows", tags=["workflows"])
app.include_router(chat.router, prefix=settings.API_V1_STR + "/chat", tags=["chat"])
app.include_router(approvals.router, prefix=f"{settings.API_V1_STR}/approvals", tags=["Approvals"])
app.include_router(artifacts.router, prefix=f"{settings.API_V1_STR}/artifacts", tags=["Artifacts"])
app.include_router(admin.router, prefix=f"{settings.API_V1_STR}/admin", tags=["Admin"])
app.include_router(agents.router, prefix=settings.API_V1_STR + "/agents", tags=["agents"])
app.include_router(teams.router, prefix=settings.API_V1_STR + "/teams", tags=["teams"])
app.include_router(billing.router, prefix=settings.API_V1_STR + "/billing", tags=["billing"])
app.include_router(policies.router, prefix=f"{settings.API_V1_STR}/policies", tags=["Policies"])
app.include_router(integrations.router, prefix=f"{settings.API_V1_STR}/integrations", tags=["Integrations"])
app.include_router(oauth.router, prefix=f"{settings.API_V1_STR}/oauth", tags=["OAuth Integrations"])
app.include_router(stripe_webhooks.router, prefix=f"{settings.API_V1_STR}/billing/stripe", tags=["Stripe Webhooks"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["Users"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Pixos v2 API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
