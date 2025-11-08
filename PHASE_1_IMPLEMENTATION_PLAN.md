# Phase 1: Agentic AI Foundation - Implementation Plan

**Branch:** `feature/phase1-agentic-ai-foundation`  
**Started:** November 6, 2025  
**Estimated Duration:** 5-7 days  
**Goal:** Build Multi-LLM Router infrastructure without breaking existing features

---

## 🎯 Success Criteria

### Functional Requirements
- ✅ Multi-LLM Router can route requests to OpenAI, Gemini, or Mixtral
- ✅ Automatic fallback to secondary provider on failure
- ✅ Quota tracking and enforcement
- ✅ Admin can configure providers via Firestore (no code deployment)
- ✅ All prompts stored in Firestore with versioning
- ✅ JSON schema validation for LLM responses

### Non-Functional Requirements
- ✅ **ZERO REGRESSION:** All existing features work exactly as before
- ✅ Response time < 5s for LLM calls (with timeout)
- ✅ Error handling with graceful fallback
- ✅ Comprehensive logging for debugging
- ✅ Unit test coverage > 80%
- ✅ Integration tests for all providers

---

## 📋 Implementation Tasks

### Task 1: Data Models (Day 1)
**Priority:** HIGH  
**Dependencies:** None

#### Files to Create:
1. `app/models/llm_config.py`
   ```python
   class LLMProvider(str, Enum):
       OPENAI = "openai"
       GEMINI = "gemini"
       MIXTRAL = "mixtral"
       ANTHROPIC = "anthropic"
   
   class LLMConfig(BaseModel):
       provider: LLMProvider
       api_key: str
       model_name: str
       priority: int  # 1 = primary, 2 = fallback, etc.
       max_tokens: int = 4000
       temperature: float = 0.7
       quota_limit: Optional[int] = None
       is_active: bool = True
   
   class LLMUsageLog(BaseModel):
       provider: LLMProvider
       model_name: str
       tokens_used: int
       cost_usd: float
       response_time_ms: int
       timestamp: datetime
       success: bool
       error: Optional[str] = None
   ```

2. `app/models/prompt_template.py`
   ```python
   class PromptTemplate(BaseModel):
       id: str
       name: str
       description: str
       system_prompt: str
       user_prompt_template: str  # With {placeholders}
       json_schema: Optional[dict] = None
       version: str = "1.0"
       created_at: datetime
       updated_at: datetime
   ```

#### Tests to Create:
- `tests/unit/test_llm_config.py`
  - Test model validation
  - Test enum values
  - Test default values

**Success Criteria:**
- ✅ Models validate correctly
- ✅ All tests pass
- ✅ No breaking changes to existing models

---

### Task 2: LLM Provider Clients (Day 1-2)
**Priority:** HIGH  
**Dependencies:** Task 1

#### Files to Create:
1. `app/services/llm/base_provider.py`
   ```python
   from abc import ABC, abstractmethod
   
   class BaseLLMProvider(ABC):
       @abstractmethod
       async def generate(
           self,
           system_prompt: str,
           user_prompt: str,
           temperature: float,
           max_tokens: int
       ) -> dict:
           """Generate response from LLM"""
           pass
       
       @abstractmethod
       def validate_response(self, response: dict, schema: dict) -> bool:
           """Validate response against JSON schema"""
           pass
   ```

2. `app/services/llm/openai_provider.py`
   ```python
   class OpenAIProvider(BaseLLMProvider):
       def __init__(self, api_key: str, model_name: str):
           self.client = OpenAI(api_key=api_key)
           self.model_name = model_name
       
       async def generate(self, ...):
           # Implementation
   ```

3. `app/services/llm/gemini_provider.py`
   ```python
   class GeminiProvider(BaseLLMProvider):
       def __init__(self, api_key: str, model_name: str):
           # Use google-generativeai library
       
       async def generate(self, ...):
           # Implementation
   ```

