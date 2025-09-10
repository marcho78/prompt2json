from typing import Dict, Optional, Tuple
from datetime import datetime, timezone, timedelta
import json
import hashlib
from fastapi import HTTPException, status, Request
from fastapi.responses import JSONResponse
import redis.asyncio as redis
from src.config import settings
import logging

logger = logging.getLogger(__name__)


class FreeRateLimiter:
    """
    Production-ready rate limiter for free AI prompt generator tool
    - IP-based tracking for anonymous users
    - Enhanced limits for registered users  
    - Redis-backed for scalability
    - Daily limits with midnight UTC reset
    """
    
    def __init__(self):
        self.redis_client = None
        self._initialize_redis()
    
    def _initialize_redis(self):
        """Initialize Redis connection - DISABLED for deployment stability"""
        try:
            # Temporarily disable Redis for deployment stability
            logger.info("Redis disabled for deployment - using in-memory rate limiting")
            self.redis_client = None
            self._memory_storage = {}
        except Exception as e:
            logger.warning(f"Redis initialization failed, using in-memory fallback: {e}")
            self.redis_client = None
            self._memory_storage = {}
    
    def get_user_identifier(self, request: Request, user_id: Optional[str] = None) -> str:
        """
        Get unique identifier for rate limiting
        Priority: user_id > IP address > browser fingerprint
        """
        if user_id:
            return f"user:{user_id}"
        
        # Get IP address (handle proxy headers)
        ip = (
            request.headers.get("X-Forwarded-For", "").split(",")[0].strip() or
            request.headers.get("X-Real-IP", "") or
            request.client.host if request.client else "unknown"
        )
        
        # Create browser fingerprint as fallback
        user_agent = request.headers.get("User-Agent", "")
        accept_lang = request.headers.get("Accept-Language", "")
        fingerprint = hashlib.md5(f"{ip}:{user_agent}:{accept_lang}".encode()).hexdigest()[:8]
        
        return f"ip:{ip}:{fingerprint}"
    
    async def is_registered_user(self, identifier: str) -> bool:
        """Check if identifier represents a registered user"""
        return identifier.startswith("user:")
    
    def get_user_limits(self, is_registered: bool) -> Dict[str, int]:
        """Get limits based on user type"""
        if is_registered:
            return {
                'daily_requests': settings.REGISTERED_DAILY_REQUESTS,
                'daily_tokens': settings.REGISTERED_DAILY_TOKENS,
                'max_tokens_per_request': settings.REGISTERED_MAX_TOKENS_PER_REQUEST
            }
        else:
            return {
                'daily_requests': settings.ANONYMOUS_DAILY_REQUESTS,
                'daily_tokens': settings.ANONYMOUS_DAILY_TOKENS,
                'max_tokens_per_request': settings.ANONYMOUS_MAX_TOKENS_PER_REQUEST
            }
    
    async def check_limits(
        self, 
        request: Request, 
        estimated_tokens: int = 2000,
        user_id: Optional[str] = None,
        endpoint: str = "general"
    ) -> Dict:
        """
        Check rate limits and return usage statistics
        Raises HTTPException if limits exceeded
        """
        identifier = self.get_user_identifier(request, user_id)
        is_registered = await self.is_registered_user(identifier)
        limits = self.get_user_limits(is_registered)
        
        # Get current date for daily limits
        current_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        
        # Redis keys
        request_key = f"limit:daily:requests:{identifier}:{current_date}"
        token_key = f"limit:daily:tokens:{identifier}:{current_date}"
        
        # Get current usage
        try:
            if self.redis_client:
                current_requests = int(await self.redis_client.get(request_key) or 0)
                current_tokens = int(await self.redis_client.get(token_key) or 0)
            else:
                # Fallback to in-memory storage
                current_requests = self._memory_storage.get(request_key, 0)
                current_tokens = self._memory_storage.get(token_key, 0)
        except Exception as e:
            logger.error(f"Redis error in rate limiting: {e}")
            current_requests = current_tokens = 0
        
        # Apply endpoint-specific limits
        endpoint_limits = self._get_endpoint_limits(endpoint, is_registered)
        if endpoint_limits:
            # Check endpoint-specific request limit
            if 'requests_per_day' in endpoint_limits:
                endpoint_request_key = f"limit:endpoint:{endpoint}:{identifier}:{current_date}"
                try:
                    if self.redis_client:
                        endpoint_requests = int(await self.redis_client.get(endpoint_request_key) or 0)
                    else:
                        endpoint_requests = self._memory_storage.get(endpoint_request_key, 0)
                except Exception:
                    endpoint_requests = 0
                
                if endpoint_requests >= endpoint_limits['requests_per_day']:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail={
                            'error': 'ENDPOINT_REQUEST_LIMIT_EXCEEDED',
                            'message': f"You've reached your daily limit for {endpoint}. Try again tomorrow.",
                            'endpoint': endpoint,
                            'limit': endpoint_limits['requests_per_day'],
                            'reset_time': self._get_next_reset_time()
                        }
                    )
        
        # Check if request would exceed per-request token limit
        if estimated_tokens > limits['max_tokens_per_request']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    'error': 'REQUEST_TOO_LARGE',
                    'message': f"This request requires {estimated_tokens} tokens, but limit is {limits['max_tokens_per_request']}.",
                    'estimated_tokens': estimated_tokens,
                    'max_tokens_per_request': limits['max_tokens_per_request'],
                    'tips': [
                        "Try using 'simple' complexity mode",
                        "Reduce input text length",
                        "Register for free to get higher limits" if not is_registered else "Consider breaking into smaller requests"
                    ]
                }
            )
        
        # Check daily request limit
        if current_requests >= limits['daily_requests']:
            upgrade_message = "" if is_registered else " Register for free to get 5x more usage."
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    'error': 'DAILY_REQUEST_LIMIT_EXCEEDED',
                    'message': f"You've reached your daily limit of {limits['daily_requests']} requests. Please try again tomorrow.{upgrade_message}",
                    'limit': limits['daily_requests'],
                    'used': current_requests,
                    'reset_time': self._get_next_reset_time(),
                    'upgrade_url': '/auth/register' if not is_registered else None
                }
            )
        
        # Check daily token limit
        if current_tokens + estimated_tokens > limits['daily_tokens']:
            upgrade_message = "" if is_registered else " Register for free to get 4x more tokens."
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    'error': 'DAILY_TOKEN_LIMIT_EXCEEDED',
                    'message': f"You've used your daily token allowance. Try simpler prompts or wait until tomorrow.{upgrade_message}",
                    'limit': limits['daily_tokens'],
                    'used': current_tokens,
                    'estimated_for_request': estimated_tokens,
                    'reset_time': self._get_next_reset_time(),
                    'tips': [
                        "Use 'simple' complexity for fewer tokens",
                        "Optimize your prompts to use fewer tokens",
                        "Register for free to get 200,000 daily tokens" if not is_registered else "Try breaking large requests into smaller ones"
                    ]
                }
            )
        
        # Update counters (increment usage)
        try:
            if self.redis_client:
                # Use pipeline for atomic operations
                pipe = self.redis_client.pipeline()
                pipe.incr(request_key)
                pipe.expire(request_key, 86400)  # 24 hours
                pipe.incr(token_key, estimated_tokens)
                pipe.expire(token_key, 86400)
                
                # Update endpoint-specific counter if applicable
                if endpoint_limits and 'requests_per_day' in endpoint_limits:
                    endpoint_request_key = f"limit:endpoint:{endpoint}:{identifier}:{current_date}"
                    pipe.incr(endpoint_request_key)
                    pipe.expire(endpoint_request_key, 86400)
                
                await pipe.execute()
            else:
                # Fallback to in-memory storage
                self._memory_storage[request_key] = current_requests + 1
                self._memory_storage[token_key] = current_tokens + estimated_tokens
                
                if endpoint_limits and 'requests_per_day' in endpoint_limits:
                    endpoint_request_key = f"limit:endpoint:{endpoint}:{identifier}:{current_date}"
                    self._memory_storage[endpoint_request_key] = self._memory_storage.get(endpoint_request_key, 0) + 1
        
        except Exception as e:
            logger.error(f"Failed to update rate limit counters: {e}")
        
        # Calculate remaining usage
        requests_remaining = limits['daily_requests'] - current_requests - 1
        tokens_remaining = limits['daily_tokens'] - current_tokens - estimated_tokens
        
        # Calculate warning levels
        request_usage_percent = (current_requests + 1) / limits['daily_requests']
        token_usage_percent = (current_tokens + estimated_tokens) / limits['daily_tokens']
        
        return {
            'allowed': True,
            'user_type': 'registered' if is_registered else 'anonymous',
            'limits': limits,
            'usage': {
                'requests_used': current_requests + 1,
                'tokens_used': current_tokens + estimated_tokens,
                'requests_remaining': requests_remaining,
                'tokens_remaining': tokens_remaining
            },
            'warnings': {
                'near_request_limit': request_usage_percent >= settings.WARNING_THRESHOLD,
                'near_token_limit': token_usage_percent >= settings.WARNING_THRESHOLD,
                'request_usage_percent': round(request_usage_percent * 100, 1),
                'token_usage_percent': round(token_usage_percent * 100, 1)
            },
            'reset_time': self._get_next_reset_time()
        }
    
    def _get_endpoint_limits(self, endpoint: str, is_registered: bool) -> Optional[Dict]:
        """Get endpoint-specific limits"""
        if is_registered:
            endpoint_limits = {
                'generate-prompt': {'requests_per_day': 30},
                'optimize-prompt': {'requests_per_day': 20},
                'test-prompt': {'requests_per_day': 20},
                'batch-generate': {'requests_per_day': 5}
            }
        else:
            endpoint_limits = {
                'generate-prompt': {'requests_per_day': 10},
                'optimize-prompt': {'requests_per_day': 5},
                'test-prompt': {'requests_per_day': 5}
            }
        
        return endpoint_limits.get(endpoint)
    
    def _get_next_reset_time(self) -> str:
        """Get next UTC midnight as ISO string"""
        now = datetime.now(timezone.utc)
        next_midnight = now.replace(hour=0, minute=0, second=0, microsecond=0) + \
                       timedelta(days=1)
        return next_midnight.isoformat()
    
    async def get_usage_stats(self, request: Request, user_id: Optional[str] = None) -> Dict:
        """Get current usage statistics for a user"""
        identifier = self.get_user_identifier(request, user_id)
        is_registered = await self.is_registered_user(identifier)
        limits = self.get_user_limits(is_registered)
        
        current_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        request_key = f"limit:daily:requests:{identifier}:{current_date}"
        token_key = f"limit:daily:tokens:{identifier}:{current_date}"
        
        try:
            if self.redis_client:
                current_requests = int(await self.redis_client.get(request_key) or 0)
                current_tokens = int(await self.redis_client.get(token_key) or 0)
            else:
                current_requests = self._memory_storage.get(request_key, 0)
                current_tokens = self._memory_storage.get(token_key, 0)
        except Exception as e:
            logger.error(f"Redis error getting usage stats: {e}")
            current_requests = current_tokens = 0
        
        return {
            'user_type': 'registered' if is_registered else 'anonymous',
            'limits': limits,
            'usage': {
                'requests_used': current_requests,
                'tokens_used': current_tokens,
                'requests_remaining': max(0, limits['daily_requests'] - current_requests),
                'tokens_remaining': max(0, limits['daily_tokens'] - current_tokens)
            },
            'usage_percent': {
                'requests': round((current_requests / limits['daily_requests']) * 100, 1),
                'tokens': round((current_tokens / limits['daily_tokens']) * 100, 1)
            },
            'reset_time': self._get_next_reset_time()
        }


