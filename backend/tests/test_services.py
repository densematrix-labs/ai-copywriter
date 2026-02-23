import pytest
from datetime import datetime, timedelta

from app.services.token_service import (
    check_can_generate,
    consume_generation,
    get_free_trial_usage,
    create_token,
)
from app.models import GenerationToken, FreeTrialUsage


def test_free_trial_initial(db):
    """New device should have free trial"""
    can_gen, remaining, is_free = check_can_generate(db, "new-device-123")
    
    assert can_gen == True
    assert remaining == 3  # FREE_GENERATIONS_PER_DEVICE
    assert is_free == True


def test_free_trial_consume(db):
    """Consuming free trial should work"""
    device_id = "test-device-456"
    
    # First generation
    success, remaining, was_free = consume_generation(db, device_id)
    assert success == True
    assert remaining == 2
    assert was_free == True
    
    # Second generation
    success, remaining, was_free = consume_generation(db, device_id)
    assert success == True
    assert remaining == 1
    assert was_free == True


def test_free_trial_exhausted(db):
    """Exhausted free trial should fail"""
    device_id = "exhausted-device"
    
    # Exhaust free trial
    usage = FreeTrialUsage(device_id=device_id, generations_used=3)
    db.add(usage)
    db.commit()
    
    can_gen, remaining, is_free = check_can_generate(db, device_id)
    
    assert can_gen == False
    assert remaining == 0


def test_paid_token_priority(db):
    """Paid tokens should be used before free trial"""
    device_id = "paid-user-device"
    
    # Create paid token
    token = create_token(db, device_id, "pack_10", 10, 365)
    
    can_gen, remaining, is_free = check_can_generate(db, device_id)
    
    assert can_gen == True
    assert remaining == 10
    assert is_free == False


def test_paid_token_consume(db):
    """Consuming paid token should work"""
    device_id = "paid-consumer"
    
    # Create token
    create_token(db, device_id, "pack_10", 10, 365)
    
    # Consume
    success, remaining, was_free = consume_generation(db, device_id)
    
    assert success == True
    assert remaining == 9
    assert was_free == False


def test_expired_token_ignored(db):
    """Expired tokens should not be counted"""
    device_id = "expired-token-device"
    
    # Create expired token
    token = GenerationToken(
        device_id=device_id,
        product_sku="pack_10",
        total_generations=10,
        remaining_generations=10,
        expires_at=datetime.utcnow() - timedelta(days=1)  # Expired
    )
    db.add(token)
    db.commit()
    
    can_gen, remaining, is_free = check_can_generate(db, device_id)
    
    # Should fall back to free trial
    assert can_gen == True
    assert remaining == 3
    assert is_free == True


def test_multiple_tokens(db):
    """Multiple valid tokens should be summed"""
    device_id = "multi-token-device"
    
    # Create multiple tokens
    create_token(db, device_id, "pack_10", 10, 365)
    create_token(db, device_id, "pack_50", 50, 365)
    
    can_gen, remaining, is_free = check_can_generate(db, device_id)
    
    assert can_gen == True
    assert remaining == 60
    assert is_free == False


def test_get_free_trial_usage_creates(db):
    """get_free_trial_usage should create record if not exists"""
    device_id = "new-free-trial-device"
    
    usage = get_free_trial_usage(db, device_id)
    
    assert usage is not None
    assert usage.device_id == device_id
    assert usage.generations_used == 0
