"""
Unit tests for LLM Providers

Tests all provider implementations with mocked API calls.
Ensures consistent behavior across OpenAI, Gemini, and Groq providers.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

from app.services.llm.base_provider import BaseLLMProvider
from app.services.llm.openai_provider import OpenAIProvider
from app.services.llm.gemini_provider import GeminiProvider
from app.services.llm.groq_provider import GroqProvider


class TestBaseLLMProvider:
    """Test base provider interface"""
    
    def test_cannot_instantiate_abstract_class(self):
        """Test that BaseLLMProvider cannot be instantiated directly"""
        with pytest.raises(TypeError):
            BaseLLMProvider("test_key", "test_model")
    
    def test_base_provider_methods_exist(self):
        """Test that base provider defines required methods"""
        required_methods = ['generate', 'estimate_tokens', 'validate_response_schema']
        for method in required_methods:
            assert hasattr(BaseLLMProvider, method)


class TestOpenAIProvider:
    """Test OpenAI provider"""
    
    @pytest.fixture
    def provider(self):
        """Create OpenAI provider instance"""
        return OpenAIProvider(api_key="test_key", model_name="gpt-4o-mini")
    
    def test_initialization(self, provider):
        """Test provider initializes correctly"""
        assert provider.api_key == "test_key"
        assert provider.model_name == "gpt-4o-mini"
        assert provider.provider_name == "openai"
        assert provider.client is not None
    
    @pytest.mark.asyncio
    async def test_generate_success(self, provider):
        """Test successful generation"""
        # Mock response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage.total_tokens = 100
        mock_response.usage.prompt_tokens = 50
        mock_response.usage.completion_tokens = 50
        
        # Patch API call
        with patch.object(provider.client.chat.completions, 'create', new=AsyncMock(return_value=mock_response)):
            result = await provider.generate(
                system_prompt="You are a helpful assistant",
                user_prompt="Hello",
                temperature=0.7,
                max_tokens=1000
            )
        
        assert result["content"] == "Test response"
        assert result["tokens_used"] == 100
        assert result["prompt_tokens"] == 50
        assert result["completion_tokens"] == 50
        assert result["model_used"] == "gpt-4o-mini"
        assert "response_time_ms" in result
        assert result["response_time_ms"] >= 0
    
    @pytest.mark.asyncio
    async def test_generate_with_json_format(self, provider):
        """Test generation with JSON format"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"key": "value"}'
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage.total_tokens = 50
        mock_response.usage.prompt_tokens = 25
        mock_response.usage.completion_tokens = 25
        
        with patch.object(provider.client.chat.completions, 'create', new=AsyncMock(return_value=mock_response)) as mock_create:
            result = await provider.generate(
                system_prompt="System",
                user_prompt="User",
                response_format="json"
            )
            
            # Verify response_format was passed
            call_args = mock_create.call_args
            assert call_args.kwargs["response_format"] == {"type": "json_object"}
    
    @pytest.mark.asyncio
    async def test_generate_api_error(self, provider):
        """Test API error handling"""
        with patch.object(provider.client.chat.completions, 'create', new=AsyncMock(side_effect=Exception("API Error"))):
            with pytest.raises(Exception, match="OpenAI API error"):
                await provider.generate(
                    system_prompt="System",
                    user_prompt="User"
                )
    
    def test_estimate_tokens(self, provider):
        """Test token estimation"""
        text = "Hello world this is a test"
        tokens = provider.estimate_tokens(text)
        
        # Should return a positive number
        assert tokens > 0
        # Should be reasonable (not too large or too small)
        assert tokens > 1
        assert tokens < 100
    
    def test_get_model_info(self, provider):
        """Test model info retrieval"""
        info = provider.get_model_info()
        
        assert "provider" in info
        assert "model" in info
        assert "context_window" in info
        assert "cost_per_1k_input" in info
        assert "cost_per_1k_output" in info
        
        assert info["provider"] == "openai"
        assert info["model"] == "gpt-4o-mini"
        assert info["context_window"] == 128000
    
    def test_get_provider_info(self, provider):
        """Test provider info"""
        info = provider.get_provider_info()
        
        assert info["provider"] == "openai"
        assert info["model"] == "gpt-4o-mini"
        assert "class" in info