4. `app/services/llm/mixtral_provider.py`
   ```python
   class MixtralProvider(BaseLLMProvider):
       def __init__(self, api_key: str, model_name: str):
           # Use Mistral API or Hugging Face
       
       async def generate(self, ...):
           # Implementation
   ```

#### Tests to Create:
- `tests/unit/test_openai_provider.py`
- `tests/unit/test_gemini_provider.py`
- `tests/unit/test_mixtral_provider.py`
- `tests/integration/test_providers.py` (with mocked API calls)

**Success Criteria:**
- ✅ Each provider can generate responses
- ✅ Error handling works (timeout, API errors)
- ✅ Response validation works
- ✅ All tests pass

---

### Task 3: LLM Router Service (Day 2-3)
**Priority:** HIGH  
**Dependencies:** Task 2

#### Files to Create:
1. `app/services/llm/llm_router.py`
   ```python
   class LLMRouter:
       def __init__(self, db: firestore.Client):
           self.db = db
           self.providers: Dict[str, BaseLLMProvider] = {}
       
       async def route_request(
           self,
           prompt_template_id: str,
           context: dict,
           preferred_provider: Optional[str] = None
       ) -> dict:
           """
           Route request to appropriate LLM provider
           1. Load prompt template from Firestore
           2. Select provider (preferred or by priority)
           3. Try primary, fallback to secondary on failure
           4. Log usage to Firestore
           5. Return response
           """
           pass
       
       async def _select_provider(self, preferred: Optional[str]) -> BaseLLMProvider:
           """Select provider based on priority and quota"""
           pass
       
       async def _log_usage(self, provider: str, tokens: int, cost: float):
           """Log usage to Firestore for quota tracking"""
           pass
   ```

#### Tests to Create:
- `tests/unit/test_llm_router.py`
  - Test provider selection logic
  - Test fallback mechanism
  - Test quota enforcement
  - Test usage logging

**Success Criteria:**
- ✅ Router selects correct provider
- ✅ Fallback works on provider failure
- ✅ Quota tracking works
- ✅ Usage logs saved to Firestore
- ✅ All tests pass

---

### Task 4: Prompt Management (Day 3)
**Priority:** MEDIUM  
**Dependencies:** Task 1

#### Files to Create:
1. `app/services/prompt_service.py`
   ```python
   class PromptService:
       def __init__(self, db: firestore.Client):
           self.db = db
       
       async def get_prompt_template(self, template_id: str) -> PromptTemplate:
           """Load prompt from Firestore"""
           pass
       
       async def render_prompt(
           self,
           template: PromptTemplate,
           context: dict
       ) -> tuple[str, str]:
           """Render system and user prompts with context"""
           pass
       
       async def create_prompt_template(self, template: PromptTemplate):
           """Save prompt to Firestore"""
           pass
   ```

#### Firestore Collections to Create:
```
admin/
  └── prompts/
      ├── chat_classification_v1/
      ├── meal_planning_v1/
      ├── workout_suggestion_v1/
      └── ...
```

#### Initial Prompts to Seed:
1. **Chat Classification** (migrate existing)
2. **Meal Planning** (new)
3. **Generic Chat** (existing fallback)

#### Tests to Create:
- `tests/unit/test_prompt_service.py`
  - Test prompt loading
  - Test template rendering
  - Test placeholder substitution

**Success Criteria:**
- ✅ Prompts load from Firestore
- ✅ Template rendering works
- ✅ Existing chat classification still works
- ✅ All tests pass

---

### Task 5: Integration with Existing Chat (Day 4)
**Priority:** HIGH (Regression Prevention)  
**Dependencies:** Tasks 3, 4

#### Files to Modify:
1. `app/routers/chat.py`
   - Replace direct OpenAI calls with `LLMRouter.route_request()`
   - Keep exact same API contract
   - Add fallback to old logic if router fails

