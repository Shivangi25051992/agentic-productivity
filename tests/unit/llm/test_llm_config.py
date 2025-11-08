"""
Unit tests for LLM Configuration models

Tests validation, quota tracking, and model behavior
"""

import pytest
from datetime import datetime, timedelta
from app.models.llm_config import (
    LLMProvider,
    LLMConfig,
    LLMUsageLog,
    LLMRequest,
    LLMResponse,
    LLMQuotaStatus
)


class TestLLMProvider:
    """Test LLMProvider enum"""
    
    def test_provider_values(self):
        """Test that all provider values are valid strings"""
        assert LLMProvider.OPENAI.value == "openai"
        assert LLMProvider.GEMINI.value == "gemini"
        assert LLMProvider.MIXTRAL.value == "mixtral"
        assert LLMProvider.ANTHROPIC.value == "anthropic"
        assert LLMProvider.GROQ.value == "groq"
    
    def test_provider_enum_membership(self):
        """Test provider enum membership"""
        assert "openai" in [p.value for p in LLMProvider]
        assert "invalid_provider" not in [p.value for p in LLMProvider]


class TestLLMConfig:
    """Test LLMConfig model"""
    
    def test_valid_config(self):
        """Test creating a valid LLM config"""
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            api_key="sk-test123",
            model_name="gpt-4o-mini"
        )
        
        assert config.provider == LLMProvider.OPENAI
        assert config.api_key == "sk-test123"
        assert config.model_name == "gpt-4o-mini"
        assert config.priority == 1  # Default
        assert config.is_active == True  # Default
        assert config.quota_used == 0  # Default
    
    def test_api_key_validation(self):
        """Test API key validation"""
        # Empty API key should fail
        with pytest.raises(ValueError, match="API key cannot be empty"):
            LLMConfig(
                provider=LLMProvider.OPENAI,
                api_key="",
                model_name="gpt-4o-mini"
            )
        
        # Whitespace-only API key should fail
        with pytest.raises(ValueError, match="API key cannot be empty"):
            LLMConfig(
                provider=LLMProvider.OPENAI,
                api_key="   ",
                model_name="gpt-4o-mini"
            )
    
    def test_model_name_validation(self):
        """Test model name validation"""
        # Empty model name should fail
        with pytest.raises(ValueError, match="Model name cannot be empty"):
            LLMConfig(
                provider=LLMProvider.OPENAI,
                api_key="sk-test123",
                model_name=""
            )
    
    def test_priority_validation(self):
        """Test priority validation"""
        # Valid priorities
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            api_key="sk-test123",
            model_name="gpt-4o-mini",
            priority=5
        )
        assert config.priority == 5
        
        # Priority too low should fail
        with pytest.raises(ValueError):
            LLMConfig(
                provider=LLMProvider.OPENAI,
                api_key="sk-test123",
                model_name="gpt-4o-mini",
                priority=0
            )
        
        # Priority too high should fail
        with pytest.raises(ValueError):
            LLMConfig(
                provider=LLMProvider.OPENAI,
                api_key="sk-test123",
                model_name="gpt-4o-mini",
                priority=11
            )
    
    def test_temperature_validation(self):
        """Test temperature validation"""
        # Valid temperature
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            api_key="sk-test123",
            model_name="gpt-4o-mini",
            temperature=1.0
        )
        assert config.temperature == 1.0
        
        # Temperature too low should fail
        with pytest.raises(ValueError):
            LLMConfig(
                provider=LLMProvider.OPENAI,
                api_key="sk-test123",
                model_name="gpt-4o-mini",
                temperature=-0.1
            )
        
        # Temperature too high should fail
        with pytest.raises(ValueError):
            LLMConfig(
                provider=LLMProvider.OPENAI,
                api_key="sk-test123",
                model_name="gpt-4o-mini",
                temperature=2.1
            )
    
    def test_quota_exceeded_no_limit(self):
        """Test quota check with no limit"""
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            api_key="sk-test123",
            model_name="gpt-4o-mini",
            quota_limit=None,
            quota_used=1000000
        )
        
        assert not config.is_quota_exceeded()
    
    def test_quota_exceeded_under_limit(self):
        """Test quota check when under limit"""
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            api_key="sk-test123",
            model_name="gpt-4o-mini",
            quota_limit=10000,
            quota_used=5000
        )
        
        assert not config.is_quota_exceeded()
    
    def test_quota_exceeded_at_limit(self):
        """Test quota check when at limit"""
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            api_key="sk-test123",
            model_name="gpt-4o-mini",
            quota_limit=10000,
            quota_used=10000
        )
        
        assert config.is_quota_exceeded()
    
    def test_quota_exceeded_over_limit(self):
        """Test quota check when over limit"""
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            api_key="sk-test123",
            model_name="gpt-4o-mini",
            quota_limit=10000,
            quota_used=15000
        )
        
        assert config.is_quota_exceeded()
    
    def test_can_be_used_active_no_quota(self):
        """Test can_be_used with active config and no quota limit"""
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            api_key="sk-test123",
            model_name="gpt-4o-mini",
            is_active=True,
            quota_limit=None
        )
        
        assert config.can_be_used()
    
    def test_can_be_used_inactive(self):
        """Test can_be_used with inactive config"""
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            api_key="sk-test123",
            model_name="gpt-4o-mini",
            is_active=False
        )
        
        assert not config.can_be_used()
    
    def test_can_be_used_quota_exceeded(self):
        """Test can_be_used with quota exceeded"""
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            api_key="sk-test123",
            model_name="gpt-4o-mini",
            is_active=True,
            quota_limit=10000,
            quota_used=10000
        )
        
        assert not config.can_be_used()
    
    def test_to_dict_and_from_dict(self):
        """Test serialization and deserialization"""
        original = LLMConfig(
            provider=LLMProvider.GEMINI,
            api_key="test-key",
            model_name="gemini-1.5-pro",
            priority=2,
            temperature=0.5
        )
        
        # Convert to dict
        data = original.to_dict()
        assert isinstance(data, dict)
        assert data['provider'] == 'gemini'
        assert data['api_key'] == 'test-key'
        
        # Convert back from dict
        restored = LLMConfig.from_dict(data)
        assert restored.provider == original.provider
        assert restored.api_key == original.api_key
        assert restored.model_name == original.model_name
        assert restored.priority == original.priority


