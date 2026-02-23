import json
import hmac
import hashlib
import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from ..database import get_db
from ..config import get_settings
from ..models import GenerationToken, PaymentTransaction
from ..schemas import CheckoutRequest, CheckoutResponse
from ..metrics import (
    payment_checkout_created, payment_success, payment_revenue_cents,
    tokens_created, TOOL_NAME
)

settings = get_settings()
router = APIRouter(prefix="/api/v1/payment", tags=["payment"])

# Product configuration
PRODUCTS = {
    "pack_10": {"generations": 10, "price_cents": 499, "name": "Starter Pack"},
    "pack_50": {"generations": 50, "price_cents": 1499, "name": "Pro Pack"},
    "pack_200": {"generations": 200, "price_cents": 3999, "name": "Business Pack"},
}


def get_creem_product_id(sku: str) -> str:
    """Get Creem product ID for a SKU."""
    try:
        product_ids = json.loads(settings.CREEM_PRODUCT_IDS)
        return product_ids.get(sku, "")
    except json.JSONDecodeError:
        return ""


@router.post("/create-checkout", response_model=CheckoutResponse)
async def create_checkout(request: CheckoutRequest):
    """Create a Creem checkout session."""
    
    if request.product_sku not in PRODUCTS:
        raise HTTPException(status_code=400, detail="Invalid product SKU")
    
    product_id = get_creem_product_id(request.product_sku)
    if not product_id:
        raise HTTPException(status_code=400, detail="Product not configured")
    
    if not settings.CREEM_API_KEY:
        raise HTTPException(status_code=500, detail="Payment not configured")
    
    # Track metrics
    payment_checkout_created.labels(tool=TOOL_NAME, product_sku=request.product_sku).inc()
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{settings.CREEM_API_BASE}/v1/checkouts",
            headers={
                "Authorization": f"Bearer {settings.CREEM_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "product_id": product_id,
                "success_url": request.success_url,
                "cancel_url": request.cancel_url,
                "metadata": {
                    "device_id": request.device_id,
                    "product_sku": request.product_sku
                }
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"Checkout creation failed: {response.text}"
            )
        
        data = response.json()
        return CheckoutResponse(
            checkout_url=data["checkout_url"],
            checkout_id=data["id"]
        )


@router.post("/webhook")
async def handle_webhook(
    request: Request,
    x_creem_signature: str = Header(None),
    db: Session = Depends(get_db)
):
    """Handle Creem webhook events."""
    
    body = await request.body()
    
    # Verify signature
    if settings.CREEM_WEBHOOK_SECRET and x_creem_signature:
        expected_sig = hmac.new(
            settings.CREEM_WEBHOOK_SECRET.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(expected_sig, x_creem_signature):
            raise HTTPException(status_code=401, detail="Invalid signature")
    
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    event_type = payload.get("type")
    
    if event_type == "checkout.completed":
        await handle_checkout_completed(payload, db)
    
    return {"status": "ok"}


async def handle_checkout_completed(payload: dict, db: Session):
    """Handle successful checkout."""
    
    data = payload.get("data", {})
    checkout = data.get("object", data)
    
    metadata = checkout.get("metadata", {})
    device_id = metadata.get("device_id")
    product_sku = metadata.get("product_sku")
    
    if not device_id or not product_sku:
        return
    
    if product_sku not in PRODUCTS:
        return
    
    product = PRODUCTS[product_sku]
    transaction_id = checkout.get("id") or checkout.get("checkout_id")
    
    # Check for duplicate
    existing = db.query(PaymentTransaction).filter(
        PaymentTransaction.provider_transaction_id == transaction_id
    ).first()
    
    if existing:
        return
    
    # Create token
    token = GenerationToken(
        device_id=device_id,
        product_sku=product_sku,
        total_generations=product["generations"],
        remaining_generations=product["generations"],
        expires_at=datetime.utcnow() + timedelta(days=365)
    )
    db.add(token)
    db.flush()
    
    # Create transaction record
    transaction = PaymentTransaction(
        token_id=token.id,
        product_sku=product_sku,
        provider="creem",
        provider_transaction_id=transaction_id,
        amount_cents=product["price_cents"],
        currency="USD",
        status="completed",
        device_id=device_id
    )
    db.add(transaction)
    db.commit()
    
    # Track metrics
    payment_success.labels(tool=TOOL_NAME, product_sku=product_sku, currency="USD").inc()
    payment_revenue_cents.labels(tool=TOOL_NAME, product_sku=product_sku, currency="USD").inc(product["price_cents"])
    tokens_created.labels(tool=TOOL_NAME, product_sku=product_sku).inc()


@router.get("/products")
async def get_products():
    """Get available products."""
    return {
        "products": [
            {
                "sku": sku,
                "name": info["name"],
                "generations": info["generations"],
                "price_cents": info["price_cents"],
                "price_display": f"${info['price_cents'] / 100:.2f}",
                "per_generation": f"${info['price_cents'] / info['generations'] / 100:.2f}"
            }
            for sku, info in PRODUCTS.items()
        ]
    }
