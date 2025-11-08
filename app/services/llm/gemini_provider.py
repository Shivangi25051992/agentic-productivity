"""
Google Gemini LLM Provider

Implementation of BaseLLMProvider for Google's Gemini models.
Supports Gemini 1.5 Pro, Gemini 1.5 Flash, and other Gemini models.
"""

from typing import Dict, Any, Optional
import json
from app.services.llm.base_provider import BaseLLMProvider

# Google Generative AI is optional - graceful fallback if not available
try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None
    HarmCategory = None
    HarmBlockThreshold = None


class GeminiProvider(BaseLLMProvider):
    """
    Google Gemini provider implementation
    
    Supports:
    - Gemini 1.5 Pro (best quality, most capable)
    - Gemini 1.5 Flash (fast, efficient)
    - Gemini Pro (legacy)
    """
    
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        """
        Initialize Gemini provider
        
        Args:
            api_key: Google AI API key
            model_name: Model to use (default: gemini-1.5-flash)
        
        Raises:
            ImportError: If google-generativeai not installed
        """
        super().__init__(api_key, model_name)
        
        if not GENAI_AVAILABLE or genai is None:
            raise ImportError(
                "google-generativeai is not installed. "
                "Install it with: pip install google-generativeai"
            )
        
        # Configure API key
        genai.configure(api_key=api_key)
        
        # Initialize model
        self.model = genai.GenerativeModel(model_name)
        
        # Safety settings - balanced approach for nutrition/fitness content
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }
    
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        response_format: str = "text"
    ) -> Dict[str, Any]:
        """
        Generate response using Gemini API
        
        Args:
            system_prompt: System instructions (prepended to user prompt)
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
        
        try:
            # Gemini doesn't have separate system/user roles like OpenAI
            # Combine system and user prompts
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            # Add JSON instruction if needed
            if response_format == "json":
                full_prompt += "\n\nRespond ONLY with valid JSON. Do not include any text before or after the JSON."
            
            # Configure generation parameters
            generation_config = genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                candidate_count=1
            )
            
            # Generate content
            response = self.model.generate_content(
                full_prompt,
                generation_config=generation_config,
                safety_settings=self.safety_settings
            )
            
            # Extract response text
            content = response.text
            
            # Estimate token usage (Gemini doesn't provide exact counts in API response)
            prompt_tokens = self.estimate_tokens(full_prompt)
            completion_tokens = self.estimate_tokens(content)
            tokens_used = prompt_tokens + completion_tokens
            
            response_time_ms = self._calculate_elapsed_ms(start_time)
            
            # Check for safety blocks
            if not response.candidates:
                raise Exception("Response blocked by safety filters")
            
            # Get finish reason
            finish_reason = response.candidates[0].finish_reason.name if response.candidates else "UNKNOWN"
            
            return {
                "content": content,
                "tokens_used": tokens_used,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "response_time_ms": response_time_ms,
                "model_used": self.model_name,
                "finish_reason": finish_reason
            }
            
        except Exception as e:
            response_time_ms = self._calculate_elapsed_ms(start_time)
            
            # Improve error messages
            error_msg = str(e)
            if "quota" in error_msg.lower():
                raise Exception(f"Gemini API quota exceeded: {error_msg}") from e
            elif "safety" in error_msg.lower():
                raise Exception(f"Gemini safety filter triggered: {error_msg}") from e
            else:
                raise Exception(f"Gemini API error: {error_msg}") from e
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate tokens for Gemini models
        
        Gemini uses SentencePiece tokenization, similar to other modern LLMs.
        This is a rough approximation.
        
        Args:
            text: Text to estimate tokens for
        
        Returns:
            Estimated token count
        """
        # Gemini tokenization is roughly 4 characters per token for English
        # More accurate would require the actual tokenizer, but this is sufficient
        # for quota enforcement
        char_count = len(text)
        
        # Estimate based on character count
        # Gemini is slightly more efficient than GPT, so use 3.5 chars/token
        estimated_tokens = int(char_count / 3.5)
        
        # Minimum of 1 token
        return max(1, estimated_tokens)
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current Gemini model
        
        Returns:
            Model metadata including costs and limits
        """
        # Model information (as of Nov 2024)
        model_info = {
            "gemini-1.5-pro": {
                "context_window": 2000000,  # 2M tokens!
                "cost_per_1k_input": 0.0025,
                "cost_per_1k_output": 0.0075,
                "description": "Most capable Gemini model"
            },
            "gemini-1.5-flash": {
                "context_window": 1000000,  # 1M tokens
                "cost_per_1k_input": 0.00015,
                "cost_per_1k_output": 0.00060,
                "description": "Fast and efficient Gemini model"
            },
            "gemini-pro": {
                "context_window": 32000,
                "cost_per_1k_input": 0.0005,
                "cost_per_1k_output": 0.0015,
                "description": "Legacy Gemini Pro model"
            }
        }
        
        info = model_info.get(self.model_name, {
            "context_window": 32000,
            "cost_per_1k_input": 0.001,
            "cost_per_1k_output": 0.002,
            "description": "Unknown Gemini model"
        })
        
        return {
            **self.get_provider_info(),
            **info
        }
    
    @staticmethod
    def is_available() -> bool:
        """
        Check if Gemini provider is available (dependencies installed)
        
        Returns:
            True if google-generativeai is installed
        """
        return GENAI_AVAILABLE

