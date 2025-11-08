"""
LLM Router - Multi-Provider Orchestration for Agentic AI
=========================================================
Supports: OpenAI, Anthropic Claude, Google Gemini
Features: Auto-selection, failover, cost tracking, analytics

Architecture Principles:
- Zero regression: Isolated service, doesn't touch existing code
- Agentic AI: Intelligent provider selection based on context
- Production-ready: Comprehensive error handling and logging
- Monetization-first: Full cost tracking and analytics
"""

from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime
import os
import json
from openai import AsyncOpenAI
from google.cloud import firestore

class LLMProvider(str, Enum):
    """Supported LLM providers"""
    OPENAI_GPT4O_MINI = "openai_gpt4o_mini"
    OPENAI_GPT4O = "openai_gpt4o"
    CLAUDE_35_SONNET = "claude_35_sonnet"
    GEMINI_PRO = "gemini_pro"

class LLMConfig:
    """Configuration for each LLM provider"""
    def __init__(
        self,
        provider: LLMProvider,
        model_name: str,
        cost_per_1k_input: float,
        cost_per_1k_output: float,
        max_tokens: int,
        enabled: bool = True,
        priority: int = 1,
        quota_per_day: Optional[int] = None
    ):
        self.provider = provider
        self.model_name = model_name
        self.cost_per_1k_input = cost_per_1k_input
        self.cost_per_1k_output = cost_per_1k_output
        self.max_tokens = max_tokens
        self.enabled = enabled
        self.priority = priority
        self.quota_per_day = quota_per_day
        self.usage_today = 0

