from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import CopyGenerateRequest, CopyGenerateResponse, CopyVariation
from ..services.copy_service import generate_copy, format_variation_content
from ..services.token_service import check_can_generate, consume_generation
from ..metrics import copy_generated, tokens_consumed, free_trial_used, TOOL_NAME

router = APIRouter(prefix="/api/v1/copy", tags=["copy"])


@router.post("/generate", response_model=CopyGenerateResponse)
async def generate_copy_endpoint(
    request: CopyGenerateRequest,
    db: Session = Depends(get_db)
):
    """Generate copy variations."""
    
    # Check if device can generate
    can_generate, remaining, is_free = check_can_generate(db, request.device_id)
    
    if not can_generate:
        raise HTTPException(
            status_code=402,
            detail="No generations remaining. Please purchase a pack to continue."
        )
    
    # Consume one generation
    success, new_remaining, was_free = consume_generation(db, request.device_id)
    
    if not success:
        raise HTTPException(
            status_code=402,
            detail="Failed to consume generation. Please try again."
        )
    
    # Track metrics
    if was_free:
        free_trial_used.labels(tool=TOOL_NAME).inc()
    else:
        tokens_consumed.labels(tool=TOOL_NAME).inc()
    
    copy_generated.labels(tool=TOOL_NAME, copy_type=request.copy_type.value).inc()
    
    try:
        # Generate copy
        raw_variations = await generate_copy(
            copy_type=request.copy_type,
            topic=request.topic,
            tone=request.tone,
            language=request.language,
            variations=request.variations
        )
        
        # Format variations
        variations = []
        for i, var in enumerate(raw_variations[:request.variations]):
            content = format_variation_content(request.copy_type, var)
            variations.append(CopyVariation(
                id=i + 1,
                content=content,
                word_count=len(content.split())
            ))
        
        return CopyGenerateResponse(
            success=True,
            variations=variations,
            copy_type=request.copy_type,
            remaining_generations=new_remaining,
            is_free_trial=was_free
        )
        
    except Exception as e:
        # Refund the generation on error
        # (In production, you'd want more sophisticated error handling)
        raise HTTPException(
            status_code=500,
            detail=f"Generation failed: {str(e)}"
        )


@router.get("/types")
async def get_copy_types():
    """Get available copy types."""
    return {
        "types": [
            {"id": "marketing", "name": "Marketing Copy", "icon": "📣", "description": "Headlines, taglines, and marketing messages"},
            {"id": "product", "name": "Product Description", "icon": "🛍️", "description": "E-commerce product descriptions"},
            {"id": "ad", "name": "Ad Copy", "icon": "📱", "description": "Facebook, Google, LinkedIn ads"},
            {"id": "email", "name": "Email Subject Lines", "icon": "📧", "description": "High-converting email subjects"},
            {"id": "social", "name": "Social Media", "icon": "📲", "description": "Instagram, Twitter, LinkedIn posts"},
            {"id": "blog", "name": "Blog Intro", "icon": "📝", "description": "Engaging blog introductions"},
        ]
    }
