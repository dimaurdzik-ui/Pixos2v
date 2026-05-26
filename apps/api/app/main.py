import logging
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apps.api.app.core.config import settings
from apps.api.app.api.endpoints import agents, workflows, chat, teams, billing, policies, approvals, artifacts, admin, integrations, stripe_webhooks, oauth, users

# Configure Structured Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [req_id=%(request_id)s] - %(message)s'
)

class RequestIDFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, 'request_id'):
            record.request_id = 'N/A'
        return True

for handler in logging.root.handlers:
    handler.addFilter(RequestIDFilter())

# Pure ASGI middleware (avoids BaseHTTPMiddleware/asyncpg event-loop conflicts)
class RequestIDMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            headers = dict(scope.get("headers", []))
            request_id = headers.get(b"x-request-id", str(uuid.uuid4()).encode()).decode()
            scope["state"] = scope.get("state", {})
            scope["state"]["request_id"] = request_id

            logger = logging.getLogger("api")
            extra = {"request_id": request_id}
            logger.info(f"Incoming Request: {scope.get('method', '?')} {scope.get('path', '?')}", extra=extra)

            async def send_with_header(message):
                if message["type"] == "http.response.start":
                    headers_list = list(message.get("headers", []))
                    headers_list.append((b"x-request-id", request_id.encode()))
                    message = {**message, "headers": headers_list}
                    logger.info(f"Outgoing Response: {message.get('status', '?')}", extra=extra)
                await send(message)

            await self.app(scope, receive, send_with_header)
        else:
            await self.app(scope, receive, send)


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
