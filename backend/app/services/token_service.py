from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from ..models import GenerationToken, FreeTrialUsage
from ..config import get_settings

settings = get_settings()


def get_free_trial_usage(db: Session, device_id: str) -> FreeTrialUsage:
    """Get or create free trial usage record."""
    usage = db.query(FreeTrialUsage).filter(
        FreeTrialUsage.device_id == device_id
    ).first()
    
    if not usage:
        usage = FreeTrialUsage(device_id=device_id, generations_used=0)
        db.add(usage)
        db.commit()
        db.refresh(usage)
    
    return usage


def check_can_generate(db: Session, device_id: str) -> Tuple[bool, Optional[int], bool]:
    """
    Check if device can generate.
    Returns: (can_generate, remaining_count, is_free_trial)
    """
    # First check for paid tokens
    now = datetime.utcnow()
    tokens = db.query(GenerationToken).filter(
        GenerationToken.device_id == device_id,
        GenerationToken.remaining_generations > 0,
        GenerationToken.expires_at > now
    ).all()
    
    total_remaining = sum(t.remaining_generations for t in tokens)
    
    if total_remaining > 0:
        return True, total_remaining, False
    
    # Check free trial
    usage = get_free_trial_usage(db, device_id)
    free_remaining = settings.FREE_GENERATIONS_PER_DEVICE - usage.generations_used
    
    if free_remaining > 0:
        return True, free_remaining, True
    
    return False, 0, False


def consume_generation(db: Session, device_id: str) -> Tuple[bool, Optional[int], bool]:
    """
    Consume one generation.
    Returns: (success, remaining_after, was_free_trial)
    """
    # Try to consume from paid tokens first
    now = datetime.utcnow()
    token = db.query(GenerationToken).filter(
        GenerationToken.device_id == device_id,
        GenerationToken.remaining_generations > 0,
        GenerationToken.expires_at > now
    ).order_by(GenerationToken.expires_at.asc()).first()
    
    if token:
        token.remaining_generations -= 1
        db.commit()
        
        # Calculate total remaining
        total = db.query(GenerationToken).filter(
            GenerationToken.device_id == device_id,
            GenerationToken.remaining_generations > 0,
            GenerationToken.expires_at > now
        ).all()
        total_remaining = sum(t.remaining_generations for t in total)
        
        return True, total_remaining, False
    
    # Try free trial
    usage = get_free_trial_usage(db, device_id)
    free_remaining = settings.FREE_GENERATIONS_PER_DEVICE - usage.generations_used
    
    if free_remaining > 0:
        usage.generations_used += 1
        usage.last_used_at = now
        db.commit()
        return True, free_remaining - 1, True
    
    return False, 0, False


def get_tokens_by_device(db: Session, device_id: str) -> list:
    """Get all valid tokens for a device."""
    now = datetime.utcnow()
    return db.query(GenerationToken).filter(
        GenerationToken.device_id == device_id,
        GenerationToken.expires_at > now
    ).all()


def create_token(
    db: Session,
    device_id: str,
    product_sku: str,
    total_generations: int,
    expires_days: int = 365
) -> GenerationToken:
    """Create a new generation token."""
    token = GenerationToken(
        device_id=device_id,
        product_sku=product_sku,
        total_generations=total_generations,
        remaining_generations=total_generations,
        expires_at=datetime.utcnow() + timedelta(days=expires_days)
    )
    db.add(token)
    db.commit()
    db.refresh(token)
    return token
