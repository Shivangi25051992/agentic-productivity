"""
Prompt Template Models

Defines data models for managing LLM prompt templates with versioning,
variable substitution, and JSON schema validation.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import uuid
import re


class PromptTemplate(BaseModel):
    """
    Reusable prompt template with variable substitution
    
    Stored in Firestore: admin/prompts/{template_id}
    Supports versioning and template inheritance
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Unique name for the template")
    description: str = Field(..., description="What this prompt is used for")
    
    # Prompt content
    system_prompt: str = Field(..., description="System/role instructions for the LLM")
    user_prompt_template: str = Field(..., description="User prompt with {placeholder} variables")
    
    # Validation
    required_context_keys: List[str] = Field(default_factory=list, description="Required keys in context dict")
    json_schema: Optional[Dict[str, Any]] = Field(None, description="Expected JSON schema for LLM response")
    
    # Configuration
    default_temperature: float = Field(0.7, ge=0.0, le=2.0)
    default_max_tokens: int = Field(4000, ge=100, le=32000)
    response_format: str = Field("text", description="Expected response format: text or json")
    
    # Versioning
    version: str = Field("1.0", description="Semantic version (e.g., 1.0, 1.1, 2.0)")
    parent_template_id: Optional[str] = Field(None, description="ID of parent template if inherited")
    is_active: bool = Field(True, description="Whether this template is currently in use")
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[str] = None  # Admin user ID
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    
    # Usage tracking
    usage_count: int = Field(0, ge=0, description="Number of times this template has been used")
    
    @field_validator('name')
    @classmethod
    def name_valid(cls, v):
        """Ensure name is valid (alphanumeric, underscores, hyphens)"""
        if not v or not v.strip():
            raise ValueError("Name cannot be empty")
        
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError("Name must contain only alphanumeric characters, underscores, and hyphens")
        
        return v.strip()
    
    @field_validator('version')
    @classmethod
    def version_valid(cls, v):
        """Ensure version follows semantic versioning"""
        if not re.match(r'^\d+\.\d+(\.\d+)?$', v):
            raise ValueError("Version must follow semantic versioning (e.g., 1.0, 1.1, 2.0.1)")
        return v
    
    @field_validator('response_format')
    @classmethod
    def response_format_valid(cls, v):
        """Ensure response format is valid"""
        valid_formats = ['text', 'json']
        if v not in valid_formats:
            raise ValueError(f"Response format must be one of: {', '.join(valid_formats)}")
        return v
    
    def extract_placeholders(self) -> List[str]:
        """Extract all {placeholder} variables from user prompt template"""
        return re.findall(r'\{(\w+)\}', self.user_prompt_template)
    
    def validate_context(self, context: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate that context contains all required keys
        
        Returns:
            (is_valid, error_message)
        """
        # Check required context keys
        missing_keys = [key for key in self.required_context_keys if key not in context]
        if missing_keys:
            return False, f"Missing required context keys: {', '.join(missing_keys)}"
        
        # Check that all placeholders can be filled
        placeholders = self.extract_placeholders()
        missing_placeholders = [p for p in placeholders if p not in context]
        if missing_placeholders:
            return False, f"Missing context values for placeholders: {', '.join(missing_placeholders)}"
        
        return True, None
    
    def render(self, context: Dict[str, Any]) -> tuple[str, str]:
        """
        Render the template with provided context
        
        Returns:
            (system_prompt, user_prompt)
        
        Raises:
            ValueError: If context is invalid
        """
        is_valid, error = self.validate_context(context)
        if not is_valid:
            raise ValueError(error)
        
        # Render user prompt by replacing placeholders
        user_prompt = self.user_prompt_template
        for key, value in context.items():
            placeholder = f"{{{key}}}"
            if placeholder in user_prompt:
                user_prompt = user_prompt.replace(placeholder, str(value))
        
        return self.system_prompt, user_prompt
    
    def to_dict(self) -> dict:
        """Convert to dictionary for Firestore storage"""
        data = self.model_dump()
        data['created_at'] = self.created_at
        data['updated_at'] = self.updated_at
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PromptTemplate':
        """Create from Firestore dictionary"""
        return cls(**data)
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "name": "meal_planning_v1",
            "description": "Generate personalized meal plan based on user profile",
            "system_prompt": "You are an expert nutrition AI specialized in personalized meal planning.",
            "user_prompt_template": "Generate a {num_days}-day meal plan for a {age}-year-old {gender} with goal: {fitness_goal}",
            "required_context_keys": ["num_days", "age", "gender", "fitness_goal"],
            "response_format": "json",
            "version": "1.0"
        }
    })


class PromptVersion(BaseModel):
    """
    Version history entry for a prompt template
    
    Stored in Firestore: admin/prompts/{template_id}/versions/{version_id}
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    template_id: str
    version: str
    
    # Snapshot of template at this version
    system_prompt: str
    user_prompt_template: str
    json_schema: Optional[Dict[str, Any]] = None
    
    # Change tracking
    change_description: str = Field(..., description="What changed in this version")
    changed_by: Optional[str] = None  # Admin user ID
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> dict:
        """Convert to dictionary for Firestore storage"""
        data = self.model_dump()
        data['timestamp'] = self.timestamp
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PromptVersion':
        """Create from Firestore dictionary"""
        return cls(**data)


class PromptUsageStats(BaseModel):
    """
    Usage statistics for a prompt template
    
    Aggregated stats for analytics
    """
    template_id: str
    template_name: str
    
    # Usage metrics
    total_uses: int = 0
    successful_uses: int = 0
    failed_uses: int = 0
    
    # Performance metrics
    avg_response_time_ms: float = 0.0
    avg_tokens_used: float = 0.0
    
    # Cost metrics
    total_cost_usd: float = 0.0
    
    # Time period
    period_start: datetime
    period_end: datetime
    
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_uses == 0:
            return 0.0
        return (self.successful_uses / self.total_uses) * 100
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "template_id": "meal_planning_v1",
            "template_name": "meal_planning_v1",
            "total_uses": 1000,
            "successful_uses": 985,
            "failed_uses": 15,
            "avg_response_time_ms": 2500.0,
            "avg_tokens_used": 3500.0,
            "total_cost_usd": 25.50
        }
    })

