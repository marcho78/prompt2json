from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from src.api.dependencies import get_current_user
from src.models.database import get_db, User

# Optional security for endpoints that support both authenticated and anonymous users
security_optional = HTTPBearer(auto_error=False)


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_optional),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if authenticated, None if anonymous
    Used for endpoints that support both authenticated and anonymous users
    """
    if not credentials:
        return None
    
    try:
        # Use existing get_current_user function but handle exceptions
        return get_current_user(credentials, db)
    except HTTPException:
        # Invalid token, treat as anonymous user
        return None
