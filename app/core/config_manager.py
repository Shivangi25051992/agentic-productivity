"""
Configuration Management Service
Follows 12-factor app principles: https://12factor.net/config
All configuration comes from environment variables, never hardcoded.
"""

import os
from typing import List, Optional
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field, validator
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Validates all required configuration on startup.
    """
    
    # ============================================================================
    # ENVIRONMENT
    # ============================================================================
    environment: str = Field(
        default="development",
        description="Deployment environment: development, staging, production"
    )
    
    # ============================================================================
    # API KEYS (Required)
    # ============================================================================
    openai_api_key: str = Field(
        ...,  # Required
        description="OpenAI API key for LLM services"
    )
    
    # ============================================================================
    # GOOGLE CLOUD / FIREBASE (Required)
    # ============================================================================
    google_cloud_project: str = Field(
        ...,  # Required
        description="Google Cloud Project ID"
    )
    
    firebase_project_id: Optional[str] = Field(
        default=None,
        description="Firebase Project ID (defaults to google_cloud_project)"
    )
    
    google_application_credentials: Optional[str] = Field(
        default=None,
        description="Path to Google Cloud service account JSON file"
    )
    
    # ============================================================================
    # CORS (Required for production)
    # ============================================================================
    cors_origins: str = Field(
        default="*",
        description="Comma-separated list of allowed CORS origins. Use * for development."
    )
    
    # ============================================================================
    # ADMIN (Optional)
    # ============================================================================
    admin_username: Optional[str] = Field(
        default=None,
        description="Admin portal username"
    )
    
    admin_password: Optional[str] = Field(
        default=None,
        description="Admin portal password (plain text)"
    )
    
    admin_password_bcrypt: Optional[str] = Field(
        default=None,
        description="Admin portal password (bcrypt hash)"
    )
    
    admin_secret_key: Optional[str] = Field(
        default=None,
        description="JWT secret key for admin tokens"
    )
    
    admin_ip_whitelist: str = Field(
        default="",
        description="Comma-separated list of allowed admin IPs. Empty = disabled."
    )
    
    # ============================================================================
    # ENCRYPTION
    # ============================================================================
    encryption_key: Optional[str] = Field(
        default=None,
        description="Fernet encryption key for sensitive data"
    )
    
    # ============================================================================
    # FEATURE FLAGS
    # ============================================================================
    enable_free_tier_limits: bool = Field(
        default=True,
        description="Enable free tier meal plan limits (3 plans/week)"
    )
    
    enable_parallel_generation: bool = Field(
        default=True,
        description="Enable parallel meal plan generation (faster)"
    )
    
    enable_analytics: bool = Field(
        default=True,
        description="Enable analytics and monitoring"
    )
    
    # ============================================================================
    # PERFORMANCE
    # ============================================================================
    max_llm_timeout: int = Field(
        default=120,
        description="Maximum timeout for LLM API calls (seconds)"
    )
    
    max_concurrent_llm_calls: int = Field(
        default=7,
        description="Maximum concurrent LLM API calls (for parallel generation)"
    )
    
    # ============================================================================
    # REDIS CACHE (Optional - Phase 1 Performance)
    # ============================================================================
    redis_enabled: bool = Field(
        default=False,
        description="Enable Redis caching for timeline/dashboard"
    )
    
    redis_host: str = Field(
        default="localhost",
        description="Redis server host"
    )
    
    redis_port: int = Field(
        default=6379,
        description="Redis server port"
    )
    
    redis_db: int = Field(
        default=0,
        description="Redis database number"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
        # Try .env.local for local overrides
        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            return (
                init_settings,
                env_settings,
                file_secret_settings,
            )
    
    # ============================================================================
    # VALIDATORS
    # ============================================================================
    
    @validator("environment")
    def validate_environment(cls, v):
        """Ensure environment is one of the allowed values."""
        allowed = ["development", "staging", "production"]
        if v.lower() not in allowed:
            raise ValueError(f"environment must be one of {allowed}, got: {v}")
        return v.lower()
    
    @validator("firebase_project_id", always=True)
    def default_firebase_project(cls, v, values):
        """Default firebase_project_id to google_cloud_project if not set."""
        if v is None and "google_cloud_project" in values:
            return values["google_cloud_project"]
        return v
    
    @validator("cors_origins")
    def validate_cors_origins(cls, v, values):
        """Validate CORS origins for production."""
        env = values.get("environment", "development")
        if env == "production" and v == "*":
            logger.warning(
                "⚠️  CORS set to '*' in production! This is insecure. "
                "Set CORS_ORIGINS to specific domains."
            )
        return v
    
    # ============================================================================
    # COMPUTED PROPERTIES
    # ============================================================================
    
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment == "development"
    
    @property
    def is_staging(self) -> bool:
        """Check if running in staging."""
        return self.environment == "staging"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins into a list."""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
    
    @property
    def admin_ip_whitelist_list(self) -> List[str]:
        """Parse admin IP whitelist into a list."""
        if not self.admin_ip_whitelist:
            return []
        return [ip.strip() for ip in self.admin_ip_whitelist.split(",") if ip.strip()]
    
    # ============================================================================
    # VALIDATION
    # ============================================================================
    
    def validate_production_config(self) -> List[str]:
        """
        Validate that production configuration is secure and complete.
        Returns list of warnings/errors.
        """
        issues = []
        
        if self.is_production:
            # Check CORS
            if self.cors_origins == "*":
                issues.append("🔴 CRITICAL: CORS set to '*' in production")
            
            # Check admin security
            if self.admin_username and not self.admin_password_bcrypt:
                issues.append("⚠️  WARNING: Admin using plain password, not bcrypt hash")
            
            # Check encryption
            if not self.encryption_key:
                issues.append("⚠️  WARNING: ENCRYPTION_KEY not set")
        
        return issues
    
    def log_configuration(self):
        """Log current configuration (safe, no secrets)."""
        logger.info("=" * 60)
        logger.info("🔧 CONFIGURATION")
        logger.info("=" * 60)
        logger.info(f"Environment:              {self.environment}")
        logger.info(f"Google Cloud Project:     {self.google_cloud_project}")
        logger.info(f"Firebase Project:         {self.firebase_project_id}")
        logger.info(f"CORS Origins:             {len(self.cors_origins_list)} origins")
        logger.info(f"OpenAI API Key:           {'✅ SET' if self.openai_api_key else '❌ MISSING'}")
        logger.info(f"Admin Enabled:            {'✅ YES' if self.admin_username else '❌ NO'}")
        logger.info(f"Free Tier Limits:         {'✅ ENABLED' if self.enable_free_tier_limits else '❌ DISABLED'}")
        logger.info(f"Parallel Generation:      {'✅ ENABLED' if self.enable_parallel_generation else '❌ DISABLED'}")
        logger.info(f"Max LLM Timeout:          {self.max_llm_timeout}s")
        logger.info(f"Max Concurrent LLM Calls: {self.max_concurrent_llm_calls}")
        logger.info("=" * 60)
        
        # Log production warnings
        if self.is_production:
            issues = self.validate_production_config()
            if issues:
                logger.warning("⚠️  PRODUCTION CONFIGURATION ISSUES:")
                for issue in issues:
                    logger.warning(f"   {issue}")


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings (cached).
    This ensures settings are loaded only once and reused.
    """
    try:
        settings = Settings()
        settings.log_configuration()
        
        # Validate production config
        if settings.is_production:
            issues = settings.validate_production_config()
            if any("CRITICAL" in issue for issue in issues):
                raise ValueError(
                    "Critical configuration issues in production:\n" + 
                    "\n".join(issues)
                )
        
        return settings
    except Exception as e:
        logger.error(f"❌ Failed to load configuration: {e}")
        raise


# Convenience exports
settings = get_settings()


