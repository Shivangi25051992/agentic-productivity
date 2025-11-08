"""
LLM Router Service

Intelligent routing of LLM requests across multiple providers with:
- Automatic provider selection based on priority and quota
- Fallback to secondary providers on failure
- Usage tracking and quota enforcement
- Integration with Firestore for configuration
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from google.cloud import firestore
import time

from app.models.llm_config import (
    LLMProvider,
    LLMConfig,
    LLMRequest,
    LLMResponse,
    LLMUsageLog,
    LLMQuotaStatus
)
from app.services.llm.base_provider import BaseLLMProvider
from app.services.llm.openai_provider import OpenAIProvider
from app.services.llm.gemini_provider import GeminiProvider
from app.services.llm.groq_provider import GroqProvider


class LLMRouter:
    """
    LLM Router - Intelligent multi-provider routing
    
    Features:
    - Priority-based provider selection
    - Automatic fallback on failure
    - Quota tracking and enforcement
    - Usage logging to Firestore
    - Provider health monitoring
    """
    
    # Map provider enum to provider class
    PROVIDER_CLASSES = {
        LLMProvider.OPENAI: OpenAIProvider,
        LLMProvider.GEMINI: GeminiProvider,
        LLMProvider.GROQ: GroqProvider,
    }
    
    def __init__(self, db: firestore.Client):
        """
        Initialize LLM Router
        
        Args:
            db: Firestore client for configuration and usage tracking
        """
        self.db = db
        self.providers_cache: Dict[str, BaseLLMProvider] = {}
        self.config_cache: Dict[str, LLMConfig] = {}
        self.cache_ttl_seconds = 300  # Cache configs for 5 minutes
        self.last_cache_refresh: Optional[datetime] = None
    
    async def route_request(
        self,
        request: LLMRequest
    ) -> LLMResponse:
        """
        Route LLM request to appropriate provider with automatic fallback
        
        Args:
            request: LLM request with prompts (direct or template-based) and preferences
        
        Returns:
            LLMResponse with generated content and metadata
        
        Raises:
            Exception: If all providers fail
        """
        start_time = time.perf_counter()
        
        # Get prompts (direct or from template)
        if request.system_prompt and request.user_prompt:
            # Direct prompt mode
            system_prompt = request.system_prompt
            user_prompt = request.user_prompt
        elif request.prompt_template_id:
            # Template mode (not implemented in this integration - would use PromptService)
            raise Exception("Template-based prompts not yet implemented - use direct prompts")
        else:
            raise Exception("Either direct prompts or prompt_template_id must be provided")
        
        # Load provider configurations
        configs = await self._load_provider_configs()
        
        if not configs:
            raise Exception("No LLM providers configured")
        
        # Select providers in priority order
        providers_to_try = self._select_providers(configs, request.preferred_provider)
        
        if not providers_to_try:
            raise Exception("No available LLM providers (all inactive or quota exceeded)")
        
        # Try providers in order until one succeeds
        last_error = None
        fallback_used = False
        
        for idx, config in enumerate(providers_to_try):
            if idx > 0:
                fallback_used = True
                print(f"🔄 [LLM ROUTER] Trying fallback provider: {config.provider}")
            
            try:
                # Get or create provider instance
                provider = self._get_provider_instance(config)
                
                # Generate response
                generation_start = time.perf_counter()
                
                result = await provider.generate(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    temperature=request.temperature or config.temperature,
                    max_tokens=request.max_tokens or config.max_tokens,
                    response_format=request.response_format or "text"
                )
                
                generation_time_ms = int((time.perf_counter() - generation_start) * 1000)
                
                # Update quota (fire-and-forget, don't block response)
                import asyncio
                asyncio.create_task(self._update_quota(config, result["tokens_used"]))
                
                # Log usage (fire-and-forget, don't block response)
                asyncio.create_task(self._log_usage(
                    config=config,
                    request=request,
                    tokens_used=result["tokens_used"],
                    prompt_tokens=result["prompt_tokens"],
                    completion_tokens=result["completion_tokens"],
                    response_time_ms=generation_time_ms,
                    success=True
                ))
                
                # Create response
                response = LLMResponse(
                    content=result["content"],
                    provider_used=config.provider,
                    model_used=result["model_used"],
                    tokens_used=result["tokens_used"],
                    prompt_tokens=result["prompt_tokens"],
                    completion_tokens=result["completion_tokens"],
                    response_time_ms=generation_time_ms,
                    success=True,
                    fallback_used=fallback_used
                )
                
                print(f"✅ [LLM ROUTER] Success with {config.provider}: {result['tokens_used']} tokens")
                
                return response
                
            except Exception as e:
                last_error = e
                error_msg = str(e)
                
                print(f"❌ [LLM ROUTER] {config.provider} failed: {error_msg}")
                
                # Log failed attempt (fire-and-forget)
                import asyncio
                asyncio.create_task(self._log_usage(
                    config=config,
                    request=request,
                    tokens_used=0,
                    prompt_tokens=0,
                    completion_tokens=0,
                    response_time_ms=0,
                    success=False,
                    error=error_msg
                ))
                
                # Continue to next provider
                continue
        
        # All providers failed
        total_time_ms = int((time.perf_counter() - start_time) * 1000)
        raise Exception(
            f"All LLM providers failed. Tried {len(providers_to_try)} provider(s). "
            f"Last error: {str(last_error)}"
        )
    
    async def _load_provider_configs(self) -> List[LLMConfig]:
        """
        Load provider configurations from Firestore
        
        Returns:
            List of LLMConfig objects
        """
        # Check if cache is valid
        if self.last_cache_refresh:
            age_seconds = (datetime.now(timezone.utc) - self.last_cache_refresh).total_seconds()
            if age_seconds < self.cache_ttl_seconds:
                return list(self.config_cache.values())
        
        # Load from Firestore
        configs = []
        
        try:
            # Query active providers from llm_configs collection
            providers_ref = self.db.collection('llm_configs')
            docs = providers_ref.where('is_active', '==', True).stream()
            
            for doc in docs:
                try:
                    config = LLMConfig.from_dict(doc.to_dict())
                    configs.append(config)
                    self.config_cache[config.id] = config
                except Exception as e:
                    print(f"⚠️ [LLM ROUTER] Error parsing config {doc.id}: {e}")
            
            self.last_cache_refresh = datetime.now(timezone.utc)
            
        except Exception as e:
            print(f"⚠️ [LLM ROUTER] Error loading configs from Firestore: {e}")
            
            # Fallback to cached configs if available
            if self.config_cache:
                print(f"ℹ️ [LLM ROUTER] Using {len(self.config_cache)} cached configs")
                return list(self.config_cache.values())
            
            # No configs available
            print(f"❌ [LLM ROUTER] No provider configs available")
        
        return configs
    
    def _select_providers(
        self,
        configs: List[LLMConfig],
        preferred_provider: Optional[LLMProvider] = None
    ) -> List[LLMConfig]:
        """
        Select providers in priority order
        
        Args:
            configs: Available provider configurations
            preferred_provider: Preferred provider (if any)
        
        Returns:
            List of configs sorted by priority
        """
        # Filter out providers that can't be used (inactive or quota exceeded)
        usable_configs = [c for c in configs if c.can_be_used()]
        
        if not usable_configs:
            return []
        
        # Sort by priority first (1 = highest priority)
        usable_configs.sort(key=lambda c: c.priority)
        
        # If preferred provider specified and available, move it to first position
        if preferred_provider:
            preferred_config = next((c for c in usable_configs if c.provider == preferred_provider), None)
            if preferred_config:
                # Remove from current position and put at front
                usable_configs.remove(preferred_config)
                usable_configs.insert(0, preferred_config)
        
        return usable_configs
    
    def _get_provider_instance(self, config: LLMConfig) -> BaseLLMProvider:
        """
        Get or create provider instance
        
        Args:
            config: Provider configuration
        
        Returns:
            Provider instance
        
        Raises:
            Exception: If provider class not found or initialization fails
        """
        # Check cache
        cache_key = f"{config.provider}:{config.model_name}"
        if cache_key in self.providers_cache:
            return self.providers_cache[cache_key]
        
        # Get provider class
        provider_class = self.PROVIDER_CLASSES.get(config.provider)
        if not provider_class:
            raise Exception(f"Unknown provider: {config.provider}")
        
        # Create instance
        try:
            provider = provider_class(
                api_key=config.api_key,
                model_name=config.model_name
            )
            
            # Cache it
            self.providers_cache[cache_key] = provider
            
            return provider
            
        except Exception as e:
            raise Exception(f"Failed to initialize {config.provider}: {str(e)}") from e
    
    async def _update_quota(self, config: LLMConfig, tokens_used: int):
        """
        Update provider quota usage (FIXED PATH + ASYNC)
        
        Args:
            config: Provider configuration
            tokens_used: Number of tokens used
        """
        try:
            # FIX: Correct path is llm_configs/{id}, not admin/llm_config/providers/{id}
            provider_ref = self.db.collection('llm_configs').document(config.id)
            
            # Increment quota_used (ASYNC - non-blocking)
            import asyncio
            await asyncio.to_thread(provider_ref.update, {
                'quota_used': firestore.Increment(tokens_used),
                'updated_at': datetime.now(timezone.utc)
            })
            
            # Update cache
            if config.id in self.config_cache:
                self.config_cache[config.id].quota_used += tokens_used
            
        except Exception as e:
            print(f"⚠️ [LLM ROUTER] Error updating quota for {config.provider}: {e}")
    
    async def _log_usage(
        self,
        config: LLMConfig,
        request: LLMRequest,
        tokens_used: int,
        prompt_tokens: int,
        completion_tokens: int,
        response_time_ms: int,
        success: bool,
        error: Optional[str] = None
    ):
        """
        Log usage to Firestore for analytics
        
        Args:
            config: Provider configuration
            request: Original request
            tokens_used: Total tokens used
            prompt_tokens: Prompt tokens
            completion_tokens: Completion tokens
            response_time_ms: Response time in milliseconds
            success: Whether request succeeded
            error: Error message if failed
        """
        try:
            # Calculate cost if available
            cost_usd = None
            if config.cost_per_1k_tokens:
                cost_usd = (tokens_used / 1000) * config.cost_per_1k_tokens
            
            # Create usage log
            usage_log = LLMUsageLog(
                provider=config.provider,
                model_name=config.model_name,
                prompt_template_id=request.prompt_template_id,
                user_id=request.user_id,
                request_type=request.request_type,
                tokens_used=tokens_used,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                response_time_ms=response_time_ms,
                cost_usd=cost_usd,
                success=success,
                error=error
            )
            
            # Save to Firestore
            usage_ref = self.db.collection('admin').document('llm_usage_logs')\
                               .collection('logs').document(usage_log.id)
            usage_ref.set(usage_log.to_dict())
            
        except Exception as e:
            print(f"⚠️ [LLM ROUTER] Error logging usage: {e}")
            # Don't raise - logging failures shouldn't break the request
    
    async def get_quota_status(self, provider: Optional[LLMProvider] = None) -> List[LLMQuotaStatus]:
        """
        Get quota status for all providers or a specific provider
        
        Args:
            provider: Specific provider to check (None = all providers)
        
        Returns:
            List of quota status objects
        """
        configs = await self._load_provider_configs()
        
        if provider:
            configs = [c for c in configs if c.provider == provider]
        
        return [LLMQuotaStatus.from_config(c) for c in configs]
    
    async def refresh_cache(self):
        """Force refresh of configuration cache"""
        self.last_cache_refresh = None
        self.config_cache.clear()
        await self._load_provider_configs()
        print(f"✅ [LLM ROUTER] Cache refreshed: {len(self.config_cache)} configs loaded")

