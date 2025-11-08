"""
Unit tests for LLM Router

Tests provider selection, fallback logic, quota enforcement, and usage tracking.
Critical for ensuring zero regression and robust error handling.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from typing import List

from app.models.llm_config import (
    LLMProvider,
    LLMConfig,
    LLMRequest,
    LLMResponse
)
from app.services.llm.llm_router import LLMRouter


class TestLLMRouter:
    """Test LLM Router functionality"""
    
    @pytest.fixture
    def mock_db(self):
        """Create mock Firestore client"""
        return MagicMock()
    
    @pytest.fixture
    def router(self, mock_db):
        """Create LLM Router instance"""
        return LLMRouter(db=mock_db)
    
    @pytest.fixture
    def sample_config_openai(self):
        """Sample OpenAI configuration"""
        return LLMConfig(
            id="config1",
            provider=LLMProvider.OPENAI,
            api_key="test_openai_key",
            model_name="gpt-4o-mini",
            priority=1,
            is_active=True,
            quota_limit=100000,
            quota_used=0
        )
    
    @pytest.fixture
    def sample_config_gemini(self):
        """Sample Gemini configuration"""
        return LLMConfig(
            id="config2",
            provider=LLMProvider.GEMINI,
            api_key="test_gemini_key",
            model_name="gemini-1.5-flash",
            priority=2,
            is_active=True,
            quota_limit=50000,
            quota_used=0
        )
    
    @pytest.fixture
    def sample_request(self):
        """Sample LLM request"""
        return LLMRequest(
            prompt_template_id="test_template",
            context={"test": "value"},
            user_id="test_user",
            request_type="chat"
        )


class TestProviderSelection(TestLLMRouter):
    """Test provider selection logic"""
    
    def test_select_providers_by_priority(self, router, sample_config_openai, sample_config_gemini):
        """Test that providers are selected by priority"""
        # Set different priorities
        sample_config_openai.priority = 2
        sample_config_gemini.priority = 1  # Higher priority (lower number)
        
        configs = [sample_config_openai, sample_config_gemini]
        selected = router._select_providers(configs)
        
        # Gemini should be first (priority 1)
        assert selected[0].provider == LLMProvider.GEMINI
        assert selected[1].provider == LLMProvider.OPENAI
    
    def test_select_preferred_provider(self, router, sample_config_openai, sample_config_gemini):
        """Test that preferred provider is selected first"""
        # OpenAI has higher priority (1), but user prefers Gemini
        sample_config_openai.priority = 1
        sample_config_gemini.priority = 2
        
        configs = [sample_config_openai, sample_config_gemini]
        
        # Request prefers Gemini
        selected = router._select_providers(configs, preferred_provider=LLMProvider.GEMINI)
        
        # Gemini should be first despite lower priority
        assert selected[0].provider == LLMProvider.GEMINI
        assert selected[1].provider == LLMProvider.OPENAI
    
    def test_filter_inactive_providers(self, router, sample_config_openai, sample_config_gemini):
        """Test that inactive providers are filtered out"""
        sample_config_openai.is_active = False  # Inactive
        
        configs = [sample_config_openai, sample_config_gemini]
        selected = router._select_providers(configs)
        
        # Only Gemini should be selected
        assert len(selected) == 1
        assert selected[0].provider == LLMProvider.GEMINI
    
    def test_filter_quota_exceeded_providers(self, router, sample_config_openai, sample_config_gemini):
        """Test that providers with exceeded quota are filtered out"""
        sample_config_openai.quota_limit = 1000
        sample_config_openai.quota_used = 1000  # Quota exceeded
        
        configs = [sample_config_openai, sample_config_gemini]
        selected = router._select_providers(configs)
        
        # Only Gemini should be selected
        assert len(selected) == 1
        assert selected[0].provider == LLMProvider.GEMINI
    
    def test_no_usable_providers(self, router, sample_config_openai):
        """Test when no providers are usable"""
        sample_config_openai.is_active = False
        
        selected = router._select_providers([sample_config_openai])
        
        assert len(selected) == 0


class TestProviderInstantiation(TestLLMRouter):
    """Test provider instance creation"""
    
    def test_get_provider_instance_openai(self, router, sample_config_openai):
        """Test creating OpenAI provider instance"""
        provider = router._get_provider_instance(sample_config_openai)
        
        assert provider is not None
        assert provider.model_name == "gpt-4o-mini"
        assert provider.provider_name == "openai"
    
    def test_provider_instance_caching(self, router, sample_config_openai):
        """Test that provider instances are cached"""
        provider1 = router._get_provider_instance(sample_config_openai)
        provider2 = router._get_provider_instance(sample_config_openai)
        
        # Should be same instance
        assert provider1 is provider2
    
    def test_unknown_provider_error(self, router, sample_config_openai):
        """Test error handling for unknown provider"""
        # Temporarily remove OpenAI from provider classes to simulate unknown provider
        original_classes = router.PROVIDER_CLASSES.copy()
        router.PROVIDER_CLASSES = {}  # Empty dict = no providers known
        
        try:
            with pytest.raises(Exception, match="Unknown provider"):
                router._get_provider_instance(sample_config_openai)
        finally:
            # Restore original classes
            router.PROVIDER_CLASSES = original_classes


class TestRouteRequest(TestLLMRouter):
    """Test request routing"""
    
    @pytest.mark.asyncio
    async def test_successful_routing(self, router, sample_config_openai, sample_request):
        """Test successful request routing"""
        # Mock loading configs
        with patch.object(router, '_load_provider_configs', new=AsyncMock(return_value=[sample_config_openai])):
            # Mock provider response
            mock_provider = MagicMock()
            mock_provider.generate = AsyncMock(return_value={
                "content": "Test response",
                "tokens_used": 100,
                "prompt_tokens": 50,
                "completion_tokens": 50,
                "response_time_ms": 1000,
                "model_used": "gpt-4o-mini"
            })
            
            with patch.object(router, '_get_provider_instance', return_value=mock_provider):
                # Mock quota update and logging
                with patch.object(router, '_update_quota', new=AsyncMock()):
                    with patch.object(router, '_log_usage', new=AsyncMock()):
                        response = await router.route_request(
                            request=sample_request,
                            system_prompt="System",
                            user_prompt="User"
                        )
                        
                        assert response.content == "Test response"
                        assert response.provider_used == LLMProvider.OPENAI
                        assert response.tokens_used == 100
                        assert response.success == True
                        assert response.fallback_used == False
    
    @pytest.mark.asyncio
    async def test_fallback_on_primary_failure(self, router, sample_config_openai, sample_config_gemini, sample_request):
        """Test fallback to secondary provider when primary fails"""
        # Mock loading configs (OpenAI first, Gemini second)
        sample_config_openai.priority = 1
        sample_config_gemini.priority = 2
        
        with patch.object(router, '_load_provider_configs', 
                         new=AsyncMock(return_value=[sample_config_openai, sample_config_gemini])):
            # Mock OpenAI to fail
            mock_openai = MagicMock()
            mock_openai.generate = AsyncMock(side_effect=Exception("OpenAI API error"))
            
            # Mock Gemini to succeed
            mock_gemini = MagicMock()
            mock_gemini.generate = AsyncMock(return_value={
                "content": "Gemini response",
                "tokens_used": 80,
                "prompt_tokens": 40,
                "completion_tokens": 40,
                "response_time_ms": 800,
                "model_used": "gemini-1.5-flash"
            })
            
            def get_provider(config):
                if config.provider == LLMProvider.OPENAI:
                    return mock_openai
                return mock_gemini
            
            with patch.object(router, '_get_provider_instance', side_effect=get_provider):
                with patch.object(router, '_update_quota', new=AsyncMock()):
                    with patch.object(router, '_log_usage', new=AsyncMock()):
                        response = await router.route_request(
                            request=sample_request,
                            system_prompt="System",
                            user_prompt="User"
                        )
                        
                        # Should succeed with Gemini (fallback)
                        assert response.content == "Gemini response"
                        assert response.provider_used == LLMProvider.GEMINI
                        assert response.fallback_used == True
    
    @pytest.mark.asyncio
    async def test_all_providers_fail(self, router, sample_config_openai, sample_request):
        """Test when all providers fail"""
        with patch.object(router, '_load_provider_configs', new=AsyncMock(return_value=[sample_config_openai])):
            # Mock provider to fail
            mock_provider = MagicMock()
            mock_provider.generate = AsyncMock(side_effect=Exception("API Error"))
            
            with patch.object(router, '_get_provider_instance', return_value=mock_provider):
                with patch.object(router, '_log_usage', new=AsyncMock()):
                    with pytest.raises(Exception, match="All LLM providers failed"):
                        await router.route_request(
                            request=sample_request,
                            system_prompt="System",
                            user_prompt="User"
                        )
    
    @pytest.mark.asyncio
    async def test_no_providers_configured(self, router, sample_request):
        """Test when no providers are configured"""
        with patch.object(router, '_load_provider_configs', new=AsyncMock(return_value=[])):
            with pytest.raises(Exception, match="No LLM providers configured"):
                await router.route_request(
                    request=sample_request,
                    system_prompt="System",
                    user_prompt="User"
                )


class TestQuotaManagement(TestLLMRouter):
    """Test quota tracking and enforcement"""
    
    @pytest.mark.asyncio
    async def test_update_quota(self, router, sample_config_openai):
        """Test quota update after successful request"""
        # Mock Firestore document reference
        mock_doc_ref = MagicMock()
        mock_collection = MagicMock()
        mock_collection.document.return_value = mock_doc_ref
        mock_doc = MagicMock()
        mock_doc.collection.return_value = mock_collection
        mock_admin = MagicMock()
        mock_admin.document.return_value = mock_doc
        router.db.collection.return_value = mock_admin
        
        # Update cache
        router.config_cache[sample_config_openai.id] = sample_config_openai
        
        await router._update_quota(sample_config_openai, tokens_used=500)
        
        # Check Firestore update was called
        mock_doc_ref.update.assert_called_once()
        
        # Check cache was updated
        assert router.config_cache[sample_config_openai.id].quota_used == 500
    
    @pytest.mark.asyncio
    async def test_get_quota_status(self, router, sample_config_openai, sample_config_gemini):
        """Test getting quota status"""
        sample_config_openai.quota_limit = 10000
        sample_config_openai.quota_used = 3000
        
        with patch.object(router, '_load_provider_configs', 
                         new=AsyncMock(return_value=[sample_config_openai, sample_config_gemini])):
            statuses = await router.get_quota_status()
            
            assert len(statuses) == 2
            openai_status = next(s for s in statuses if s.provider == LLMProvider.OPENAI)
            assert openai_status.quota_used == 3000
            assert openai_status.quota_remaining == 7000
            assert openai_status.percentage_used == 30.0
    
    @pytest.mark.asyncio
    async def test_get_quota_status_specific_provider(self, router, sample_config_openai, sample_config_gemini):
        """Test getting quota status for specific provider"""
        with patch.object(router, '_load_provider_configs', 
                         new=AsyncMock(return_value=[sample_config_openai, sample_config_gemini])):
            statuses = await router.get_quota_status(provider=LLMProvider.OPENAI)
            
            assert len(statuses) == 1
            assert statuses[0].provider == LLMProvider.OPENAI


class TestCaching(TestLLMRouter):
    """Test configuration caching"""
    
    @pytest.mark.asyncio
    async def test_cache_refresh(self, router, sample_config_openai):
        """Test cache refresh functionality"""
        # Mock Firestore query
        mock_doc = MagicMock()
        mock_doc.id = sample_config_openai.id
        mock_doc.to_dict.return_value = sample_config_openai.to_dict()
        
        mock_stream = MagicMock()
        mock_stream.stream.return_value = [mock_doc]
        
        mock_where = MagicMock()
        mock_where.stream.return_value = [mock_doc]
        
        mock_providers = MagicMock()
        mock_providers.where.return_value = mock_where
        
        mock_llm_doc = MagicMock()
        mock_llm_doc.collection.return_value = mock_providers
        
        mock_admin = MagicMock()
        mock_admin.document.return_value = mock_llm_doc
        
        router.db.collection.return_value = mock_admin
        
        await router.refresh_cache()
        
        assert len(router.config_cache) == 1
        assert sample_config_openai.id in router.config_cache


class TestUsageLogging(TestLLMRouter):
    """Test usage tracking and logging"""
    
    @pytest.mark.asyncio
    async def test_log_successful_usage(self, router, sample_config_openai, sample_request):
        """Test logging of successful request"""
        # Mock Firestore
        mock_doc_ref = MagicMock()
        mock_logs = MagicMock()
        mock_logs.document.return_value = mock_doc_ref
        mock_usage_doc = MagicMock()
        mock_usage_doc.collection.return_value = mock_logs
        mock_admin = MagicMock()
        mock_admin.document.return_value = mock_usage_doc
        router.db.collection.return_value = mock_admin
        
        await router._log_usage(
            config=sample_config_openai,
            request=sample_request,
            tokens_used=100,
            prompt_tokens=50,
            completion_tokens=50,
            response_time_ms=1000,
            success=True
        )
        
        # Verify Firestore set was called
        mock_doc_ref.set.assert_called_once()
        
        # Verify log structure
        call_args = mock_doc_ref.set.call_args[0][0]
        assert call_args['provider'] == 'openai'
        assert call_args['tokens_used'] == 100
        assert call_args['success'] == True
    
    @pytest.mark.asyncio
    async def test_log_failed_usage(self, router, sample_config_openai, sample_request):
        """Test logging of failed request"""
        mock_doc_ref = MagicMock()
        mock_logs = MagicMock()
        mock_logs.document.return_value = mock_doc_ref
        mock_usage_doc = MagicMock()
        mock_usage_doc.collection.return_value = mock_logs
        mock_admin = MagicMock()
        mock_admin.document.return_value = mock_usage_doc
        router.db.collection.return_value = mock_admin
        
        await router._log_usage(
            config=sample_config_openai,
            request=sample_request,
            tokens_used=0,
            prompt_tokens=0,
            completion_tokens=0,
            response_time_ms=0,
            success=False,
            error="API Error"
        )
        
        # Verify log structure
        call_args = mock_doc_ref.set.call_args[0][0]
        assert call_args['success'] == False
        assert call_args['error'] == "API Error"