class TestGeminiProvider:
    """Test Gemini provider"""
    
    @pytest.fixture
    def provider(self):
        """Create Gemini provider instance (or skip if not available)"""
        try:
            return GeminiProvider(api_key="test_key", model_name="gemini-1.5-flash")
        except ImportError:
            pytest.skip("google-generativeai not installed")
    
    def test_initialization(self, provider):
        """Test provider initializes correctly"""
        assert provider.api_key == "test_key"
        assert provider.model_name == "gemini-1.5-flash"
        assert provider.provider_name == "gemini"
    
    @pytest.mark.asyncio
    async def test_generate_success(self, provider):
        """Test successful generation"""
        # Mock response
        mock_response = MagicMock()
        mock_response.text = "Test response from Gemini"
        mock_response.candidates = [MagicMock()]
        mock_response.candidates[0].finish_reason.name = "STOP"
        
        # Patch generate_content
        with patch.object(provider.model, 'generate_content', return_value=mock_response):
            result = await provider.generate(
                system_prompt="You are a helpful assistant",
                user_prompt="Hello"
            )
        
        assert result["content"] == "Test response from Gemini"
        assert result["tokens_used"] > 0
        assert result["model_used"] == "gemini-1.5-flash"
        assert "response_time_ms" in result
    
    @pytest.mark.asyncio
    async def test_generate_safety_block(self, provider):
        """Test safety filter blocking"""
        mock_response = MagicMock()
        mock_response.candidates = []  # Empty = blocked
        
        with patch.object(provider.model, 'generate_content', return_value=mock_response):
            with pytest.raises(Exception, match="safety filters"):
                await provider.generate(
                    system_prompt="System",
                    user_prompt="User"
                )
    
    def test_estimate_tokens(self, provider):
        """Test token estimation"""
        text = "Hello world this is a test"
        tokens = provider.estimate_tokens(text)
        
        assert tokens > 0
        assert tokens > 1
        assert tokens < 100
    
    def test_get_model_info(self, provider):
        """Test model info retrieval"""
        info = provider.get_model_info()
        
        assert "provider" in info
        assert "model" in info
        assert "context_window" in info
        assert info["provider"] == "gemini"
        assert info["model"] == "gemini-1.5-flash"
        assert info["context_window"] == 1000000  # 1M tokens
    
    def test_is_available(self):
        """Test availability check"""
        # Just check it returns a boolean
        available = GeminiProvider.is_available()
        assert isinstance(available, bool)