2. `app/main.py`
   - Initialize LLMRouter on startup
   - Keep existing OpenAI client for backward compatibility

#### Changes:
```python
# OLD (current):
response = await openai_client.chat.completions.create(...)

# NEW (with router):
response = await llm_router.route_request(
    prompt_template_id="chat_classification_v1",
    context={"user_message": message_content},
    preferred_provider="openai"  # Default to OpenAI for compatibility
)
```

#### Regression Tests:
- `tests/regression/test_chat_functionality.py`
  - Test chat classification still works
  - Test meal logging still works
  - Test workout logging still works
  - Test generic chat still works

**Success Criteria:**
- ✅ All existing chat features work EXACTLY as before
- ✅ Response format unchanged
- ✅ No increase in response time
- ✅ All regression tests pass

---

### Task 6: Admin Configuration UI (Day 5) [OPTIONAL for Phase 1]
**Priority:** LOW  
**Dependencies:** Tasks 1-4

#### Files to Create:
1. `app/routers/admin_llm_config.py`
   - CRUD endpoints for LLM providers
   - CRUD endpoints for prompt templates
   - Usage analytics endpoint

#### Endpoints:
```python
POST   /admin/llm/providers          # Add provider
GET    /admin/llm/providers          # List providers
PUT    /admin/llm/providers/{id}     # Update provider
DELETE /admin/llm/providers/{id}     # Deactivate provider

POST   /admin/prompts                # Create prompt template
GET    /admin/prompts                # List templates
GET    /admin/prompts/{id}           # Get template
PUT    /admin/prompts/{id}           # Update template

GET    /admin/llm/usage              # Get usage stats
```

**Success Criteria:**
- ✅ Admin can add/edit providers
- ✅ Admin can update prompts without code deployment
- ✅ Usage analytics visible

---

### Task 7: Documentation & Deployment (Day 5-6)
**Priority:** HIGH

#### Documents to Create:
1. `docs/LLM_ROUTER_GUIDE.md`
   - How to add a new provider
   - How to create a prompt template
   - How to use the router

2. `docs/PROVIDER_SETUP.md`
   - API key setup for OpenAI
   - API key setup for Gemini
   - API key setup for Mixtral

3. `docs/MIGRATION_GUIDE.md`
   - How to migrate existing LLM calls to router
   - Breaking changes (should be none)

#### Deployment Checklist:
- [ ] All tests passing (unit + integration + regression)
- [ ] Performance benchmarks meet requirements
- [ ] Error handling tested
- [ ] Logging verified
- [ ] Documentation complete
- [ ] Code review done
- [ ] Firestore seed data ready

---

## 🧪 Testing Strategy

### 1. Unit Tests (70% coverage minimum)
```bash
pytest tests/unit/ -v --cov=app/services/llm --cov=app/models
```

### 2. Integration Tests
```bash
pytest tests/integration/ -v
```

Test scenarios:
- Provider selection logic
- Fallback mechanism
- Quota enforcement
- Prompt rendering
- End-to-end LLM call

### 3. Regression Tests (CRITICAL)
```bash
pytest tests/regression/ -v
```

Test ALL existing features:
- ✅ Chat classification
- ✅ Meal logging via chat
- ✅ Workout logging via chat
- ✅ Generic chat responses
- ✅ Task creation
- ✅ Timeline updates

### 4. Performance Tests
```bash
pytest tests/performance/ -v
```

Benchmarks:
- LLM response time < 5s
- Router overhead < 100ms
- Firestore queries < 500ms

---

## 🚨 Regression Prevention Checklist

### Before ANY commit:
- [ ] Run `pytest tests/regression/` - ALL must pass
- [ ] Test chat classification manually
- [ ] Test meal logging via chat manually
- [ ] Check backend logs for errors
- [ ] Verify API response formats unchanged