class TestLLMUsageLog:
    """Test LLMUsageLog model"""
    
    def test_valid_usage_log(self):
        """Test creating a valid usage log"""
        log = LLMUsageLog(
            provider=LLMProvider.OPENAI,
            model_name="gpt-4o-mini",
            request_type="chat",
            tokens_used=1500,
            prompt_tokens=500,
            completion_tokens=1000,
            response_time_ms=2000,
            success=True
        )
        
        assert log.provider == LLMProvider.OPENAI
        assert log.tokens_used == 1500
        assert log.success == True
    
    def test_usage_log_with_error(self):
        """Test usage log for failed request"""
        log = LLMUsageLog(
            provider=LLMProvider.GEMINI,
            model_name="gemini-1.5-pro",
            request_type="meal_plan",
            tokens_used=0,
            prompt_tokens=500,
            completion_tokens=0,
            response_time_ms=1000,
            success=False,
            error="API rate limit exceeded",
            error_code="rate_limit"
        )
        
        assert not log.success
        assert log.error == "API rate limit exceeded"
        assert log.error_code == "rate_limit"
    
    def test_usage_log_with_cost(self):
        """Test usage log with cost tracking"""
        log = LLMUsageLog(
            provider=LLMProvider.OPENAI,
            model_name="gpt-4o-mini",
            request_type="chat",
            tokens_used=10000,
            prompt_tokens=5000,
            completion_tokens=5000,
            response_time_ms=3000,
            cost_usd=0.15,
            success=True
        )
        
        assert log.cost_usd == 0.15
    
    def test_to_dict_and_from_dict(self):
        """Test serialization"""
        original = LLMUsageLog(
            provider=LLMProvider.MIXTRAL,
            model_name="mixtral-8x7b",
            request_type="chat",
            tokens_used=2000,
            prompt_tokens=1000,
            completion_tokens=1000,
            response_time_ms=1500,
            success=True
        )
        
        data = original.to_dict()
        restored = LLMUsageLog.from_dict(data)
        
        assert restored.provider == original.provider
        assert restored.tokens_used == original.tokens_used