class LLMRouter:
    """
    Intelligent LLM Router with:
    - Multi-provider support (OpenAI, Claude, Gemini)
    - Auto-selection based on cost/performance/quota
    - Automatic failover chain
    - Usage tracking and analytics
    - Dynamic configuration from Firestore
    """
    
    def __init__(self):
        from app.core.config_manager import settings
        
        project = settings.google_cloud_project
        self.db = firestore.Client(project=project) if project else None
        
        # Initialize OpenAI client (primary provider)
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        
        self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
        
        # Initialize other providers (optional for MVP)
        # Claude and Gemini can be added when API keys are available
        self.anthropic_client = None
        self.gemini_client = None
        
        # Default configurations (can be overridden from Firestore)
        self.default_configs = {
            LLMProvider.OPENAI_GPT4O_MINI: LLMConfig(
                provider=LLMProvider.OPENAI_GPT4O_MINI,
                model_name="gpt-4o-mini",
                cost_per_1k_input=0.00015,
                cost_per_1k_output=0.0006,
                max_tokens=16000,
                enabled=True,
                priority=1,  # Highest priority (default)
                quota_per_day=10000
            ),
            LLMProvider.OPENAI_GPT4O: LLMConfig(
                provider=LLMProvider.OPENAI_GPT4O,
                model_name="gpt-4o",
                cost_per_1k_input=0.0025,
                cost_per_1k_output=0.01,
                max_tokens=16000,
                enabled=True,
                priority=2,  # Fallback
                quota_per_day=5000
            ),
            LLMProvider.CLAUDE_35_SONNET: LLMConfig(
                provider=LLMProvider.CLAUDE_35_SONNET,
                model_name="claude-3-5-sonnet-20241022",
                cost_per_1k_input=0.003,
                cost_per_1k_output=0.015,
                max_tokens=8192,
                enabled=False,  # Disabled until API key added
                priority=3,
                quota_per_day=5000
            ),
            LLMProvider.GEMINI_PRO: LLMConfig(
                provider=LLMProvider.GEMINI_PRO,
                model_name="gemini-1.5-pro",
                cost_per_1k_input=0.00125,
                cost_per_1k_output=0.005,
                max_tokens=8192,
                enabled=False,  # Disabled until API key added
                priority=4,
                quota_per_day=5000
            ),
        }
        
        # Load configurations from Firestore (hot-reloadable)
        self.configs = self._load_configs()
        
        print("✅ [LLM ROUTER] Initialized successfully")
        print(f"   Primary: {self.configs[LLMProvider.OPENAI_GPT4O_MINI].model_name}")
        print(f"   Fallback: {self.configs[LLMProvider.OPENAI_GPT4O].model_name}")
    
    def _load_configs(self) -> Dict[LLMProvider, LLMConfig]:
        """Load LLM configurations from Firestore (hot-reloadable)"""
        if not self.db:
            print("ℹ️ [LLM ROUTER] No Firestore client, using defaults")
            return self.default_configs
        
        try:
            config_doc = self.db.collection('system_config').document('llm_providers').get()
            
            if config_doc.exists:
                config_data = config_doc.to_dict()
                print("✅ [LLM ROUTER] Loaded configs from Firestore")
                
                # Merge with defaults
                configs = self.default_configs.copy()
                for provider_key, provider_data in config_data.items():
                    if provider_key in LLMProvider.__members__.values():
                        provider = LLMProvider(provider_key)
                        if provider in configs:
                            # Update from Firestore
                            configs[provider].enabled = provider_data.get('enabled', configs[provider].enabled)
                            configs[provider].priority = provider_data.get('priority', configs[provider].priority)
                            configs[provider].quota_per_day = provider_data.get('quota_per_day', configs[provider].quota_per_day)
                
                return configs
            else:
                print("ℹ️ [LLM ROUTER] No Firestore config found, using defaults")
                return self.default_configs
                
        except Exception as e:
            print(f"⚠️ [LLM ROUTER] Error loading configs: {e}, using defaults")
            return self.default_configs
    
    async def generate_meal_plan(
        self,
        prompt: str,
        system_instruction: str,
        user_id: str,
        preferred_provider: Optional[LLMProvider] = None,
        max_cost: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Generate meal plan using best available LLM
        
        Args:
            prompt: User-specific meal plan prompt
            system_instruction: System-level instructions
            user_id: For analytics and cost tracking
            preferred_provider: Optional provider preference
            max_cost: Optional max cost constraint
        
        Returns:
            {
                'meal_plan': {...},  # Parsed meal plan JSON
                'provider_used': 'openai_gpt4o_mini',
                'model_name': 'gpt-4o-mini',
                'cost': 0.005,
                'tokens_input': 2000,
                'tokens_output': 1500,
                'latency_ms': 2500,
                'timestamp': '2025-11-08T...',
                'providers_tried': ['openai_gpt4o_mini']
            }
        """
        
        start_time = datetime.now()
        
        print(f"🤖 [LLM ROUTER] Starting meal plan generation for user: {user_id}")
        
        # 1. Select provider
        provider = self._select_provider(
            preferred=preferred_provider,
            max_cost=max_cost
        )
        
        if not provider:
            raise Exception("No available LLM provider")
        
        print(f"🎯 [LLM ROUTER] Selected provider: {provider.provider.value}")
        print(f"   Model: {provider.model_name}")
        print(f"   Priority: {provider.priority}")
        print(f"   Estimated cost: ${self._estimate_cost(provider):.4f}")
        
        # 2. Generate with selected provider (with failover)
        result = None
        providers_tried = []
        last_error = None
        
        for attempt_provider in self._get_failover_chain(provider):
            try:
                providers_tried.append(attempt_provider.provider.value)
                print(f"🔄 [LLM ROUTER] Attempting with {attempt_provider.provider.value}...")
                
                if attempt_provider.provider in [LLMProvider.OPENAI_GPT4O_MINI, LLMProvider.OPENAI_GPT4O]:
                    result = await self._generate_openai(prompt, system_instruction, attempt_provider)
                elif attempt_provider.provider == LLMProvider.CLAUDE_35_SONNET:
                    result = await self._generate_claude(prompt, system_instruction, attempt_provider)
                elif attempt_provider.provider == LLMProvider.GEMINI_PRO:
                    result = await self._generate_gemini(prompt, system_instruction, attempt_provider)
                
                if result:
                    print(f"✅ [LLM ROUTER] Success with {attempt_provider.provider.value}")
                    break
                    
            except Exception as e:
                last_error = e
                print(f"❌ [LLM ROUTER] Failed with {attempt_provider.provider.value}: {str(e)[:200]}")
                continue
        
        if not result:
            error_msg = f"All LLM providers failed. Tried: {providers_tried}. Last error: {last_error}"
            print(f"❌ [LLM ROUTER] {error_msg}")
            raise Exception(error_msg)
        
        # 3. Calculate metrics
        end_time = datetime.now()
        latency_ms = (end_time - start_time).total_seconds() * 1000
        
        print(f"⚡ [LLM ROUTER] Generation completed in {latency_ms:.0f}ms")
        print(f"💰 [LLM ROUTER] Cost: ${result['cost']:.4f}")
        
        # 4. Log analytics (async, non-blocking)
        try:
            await self._log_analytics(
                user_id=user_id,
                provider=result['provider_used'],
                model_name=result['model_name'],
                cost=result['cost'],
                tokens_input=result['tokens_input'],
                tokens_output=result['tokens_output'],
                latency_ms=latency_ms,
                success=True,
                providers_tried=providers_tried
            )
        except Exception as e:
            print(f"⚠️ [LLM ROUTER] Analytics logging failed (non-critical): {e}")
        
        result['latency_ms'] = latency_ms
        result['timestamp'] = end_time.isoformat()
        result['providers_tried'] = providers_tried
        
        return result
    
    def _select_provider(
        self,
        preferred: Optional[LLMProvider] = None,
        max_cost: Optional[float] = None
    ) -> Optional[LLMConfig]:
        """
        Select best provider based on:
        1. User preference (if specified)
        2. Cost constraint (if specified)
        3. Quota availability
        4. Priority order
        """
        
        # If preferred provider specified and available, use it
        if preferred and preferred in self.configs:
            config = self.configs[preferred]
            if config.enabled and self._check_quota(config):
                return config
        
        # Otherwise, select by priority
        available_providers = [
            config for config in self.configs.values()
            if config.enabled and self._check_quota(config)
        ]
        
        # Filter by cost if constraint specified
        if max_cost:
            available_providers = [
                p for p in available_providers
                if self._estimate_cost(p) <= max_cost
            ]
        
        if not available_providers:
            return None
        
        # Sort by priority (lower number = higher priority)
        available_providers.sort(key=lambda x: x.priority)
        
        return available_providers[0]
    
    def _get_failover_chain(self, primary: LLMConfig) -> List[LLMConfig]:
        """Get ordered list of providers for failover"""
        chain = [primary]
        
        # Add other enabled providers in priority order
        fallbacks = [
            config for config in self.configs.values()
            if config.enabled and config != primary and self._check_quota(config)
        ]
        fallbacks.sort(key=lambda x: x.priority)
        
        chain.extend(fallbacks)
        
        print(f"🔗 [LLM ROUTER] Failover chain: {[c.provider.value for c in chain]}")
        
        return chain
    
    def _check_quota(self, config: LLMConfig) -> bool:
        """Check if provider has quota remaining"""
        if config.quota_per_day is None:
            return True
        return config.usage_today < config.quota_per_day
    
    def _estimate_cost(self, config: LLMConfig) -> float:
        """Estimate cost for typical meal plan generation"""
        # Assume ~2500 input tokens, ~2000 output tokens (typical meal plan)
        input_cost = (2500 / 1000) * config.cost_per_1k_input
        output_cost = (2000 / 1000) * config.cost_per_1k_output
        return input_cost + output_cost
    
    async def _generate_openai(
        self,
        prompt: str,
        system_instruction: str,
        config: LLMConfig
    ) -> Dict[str, Any]:
        """Generate using OpenAI (GPT-4o-mini or GPT-4o)"""
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=config.model_name,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            # Parse JSON response
            meal_plan = json.loads(response.choices[0].message.content)
            
            # Calculate cost
            tokens_input = response.usage.prompt_tokens
            tokens_output = response.usage.completion_tokens
            cost = (tokens_input / 1000 * config.cost_per_1k_input) + \
                   (tokens_output / 1000 * config.cost_per_1k_output)
            
            return {
                'meal_plan': meal_plan,
                'provider_used': config.provider.value,
                'model_name': config.model_name,
                'cost': cost,
                'tokens_input': tokens_input,
                'tokens_output': tokens_output,
            }
            
        except Exception as e:
            print(f"❌ [OPENAI] Generation failed: {e}")
            raise
    
    async def _generate_claude(
        self,
        prompt: str,
        system_instruction: str,
        config: LLMConfig
    ) -> Dict[str, Any]:
        """Generate using Anthropic Claude (future implementation)"""
        
        if not self.anthropic_client:
            raise Exception("Anthropic client not initialized (API key missing)")
        
        # TODO: Implement when Anthropic API key is available
        raise NotImplementedError("Claude integration pending API key")
    
    async def _generate_gemini(
        self,
        prompt: str,
        system_instruction: str,
        config: LLMConfig
    ) -> Dict[str, Any]:
        """Generate using Google Gemini (future implementation)"""
        
        if not self.gemini_client:
            raise Exception("Gemini client not initialized (API key missing)")
        
        # TODO: Implement when Google API key is available
        raise NotImplementedError("Gemini integration pending API key")
    
    async def _log_analytics(
        self,
        user_id: str,
        provider: str,
        model_name: str,
        cost: float,
        tokens_input: int,
        tokens_output: int,
        latency_ms: float,
        success: bool,
        providers_tried: List[str]
    ):
        """Log generation analytics to Firestore"""
        
        if not self.db:
            print("ℹ️ [LLM ANALYTICS] Firestore not available, skipping analytics")
            return
        
        try:
            analytics_ref = self.db.collection('llm_analytics').document()
            analytics_ref.set({
                'user_id': user_id,
                'provider': provider,
                'model_name': model_name,
                'cost': cost,
                'tokens_input': tokens_input,
                'tokens_output': tokens_output,
                'latency_ms': latency_ms,
                'success': success,
                'providers_tried': providers_tried,
                'timestamp': firestore.SERVER_TIMESTAMP,
                'feature': 'meal_plan_generation'
            })
            
            print(f"📊 [LLM ANALYTICS] Logged: {provider}, ${cost:.4f}, {latency_ms:.0f}ms")
            
        except Exception as e:
            print(f"⚠️ [LLM ANALYTICS] Failed to log (non-critical): {e}")

