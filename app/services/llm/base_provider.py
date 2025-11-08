"""
Base LLM Provider Interface

Abstract base class defining the interface for all LLM providers.
Ensures consistent behavior across OpenAI, Gemini, Mixtral, etc.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import time
import json

# jsonschema is optional - schema validation will be skipped if not available
try:
    from jsonschema import validate, ValidationError as JSONSchemaValidationError
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False
    validate = None
    JSONSchemaValidationError = Exception


class BaseLLMProvider(ABC):
    """
    Abstract base class for LLM providers
    
    All provider implementations must inherit from this class and
    implement the required methods.
    """
    
    def __init__(self, api_key: str, model_name: str):
        """
        Initialize the provider
        
        Args:
            api_key: API key for the provider
            model_name: Name of the model to use
        """
        self.api_key = api_key
        self.model_name = model_name
        self.provider_name = self.__class__.__name__.replace('Provider', '').lower()
    
    @abstractmethod
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        response_format: str = "text"
    ) -> Dict[str, Any]:
        """
        Generate a response from the LLM
        
        Args:
            system_prompt: System/role instructions
            user_prompt: User's actual prompt
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens to generate
            response_format: "text" or "json"
        
        Returns:
            Dictionary with:
                - content: Generated text
                - tokens_used: Total tokens consumed
                - prompt_tokens: Tokens in prompt
                - completion_tokens: Tokens in completion
                - response_time_ms: Response time in milliseconds
                - model_used: Specific model that was used
        
        Raises:
            Exception: If API call fails
        """
        pass
    
    def validate_response_schema(
        self,
        response_content: str,
        schema: Optional[Dict[str, Any]] = None
    ) -> tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Validate response against JSON schema
        
        Args:
            response_content: The LLM response content
            schema: JSON schema to validate against (if None, skips validation)
        
        Returns:
            Tuple of (is_valid, error_message, parsed_json)
            - is_valid: Whether validation passed
            - error_message: Error description if validation failed
            - parsed_json: Parsed JSON object if valid, None otherwise
        """
        if schema is None:
            return True, None, None
        
        # Check if jsonschema is available
        if not JSONSCHEMA_AVAILABLE or validate is None:
            # Can't validate without jsonschema - just parse JSON and return
            try:
                parsed = json.loads(response_content)
                return True, None, parsed
            except json.JSONDecodeError as e:
                return False, f"Invalid JSON: {str(e)}", None
        
        # Try to parse JSON
        try:
            parsed = json.loads(response_content)
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {str(e)}", None
        
        # Validate against schema
        try:
            validate(instance=parsed, schema=schema)
            return True, None, parsed
        except JSONSchemaValidationError as e:
            return False, f"Schema validation failed: {str(e)}", None
    
    def _measure_time(self):
        """
        Context manager for measuring execution time
        
        Usage:
            start = time.perf_counter()
            ... do work ...
            elapsed_ms = int((time.perf_counter() - start) * 1000)
        """
        return time.perf_counter()
    
    def _calculate_elapsed_ms(self, start_time: float) -> int:
        """Calculate elapsed time in milliseconds"""
        return int((time.perf_counter() - start_time) * 1000)
    
    @abstractmethod
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate number of tokens in text
        
        Args:
            text: Text to estimate tokens for
        
        Returns:
            Estimated token count
        
        Note:
            Different providers have different tokenization.
            This is an approximation for quota enforcement.
        """
        pass
    
    def get_provider_info(self) -> Dict[str, str]:
        """
        Get information about this provider
        
        Returns:
            Dictionary with provider metadata
        """
        return {
            "provider": self.provider_name,
            "model": self.model_name,
            "class": self.__class__.__name__
        }