class TestLLMRequest:
    """Test LLMRequest model"""
    
    def test_valid_request(self):
        """Test creating a valid LLM request"""
        request = LLMRequest(
            prompt_template_id="meal_planning_v1",
            context={"num_days": 7, "user_goal": "lose_weight"}
        )
        
        assert request.prompt_template_id == "meal_planning_v1"
        assert request.context["num_days"] == 7
    
    def test_request_with_overrides(self):
        """Test request with parameter overrides"""
        request = LLMRequest(
            prompt_template_id="chat_classification_v1",
            context={"message": "I ate pizza"},
            preferred_provider=LLMProvider.GEMINI,
            temperature=0.3,
            max_tokens=500
        )
        
        assert request.preferred_provider == LLMProvider.GEMINI
        assert request.temperature == 0.3
        assert request.max_tokens == 500


class TestLLMResponse:
    """Test LLMResponse model"""
    
    def test_valid_response(self):
        """Test creating a valid LLM response"""
        response = LLMResponse(
            content="Generated meal plan...",
            provider_used=LLMProvider.OPENAI,
            model_used="gpt-4o-mini",
            tokens_used=3000,
            prompt_tokens=1000,
            completion_tokens=2000,
            response_time_ms=2500
        )
        
        assert response.content == "Generated meal plan..."
        assert response.provider_used == LLMProvider.OPENAI
        assert response.success == True
        assert response.fallback_used == False
    
    def test_response_with_fallback(self):
        """Test response when fallback was used"""
        response = LLMResponse(
            content="Response from fallback provider",
            provider_used=LLMProvider.GEMINI,
            model_used="gemini-1.5-pro",
            tokens_used=2000,
            prompt_tokens=800,
            completion_tokens=1200,
            response_time_ms=3000,
            fallback_used=True
        )
        
        assert response.fallback_used == True
    
    def test_response_with_structured_data(self):
        """Test response with JSON structured data"""
        response = LLMResponse(
            content='{"meals": [...]}',
            provider_used=LLMProvider.OPENAI,
            model_used="gpt-4o-mini",
            tokens_used=4000,
            prompt_tokens=1500,
            completion_tokens=2500,
            response_time_ms=3500,
            structured_data={"meals": [{"name": "Breakfast", "calories": 500}]}
        )
        
        assert response.structured_data is not None
        assert "meals" in response.structured_data


class TestLLMQuotaStatus:
    """Test LLMQuotaStatus model"""
    
    def test_from_config_no_limit(self):
        """Test quota status with no limit"""
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            api_key="sk-test",
            model_name="gpt-4o-mini",
            quota_limit=None,
            quota_used=5000
        )
        
        status = LLMQuotaStatus.from_config(config)
        
        assert status.provider == LLMProvider.OPENAI
        assert status.quota_limit is None
        assert status.quota_used == 5000
        assert status.quota_remaining is None
        assert status.percentage_used == 0.0
        assert not status.is_exceeded
    
    def test_from_config_under_limit(self):
        """Test quota status under limit"""
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            api_key="sk-test",
            model_name="gpt-4o-mini",
            quota_limit=10000,
            quota_used=3000
        )
        
        status = LLMQuotaStatus.from_config(config)
        
        assert status.quota_limit == 10000
        assert status.quota_used == 3000
        assert status.quota_remaining == 7000
        assert status.percentage_used == 30.0
        assert not status.is_exceeded
    
    def test_from_config_exceeded(self):
        """Test quota status when exceeded"""
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            api_key="sk-test",
            model_name="gpt-4o-mini",
            quota_limit=10000,
            quota_used=12000
        )
        
        status = LLMQuotaStatus.from_config(config)
        
        assert status.quota_limit == 10000
        assert status.quota_used == 12000
        assert status.quota_remaining == 0  # Clamped to 0
        assert status.percentage_used == 120.0
        assert status.is_exceeded

