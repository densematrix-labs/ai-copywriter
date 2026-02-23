import httpx
from typing import List, Dict, Any
from ..config import get_settings
from ..schemas import CopyType

settings = get_settings()

COPY_PROMPTS = {
    CopyType.MARKETING: """Generate {variations} creative marketing copy variations for: {topic}

Tone: {tone}
Language: {language}

Requirements:
- Each variation should be unique and compelling
- Include a headline and body copy
- Focus on benefits and emotional appeal
- Keep each variation concise (50-100 words)

Output format: JSON array with objects containing "headline" and "body" fields.""",

    CopyType.PRODUCT: """Generate {variations} product description variations for: {topic}

Tone: {tone}
Language: {language}

Requirements:
- Highlight key features and benefits
- Include sensory details when relevant
- Create urgency or desire
- Each variation 80-150 words

Output format: JSON array with objects containing "title" and "description" fields.""",

    CopyType.AD: """Generate {variations} ad copy variations for: {topic}

Tone: {tone}
Language: {language}

Requirements:
- Attention-grabbing headlines
- Clear call-to-action
- Suitable for Facebook/Google/LinkedIn ads
- Each variation: headline (max 30 chars) + primary text (max 125 chars) + CTA

Output format: JSON array with objects containing "headline", "primary_text", and "cta" fields.""",

    CopyType.EMAIL: """Generate {variations} email subject line variations for: {topic}

Tone: {tone}
Language: {language}

Requirements:
- Create curiosity or urgency
- Under 50 characters each
- High open rate potential
- Avoid spam trigger words

Output format: JSON array with objects containing "subject" and "preview_text" fields.""",

    CopyType.SOCIAL: """Generate {variations} social media post variations for: {topic}

Tone: {tone}
Language: {language}

Requirements:
- Platform-agnostic (works for Instagram, Twitter, LinkedIn)
- Include relevant hashtag suggestions
- Engaging and shareable
- Each variation 100-200 characters

Output format: JSON array with objects containing "post" and "hashtags" fields.""",

    CopyType.BLOG: """Generate {variations} blog intro paragraph variations for: {topic}

Tone: {tone}
Language: {language}

Requirements:
- Hook the reader immediately
- Set up the article premise
- Each variation 100-150 words
- Include a thesis statement

Output format: JSON array with objects containing "hook" and "intro" fields.""",
}


async def generate_copy(
    copy_type: CopyType,
    topic: str,
    tone: str,
    language: str,
    variations: int
) -> List[Dict[str, Any]]:
    """Generate copy using LLM proxy."""
    
    prompt = COPY_PROMPTS[copy_type].format(
        variations=variations,
        topic=topic,
        tone=tone,
        language=language
    )
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{settings.LLM_PROXY_URL}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.LLM_PROXY_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a world-class copywriter. Generate creative, compelling copy. Always respond with valid JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.8,
                "max_tokens": 2000,
                "response_format": {"type": "json_object"}
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"LLM API error: {response.status_code}")
        
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        
        # Parse JSON response
        import json
        try:
            parsed = json.loads(content)
            # Handle both array and object with array field
            if isinstance(parsed, list):
                return parsed
            elif isinstance(parsed, dict):
                # Find the first array in the response
                for key in parsed:
                    if isinstance(parsed[key], list):
                        return parsed[key]
                return [parsed]
            return [parsed]
        except json.JSONDecodeError:
            # Fallback: return content as single variation
            return [{"content": content}]


def format_variation_content(copy_type: CopyType, variation: Dict[str, Any]) -> str:
    """Format variation dict to readable string."""
    
    if copy_type == CopyType.MARKETING:
        headline = variation.get("headline", "")
        body = variation.get("body", variation.get("content", ""))
        return f"**{headline}**\n\n{body}" if headline else body
    
    elif copy_type == CopyType.PRODUCT:
        title = variation.get("title", "")
        desc = variation.get("description", variation.get("content", ""))
        return f"**{title}**\n\n{desc}" if title else desc
    
    elif copy_type == CopyType.AD:
        headline = variation.get("headline", "")
        text = variation.get("primary_text", "")
        cta = variation.get("cta", "")
        parts = []
        if headline:
            parts.append(f"📢 {headline}")
        if text:
            parts.append(text)
        if cta:
            parts.append(f"👉 {cta}")
        return "\n".join(parts) if parts else str(variation)
    
    elif copy_type == CopyType.EMAIL:
        subject = variation.get("subject", "")
        preview = variation.get("preview_text", "")
        return f"📧 Subject: {subject}\n📄 Preview: {preview}" if subject else str(variation)
    
    elif copy_type == CopyType.SOCIAL:
        post = variation.get("post", variation.get("content", ""))
        hashtags = variation.get("hashtags", [])
        if isinstance(hashtags, list):
            hashtags = " ".join(hashtags)
        return f"{post}\n\n{hashtags}" if hashtags else post
    
    elif copy_type == CopyType.BLOG:
        hook = variation.get("hook", "")
        intro = variation.get("intro", variation.get("content", ""))
        return f"🪝 {hook}\n\n{intro}" if hook else intro
    
    return str(variation.get("content", variation))
