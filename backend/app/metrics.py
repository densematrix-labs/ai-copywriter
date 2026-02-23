import os
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import APIRouter
from fastapi.responses import Response

TOOL_NAME = os.getenv("TOOL_NAME", "ai-copywriter")

# HTTP Metrics
http_requests = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["tool", "endpoint", "method", "status"]
)

http_request_duration = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration",
    ["tool", "endpoint", "method"]
)

# Payment Metrics
payment_checkout_created = Counter(
    "payment_checkout_created_total",
    "Checkouts created",
    ["tool", "product_sku"]
)

payment_success = Counter(
    "payment_success_total",
    "Successful payments",
    ["tool", "product_sku", "currency"]
)

payment_revenue_cents = Counter(
    "payment_revenue_cents_total",
    "Total revenue in cents",
    ["tool", "product_sku", "currency"]
)

# Token Metrics
tokens_created = Counter(
    "tokens_created_total",
    "Tokens created",
    ["tool", "product_sku"]
)

tokens_consumed = Counter(
    "tokens_consumed_total",
    "Tokens consumed",
    ["tool"]
)

# Usage Metrics
free_trial_used = Counter(
    "free_trial_used_total",
    "Free trials used",
    ["tool"]
)

copy_generated = Counter(
    "copy_generated_total",
    "Copy generations",
    ["tool", "copy_type"]
)

# Crawler Metrics
crawler_visits = Counter(
    "crawler_visits_total",
    "Crawler visits",
    ["tool", "bot"]
)

metrics_router = APIRouter()


@metrics_router.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