### Before merging to main:
- [ ] Full test suite passes
- [ ] Manual testing of all features
- [ ] Performance benchmarks met
- [ ] Code review approved
- [ ] Documentation updated

---

## 📁 File Structure

```
app/
├── models/
│   ├── llm_config.py          [NEW]
│   └── prompt_template.py     [NEW]
├── services/
│   └── llm/
│       ├── __init__.py        [NEW]
│       ├── base_provider.py   [NEW]
│       ├── openai_provider.py [NEW]
│       ├── gemini_provider.py [NEW]
│       ├── mixtral_provider.py[NEW]
│       ├── llm_router.py      [NEW]
│       └── provider_manager.py[NEW]
│   ├── prompt_service.py      [NEW]
└── routers/
    ├── chat.py                [MODIFY]
    └── admin_llm_config.py    [NEW]

tests/
├── unit/
│   ├── test_llm_config.py     [NEW]
│   ├── test_providers.py      [NEW]
│   ├── test_llm_router.py     [NEW]
│   └── test_prompt_service.py [NEW]
├── integration/
│   └── test_llm_integration.py[NEW]
├── regression/
│   └── test_chat_functionality.py [NEW]
└── performance/
    └── test_llm_performance.py[NEW]

docs/
├── LLM_ROUTER_GUIDE.md        [NEW]
├── PROVIDER_SETUP.md          [NEW]
└── MIGRATION_GUIDE.md         [NEW]
```

---

## 🔄 Development Workflow

### Day-by-Day Plan:

**Day 1:** Tasks 1-2 (Models + Provider Clients)
- Create data models
- Create base provider interface
- Implement OpenAI provider (easiest first)
- Write unit tests
- Commit: `feat(llm): add provider models and OpenAI implementation`

**Day 2:** Task 2-3 (More Providers + Router)
- Implement Gemini provider
- Implement Mixtral provider
- Create LLM Router service
- Write unit tests
- Commit: `feat(llm): add Gemini/Mixtral providers and router`

**Day 3:** Task 4 (Prompt Management)
- Create prompt service
- Create Firestore seed data
- Test prompt loading and rendering
- Commit: `feat(llm): add prompt management system`

**Day 4:** Task 5 (Integration)
- Integrate router with existing chat
- Run regression tests
- Fix any issues
- Commit: `feat(llm): integrate router with chat (backward compatible)`

**Day 5:** Task 6-7 (Admin UI + Docs)
- Create admin endpoints
- Write documentation
- Final testing
- Commit: `feat(llm): add admin config and documentation`

**Day 6:** Testing & Polish
- Full regression testing
- Performance testing
- Bug fixes
- Code review
- Commit: `test(llm): comprehensive test coverage and benchmarks`

**Day 7:** Merge & Deploy
- Final review
- Merge to main
- Deploy to staging
- Smoke test
- Deploy to production

---

## 🎯 Definition of Done

Phase 1 is complete when:
1. ✅ All tasks (1-5) complete
2. ✅ All tests passing (unit + integration + regression)
3. ✅ Zero regressions in existing features
4. ✅ Documentation complete
5. ✅ Code reviewed and approved
6. ✅ Performance benchmarks met
7. ✅ Deployed to staging successfully
8. ✅ Manual smoke testing passed

---

## 🚀 Next: Phase 2

Once Phase 1 is complete and stable:
- Phase 2: Agentic Meal Planning Core
- Use the new LLM Router for meal plan generation
- Integrate with user profiles
- Add explainability

---

## 📞 Contacts & Resources

**Dependencies:**
- OpenAI API: https://platform.openai.com/docs
- Google Gemini API: https://ai.google.dev/docs
- Mistral/Mixtral API: https://docs.mistral.ai/

**Testing:**
- Pytest: https://docs.pytest.org/
- Coverage: https://coverage.readthedocs.io/

---

**Status:** 🟢 Ready to start  
**Last Updated:** November 6, 2025

