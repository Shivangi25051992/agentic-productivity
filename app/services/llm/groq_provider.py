"""
Groq LLM Provider

Implementation of BaseLLMProvider for Groq's fast inference API.
Supports Mixtral, Llama, and other open-source models with blazing fast inference.
"""

from typing import Dict, Any, Optional
from app.services.llm.base_provider import BaseLLMProvider

# Groq client is optional - graceful fallback if not available
try:
    from groq import Groq, AsyncGroq, GroqError
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    Groq = None
    AsyncGroq = None
    GroqError = Exception


class GroqProvider(BaseLLMProvider):
    """
    Groq provider implementation (for Mixtral, Llama, etc.)
    
    Groq provides extremely fast inference for open-source models:
    - Mixtral 8x7B (best for complex reasoning)
    - Llama 3 70B (best for general tasks)
    - Llama 3 8B (fastest, good for simple tasks)
    
    Note: Groq has generous free tier but rate limits
    """
    
    def __init__(self, api_key: str, model_name: str = "mixtral-8x7b-32768"):
        """
        Initialize Groq provider
        
        Args:
            api_key: Groq API key
            model_name: Model to use (default: mixtral-8x7b-32768)
        
        Raises:
            ImportError: If groq client not installed
        """
        super().__init__(api_key, model_name)
        
        if not GROQ_AVAILABLE or AsyncGroq is None:
            raise ImportError(
                "groq is not installed. "
                "Install it with: pip install groq"
            )
        
        # Initialize async client
        self.client = AsyncGroq(api_key=api_key)
    
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        response_format: str = "text"
    ) -> Dict[str, Any]:
        """
        Generate response using Groq API
        
        Args:
            system_prompt: System instructions
            user_prompt: User's prompt
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens to generate
            response_format: "text" or "json"
        
        Returns:
            Dictionary with response data and usage metrics
        
        Raises:
            Exception: If API call fails
        """
        start_time = self._measure_time()
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            # Prepare API call parameters
            api_params = {
                "model": self.model_name,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            # Add JSON mode if supported and requested
            # Note: Not all Groq models support JSON mode
            if response_format == "json" and self._supports_json_mode():
                api_params["response_format"] = {"type": "json_object"}
            elif response_format == "json":
                # Add instruction to prompt for models without native JSON mode
                messages.append({
                    "role": "system",
                    "content": "Respond ONLY with valid JSON. Do not include any text before or after the JSON."
                })
            
            # Make API call
            response = await self.client.chat.completions.create(**api_params)
            
            # Extract response data
            content = response.choices[0].message.content
            
            # Get token usage (Groq provides accurate counts)
            usage = response.usage
            tokens_used = usage.total_tokens
            prompt_tokens = usage.prompt_tokens
            completion_tokens = usage.completion_tokens
            
            response_time_ms = self._calculate_elapsed_ms(start_time)
            
            return {
                "content": content,
                "tokens_used": tokens_used,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "response_time_ms": response_time_ms,
                "model_used": self.model_name,
                "finish_reason": response.choices[0].finish_reason
            }
            
        except GroqError as e:
            response_time_ms = self._calculate_elapsed_ms(start_time)
            
            # Improve error messages
            error_msg = str(e)
            if "rate_limit" in error_msg.lower():
                raise Exception(f"Groq rate limit exceeded: {error_msg}") from e
            elif "quota" in error_msg.lower():
                raise Exception(f"Groq quota exceeded: {error_msg}") from e
            else:
                raise Exception(f"Groq API error: {error_msg}") from e
        except Exception as e:
            response_time_ms = self._calculate_elapsed_ms(start_time)
            raise Exception(f"Groq API error: {str(e)}") from e
    
    def _supports_json_mode(self) -> bool:
        """
        Check if current model supports native JSON mode
        
        Returns:
            True if model supports JSON mode
        """
        # Models with native JSON mode support
        json_models = [
            "mixtral-8x7b-32768",
            "llama-3.1-70b-versatile",
            "llama-3.1-8b-instant"
        ]
        return self.model_name in json_models
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate tokens for Groq models
        
        Different models use different tokenizers:
        - Mixtral uses a SentencePiece tokenizer
        - Llama uses a different tokenizer
        
        This is a rough approximation for all models.
        
        Args:
            text: Text to estimate tokens for
        
        Returns:
            Estimated token count
        """
        # Most models: approximately 4 characters per token
        char_count = len(text)
        estimated_tokens = int(char_count / 4)
        
        # Minimum of 1 token
        return max(1, estimated_tokens)
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current Groq model
        
        Returns:
            Model metadata including speeds and limits
        """
        # Model information (as of Nov 2024)
        model_info = {
            "mixtral-8x7b-32768": {
                "context_window": 32768,
                "cost_per_1k_input": 0.0,  # Free tier available
                "cost_per_1k_output": 0.0,  # Free tier available
                "tokens_per_minute": 30000,  # Rate limit
                "description": "Mixtral 8x7B - Best for reasoning and analysis",
                "speed": "~600 tokens/sec"
            },
            "llama-3.1-70b-versatile": {
                "context_window": 131072,  # 128K context!
                "cost_per_1k_input": 0.0,
                "cost_per_1k_output": 0.0,
                "tokens_per_minute": 30000,
                "description": "Llama 3.1 70B - Most capable, large context",
                "speed": "~300 tokens/sec"
            },
            "llama-3.1-8b-instant": {
                "context_window": 131072,
                "cost_per_1k_input": 0.0,
                "cost_per_1k_output": 0.0,
                "tokens_per_minute": 30000,
                "description": "Llama 3.1 8B - Fastest, good for simple tasks",
                "speed": "~800 tokens/sec"
            },
            "llama3-70b-8192": {
                "context_window": 8192,
                "cost_per_1k_input": 0.0,
                "cost_per_1k_output": 0.0,
                "tokens_per_minute": 30000,
                "description": "Llama 3 70B - High quality, medium context",
                "speed": "~400 tokens/sec"
            },
            "llama3-8b-8192": {
                "context_window": 8192,
                "cost_per_1k_input": 0.0,
                "cost_per_1k_output": 0.0,
                "tokens_per_minute": 30000,
                "description": "Llama 3 8B - Fast and efficient",
                "speed": "~800 tokens/sec"
            }
        }
        
        info = model_info.get(self.model_name, {
            "context_window": 8192,
            "cost_per_1k_input": 0.0,
            "cost_per_1k_output": 0.0,
            "tokens_per_minute": 30000,
            "description": "Unknown Groq model",
            "speed": "Unknown"
        })
        
        return {
            **self.get_provider_info(),
            **info,
            "note": "Groq provides free tier with rate limits. Check groq.com for current limits."
        }
    
    @staticmethod
    def is_available() -> bool:
        """
        Check if Groq provider is available (dependencies installed)
        
        Returns:
            True if groq client is installed
        """
        return GROQ_AVAILABLE