# Global rate limiter instance
rate_limiter = FreeRateLimiter()


async def apply_rate_limit(
    request: Request,
    estimated_tokens: int = 2000,
    user_id: Optional[str] = None,
    endpoint: str = "general"
) -> Dict:
    """
    Apply rate limiting to a request
    Returns usage statistics and adds rate limit headers to response
    """
    usage_stats = await rate_limiter.check_limits(
        request=request,
        estimated_tokens=estimated_tokens,
        user_id=user_id,
        endpoint=endpoint
    )
    
    return usage_stats


def add_rate_limit_headers(response: JSONResponse, usage_stats: Dict) -> JSONResponse:
    """Add rate limiting headers to response"""
    limits = usage_stats['limits']
    usage = usage_stats['usage']
    
    response.headers.update({
        'X-RateLimit-Type': 'daily',
        'X-RateLimit-Limit-Requests': str(limits['daily_requests']),
        'X-RateLimit-Remaining-Requests': str(usage['requests_remaining']),
        'X-RateLimit-Limit-Tokens': str(limits['daily_tokens']),
        'X-RateLimit-Remaining-Tokens': str(usage['tokens_remaining']),
        'X-RateLimit-Reset': usage_stats['reset_time'],
        'X-RateLimit-User-Type': usage_stats['user_type']
    })
    
    return response
