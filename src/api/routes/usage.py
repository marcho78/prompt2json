from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import Optional
from src.models.database import get_db, User
from src.api.dependencies_optional import get_current_user_optional
from src.middleware.rate_limiter import rate_limiter

router = APIRouter()


@router.get("/usage")
async def get_usage_stats(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Get current usage statistics for the user
    Shows daily request and token usage with limits
    """
    
    user_id = str(current_user.id) if current_user else None
    
    usage_stats = await rate_limiter.get_usage_stats(
        request=request,
        user_id=user_id
    )
    
    # Add helpful messages based on usage
    messages = []
    usage_percent = usage_stats['usage_percent']
    
    if usage_percent['requests'] >= 90:
        if usage_stats['user_type'] == 'anonymous':
            messages.append("You're near your request limit! Register for free to get 5x more daily requests.")
        else:
            messages.append("You're near your daily request limit. Resets at midnight UTC.")
    elif usage_percent['requests'] >= 80:
        messages.append(f"You have {usage_stats['usage']['requests_remaining']} requests remaining today.")
    
    if usage_percent['tokens'] >= 90:
        if usage_stats['user_type'] == 'anonymous':
            messages.append("You're near your token limit! Register for free to get 4x more daily tokens.")
        else:
            messages.append("You're near your daily token limit. Try using 'simple' mode to save tokens.")
    elif usage_percent['tokens'] >= 80:
        messages.append(f"You have {usage_stats['usage']['tokens_remaining']:,} tokens remaining today.")
    
    # Add upgrade benefits for anonymous users
    upgrade_benefits = None
    if usage_stats['user_type'] == 'anonymous':
        upgrade_benefits = {
            'requests': f"50 daily requests (5x more than {usage_stats['limits']['daily_requests']})",
            'tokens': f"200,000 daily tokens (4x more than {usage_stats['limits']['daily_tokens']:,})",
            'features': [
                "Access to 'complex' prompt generation",
                "Higher per-request token limits",
                "Prompt history and management",
                "Priority support"
            ]
        }
    
    return {
        'user_type': usage_stats['user_type'],
        'daily_limits': {
            'requests': {
                'limit': usage_stats['limits']['daily_requests'],
                'used': usage_stats['usage']['requests_used'],
                'remaining': usage_stats['usage']['requests_remaining'],
                'usage_percent': usage_percent['requests']
            },
            'tokens': {
                'limit': usage_stats['limits']['daily_tokens'],
                'used': usage_stats['usage']['tokens_used'],
                'remaining': usage_stats['usage']['tokens_remaining'],
                'usage_percent': usage_percent['tokens']
            }
        },
        'per_request_limits': {
            'max_tokens': usage_stats['limits']['max_tokens_per_request']
        },
        'reset_time': usage_stats['reset_time'],
        'messages': messages,
        'upgrade_benefits': upgrade_benefits
    }


@router.get("/usage/simple")
async def get_simple_usage(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Simple usage endpoint for frontend components
    Returns just the essential usage data
    """
    
    user_id = str(current_user.id) if current_user else None
    usage_stats = await rate_limiter.get_usage_stats(request=request, user_id=user_id)
    
    return {
        'requests_used': usage_stats['usage']['requests_used'],
        'requests_limit': usage_stats['limits']['daily_requests'],
        'tokens_used': usage_stats['usage']['tokens_used'],
        'tokens_limit': usage_stats['limits']['daily_tokens'],
        'user_type': usage_stats['user_type'],
        'warning_level': 'high' if max(usage_stats['usage_percent']['requests'], usage_stats['usage_percent']['tokens']) >= 90 else 
                        'medium' if max(usage_stats['usage_percent']['requests'], usage_stats['usage_percent']['tokens']) >= 80 else 
                        'low'
    }
