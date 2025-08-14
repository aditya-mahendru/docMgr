"""
User Management Models
Pydantic models for user authentication, sessions, and chat functionality
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

# User Registration and Authentication Models
class UserRegistration(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Username for the account")
    email: EmailStr = Field(..., description="Email address for the account")
    password: str = Field(..., min_length=8, max_length=128, description="Password for the account")
    subscription_tier: Optional[str] = Field(default="free", description="Subscription tier")
    
    @validator('username')
    def validate_username(cls, v):
        if not v.isalnum():
            raise ValueError('Username must contain only alphanumeric characters')
        return v.lower()

class UserLogin(BaseModel):
    username: str = Field(..., description="Username or email for login")
    password: str = Field(..., description="Password for login")

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: str
    last_login: Optional[str]
    is_active: bool
    total_documents: int
    total_llm_calls: int
    total_tokens_processed: int
    subscription_tier: str
    api_quota: int
    api_quota_reset_date: str

class AuthResponse(BaseModel):
    success: bool
    user: Optional[UserResponse]
    session_token: Optional[str]
    expires_at: Optional[str]
    error: Optional[str]

# Session Management Models
class SessionInfo(BaseModel):
    session_id: int
    user_id: int
    username: str
    email: str
    subscription_tier: str
    expires_at: str
    created_at: str
    last_activity: str

class SessionValidation(BaseModel):
    valid: bool
    session_info: Optional[SessionInfo]
    error: Optional[str]

# Chat Models
class ChatMessage(BaseModel):
    content: str = Field(..., min_length=1, max_length=10000, description="Message content")
    conversation_id: Optional[str] = Field(None, description="Conversation identifier")
    
    @validator('content')
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError('Message content cannot be empty')
        return v.strip()

class ChatResponse(BaseModel):
    success: bool
    message_id: Optional[int]
    timestamp: Optional[str]
    error: Optional[str]

class ChatMessageResponse(BaseModel):
    id: int
    message_type: str  # 'user' or 'assistant'
    content: str
    timestamp: str
    tokens_used: Optional[int]
    llm_model: Optional[str]
    response_time_ms: Optional[int]
    cost_estimate: Optional[float]

class ConversationHistory(BaseModel):
    success: bool
    messages: List[ChatMessageResponse]
    total_messages: int
    conversation_id: Optional[str]

class ConversationStart(BaseModel):
    success: bool
    conversation_id: Optional[str]
    session_id: Optional[int]
    user_id: Optional[int]
    started_at: Optional[str]
    error: Optional[str]

# User Profile and Statistics Models
class UserProfile(BaseModel):
    id: int
    username: str
    email: str
    created_at: str
    last_login: Optional[str]
    is_active: bool
    total_documents: int
    total_llm_calls: int
    total_tokens_processed: int
    subscription_tier: str
    api_quota: int
    api_quota_reset_date: str

class UserStats(BaseModel):
    success: bool
    period_days: int
    message_stats: Dict[str, Dict[str, Any]]
    total_tokens: int
    total_cost: float
    avg_response_time_ms: float
    conversation_count: int

class UserActivitySummary(BaseModel):
    success: bool
    activity_counts: Dict[str, int]
    recent_documents: int
    period_days: int

# Chat Statistics Models
class ChatStats(BaseModel):
    success: bool
    period_days: int
    message_stats: Dict[str, Dict[str, Any]]
    total_tokens: int
    total_cost: float
    avg_response_time_ms: float
    conversation_count: int

class ChatSearchResult(BaseModel):
    id: int
    message_type: str
    content: str
    timestamp: str
    conversation_id: Optional[str]

class ChatSearchResponse(BaseModel):
    success: bool
    query: str
    results: List[ChatSearchResult]
    total_results: int

# Error Response Models
class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

# Success Response Models
class SuccessResponse(BaseModel):
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None

# Logout Models
class LogoutRequest(BaseModel):
    session_token: str

class LogoutResponse(BaseModel):
    success: bool
    message: str

# Password Change Models
class PasswordChange(BaseModel):
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password")
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('New password must be at least 8 characters long')
        return v

class PasswordChangeResponse(BaseModel):
    success: bool
    message: str
    error: Optional[str]

# Subscription Models
class SubscriptionTier(BaseModel):
    tier: str
    name: str
    description: str
    monthly_cost: float
    api_quota: int
    features: List[str]

class SubscriptionChange(BaseModel):
    new_tier: str = Field(..., description="New subscription tier")

class SubscriptionResponse(BaseModel):
    success: bool
    current_tier: str
    new_tier: Optional[str]
    message: str
    error: Optional[str]

# API Quota Models
class QuotaInfo(BaseModel):
    current_usage: int
    quota_limit: int
    reset_date: str
    remaining: int
    usage_percentage: float

class QuotaResponse(BaseModel):
    success: bool
    quota_info: Optional[QuotaInfo]
    error: Optional[str]
