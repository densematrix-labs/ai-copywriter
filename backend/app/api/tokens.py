from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from ..database import get_db
from ..models import GenerationToken
from ..schemas import TokensByDeviceResponse, TokenInfo
from ..services.token_service import check_can_generate
from ..config import get_settings

settings = get_settings()
router = APIRouter(prefix="/api/v1/tokens", tags=["tokens"])


@router.get("/by-device/{device_id}", response_model=TokensByDeviceResponse)
async def get_tokens_by_device(device_id: str, db: Session = Depends(get_db)):
    """Get all tokens for a device."""
    
    now = datetime.utcnow()
    tokens = db.query(GenerationToken).filter(
        GenerationToken.device_id == device_id,
        GenerationToken.expires_at > now
    ).all()
    
    token_list = [
        TokenInfo(
            token=t.token,
            product_sku=t.product_sku,
            total_generations=t.total_generations,
            remaining_generations=t.remaining_generations,
            expires_at=t.expires_at
        )
        for t in tokens
    ]
    
    total_remaining = sum(t.remaining_generations for t in tokens)
    
    return TokensByDeviceResponse(tokens=token_list, total_remaining=total_remaining)


@router.get("/status/{device_id}")
async def get_device_status(device_id: str, db: Session = Depends(get_db)):
    """Get generation status for a device."""
    
    can_generate, remaining, is_free = check_can_generate(db, device_id)
    
    return {
        "can_generate": can_generate,
        "remaining_generations": remaining,
        "is_free_trial": is_free,
        "free_trial_limit": settings.FREE_GENERATIONS_PER_DEVICE
    }
