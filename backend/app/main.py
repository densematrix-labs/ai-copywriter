import re
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .config import get_settings
from .database import init_db
from .api import copy, payment, tokens
from .metrics import metrics_router, http_requests, crawler_visits, TOOL_NAME

settings = get_settings()

BOT_PATTERNS = ["Googlebot", "bingbot", "Baiduspider", "YandexBot", "DuckDuckBot", "Slurp", "msnbot"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Free AI Copywriting Tool - Copy.ai Alternative",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def track_metrics(request: Request, call_next):
    # Track crawler visits
    ua = request.headers.get("user-agent", "")
    for bot in BOT_PATTERNS:
        if bot.lower() in ua.lower():
            crawler_visits.labels(tool=TOOL_NAME, bot=bot).inc()
            break
    
    response = await call_next(request)
    
    # Track HTTP requests
    endpoint = request.url.path
    method = request.method
    status = response.status_code
    http_requests.labels(
        tool=TOOL_NAME,
        endpoint=endpoint,
        method=method,
        status=status
    ).inc()
    
    return response


# Include routers
app.include_router(copy.router)
app.include_router(payment.router)
app.include_router(tokens.router)
app.include_router(metrics_router)


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "service": settings.APP_NAME
    }


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "Free AI Copywriting Tool - Copy.ai Alternative",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "copy_types": "/api/v1/copy/types",
            "generate": "POST /api/v1/copy/generate",
            "products": "/api/v1/payment/products"
        }
    }
