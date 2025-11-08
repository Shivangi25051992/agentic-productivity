"""
LLM Configuration Models

Defines data models for multi-LLM provider management, configuration,
and usage tracking for the Agentic AI system.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, Dict, Any
from enum import Enum
from datetime import datetime, timezone
import uuid


class LLMProvider(str, Enum):
    """
    Supported LLM providers
    
    Extensible enum - add new providers as they become available
    """
    OPENAI = "openai"
    GEMINI = "gemini"
    MIXTRAL = "mixtral"
    ANTHROPIC = "anthropic"
    GROQ = "groq"


class LLMConfig(BaseModel):
    """
    Configuration for a specific LLM provider
    
    Stores API credentials, model settings, and operational parameters.
    Admin-configurable via Firestore collection: admin/llm_providers/{provider_id}
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    provider: LLMProvider
    api_key: str = Field(..., description="API key for the provider (encrypted in storage)")
    model_name: str = Field(..., description="Specific model to use (e.g., gpt-4o-mini, gemini-1.5-pro)")
    priority: int = Field(1, ge=1, le=10, description="Priority for provider selection (1=highest)")
    
    # Model parameters
    max_tokens: int = Field(4000, ge=100, le=32000, description="Maximum tokens per request")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Sampling temperature")
    top_p: Optional[float] = Field(0.9, ge=0.0, le=1.0, description="Nucleus sampling parameter")
    
    # Operational settings
    is_active: bool = Field(True, description="Whether this provider is currently enabled")
    quota_limit: Optional[int] = Field(None, description="Monthly token quota limit (None = unlimited)")
    quota_used: int = Field(0, ge=0, description="Tokens used in current month")
    
    # Cost tracking
    cost_per_1k_tokens: Optional[float] = Field(None, description="Cost per 1000 tokens in USD")
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[str] = None  # Admin user ID
    
    @field_validator('api_key')
    @classmethod
    def api_key_not_empty(cls, v):
        """Ensure API key is not empty"""
        if not v or not v.strip():
            raise ValueError("API key cannot be empty")
        return v.strip()
    
    @field_validator('model_name')
    @classmethod
    def model_name_not_empty(cls, v):
        """Ensure model name is not empty"""
        if not v or not v.strip():
            raise ValueError("Model name cannot be empty")
        return v.strip()
    
    def is_quota_exceeded(self) -> bool:
        """Check if quota limit has been exceeded"""
        if self.quota_limit is None:
            return False
        return self.quota_used >= self.quota_limit
    
    def can_be_used(self) -> bool:
        """Check if this provider can be used (active and under quota)"""
        return self.is_active and not self.is_quota_exceeded()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for Firestore storage"""
        data = self.model_dump()
        data['created_at'] = self.created_at
        data['updated_at'] = self.updated_at
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'LLMConfig':
        """Create from Firestore dictionary"""
        return cls(**data)
    
    model_config = ConfigDict(use_enum_values=True)


class LLMUsageLog(BaseModel):
    """
    Log entry for LLM API usage
    
    Stored in Firestore: admin/llm_usage_logs/{log_id}
    Used for analytics, billing, and quota tracking
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    provider: LLMProvider
    model_name: str
    
    # Request details
    prompt_template_id: Optional[str] = None
    user_id: Optional[str] = None  # If user-specific request
    request_type: str = Field(..., description="Type of request (chat, meal_plan, workout, etc.)")
    
    # Usage metrics
    tokens_used: int = Field(ge=0, description="Total tokens consumed")
    prompt_tokens: int = Field(ge=0, description="Tokens in prompt")
    completion_tokens: int = Field(ge=0, description="Tokens in completion")
    
    # Performance metrics
    response_time_ms: int = Field(ge=0, description="Response time in milliseconds")
    
    # Cost tracking
    cost_usd: Optional[float] = Field(None, ge=0.0, description="Cost in USD")
    
    # Outcome
    success: bool = Field(True, description="Whether request succeeded")
    error: Optional[str] = None  # Error message if success=False
    error_code: Optional[str] = None  # Error code for categorization
    
    # Metadata
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> dict:
        """Convert to dictionary for Firestore storage"""
        data = self.model_dump()
        data['timestamp'] = self.timestamp
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'LLMUsageLog':
        """Create from Firestore dictionary"""
        return cls(**data)
    
    model_config = ConfigDict(use_enum_values=True)


class LLMRequest(BaseModel):
    """
    Request to the LLM Router
    
    Unified interface for all LLM requests regardless of provider
    Supports both template-based and direct prompt modes
    """
    # Template-based mode (preferred)
    prompt_template_id: Optional[str] = Field(None, description="ID of prompt template to use")
    context: Dict[str, Any] = Field(default_factory=dict, description="Context variables for template")
    
    # Direct prompt mode (for backward compatibility)
    system_prompt: Optional[str] = Field(None, description="Direct system prompt (if not using template)")
    user_prompt: Optional[str] = Field(None, description="Direct user prompt (if not using template)")
    
    # Optional overrides
    preferred_provider: Optional[LLMProvider] = None
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=100, le=32000)
    response_format: Optional[str] = Field(None, description="Response format: 'text' or 'json'")
    
    # Metadata
    user_id: Optional[str] = None
    request_type: str = "generic"  # chat, meal_plan, workout, etc.
    
    model_config = ConfigDict(use_enum_values=True)


class LLMResponse(BaseModel):
    """
    Response from the LLM Router
    
    Standardized response format with metadata
    """
    content: str = Field(..., description="Generated content")
    provider_used: LLMProvider = Field(..., description="Provider that fulfilled the request")
    model_used: str = Field(..., description="Specific model that was used")
    
    # Usage metrics
    tokens_used: int = Field(ge=0)
    prompt_tokens: int = Field(ge=0)
    completion_tokens: int = Field(ge=0)
    response_time_ms: int = Field(ge=0)
    
    # Optional structured data
    structured_data: Optional[Dict[str, Any]] = None  # If JSON response
    
    # Metadata
    success: bool = True
    fallback_used: bool = Field(False, description="Whether fallback provider was used")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    model_config = ConfigDict(use_enum_values=True)


class LLMQuotaStatus(BaseModel):
    """
    Current quota status for a provider
    
    Used for monitoring and quota enforcement
    """
    provider: LLMProvider
    quota_limit: Optional[int] = None  # None = unlimited
    quota_used: int = 0
    quota_remaining: Optional[int] = None
    percentage_used: float = 0.0
    is_exceeded: bool = False
    reset_date: Optional[datetime] = None  # When quota resets
    
    @classmethod
    def from_config(cls, config: LLMConfig) -> 'LLMQuotaStatus':
        """Create quota status from config"""
        quota_remaining = None
        percentage_used = 0.0
        is_exceeded = False
        
        if config.quota_limit is not None:
            quota_remaining = max(0, config.quota_limit - config.quota_used)
            percentage_used = (config.quota_used / config.quota_limit) * 100
            is_exceeded = config.quota_used >= config.quota_limit
        
        return cls(
            provider=config.provider,
            quota_limit=config.quota_limit,
            quota_used=config.quota_used,
            quota_remaining=quota_remaining,
            percentage_used=percentage_used,
            is_exceeded=is_exceeded
        )
    
    model_config = ConfigDict(use_enum_values=True)

