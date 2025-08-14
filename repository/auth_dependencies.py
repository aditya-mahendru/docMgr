"""
Authentication Dependencies
FastAPI dependencies for user authentication and session management
"""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
from repository.user_manager import UserManager
from models.user_models import SessionInfo
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize security scheme
security = HTTPBearer(auto_error=False)

# Initialize user manager
user_manager = UserManager()

async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    """
    Dependency to get current authenticated user from session token
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    session_token = credentials.credentials
    
    # Validate session token
    session_info = user_manager.validate_session(session_token)
    
    if not session_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Add session info to request state for logging
    request.state.user_id = session_info['user_id']
    request.state.username = session_info['username']
    request.state.session_id = session_info['session_id']
    
    return session_info

async def get_current_active_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Dependency to get current active user (not deactivated)
    """
    if not current_user.get('is_active', False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )
    
    return current_user

async def get_current_user_optional(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict[str, Any]]:
    """
    Optional dependency to get current user (returns None if not authenticated)
    """
    if not credentials:
        return None
    
    session_token = credentials.credentials
    session_info = user_manager.validate_session(session_token)
    
    if session_info:
        # Add session info to request state for logging
        request.state.user_id = session_info['user_id']
        request.state.username = session_info['username']
        request.state.session_id = session_info['session_id']
    
    return session_info

def require_subscription_tier(required_tier: str):
    """
    Decorator to require specific subscription tier
    """
    def dependency(current_user: Dict[str, Any] = Depends(get_current_active_user)):
        user_tier = current_user.get('subscription_tier', 'free')
        
        # Define tier hierarchy
        tier_hierarchy = {
            'free': 0,
            'basic': 1,
            'premium': 2,
            'enterprise': 3
        }
        
        user_level = tier_hierarchy.get(user_tier, 0)
        required_level = tier_hierarchy.get(required_tier, 0)
        
        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Subscription tier '{required_tier}' required. Current tier: '{user_tier}'"
            )
        
        return current_user
    
    return dependency

def require_api_quota():
    """
    Dependency to check if user has remaining API quota
    """
    def dependency(current_user: Dict[str, Any] = Depends(get_current_active_user)):
        # Get current quota usage
        user_profile = user_manager.get_user_profile(current_user['user_id'])
        
        if not user_profile:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to retrieve user profile"
            )
        
        # Check if quota is exceeded
        if user_profile['total_llm_calls'] >= user_profile['api_quota']:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="API quota exceeded. Please upgrade your subscription or wait for quota reset."
            )
        
        return current_user
    
    return dependency

def get_client_info(request: Request) -> Dict[str, str]:
    """
    Extract client information from request
    """
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    
    return {
        "ip_address": client_ip,
        "user_agent": user_agent
    }

# Convenience functions for common permission checks
def require_basic_tier():
    """Require basic subscription tier or higher"""
    return require_subscription_tier("basic")

def require_premium_tier():
    """Require premium subscription tier or higher"""
    return require_subscription_tier("premium")

def require_enterprise_tier():
    """Require enterprise subscription tier"""
    return require_subscription_tier("enterprise")