class TestGroqProvider:
    """Test Groq provider"""
    
    @pytest.fixture
    def provider(self):
        """Create Groq provider instance (or skip if not available)"""
        try:
            return GroqProvider(api_key="test_key", model_name="mixtral-8x7b-32768")
        except ImportError:
            pytest.skip("groq client not installed")
    
    def test_initialization(self, provider):
        """Test provider initializes correctly"""
        assert provider.api_key == "test_key"
        assert provider.model_name == "mixtral-8x7b-32768"
        assert provider.provider_name == "groq"
        assert provider.client is not None
    
    @pytest.mark.asyncio
    async def test_generate_success(self, provider):
        """Test successful generation"""
        # Mock response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response from Mixtral"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage.total_tokens = 150
        mock_response.usage.prompt_tokens = 75
        mock_response.usage.completion_tokens = 75
        
        with patch.object(provider.client.chat.completions, 'create', new=AsyncMock(return_value=mock_response)):
            result = await provider.generate(
                system_prompt="You are a helpful assistant",
                user_prompt="Hello"
            )
        
        assert result["content"] == "Test response from Mixtral"
        assert result["tokens_used"] == 150
        assert result["prompt_tokens"] == 75
        assert result["completion_tokens"] == 75
        assert result["model_used"] == "mixtral-8x7b-32768"
    
    @pytest.mark.asyncio
    async def test_generate_with_json_mode(self, provider):
        """Test generation with JSON mode (supported model)"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"result": "success"}'
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage.total_tokens = 50
        mock_response.usage.prompt_tokens = 25
        mock_response.usage.completion_tokens = 25
        
        with patch.object(provider.client.chat.completions, 'create', new=AsyncMock(return_value=mock_response)) as mock_create:
            result = await provider.generate(
                system_prompt="System",
                user_prompt="User",
                response_format="json"
            )
            
            # Verify response_format was passed for JSON-capable models
            call_args = mock_create.call_args
            assert call_args.kwargs["response_format"] == {"type": "json_object"}
    
    def test_supports_json_mode(self, provider):
        """Test JSON mode support detection"""
        assert provider._supports_json_mode() == True  # mixtral-8x7b-32768 supports it
        
        # Test with non-JSON model
        provider.model_name = "some-other-model"
        assert provider._supports_json_mode() == False
    
    def test_estimate_tokens(self, provider):
        """Test token estimation"""
        text = "Hello world this is a test"
        tokens = provider.estimate_tokens(text)
        
        assert tokens > 0
        assert tokens > 1
        assert tokens < 100
    
    def test_get_model_info(self, provider):
        """Test model info retrieval"""
        info = provider.get_model_info()
        
        assert "provider" in info
        assert "model" in info
        assert "context_window" in info
        assert "speed" in info
        assert info["provider"] == "groq"
        assert info["model"] == "mixtral-8x7b-32768"
        assert info["context_window"] == 32768
    
    def test_is_available(self):
        """Test availability check"""
        available = GroqProvider.is_available()
        assert isinstance(available, bool)


class TestProviderConsistency:
    """Test that all providers follow the same interface"""
    
    def test_all_providers_have_generate(self):
        """Test all providers implement generate method"""
        for ProviderClass in [OpenAIProvider, GeminiProvider, GroqProvider]:
            assert hasattr(ProviderClass, 'generate')
    
    def test_all_providers_have_estimate_tokens(self):
        """Test all providers implement estimate_tokens method"""
        for ProviderClass in [OpenAIProvider, GeminiProvider, GroqProvider]:
            assert hasattr(ProviderClass, 'estimate_tokens')
    
    def test_all_providers_have_get_model_info(self):
        """Test all providers implement get_model_info method"""
        for ProviderClass in [OpenAIProvider, GeminiProvider, GroqProvider]:
            assert hasattr(ProviderClass, 'get_model_info')
    
    def test_all_providers_have_is_available(self):
        """Test all providers have is_available static method"""
        for ProviderClass in [GeminiProvider, GroqProvider]:
            assert hasattr(ProviderClass, 'is_available')
            assert callable(getattr(ProviderClass, 'is_available'))


class TestProviderSchemaValidation:
    """Test JSON schema validation across providers"""
    
    @pytest.fixture
    def openai_provider(self):
        """Create OpenAI provider"""
        return OpenAIProvider(api_key="test_key", model_name="gpt-4o-mini")
    
    def test_valid_json_schema(self, openai_provider):
        """Test validation of valid JSON against schema"""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"}
            },
            "required": ["name"]
        }
        
        valid_json = '{"name": "John", "age": 30}'
        
        is_valid, error, parsed = openai_provider.validate_response_schema(valid_json, schema)
        
        assert is_valid == True
        assert error is None
        assert parsed == {"name": "John", "age": 30}
    
    def test_invalid_json_syntax(self, openai_provider):
        """Test validation of invalid JSON syntax"""
        schema = {"type": "object"}
        invalid_json = '{name: "John"}'  # Invalid JSON
        
        is_valid, error, parsed = openai_provider.validate_response_schema(invalid_json, schema)
        
        assert is_valid == False
        assert "Invalid JSON" in error
        assert parsed is None
    
    def test_json_schema_mismatch(self, openai_provider):
        """Test validation when JSON doesn't match schema"""
        from app.services.llm.base_provider import JSONSCHEMA_AVAILABLE
        
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"}
            },
            "required": ["name"]
        }
        
        invalid_data = '{"age": 30}'  # Missing required 'name'
        
        is_valid, error, parsed = openai_provider.validate_response_schema(invalid_data, schema)
        
        if JSONSCHEMA_AVAILABLE:
            # If jsonschema is installed, validation should fail
            assert is_valid == False
            assert "Schema validation failed" in error
            assert parsed is None
        else:
            # If jsonschema not available, it will just parse JSON and return success
            assert is_valid == True
            assert error is None
            assert parsed == {"age": 30}
    
    def test_no_schema_validation(self, openai_provider):
        """Test that no schema means no validation"""
        content = "Any text here"
        
        is_valid, error, parsed = openai_provider.validate_response_schema(content, schema=None)
        
        assert is_valid == True
        assert error is None
        assert parsed is None

