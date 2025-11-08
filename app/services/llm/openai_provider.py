"""
OpenAI LLM Provider

Implementation of BaseLLMProvider for OpenAI's GPT models.
Supports GPT-4, GPT-4o, GPT-3.5, and other OpenAI models.
"""

from typing import Dict, Any, Optional
from openai import AsyncOpenAI, OpenAIError
from app.services.llm.base_provider import BaseLLMProvider

# tiktoken is optional - fallback to estimation if not available
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    tiktoken = None


class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI provider implementation
    
    Supports:
    - GPT-4o, GPT-4o-mini
    - GPT-4, GPT-4-turbo
    - GPT-3.5-turbo
    """
    
    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini"):
        """
        Initialize OpenAI provider
        
        Args:
            api_key: OpenAI API key
            model_name: Model to use (default: gpt-4o-mini)
        """
        super().__init__(api_key, model_name)
        self.client = AsyncOpenAI(api_key=api_key)
        
        # Initialize tokenizer for accurate token counting (if tiktoken available)
        self.tokenizer: Optional[Any] = None
        if TIKTOKEN_AVAILABLE and tiktoken is not None:
            try:
                self.tokenizer = tiktoken.encoding_for_model(model_name)
            except KeyError:
                # Fallback to cl100k_base for newer models
                try:
                    self.tokenizer = tiktoken.get_encoding("cl100k_base")
                except Exception:
                    pass  # Will use estimation fallback
    
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        response_format: str = "text"
    ) -> Dict[str, Any]:
        """
        Generate response using OpenAI API
        
        Args:
            system_prompt: System instructions
            user_prompt: User's prompt
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens to generate
            response_format: "text" or "json"
        
        Returns:
            Dictionary with response data and usage metrics
        
        Raises:
            OpenAIError: If API call fails
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
            
            # Add response format if JSON requested
            if response_format == "json":
                api_params["response_format"] = {"type": "json_object"}
            
            # Make API call
            response = await self.client.chat.completions.create(**api_params)
            
            # Extract response data
            content = response.choices[0].message.content
            
            # Get token usage
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
            
        except OpenAIError as e:
            response_time_ms = self._calculate_elapsed_ms(start_time)
            raise Exception(f"OpenAI API error: {str(e)}") from e
        except Exception as e:
            response_time_ms = self._calculate_elapsed_ms(start_time)
            # Re-raise with OpenAI context if not already an OpenAI error
            if "OpenAI API error" not in str(e):
                raise Exception(f"OpenAI API error: {str(e)}") from e
            raise
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate tokens using tiktoken (accurate for OpenAI models)
        
        Args:
            text: Text to count tokens for
        
        Returns:
            Token count
        """
        if self.tokenizer is not None:
            try:
                return len(self.tokenizer.encode(text))
            except Exception:
                pass
        
        # Fallback: rough estimate (4 chars per token)
        return len(text) // 4
    
    def count_message_tokens(self, messages: list[Dict[str, str]]) -> int:
        """
        Count tokens in a list of messages (more accurate than estimating text)
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
        
        Returns:
            Estimated token count including message formatting overhead
        """
        if self.tokenizer is not None:
            try:
                num_tokens = 0
                for message in messages:
                    # Every message follows <im_start>{role/name}\n{content}<im_end>\n
                    num_tokens += 4  # Message formatting tokens
                    for key, value in message.items():
                        num_tokens += len(self.tokenizer.encode(value))
                num_tokens += 2  # Every reply is primed with <im_start>assistant
                return num_tokens
            except Exception:
                pass
        
        # Fallback: rough estimation
        total_chars = sum(len(msg.get('content', '')) for msg in messages)
        return total_chars // 4
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current OpenAI model
        
        Returns:
            Model metadata
        """
        # Model context windows and costs (as of Nov 2024)
        model_info = {
            "gpt-4o": {
                "context_window": 128000,
                "cost_per_1k_input": 0.0025,
                "cost_per_1k_output": 0.0100
            },
            "gpt-4o-mini": {
                "context_window": 128000,
                "cost_per_1k_input": 0.00015,
                "cost_per_1k_output": 0.00060
            },
            "gpt-4-turbo": {
                "context_window": 128000,
                "cost_per_1k_input": 0.0100,
                "cost_per_1k_output": 0.0300
            },
            "gpt-3.5-turbo": {
                "context_window": 16385,
                "cost_per_1k_input": 0.0005,
                "cost_per_1k_output": 0.0015
            }
        }
        
        info = model_info.get(self.model_name, {
            "context_window": 4096,
            "cost_per_1k_input": 0.001,
            "cost_per_1k_output": 0.002
        })
        
        return {
            **self.get_provider_info(),
            **info
        }

