from fastapi import FastAPI, Request, HTTPException
from fastapi import Body, Depends
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
import json
import time
import logging
import re
import asyncio  # ⚡ PHASE 1: For fire-and-forget async tasks
from datetime import datetime, timezone, timedelta
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from dotenv import load_dotenv
import os
import sys
from google.cloud import firestore
from app.services.auth import get_current_user

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()
dotenv_local_path = os.path.join(os.getcwd(), '.env.local')
if os.path.exists(dotenv_local_path):
    load_dotenv(dotenv_local_path, override=True)

# Initialize configuration service
from app.core.config_manager import get_settings
settings = get_settings()

# ⚡ PERFORMANCE: Global Firestore client (reuse connection, don't create per request)
# Best practice: Instantiate once per process, reuse for all requests
_firestore_client = None

def get_firestore_client():
    """
    Get or create global Firestore client (singleton pattern).
    Reusing connection saves ~400-600ms per request.
    """
    global _firestore_client
    if _firestore_client is None:
        _firestore_client = firestore.Client()
        logger.info("✅ Firestore client initialized (global singleton)")
    return _firestore_client

app = FastAPI(title="AI Fitness & Task Tracker API", version="0.1.0")

# Add error handler middleware
from app.utils.error_handler import ErrorHandlerMiddleware
app.add_middleware(ErrorHandlerMiddleware)

# CORS configuration using settings
logger.info(f"🔒 [CORS] Configuring CORS for {settings.environment} environment")
logger.info(f"🔒 [CORS] Allowed origins: {settings.cors_origins_list}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"status": "ok", "service": "ai-fitness-task-tracker", "version": "0.1.0"}

# Routers
from app.routers import (
    users_router,
    tasks_router,
    fitness_logs_router,
    auth_router,
    fitness_router,
    admin_auth_router,
    admin_config_router,
    profile_router,
)  # noqa: E402
from app.routers.feedback_production import router as feedback_router  # noqa: E402
from app.routers.timeline import router as timeline_router  # noqa: E402

# Import models/services for persistence
from app.services import database as dbsvc  # noqa: E402
from app.models.fitness_log import FitnessLog, FitnessLogType  # noqa: E402
from app.models.task import Task, TaskPriority, TaskStatus  # noqa: E402
from app.models.user import User  # noqa: E402
from app.services.nutrition_db import get_nutrition_info, estimate_meal_nutrition  # noqa: E402
from app.services.chat_history_service import get_chat_history_service  # noqa: E402

# Initialize LLM Router for agentic AI (Phase 1)
_llm_router = None
try:
    from app.services.llm.llm_router import LLMRouter
    from app.models.llm_config import LLMRequest, LLMConfig
    
    # Initialize router
    db_client = dbsvc.get_firestore_client()
    _llm_router = LLMRouter(db=db_client)
    
    # Ensure default OpenAI config exists (synchronous at startup)
    try:
        configs_ref = db_client.collection('llm_configs')
        docs = list(configs_ref.limit(1).stream())
        
        print(f"🔍 [AGENTIC AI] Found {len(docs)} existing LLM configs in Firestore")
        
        if len(docs) == 0:
            print("⚠️  [AGENTIC AI] No LLM configs found, creating default OpenAI config...")
            api_key = os.getenv('OPENAI_API_KEY', '')
            print(f"🔍 [AGENTIC AI] OpenAI API key: {api_key[:10] if api_key else 'NOT SET'}...")
            
            if not api_key:
                print("⚠️  [AGENTIC AI] OPENAI_API_KEY not set! Router will not work.")
            else:
                default_config = LLMConfig(
                    provider='openai',
                    model_name='gpt-4o-mini',
                    api_key=api_key,
                    priority=1,
                    is_active=True,
                    temperature=0.7,
                    max_tokens=4000,
                    cost_per_1k_input_tokens=0.00015,
                    cost_per_1k_output_tokens=0.0006
                )
                
                print(f"🔍 [AGENTIC AI] Creating config document: openai_gpt4o_mini")
                doc_ref = configs_ref.document('openai_gpt4o_mini')
                doc_ref.set(default_config.model_dump())
                print("✅ [AGENTIC AI] Created default OpenAI config successfully")
                
                # Verify it was saved
                verify = doc_ref.get()
                if verify.exists:
                    print(f"✅ [AGENTIC AI] Verified config saved: provider={verify.to_dict().get('provider')}")
                else:
                    print("❌ [AGENTIC AI] Config not found after save!")
        else:
            print(f"✅ [AGENTIC AI] Using existing LLM configs")
            for doc in docs:
                data = doc.to_dict()
                print(f"   - {doc.id}: {data.get('provider')}/{data.get('model_name')} (active={data.get('is_active')})")
    except Exception as cfg_error:
        print(f"⚠️  [AGENTIC AI] Failed to create default config: {cfg_error}")
        import traceback
        traceback.print_exc()
    
    print("✅ [AGENTIC AI] LLM Router initialized successfully")
except Exception as e:
    print(f"⚠️ [AGENTIC AI] LLM Router initialization failed (falling back to direct OpenAI): {e}")
    _llm_router = None

app.include_router(users_router)
app.include_router(tasks_router)
app.include_router(fitness_logs_router)
app.include_router(auth_router)
app.include_router(fitness_router)
app.include_router(admin_auth_router)
app.include_router(admin_config_router)
from app.routers.admin_feedback import router as admin_feedback_router
app.include_router(admin_feedback_router)
from app.routers.admin import router as admin_llm_router
app.include_router(admin_llm_router)
app.include_router(profile_router)
app.include_router(feedback_router)
app.include_router(timeline_router)

# Meal management router
from app.routers.meals import router as meals_router
app.include_router(meals_router)

# Fasting & Meal Planning routers
from app.routers.fasting import router as fasting_router
from app.routers.meal_planning import router as meal_planning_router
app.include_router(fasting_router)
app.include_router(meal_planning_router)

# AI Insights endpoint
@app.get("/insights")
async def get_ai_insights(current_user: User = Depends(get_current_user)):
    """Get AI-powered insights for the user"""
    try:
        logger.info(f"Fetching insights for user: {current_user.user_id}")
        
        from app.services.ai_insights_service import get_insights_service
        from app.services import database as db_module
        from google.cloud import firestore
        import os
        
        insights_service = get_insights_service()
        
        # Get user's profile for goals
        logger.info(f"Fetching profile for insights: {current_user.user_id}")
        project = os.getenv("GOOGLE_CLOUD_PROJECT", "productivityai-mvp")
        db = firestore.Client(project=project)
        profile_doc = db.collection("user_profiles").document(current_user.user_id).get()
        
        if not profile_doc.exists:
            logger.warning(f"No profile found for insights: {current_user.user_id}")
            return {"insights": [], "summary": "Complete your profile to get personalized insights!"}
        
        profile = profile_doc.to_dict()
        
        # Get today's stats
        from datetime import datetime, timezone
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        logger.info(f"Fetching logs for insights: {current_user.user_id}")
        logs = db_module.list_fitness_logs_by_user(
            user_id=current_user.user_id,
            start_ts=today_start,
            log_type=None,
            limit=100
        )
        logger.info(f"Found {len(logs)} logs for insights")
    except Exception as e:
        logger.error(f"Error in get_ai_insights for user {current_user.user_id}: {str(e)}", exc_info=True)
        return {"insights": [], "summary": "Unable to generate insights at this time. Please try again later."}
    
    # Calculate totals
    calories_consumed = 0
    calories_burned = 0
    protein_g = 0.0
    carbs_g = 0.0
    fat_g = 0.0
    
    for log in logs:
        if log.log_type.value == "meal":
            calories_consumed += log.calories or 0
            if log.ai_parsed_data:
                protein_g += log.ai_parsed_data.get("protein_g", 0)
                carbs_g += log.ai_parsed_data.get("carbs_g", 0)
                fat_g += log.ai_parsed_data.get("fat_g", 0)
        elif log.log_type.value == "workout":
            calories_burned += log.calories or 0
    
    # Get goals from profile (profile is a dict)
    goals = profile.get("daily_goals", {})
    calories_goal = goals.get("calories", 2000)
    protein_goal = goals.get("protein_g", 150)
    carbs_goal = goals.get("carbs_g", 200)
    fat_goal = goals.get("fat_g", 65)
    
    # Calculate streak (simplified - just check if logged today)
    streak_days = 1 if len(logs) > 0 else 0
    
    # Get user's fitness goal
    user_goal = "lose_weight"  # Default
    fitness_goal = profile.get('fitness_goal', 'lose_weight')
    goal_map = {
        "lose_weight": "lose_weight",
        "gain_muscle": "gain_weight",
        "maintain": "maintain"
    }
    user_goal = goal_map.get(fitness_goal, "lose_weight")
    
    # Generate insights
    insights = insights_service.generate_insights(
        calories_consumed=calories_consumed,
        calories_goal=calories_goal,
        calories_burned=calories_burned,
        protein_g=protein_g,
        protein_goal=protein_goal,
        carbs_g=carbs_g,
        carbs_goal=carbs_goal,
        fat_g=fat_g,
        fat_goal=fat_goal,
        streak_days=streak_days,
        user_goal=user_goal
    )
    
    # Generate summary
    summary = insights_service.generate_daily_summary(
        calories_consumed=calories_consumed,
        calories_goal=calories_goal,
        protein_g=protein_g,
        protein_goal=protein_goal,
        user_goal=user_goal
    )
    
    return {
        "insights": [insight.to_dict() for insight in insights],
        "summary": summary,
        "stats": {
            "calories_consumed": calories_consumed,
            "calories_goal": calories_goal,
            "calories_burned": calories_burned,
            "protein_g": protein_g,
            "protein_goal": protein_goal,
            "streak_days": streak_days
        }
    }

# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "AI Productivity App",
        "version": "1.0.0",
        "timestamp": time.time()
    }

# Root endpoint
@app.get("/")
def root():
    """Root endpoint with API info"""
    return {
        "message": "AI Productivity App API",
        "version": "1.0.0",
        "docs": "/docs",
        "admin": "/admin",
        "health": "/health"
    }

# Static admin UI (optional): mount at /admin
try:
    from fastapi.staticfiles import StaticFiles

    app.mount(
        "/admin",
        StaticFiles(directory=os.path.join(os.getcwd(), "app/static/admin"), html=True),
        name="admin-ui",
    )
except Exception:
    pass

# Temporary chat stub so the app UI can respond
class ChatRequest(BaseModel):
    user_input: str
    type: Optional[str] = None  # "auto" by default
    client_generated_id: Optional[str] = None  # 🔑 For optimistic UI matching


class ChatItem(BaseModel):
    category: str  # meal | workout | supplement | task | reminder | other
    summary: str
    data: dict


class ChatResponse(BaseModel):
    items: List[ChatItem]
    original: str
    message: str  # Keep for backward compatibility
    
    # ✨ NEW FIELDS (Expandable Chat):
    summary: Optional[str] = None          # "🍌 1 banana logged! 105 kcal"
    suggestion: Optional[str] = None       # "Great potassium source!"
    details: Optional[Dict[str, Any]] = None  # Structured breakdown
    expandable: bool = False               # Flag for frontend
    
    # 🧠 PHASE 2 FIELDS (Explainable AI):
    confidence_score: Optional[float] = None          # 0.0 - 1.0
    confidence_level: Optional[str] = None            # "high", "medium", "low"
    confidence_factors: Optional[Dict[str, float]] = None  # Breakdown
    explanation: Optional[Dict[str, Any]] = None      # Why AI made this decision
    alternatives: Optional[List[Dict[str, Any]]] = None  # 2-3 alternative interpretations
    
    # 🎨 UX FIX: Message ID for feedback matching
    message_id: Optional[str] = None                  # Unique ID for this message
    
    needs_clarification: bool = False
    clarification_question: Optional[str] = None


def _get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    try:
        from openai import OpenAI
        return OpenAI(api_key=api_key)
    except Exception:
        return None


async def _classify_with_llm(text: str, user_id: Optional[str] = None) -> tuple[List[ChatItem], bool, Optional[str]]:
    # Get user's local time for meal classification
    user_local_time = None
    user_timezone = "UTC"
    if user_id:
        try:
            from services.timezone_service import get_user_local_time, get_user_timezone
            user_local_time = get_user_local_time(user_id)
            user_timezone = get_user_timezone(user_id)
        except Exception as e:
            print(f"Error getting user timezone: {e}")
    
    client = _get_openai_client()
    if not client:
        # Fallback heuristic with nutrition lookup
        lower = text.lower()
        items: List[ChatItem] = []
        if any(k in lower for k in ["breakfast", "lunch", "dinner", "calorie", "kcal", "ate", "meal", "egg", "chicken", "rice"]):
            # Try to get nutrition info
            nutrition = get_nutrition_info(text)
            if nutrition:
                items.append(ChatItem(
                    category="meal",
                    summary=f"{nutrition['food']} logged ({nutrition['calories']} cal)",
                    data=nutrition
                ))
            else:
                items.append(ChatItem(category="meal", summary="Meal logged", data={"meal": text, "calories": 200}))
        elif any(k in lower for k in ["workout", "gym", "run", "walk", "yoga", "swim"]):
            items.append(ChatItem(category="workout", summary="Workout logged", data={"workout": text}))
        elif any(k in lower for k in ["call", "remind", "at "]):
            items.append(ChatItem(category="reminder", summary="Reminder", data={"reminder": text}))
        else:
            items.append(ChatItem(category="task", summary="Task created", data={"title": text}))
        return items, False, None

    # Load admin-provided template if present
    template_from_admin: Optional[str] = None
    try:
        from app.services.config_service import get_active_config  # lazy import
        cfg = get_active_config()
        if cfg and getattr(cfg, "llm_prompt_template", None):
            template_from_admin = cfg.llm_prompt_template  # type: ignore[attr-defined]
    except Exception:
        template_from_admin = None

    # Add user timezone context to prompt
    timezone_context = ""
    if user_local_time:
        time_str = user_local_time.strftime('%Y-%m-%d %H:%M:%S')
        timezone_context = "\n\n**USER CONTEXT:**\n- Current time in user's timezone (" + user_timezone + "): " + time_str + "\n- Current hour: " + str(user_local_time.hour) + "\n- Use this time for meal type classification if user doesn't specify!\n"
    
    # OPTIMIZED: Shorter prompt to reduce token count and speed up response
    default_prompt = '''
You are a fitness assistant. Parse user input and extract items as JSON.
''' + timezone_context + '''
Categories: meal, workout, water, supplement, task, question

⚠️ IMPORTANT: Distinguish between:
- LOGGING: "apple", "2 eggs", "ran 5k" → Use meal/workout/water/supplement categories
- TASK CREATION: "remind me to X", "call mom at 3pm" → Use task category
- QUESTIONS/CHAT: "I am frustrated", "how does this work", "why X" → Use question category (NO logging!)

Parse input, extract items as JSON. Correct typos, make smart assumptions for portions/calories.

Rules:
- meal_type: If user says "for breakfast/lunch/dinner", use that (confidence=1.0). Otherwise infer from time.
- Split multi-item inputs into separate array items
- Water: 1 glass=250ml, 1 litre=1000ml, 1 liter=1000ml, 1l=1000ml, calories=0. ALWAYS return quantity_ml in data.
- Supplements: 0 calories (vitamins, pills, tablets have no caloric value)
- Questions/conversational messages: Use category="question", no logging data

JSON format:
{"items":[{"category":"meal|workout|water|supplement|task|question","summary":"friendly text","data":{...}}],"needs_clarification":false}

Example 1 (logging): "2 eggs for breakfast" → {"items":[{"category":"meal","summary":"2 eggs for breakfast (140kcal)","data":{"item":"eggs","quantity":"2","meal_type":"breakfast","calories":140,"protein_g":12,"carbs_g":1,"fat_g":10}}],"needs_clarification":false}
Example 2 (question): "I am frustrated" → {"items":[{"category":"question","summary":"User expressing frustration","data":{"type":"emotion"}}],"needs_clarification":false}
'''

    system_prompt = template_from_admin or default_prompt
    
    # Add current time context for meal type inference
    from datetime import datetime
    current_time = datetime.now()
    time_context = f"Current time: {current_time.strftime('%I:%M %p')} ({current_time.strftime('%A')})"
    user_prompt = f"{time_context}\nInput: {text}"
    
    try:
        # Try using LLM Router first (Phase 1 Agentic AI)
        if _llm_router:
            try:
                print("🤖 [AGENTIC AI] Using LLM Router for chat classification")
                llm_request = LLMRequest(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    temperature=0.2,
                    max_tokens=4000,
                    response_format="json",
                    user_id=user_id,
                    request_type="chat_classification"
                )
                llm_response = await _llm_router.route_request(llm_request)
                content = llm_response.content
                print(f"✅ [AGENTIC AI] Router success! Provider: {llm_response.provider_used}, Tokens: {llm_response.tokens_used}, Time: {llm_response.response_time_ms}ms")
            except Exception as router_error:
                print(f"⚠️ [AGENTIC AI] Router failed, falling back to direct OpenAI: {router_error}")
                # Fallback to direct OpenAI call
                res = client.chat.completions.create(
                    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.2,
                    response_format={"type": "json_object"},
                )
                content = res.choices[0].message.content or "{}"
        else:
            # LLM Router not available, use direct OpenAI
            res = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
                response_format={"type": "json_object"},
            )
            content = res.choices[0].message.content or "{}"
        
        data = json.loads(content)
        items_json = data.get("items") or []
        items: List[ChatItem] = []
        
        # Log confidence scores for analytics
        low_confidence_items = []
        for it in items_json:
            item_data = it.get("data") or {}
            conf_category = item_data.get("confidence_category", 1.0)
            conf_meal_type = item_data.get("confidence_meal_type", 1.0)
            conf_macros = item_data.get("confidence_macros", 1.0)
            
            # Track low confidence items for analytics (only log, don't affect clarification)
            if conf_category < 0.8 or conf_meal_type < 0.8 or conf_macros < 0.6:
                low_confidence_items.append({
                    "item": item_data.get("item"),
                    "conf_category": conf_category,
                    "conf_meal_type": conf_meal_type,
                    "conf_macros": conf_macros
                })
            
            items.append(ChatItem(
                category=it.get("category", "other"),
                summary=it.get("summary", ""),
                data=item_data
            ))
        
        if low_confidence_items:
            print(f"⚠️  Low confidence items detected: {low_confidence_items}")
        
        if not items:
            items = [ChatItem(category="task", summary="Task created", data={"title": text})]
        
        # Handle clarification_questions (plural) - join them if multiple
        clarification_questions = data.get("clarification_questions", [])
        clarification_question = None
        if clarification_questions:
            # Join multiple questions with newlines
            clarification_question = "\n".join(clarification_questions)
        
        return items, data.get("needs_clarification", False), clarification_question
    except Exception as e:
        print(f"LLM classification error: {e}")
        return [ChatItem(category="task", summary="Task created", data={"title": text})], False, None


async def _handle_fasting_commands(text: str, user_id: str, chat_history) -> Optional[ChatResponse]:
    """
    Handle fasting-related chat commands
    
    Supported commands:
    - start fast / begin fast / start fasting
    - stop fast / end fast / stop fasting / break fast
    - fast status / fasting status / how long have i been fasting
    """
    from app.services.fasting_service import get_fasting_service
    from datetime import datetime, timezone
    
    fasting_service = get_fasting_service()
    
    # Command patterns
    start_patterns = ['start fast', 'begin fast', 'start fasting', 'begin fasting', 'starting fast']
    stop_patterns = ['stop fast', 'end fast', 'stop fasting', 'end fasting', 'break fast', 'breaking fast']
    status_patterns = ['fast status', 'fasting status', 'how long', 'am i fasting', 'current fast']
    
    # Check for start fast command
    if any(pattern in text for pattern in start_patterns):
        try:
            # Check if already fasting
            current_session = await fasting_service.get_current_session(user_id)
            if current_session:
                response_msg = f"⏱️ You're already fasting! Started {_format_time_ago(current_session.start_time)}. Keep going! 💪"
            else:
                # Start new fasting session (default 16:8 protocol)
                session = await fasting_service.start_fasting(user_id, protocol="16:8", target_hours=16)
                response_msg = f"🎉 Fasting started! Your 16-hour fast is underway. You're in the anabolic state. I'll check in with you as you progress! 💪"
            
            # Save AI response to history
            chat_history.save_message(user_id, 'assistant', response_msg, {
                'category': 'fasting_command',
                'command': 'start'
            })
            
            return ChatResponse(
                items=[{
                    "category": "fasting",
                    "summary": "Fasting session started",
                    "data": {"command": "start", "protocol": "16:8"}
                }],
                original=text,
                message=response_msg,
                needs_clarification=False
            )
        except Exception as e:
            print(f"❌ [FASTING COMMAND] Error starting fast: {e}")
            error_msg = f"Sorry, I couldn't start your fast. Please try again or use the Plan tab."
            chat_history.save_message(user_id, 'assistant', error_msg)
            return ChatResponse(
                items=[],
                original=text,
                message=error_msg,
                needs_clarification=False
            )
    
    # Check for stop fast command
    elif any(pattern in text for pattern in stop_patterns):
        try:
            current_session = await fasting_service.get_current_session(user_id)
            if not current_session:
                response_msg = "You're not currently fasting. Start a fast anytime by saying 'start fast'! 🍽️"
            else:
                # End the fasting session
                ended_session = await fasting_service.end_fasting(user_id, current_session.session_id)
                duration_hours = (ended_session.end_time - ended_session.start_time).total_seconds() / 3600
                response_msg = f"✅ Fast completed! You fasted for {duration_hours:.1f} hours. Great work! 🎉"
            
            # Save AI response to history
            chat_history.save_message(user_id, 'assistant', response_msg, {
                'category': 'fasting_command',
                'command': 'stop'
            })
            
            return ChatResponse(
                items=[{
                    "category": "fasting",
                    "summary": "Fasting session ended",
                    "data": {"command": "stop"}
                }],
                original=text,
                message=response_msg,
                needs_clarification=False
            )
        except Exception as e:
            print(f"❌ [FASTING COMMAND] Error stopping fast: {e}")
            error_msg = f"Sorry, I couldn't end your fast. Please try again or use the Plan tab."
            chat_history.save_message(user_id, 'assistant', error_msg)
            return ChatResponse(
                items=[],
                original=text,
                message=error_msg,
                needs_clarification=False
            )
    
    # Check for status command
    elif any(pattern in text for pattern in status_patterns):
        try:
            current_session = await fasting_service.get_current_session(user_id)
            if not current_session:
                response_msg = "You're not currently fasting. Ready to start? Just say 'start fast'! 🍽️"
            else:
                elapsed_hours = (datetime.now(timezone.utc) - current_session.start_time).total_seconds() / 3600
                target_hours = current_session.target_hours
                progress_pct = (elapsed_hours / target_hours * 100) if target_hours > 0 else 0
                
                # Determine metabolic stage
                if elapsed_hours < 4:
                    stage = "Anabolic State 🟢"
                    stage_desc = "Your body is digesting and absorbing nutrients"
                elif elapsed_hours < 16:
                    stage = "Catabolic State 🟡"
                    stage_desc = "Your body is breaking down glycogen stores"
                elif elapsed_hours < 24:
                    stage = "Fat Burning Zone 🔵"
                    stage_desc = "Your body is burning fat for energy!"
                elif elapsed_hours < 48:
                    stage = "Ketosis 🟣"
                    stage_desc = "Your body is in ketosis - deep fat burning!"
                else:
                    stage = "Deep Ketosis 🌟"
                    stage_desc = "Maximum autophagy and cellular repair!"
                
                response_msg = (
                    f"⏱️ **Fasting Status**\n\n"
                    f"• Started: {_format_time_ago(current_session.start_time)}\n"
                    f"• Duration: {elapsed_hours:.1f} / {target_hours} hours ({progress_pct:.0f}%)\n"
                    f"• Stage: {stage}\n"
                    f"• {stage_desc}\n\n"
                    f"Keep it up! You're doing great! 💪"
                )
            
            # Save AI response to history
            chat_history.save_message(user_id, 'assistant', response_msg, {
                'category': 'fasting_command',
                'command': 'status'
            })
            
            return ChatResponse(
                items=[{
                    "category": "fasting",
                    "summary": "Fasting status",
                    "data": {"command": "status"}
                }],
                original=text,
                message=response_msg,
                needs_clarification=False
            )
        except Exception as e:
            print(f"❌ [FASTING COMMAND] Error getting fast status: {e}")
            error_msg = f"Sorry, I couldn't get your fasting status. Please try again."
            chat_history.save_message(user_id, 'assistant', error_msg)
            return ChatResponse(
                items=[],
                original=text,
                message=error_msg,
                needs_clarification=False
            )
    
    # Not a fasting command
    return None


def _format_time_ago(dt: datetime) -> str:
    """Format datetime as 'X hours ago' or 'X minutes ago'"""
    now = datetime.now(timezone.utc)
    delta = now - dt
    
    hours = delta.total_seconds() / 3600
    if hours >= 1:
        return f"{int(hours)} hour{'s' if int(hours) != 1 else ''} ago"
    else:
        minutes = delta.total_seconds() / 60
        return f"{int(minutes)} minute{'s' if int(minutes) != 1 else ''} ago"


# ⚡ PHASE 1: FAST-PATH HELPERS (bypass LLM for instant responses)

# 🏆 TOP 100 COMMON FOODS (in-memory cache for instant lookup)
COMMON_FOODS_CACHE = {
    # Format: "food_name": {"kcal_per_unit": X, "protein_g": Y, "carbs_g": Z, "fat_g": W, "unit": "piece/100g"}
    "egg": {"kcal_per_unit": 70, "protein_g": 6, "carbs_g": 0.5, "fat_g": 5, "unit": "piece", "serving_size": 1},
    "eggs": {"kcal_per_unit": 70, "protein_g": 6, "carbs_g": 0.5, "fat_g": 5, "unit": "piece", "serving_size": 1},
    "banana": {"kcal_per_unit": 105, "protein_g": 1.3, "carbs_g": 27, "fat_g": 0.3, "unit": "piece", "serving_size": 1},
    "apple": {"kcal_per_unit": 95, "protein_g": 0.5, "carbs_g": 25, "fat_g": 0.3, "unit": "piece", "serving_size": 1},
    "chicken breast": {"kcal_per_unit": 165, "protein_g": 31, "carbs_g": 0, "fat_g": 3.6, "unit": "100g", "serving_size": 100},
    "rice": {"kcal_per_unit": 130, "protein_g": 2.7, "carbs_g": 28, "fat_g": 0.3, "unit": "100g", "serving_size": 100},
    "bread": {"kcal_per_unit": 80, "protein_g": 3, "carbs_g": 15, "fat_g": 1, "unit": "slice", "serving_size": 1},
    "milk": {"kcal_per_unit": 42, "protein_g": 3.4, "carbs_g": 5, "fat_g": 1, "unit": "100ml", "serving_size": 100},
    "yogurt": {"kcal_per_unit": 59, "protein_g": 10, "carbs_g": 3.6, "fat_g": 0.4, "unit": "100g", "serving_size": 100},
    "oats": {"kcal_per_unit": 389, "protein_g": 16.9, "carbs_g": 66, "fat_g": 6.9, "unit": "100g", "serving_size": 50},
    "almonds": {"kcal_per_unit": 579, "protein_g": 21, "carbs_g": 22, "fat_g": 50, "unit": "100g", "serving_size": 30},
    "orange": {"kcal_per_unit": 62, "protein_g": 1.2, "carbs_g": 15, "fat_g": 0.2, "unit": "piece", "serving_size": 1},
    "tomato": {"kcal_per_unit": 18, "protein_g": 0.9, "carbs_g": 3.9, "fat_g": 0.2, "unit": "piece", "serving_size": 1},
    "potato": {"kcal_per_unit": 77, "protein_g": 2, "carbs_g": 17, "fat_g": 0.1, "unit": "100g", "serving_size": 150},
    "salmon": {"kcal_per_unit": 208, "protein_g": 20, "carbs_g": 0, "fat_g": 13, "unit": "100g", "serving_size": 100},
    "tuna": {"kcal_per_unit": 132, "protein_g": 28, "carbs_g": 0, "fat_g": 1.3, "unit": "100g", "serving_size": 100},
    "cheese": {"kcal_per_unit": 402, "protein_g": 25, "carbs_g": 1.3, "fat_g": 33, "unit": "100g", "serving_size": 30},
    "butter": {"kcal_per_unit": 717, "protein_g": 0.9, "carbs_g": 0.1, "fat_g": 81, "unit": "100g", "serving_size": 10},
    "pasta": {"kcal_per_unit": 131, "protein_g": 5, "carbs_g": 25, "fat_g": 1.1, "unit": "100g", "serving_size": 100},
    "avocado": {"kcal_per_unit": 160, "protein_g": 2, "carbs_g": 8.5, "fat_g": 15, "unit": "piece", "serving_size": 1},
}

async def _save_food_log_async(user_id: str, log_data: dict, client_generated_id: str = None):
    """
    Helper to save food log asynchronously using FitnessLog model
    ✅ CRITICAL FIX: Save to fitness_logs (same as LLM path) so timeline shows it
    🚀 REDIS CACHE: Invalidates timeline/dashboard cache after save
    """
    try:
        from app.models.fitness_log import FitnessLog, FitnessLogType
        from app.services.database import create_fitness_log
        from app.services.cache_service import cache_service
        import uuid
        
        # Create FitnessLog object (same format as LLM path)
        fitness_log = FitnessLog(
            log_id=str(uuid.uuid4()),
            user_id=user_id,
            log_type=FitnessLogType.meal,
            content=f"{log_data['food_name']} x{log_data['quantity']} {log_data['unit']}",
            timestamp=log_data['timestamp'],
            calories=log_data['calories'],
            ai_parsed_data={
                "meal_type": log_data['meal_type'],
                "food_name": log_data['food_name'],
                "quantity": log_data['quantity'],
                "unit": log_data['unit'],
                "protein_g": log_data['protein_g'],
                "carbs_g": log_data['carbs_g'],
                "fat_g": log_data['fat_g'],
                "source": "fast_path",  # Track that this was fast-path
                "items": [f"{log_data['quantity']} {log_data['food_name']}"],  # ✅ FIX: Add items array for frontend
            },
            client_generated_id=client_generated_id  # 🔑 Store for matching
        )
        
        # Save using same method as LLM path (ensures consistency)
        await asyncio.to_thread(create_fitness_log, fitness_log)
        print(f"✅ [FAST-PATH] Food log saved to fitness_logs: {log_data['food_name']} x{log_data['quantity']}")
        
        # ⏱️  FIRESTORE INDEXING: Wait 1 second for Firestore to index the new document
        # Without this, Timeline queries won't return the newly saved log
        await asyncio.sleep(1.0)
        print(f"⏱️  [FAST-PATH] Waited 1s for Firestore indexing")
        
        # 🚀 REDIS CACHE: Invalidate timeline and dashboard cache AFTER indexing delay
        # This prevents stale cache hits while Firestore is indexing
        cache_service.invalidate_timeline(user_id)
        cache_service.invalidate_dashboard(user_id)
        print(f"🗑️  [FAST-PATH] Cache invalidated AFTER indexing delay for user {user_id}")
        
        # ✅ NO DELAY NEEDED: Frontend will pull-to-refresh to get latest data
        print(f"✅ [FAST-PATH] Food log saved, frontend will refresh on demand")
        
    except Exception as e:
        print(f"❌ [FAST-PATH] Error saving food log: {e}")


def _is_simple_food_log(text: str) -> bool:
    """
    Detect if text is a simple food log that can be handled without LLM.
    Pattern: [quantity] [common_food] or "I ate/had [quantity] [common_food]"
    """
    import re
    
    text_lower = text.lower().strip()
    
    # Pattern 1: "I ate/had/consumed X food"
    simple_patterns = [
        r'i\s+(ate|had|consumed|eat)\s+(\d+\.?\d*)\s+(\w+)',  # "I ate 2 eggs"
        r'(\d+\.?\d*)\s+(\w+)',  # "2 eggs"
        r'ate\s+(\d+\.?\d*)\s+(\w+)',  # "ate 2 eggs"
    ]
    
    for pattern in simple_patterns:
        match = re.search(pattern, text_lower)
        if match:
            # Extract potential food name (last captured group)
            food_name = match.groups()[-1]
            # Check if it's in our common foods cache
            if food_name in COMMON_FOODS_CACHE:
                return True
    
    # Pattern 2: Just food name with quantity (no verb)
    # "2 eggs", "3 bananas", etc.
    words = text_lower.split()
    for i, word in enumerate(words):
        if word.replace('.', '').isdigit() and i + 1 < len(words):
            potential_food = words[i + 1].rstrip('s')  # Handle plurals
            if potential_food in COMMON_FOODS_CACHE:
                return True
    
    return False


async def _handle_simple_food_log(text: str, user_id: str, chat_history, client_generated_id: str = None) -> ChatResponse:
    """
    Handle simple food logging without LLM (instant response).
    Uses in-memory cache for common foods.
    """
    import re
    from datetime import datetime
    from google.cloud import firestore
    
    text_lower = text.lower().strip()
    
    # Extract quantity and food name
    quantity = 1.0
    food_name = None
    food_data = None
    
    # Try patterns
    patterns = [
        r'i\s+(?:ate|had|consumed|eat)\s+(\d+\.?\d*)\s+(\w+)',  # "I ate 2 eggs"
        r'(\d+\.?\d*)\s+(\w+)',  # "2 eggs"
        r'ate\s+(\d+\.?\d*)\s+(\w+)',  # "ate 2 eggs"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            groups = match.groups()
            if len(groups) >= 2:
                quantity = float(groups[-2])
                food_name = groups[-1].rstrip('s')  # Handle plurals
                if food_name in COMMON_FOODS_CACHE:
                    food_data = COMMON_FOODS_CACHE[food_name]
                    break
    
    if not food_data:
        return None  # Fall back to LLM
    
    # Calculate macros
    total_kcal = round(food_data["kcal_per_unit"] * quantity)
    total_protein = round(food_data["protein_g"] * quantity, 1)
    total_carbs = round(food_data["carbs_g"] * quantity, 1)
    total_fat = round(food_data["fat_g"] * quantity, 1)
    
    # Infer meal type from time
    current_hour = datetime.now().hour
    if 5 <= current_hour < 11:
        meal_type = "breakfast"
    elif 11 <= current_hour < 16:
        meal_type = "lunch"
    elif 16 <= current_hour < 20:
        meal_type = "dinner"
    else:
        meal_type = "snack"
    
    try:
        # Save to database using global Firestore client (fire-and-forget for speed)
        log_data = {
            "user_id": user_id,
            "food_name": food_name,
            "quantity": quantity,
            "unit": food_data["unit"],
            "calories": total_kcal,
            "protein_g": total_protein,
            "carbs_g": total_carbs,
            "fat_g": total_fat,
            "meal_type": meal_type,
            "timestamp": datetime.now(timezone.utc),  # ✅ FIX: Use UTC timezone
            "source": "fast_path",
        }
        
        # 🔧 CRITICAL FIX: Wait for save to complete (not fire-and-forget)
        # This ensures timeline queries AFTER save completes
        await _save_food_log_async(user_id, log_data, client_generated_id)
        
        # Generate response (MATCH LLM FORMAT for consistent UI)
        # Use emoji for food type
        food_emoji = "🥚" if "egg" in food_name else "🍽️"
        
        # Summary (shown in collapsed card)
        summary = f"{food_emoji} {quantity:.0f} {food_name}{'s' if quantity > 1 else ''} eaten logged! {total_kcal} kcal"
        
        # Suggestion (shown in blue box)
        suggestion = "Great choice! Keep it balanced. ✨"
        
        # Details (shown when expanded) - MATCH FRONTEND FORMAT
        # Frontend expects: details['nutrition'] with keys: calories, protein_g, carbs_g, fat_g
        details = {
            "nutrition": {
                "calories": total_kcal,
                "protein_g": total_protein,
                "carbs_g": total_carbs,
                "fat_g": total_fat
            },
            "meal_type": meal_type,
            "quantity": quantity,
            "unit": food_data["unit"]
        }
        
        # Full message (for chat history)
        response_msg = f"{summary}\n\n{suggestion}"
        
        # 🎨 Generate messageId for feedback matching (same as LLM path)
        ai_message_id = str(int(datetime.now().timestamp() * 1000))
        
        # Save AI response (fire-and-forget)
        asyncio.create_task(chat_history.save_message(
            user_id, 'assistant', response_msg,
            {
                'category': 'food_log',
                'food': food_name,
                'quantity': quantity,
                'kcal': total_kcal,
                'fast_path': True,  # Metric: track fast-path usage
                'expandable': True
            },
            summary=summary,
            suggestion=suggestion,
            details=details,
            expandable=True,
            message_id=ai_message_id  # 🎨 Pass messageId for feedback
        ))
        
        print(f"⚡ [FAST-PATH] Simple food log handled without LLM: {food_name} x{quantity}")
        
        # 🔧 CRITICAL FIX: Return items array so frontend knows what was logged
        # This prevents optimistic activity from being removed
        return ChatResponse(
            items=[{
                "category": "meal",
                "summary": f"{food_name} x{quantity} ({total_kcal} kcal)",
                "data": {
                    "meal": food_name,
                    "quantity": quantity,
                    "unit": food_data["unit"],
                    "calories": total_kcal,
                    "protein_g": total_protein,
                    "carbs_g": total_carbs,
                    "fat_g": total_fat,
                    "meal_type": meal_type,
                }
            }],
            original=text,
            message=response_msg,
            summary=summary,
            suggestion=suggestion,
            details=details,
            expandable=True,  # Enable expandable card UI
            message_id=ai_message_id,  # 🎨 Return messageId for feedback UI
            needs_clarification=False
        )
    except Exception as e:
        print(f"❌ [SIMPLE FOOD LOG] Error: {e}")
        return None  # Fall back to LLM


def _is_water_log(text: str) -> bool:
    """Check if text is a simple water log command"""
    water_patterns = [
        'water', 'drank', 'drink', 'glass', 'ml', 'oz', 'hydrate', 'hydration',
        '💧', '🥤', '🚰'
    ]
    # Must contain water-related keyword and be short (< 50 chars)
    return any(pattern in text for pattern in water_patterns) and len(text) < 50

def _is_supplement_log(text: str) -> bool:
    """Check if text is a simple supplement log command"""
    supplement_patterns = [
        'vitamin', 'supplement', 'pill', 'tablet', 'capsule', 'multivitamin',
        'omega', 'fish oil', 'protein powder', 'creatine', 'bcaa', 'probiotic',
        'vitamin d', 'vitamin c', 'vitamin b', 'calcium', 'magnesium', 'zinc',
        '💊', '🧪'
    ]
    # Must contain supplement-related keyword and be short (< 80 chars)
    return any(pattern in text.lower() for pattern in supplement_patterns) and len(text) < 80


async def _handle_water_fast_path_fixed(text: str, user_id: str, chat_history) -> ChatResponse:
    """Handle water logging without LLM (instant response) - FIXED VERSION"""
    import re
    from app.models.fitness_log import FitnessLog, FitnessLogType
    from app.services.database import create_fitness_log
    from app.services.cache_service import cache_service
    import uuid
    
    # Extract amount (default to 1 glass = 250ml if not specified)
    amount_ml = 250  # default
    
    # Try to extract number
    numbers = re.findall(r'\d+', text)
    if numbers:
        num = int(numbers[0])
        # If text contains 'ml' or 'oz', use that unit
        if 'ml' in text:
            amount_ml = num
        elif 'oz' in text:
            amount_ml = int(num * 29.5735)  # oz to ml
        else:
            # Assume glasses
            amount_ml = num * 250
    
    try:
        glasses = amount_ml / 250
        content_text = f"{glasses:.1f} glass{'es' if glasses != 1 else ''} of water ({amount_ml}ml)"
        
        # Create water log (same as LLM path)
        fitness_log = FitnessLog(
            log_id=str(uuid.uuid4()),
            user_id=user_id,
            log_type=FitnessLogType.water,  # ✅ CRITICAL: Save as 'water' not 'meal'
            content=content_text,
            calories=0,
            ai_parsed_data={
                "quantity_ml": amount_ml,
                "water_unit": "glasses",
                "quantity": str(glasses),
                "source": "fast_path",
            }
        )
        
        # Save to database
        await asyncio.to_thread(create_fitness_log, fitness_log)
        print(f"✅ [FAST-PATH] Water log saved: {amount_ml}ml as log_type=water")
        
        # Invalidate cache IMMEDIATELY (before indexing delay)
        cache_service.invalidate_timeline(user_id)
        cache_service.invalidate_dashboard(user_id)
        print(f"🗑️  [FAST-PATH] Cache invalidated IMMEDIATELY for user {user_id}")
        
        # ✅ NO DELAY NEEDED: Frontend will pull-to-refresh
        print(f"✅ [FAST-PATH] Water log saved, frontend will refresh on demand")
        
        response_msg = f"💧 Logged {glasses:.1f} glass{'es' if glasses != 1 else ''} ({amount_ml}ml) of water! Stay hydrated! 🎉"
        
        # Save AI response (fire-and-forget)
        asyncio.create_task(chat_history.save_message(
            user_id, 'assistant', response_msg,
            {'category': 'water_log', 'amount_ml': amount_ml}
        ))
        
        return ChatResponse(
            items=[],
            original=text,
            message=response_msg,
            summary=f"Logged {glasses:.1f} glass{'es' if glasses != 1 else ''} of water",
            suggestion="Keep up the great hydration! 💪",
            expandable=False,
            needs_clarification=False
        )
    except Exception as e:
        print(f"❌ [WATER FAST-PATH] Error: {e}")
        return None  # Fall back to normal LLM processing

async def _handle_supplement_fast_path(text: str, user_id: str, chat_history) -> ChatResponse:
    """Handle supplement logging without LLM (instant response) - 0 CALORIES"""
    import re
    from app.models.fitness_log import FitnessLog, FitnessLogType
    from app.services.database import create_fitness_log
    from app.services.cache_service import cache_service
    import uuid
    
    # Extract supplement name and quantity
    lower_text = text.lower()
    
    # Try to extract quantity (default to 1)
    quantity = 1
    numbers = re.findall(r'\d+', text)
    if numbers:
        quantity = int(numbers[0])
    
    # Extract supplement name (simple heuristic)
    supplement_name = text
    for pattern in ['vitamin', 'supplement', 'pill', 'tablet', 'capsule']:
        if pattern in lower_text:
            supplement_name = text.replace(str(quantity), '').strip()
            break
    
    try:
        content_text = f"{quantity} {supplement_name}"
        
        # Create supplement log (0 calories!)
        fitness_log = FitnessLog(
            log_id=str(uuid.uuid4()),
            user_id=user_id,
            log_type=FitnessLogType.supplement,  # ✅ CRITICAL: Save as 'supplement' not 'meal'
            content=content_text,
            calories=0,  # ✅ FIX: 0 calories, not 5!
            ai_parsed_data={
                "supplement_name": supplement_name,
                "quantity": quantity,
                "dosage": f"{quantity} tablet{'s' if quantity != 1 else ''}",
                "source": "fast_path",
            }
        )
        
        # Save to database
        await asyncio.to_thread(create_fitness_log, fitness_log)
        print(f"✅ [FAST-PATH] Supplement log saved: {supplement_name} x{quantity} as log_type=supplement (0 cal)")
        
        # Invalidate cache IMMEDIATELY (before indexing delay)
        cache_service.invalidate_timeline(user_id)
        cache_service.invalidate_dashboard(user_id)
        print(f"🗑️  [FAST-PATH] Cache invalidated IMMEDIATELY for user {user_id}")
        
        # ✅ NO DELAY NEEDED: Frontend will pull-to-refresh
        print(f"✅ [FAST-PATH] Supplement log saved, frontend will refresh on demand")
        
        response_msg = f"💊 Logged {quantity} {supplement_name}! Keep up the healthy habits! 🎉"
        
        # Save AI response (fire-and-forget)
        asyncio.create_task(chat_history.save_message(
            user_id, 'assistant', response_msg,
            {'category': 'supplement_log', 'supplement': supplement_name, 'quantity': quantity}
        ))
        
        return ChatResponse(
            items=[],
            original=text,
            message=response_msg,
            summary=f"Logged {quantity} {supplement_name}",
            suggestion="Great job staying consistent! 💪",
            expandable=False,
            needs_clarification=False
        )
    except Exception as e:
        print(f"❌ [SUPPLEMENT FAST-PATH] Error: {e}")
        return None  # Fall back to normal LLM processing


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    req: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    # ⏱️ HIGH-RESOLUTION TIMING
    t_start = time.perf_counter()
    request_id = f"{int(time.time() * 1000)}"
    
    text = (req.user_input or "").strip()
    
    # Validate input - reject meaningless single characters or very short inputs
    if len(text) < 2:
        return ChatResponse(
            items=[],
            original=text,
            message="Please provide more details. For example: '2 eggs for breakfast' or 'ran 5k'",
            needs_clarification=True,
            clarification_question="What would you like to log? (meals, workouts, tasks, etc.)"
        )
    
    # Get chat history service
    chat_history = get_chat_history_service()
    user_id = current_user.user_id  # Fixed: User model uses 'user_id' not 'uid'
    
    # ⚡ PHASE 1 OPTIMIZATION: Fire-and-forget user message save (non-blocking)
    t1 = time.perf_counter()
    print(f"⏱️ [{request_id}] START - Input: '{text[:50]}...'")
    # Save user message in background (non-blocking) - ChatGPT style
    asyncio.create_task(chat_history.save_message(user_id, 'user', text))
    t2 = time.perf_counter()
    print(f"⏱️ [{request_id}] STEP 1 - Save user message (fire-and-forget): {(t2-t1)*1000:.0f}ms")
    
    # ⚡ SMART ROUTING: Check if we can skip LLM entirely (Priority #1 optimization)
    lower_text = text.lower().strip()
    
    # Fast-path 1: Simple food logging (NEW - highest priority!)
    if _is_simple_food_log(lower_text):
        simple_food_response = await _handle_simple_food_log(lower_text, user_id, chat_history, req.client_generated_id)
        if simple_food_response:
            t_end = time.perf_counter()
            total_ms = (t_end - t_start) * 1000
            print(f"⚡ [{request_id}] FAST-PATH: Simple food log (NO LLM!) - Total: {total_ms:.0f}ms")
            return simple_food_response
    
    # Fast-path 2: Fasting commands
    fasting_command_response = await _handle_fasting_commands(lower_text, user_id, chat_history)
    if fasting_command_response:
        return fasting_command_response
    
    # Fast-path 3: Water logging (instant, no LLM needed) ✅ FIXED
    if _is_water_log(lower_text):
        water_response = await _handle_water_fast_path_fixed(lower_text, user_id, chat_history)
        if water_response:
            t_end = time.perf_counter()
            total_ms = (t_end - t_start) * 1000
            print(f"⚡ [{request_id}] FAST-PATH: Water log (NO LLM!) - Total: {total_ms:.0f}ms")
            return water_response
    
    # Fast-path 4: Supplement logging (instant, no LLM needed, 0 calories) ✅ NEW
    if _is_supplement_log(lower_text):
        supplement_response = await _handle_supplement_fast_path(lower_text, user_id, chat_history)
        if supplement_response:
            t_end = time.perf_counter()
            total_ms = (t_end - t_start) * 1000
            print(f"⚡ [{request_id}] FAST-PATH: Supplement log (NO LLM, 0 CAL!) - Total: {total_ms:.0f}ms")
            return supplement_response
    
    # ⏱️ STEP 2: Cache lookup
    t3 = time.perf_counter()
    
    # PHASE 1: Try cache-first approach for food logging
    cache_hit = False
    items = []
    needs_clarification = False
    clarification_question = None
    
    try:
        from app.services.food_macro_service import get_food_macro_service
        food_service = get_food_macro_service()
        
        # Try fuzzy match
        match_result = await food_service.fuzzy_match_food(text)
        
        if match_result.matched and match_result.food_macro:
            # CACHE HIT! Parse portion and calculate macros
            portion_result = food_service.parse_portion(text, match_result.food_macro)
            
            # Create ChatItem from cache data
            # Infer meal type from current time (same logic as LLM uses)
            from datetime import datetime
            current_hour = datetime.now().hour
            if 5 <= current_hour < 11:
                inferred_meal_type = "breakfast"
            elif 11 <= current_hour < 16:
                inferred_meal_type = "lunch"
            elif 16 <= current_hour < 22:
                inferred_meal_type = "dinner"
            else:
                inferred_meal_type = "snack"
            
            items = [ChatItem(
                category="meal",
                summary=f"{match_result.food_macro.display_name} ({portion_result.quantity} {portion_result.unit})",
                data={
                    "meal": match_result.food_macro.display_name,
                    "item": match_result.food_macro.display_name,  # ✅ FIX: Add item field
                    "meal_type": inferred_meal_type,                # ✅ FIX: Add meal_type field
                    "quantity": portion_result.quantity,
                    "unit": portion_result.unit,
                    "calories": round(portion_result.macros.calories, 1),
                    "protein_g": round(portion_result.macros.protein_g, 1),
                    "carbs_g": round(portion_result.macros.carbs_g, 1),
                    "fat_g": round(portion_result.macros.fat_g, 1),
                    "fiber_g": round(portion_result.macros.fiber_g, 1),
                    "sugar_g": round(portion_result.macros.sugar_g, 1),
                    "sodium_mg": round(portion_result.macros.sodium_mg, 1),
                    "source": portion_result.source,
                    "source_id": portion_result.source_id,
                    "cache_hit": True,
                    "confidence": match_result.confidence,
                    "match_type": match_result.match_type
                }
            )]
            cache_hit = True
            print(f"✅ CACHE HIT: {match_result.food_macro.display_name} (confidence: {match_result.confidence})")
        else:
            # CACHE MISS: Fall back to LLM
            print(f"❌ CACHE MISS: Falling back to LLM for '{text}'")
            cache_hit = False
    except Exception as e:
        print(f"⚠️  Cache lookup error (falling back to LLM): {e}")
        cache_hit = False
    
    t4 = time.perf_counter()
    print(f"⏱️ [{request_id}] STEP 2 - Cache lookup: {(t4-t3)*1000:.0f}ms (hit={cache_hit})")
    
    # If cache miss, ALWAYS use OpenAI for intelligent parsing
    # OpenAI can handle mixed categories (meals + workouts + supplements) properly
    
    # ⏱️ STEP 3: LLM Classification
    t5 = time.perf_counter()
    if not cache_hit:
        items, needs_clarification, clarification_question = await _classify_with_llm(text, user_id)
    t6 = time.perf_counter()
    if not cache_hit:
        print(f"⏱️ [{request_id}] STEP 3 - LLM classification: {(t6-t5)*1000:.0f}ms")
    
    # 🧠 PHASE 2: Calculate confidence & generate explanations
    t_phase2_start = time.perf_counter()
    confidence_score = None
    confidence_level = None
    confidence_factors_dict = None
    explanation_dict = None
    alternatives_list = None
    
    try:
        from app.services.confidence_scorer import get_confidence_scorer
        from app.services.response_explainer import get_response_explainer
        from app.services.alternative_generator import get_alternative_generator
        
        scorer = get_confidence_scorer()
        explainer = get_response_explainer()
        alt_generator = get_alternative_generator()
        
        # Convert items to dicts for Phase 2 services
        items_for_scoring = [{'category': it.category, 'summary': it.summary, 'data': it.data} for it in items]
        
        # 1. Calculate confidence
        confidence_score, confidence_factors = scorer.calculate_confidence(
            user_input=text,
            parsed_items=items_for_scoring,
            llm_response=None,  # Could pass LLM response if available
            user_history=None   # Could pass user history if available
        )
        
        # Determine confidence level
        from app.models.explainable_response import ExplainableResponse
        confidence_level_enum = ExplainableResponse.determine_confidence_level(confidence_score)
        confidence_level = confidence_level_enum.value
        
        # Convert factors to dict (use 0.0 for None values)
        confidence_factors_dict = {
            'input_clarity': confidence_factors.input_clarity,
            'data_completeness': confidence_factors.data_completeness,
            'model_certainty': confidence_factors.model_certainty,
            'historical_accuracy': confidence_factors.historical_accuracy if confidence_factors.historical_accuracy is not None else 0.0
        }
        
        # 2. Generate explanation
        primary_category = items[0].category if items else "other"
        explanation = explainer.explain_classification(
            user_input=text,
            parsed_items=items_for_scoring,
            classification=primary_category,
            confidence_score=confidence_score,
            user_context=None  # Could pass user context
        )
        
        explanation_dict = {
            'reasoning': explanation.reasoning,
            'data_sources': explanation.data_sources,
            'assumptions': explanation.assumptions,
            'why_this_classification': explanation.why_this_classification,
            'confidence_breakdown': explanation.confidence_breakdown
        }
        
        # 3. Generate alternatives (only if confidence < 0.85 AND category supports alternatives)
        # Skip alternatives for: water, supplement, task, workout (no ambiguity needed)
        primary_category = items[0].category if items else "other"
        categories_with_alternatives = ['meal']  # Only meals need alternatives
        
        if items and confidence_score < 0.85 and primary_category in categories_with_alternatives:
            primary_interpretation = items_for_scoring[0] if items_for_scoring else {}
            alternatives = alt_generator.generate_alternatives(
                user_input=text,
                primary_interpretation=primary_interpretation,
                primary_confidence=confidence_score,
                user_context=None  # Could pass user context
            )
            
            # Convert to dicts
            alternatives_list = [
                {
                    'interpretation': alt.interpretation,
                    'confidence': alt.confidence,
                    'explanation': alt.explanation,
                    'data': alt.data
                }
                for alt in alternatives
            ]
            
            if alternatives_list:
                print(f"🧠 [PHASE 2] Generated {len(alternatives_list)} alternatives (confidence={confidence_score:.2f})")
        
        print(f"🧠 [PHASE 2] Confidence: {confidence_score:.2f} ({confidence_level})")
        
    except Exception as e:
        print(f"⚠️  [PHASE 2] Explainable AI error (non-fatal): {e}")
        # Phase 2 is optional - don't break the flow
        import traceback
        traceback.print_exc()
    
    t_phase2_end = time.perf_counter()
    print(f"⏱️ [{request_id}] PHASE 2 - Explainable AI: {(t_phase2_end-t_phase2_start)*1000:.0f}ms")
    
    # If clarification is needed, still return the parsed items (don't persist them yet)
    # This allows the user to see what was understood before answering clarification
    if needs_clarification and clarification_question:
        # Save AI clarification to history (ASYNC)
        await chat_history.save_message(user_id, 'assistant', clarification_question, {
            'needs_clarification': True,
            'category': 'clarification'
        })
        
        # Convert items to response format (but don't save to DB yet)
        response_items = []
        for it in items:
            response_items.append({
                "category": it.category,
                "summary": it.summary,
                "data": it.data
            })
        
        return ChatResponse(
            items=response_items,  # Return parsed items so user can see them
            original=text,
            message=clarification_question,
            needs_clarification=True,
            clarification_question=clarification_question
        )

    # Post-process: enhance with nutrition data for meals
    for it in items:
        if it.category == "meal":
            data = it.data or {}
            
            # Skip nutrition lookup if already parsed by multi-food parser
            if data.get("multi_food_parsed"):
                # Already has accurate macros from multi-food parser
                # DO NOT call get_nutrition_info - it will override our accurate data!
                it.data = data
                continue
            
            # For non-multi-food items (LLM parsed), try old nutrition API
            # But ONLY if we don't have calories yet
            if "calories" not in data:
                meal_text = data.get("meal", text)
                nutrition = get_nutrition_info(meal_text)
                if nutrition:
                    # Merge nutrition data with LLM data
                    data.update(nutrition)
                    it.summary = f"{nutrition['food']} logged - {nutrition['calories']} cal, {nutrition['protein_g']}g protein 💪"
                else:
                    # Fallback to old estimation
                    est = _estimate_calories(meal_text, data)
                    if est is not None:
                        data["calories"] = est
            it.data = data

    # Audit log (best-effort)
    try:
        from google.cloud import firestore

        project = os.getenv("GOOGLE_CLOUD_PROJECT")
        db = firestore.Client(project=project) if project else firestore.Client()
        db.collection("activities").add(
            {
                "source": "chat",
                "text": text,
                "items": [i.model_dump() for i in items],
                "created_at": firestore.SERVER_TIMESTAMP,
                "latency_ms": int((time.time() - started) * 1000),
            }
        )
    except Exception:
        pass

    # ⏱️ STEP 4: Persist to database
    t7 = time.perf_counter()
    
    # Persist each item to Firestore
    # Group meals by meal_type to avoid duplicates (combine multi-item meals into one log)
    meals_by_type = {}
    
    try:
        for it in items:
            if it.category == "meal":
                meal_type = it.data.get("meal_type", "unknown")
                
                # Group meals of the same type together
                if meal_type not in meals_by_type:
                    meals_by_type[meal_type] = {
                        "items": [],
                        "total_calories": 0,
                        "total_protein": 0,
                        "total_carbs": 0,
                        "total_fat": 0,
                        "meal_type": meal_type
                    }
                
                # Add this item to the group
                item_name = it.data.get("item", "")
                quantity = it.data.get("quantity", "")
                meals_by_type[meal_type]["items"].append(f"{quantity} {item_name}".strip())
                meals_by_type[meal_type]["total_calories"] += it.data.get("calories", 0)
                meals_by_type[meal_type]["total_protein"] += it.data.get("protein_g", 0)
                meals_by_type[meal_type]["total_carbs"] += it.data.get("carbs_g", 0)
                meals_by_type[meal_type]["total_fat"] += it.data.get("fat_g", 0)
            
            elif it.category == "question":
                # 🎯 NEW: Handle conversational messages - DON'T create logs/tasks
                # Just skip to response generation
                print(f"💬 [CONVERSATIONAL] User asked: '{text[:50]}...'")
                # Don't persist this as a fitness log or task
                continue
            
            elif it.category == "workout":
                # Create workout log immediately
                log = FitnessLog(
                    user_id=current_user.user_id,
                    log_type=FitnessLogType.workout,
                    content=it.summary or text,
                    calories=it.data.get("calories"),
                    ai_parsed_data=it.data,
                )
                dbsvc.create_fitness_log(log)
            
            elif it.category == "water":
                # Parse quantity_ml with fallback for unit conversion
                quantity_ml = it.data.get("quantity_ml")
                
                if not quantity_ml:
                    # Fallback: parse from original text if LLM didn't provide quantity_ml
                    text_lower = text.lower()
                    
                    # Check for litres/liters
                    if "litre" in text_lower or "liter" in text_lower or re.search(r'\d+\.?\d*\s*l\b', text_lower):
                        match = re.search(r'(\d+\.?\d*)\s*(litres?|liters?|l)\b', text_lower)
                        if match:
                            quantity_ml = float(match.group(1)) * 1000
                        else:
                            quantity_ml = 1000  # Default to 1 litre
                    
                    # Check for glasses
                    elif "glass" in text_lower:
                        match = re.search(r'(\d+\.?\d*)\s*glass', text_lower)
                        if match:
                            quantity_ml = float(match.group(1)) * 250
                        else:
                            quantity_ml = 250  # Default to 1 glass
                    
                    # Check for ml
                    elif "ml" in text_lower:
                        match = re.search(r'(\d+\.?\d*)\s*ml', text_lower)
                        if match:
                            quantity_ml = float(match.group(1))
                        else:
                            quantity_ml = 250  # Default
                    
                    else:
                        # No unit specified, default to 1 glass
                        quantity_ml = 250
                
                # Create water log - save to main fitness_logs collection (same as meals/workouts)
                # Format content to include quantity for timeline display
                glasses = int(quantity_ml / 250)
                content_text = f"{glasses} glass{'es' if glasses != 1 else ''} of water ({int(quantity_ml)}ml)"
                
                log = FitnessLog(
                    user_id=current_user.user_id,
                    log_type=FitnessLogType.water,
                    content=content_text,  # Include quantity in content for timeline
                    calories=0,  # Water has no calories
                    ai_parsed_data={
                        "quantity_ml": int(quantity_ml),
                        "water_unit": it.data.get("water_unit", "glasses"),
                        "quantity": it.data.get("quantity", "1"),
                    },
                )
                dbsvc.create_fitness_log(log)
            
            elif it.category == "supplement":
                # Create supplement log - save to main fitness_logs collection (same as meals/workouts)
                log = FitnessLog(
                    user_id=current_user.user_id,
                    log_type=FitnessLogType.supplement,
                    content=it.summary or text,
                    calories=0,  # ✅ FIX: Supplements have 0 calories, not 5!
                    ai_parsed_data={
                        "supplement_name": it.data.get("supplement_name", it.data.get("item", "Unknown")),
                        "supplement_type": it.data.get("supplement_type", "other"),
                        "dosage": it.data.get("dosage", "1 tablet"),
                        "quantity": it.data.get("quantity", "1"),
                    },
                )
                dbsvc.create_fitness_log(log)
            
            elif it.category in ("task", "reminder"):
                # Create task immediately
                try:
                    t = Task(
                        user_id=current_user.user_id,
                        title=it.data.get("title") or it.summary or text,
                        description=it.data.get("notes", ""),
                        due_date=None,  # TODO: Parse due_date from natural language
                        priority=TaskPriority.medium,
                        status=TaskStatus.pending,
                    )
                    dbsvc.create_task(t)
                    print(f"✅ Task created: {t.task_id} - {t.title}")
                except Exception as e:
                    print(f"❌ Failed to create task: {e}")
                    # Don't fail the entire request, just log the error
        
        # Now create ONE log per meal type (combines multi-item meals)
        for meal_type, meal_data in meals_by_type.items():
            meal_content = ", ".join(meal_data["items"])
            
            ai_data = {
                "description": meal_content,
                "meal_type": meal_type,
                "calories": meal_data["total_calories"],
                "protein_g": meal_data["total_protein"],
                "carbs_g": meal_data["total_carbs"],
                "fat_g": meal_data["total_fat"],
                "items": meal_data["items"]
            }
            
            log = FitnessLog(
                user_id=current_user.user_id,
                log_type=FitnessLogType.meal,
                content=meal_content,
                calories=meal_data["total_calories"],
                ai_parsed_data=ai_data,
            )
            dbsvc.create_fitness_log(log)
            
    except Exception as e:
        # Log the error instead of silently swallowing it
        print(f"ERROR persisting data: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

    t8 = time.perf_counter()
    print(f"⏱️ [{request_id}] STEP 4 - DB persistence: {(t8-t7)*1000:.0f}ms")
    
    # 🚀 REDIS CACHE: Invalidate timeline and dashboard cache IMMEDIATELY
    # This prevents stale cache hits while Firestore is indexing
    from app.services.cache_service import cache_service
    cache_service.invalidate_timeline(current_user.user_id)
    cache_service.invalidate_dashboard(current_user.user_id)
    print(f"🗑️  [LLM-PATH] Cache invalidated IMMEDIATELY for user {current_user.user_id}")
    
    # ✅ NO DELAY NEEDED: Frontend will pull-to-refresh to get latest data
    print(f"✅ [LLM-PATH] Logs saved, frontend will refresh on demand")

    # ⏱️ STEP 5: Get user context
    t9 = time.perf_counter()
    
    # Generate ChatGPT-style summary format with context awareness
    from app.services.response_formatter import get_response_formatter
    from app.services.context_service import get_context_service
    
    formatter = get_response_formatter()
    context_service = get_context_service(dbsvc)
    
    # Get user context for intelligent feedback
    user_context = context_service.get_user_context(current_user.user_id)
    
    # ✨ FIX: Get TODAY's calories in REAL-TIME (no cache) for accurate progress bar
    calories_realtime, protein_realtime, meals_realtime = context_service.get_today_calories_realtime(current_user.user_id)
    print(f"🔍 [REALTIME] Today's actual calories from DB: {calories_realtime}")
    
    t10 = time.perf_counter()
    print(f"⏱️ [{request_id}] STEP 5 - Get user context: {(t10-t9)*1000:.0f}ms")
    
    # Convert items to dict format for formatter
    items_dict = []
    for item in items:
        items_dict.append({
            'category': item.category,
            'summary': item.summary,
            'data': item.data
        })
    
    # ⏱️ STEP 6: Generate response
    t11 = time.perf_counter()
    
    # Generate context-aware response based on category
    from app.services.chat_response_generator import get_chat_response_generator
    
    response_generator = get_chat_response_generator()
    user_context_dict = {
        "fitness_goal": user_context.fitness_goal,
        "daily_calorie_goal": user_context.daily_calorie_goal,
        "daily_water_goal": user_context.daily_water_goal if hasattr(user_context, 'daily_water_goal') else None,
        # ✨ FIX: Use REALTIME calories (not cached) for accurate cumulative progress bar!
        "calories_consumed_today": calories_realtime,
        "protein_today": protein_realtime,
        "meals_logged_today": meals_realtime,
    }
    
    chat_response = response_generator.generate_response(
        items=items_dict,
        user_context=user_context_dict
    )
    
    # Use the generated response
    ai_message = chat_response.response
    
    # Append context-aware personalized message if available
    context_message = context_service.generate_context_aware_message(user_context, items_dict)
    if context_message:
        ai_message = f"{ai_message}\n\n💬 Personal Insights:\n{context_message}"
    
    t12 = time.perf_counter()
    print(f"⏱️ [{request_id}] STEP 6 - Generate response: {(t12-t11)*1000:.0f}ms")
    
    # ⏱️ STEP 7: Save AI response (ASYNC - non-blocking)
    t13 = time.perf_counter()
    
    # Save AI response to history
    metadata = {
        'category': chat_response.category,
        'items_count': len(items),
        'response_type': 'context_aware',  # Mark as using new context-aware format
        'categories': chat_response.metadata.get('categories', []) if chat_response.metadata else []
    }
    
    # 🎨 UX FIX: Generate messageId BEFORE saving (for feedback matching)
    from datetime import datetime, timezone
    ai_message_id = str(int(datetime.now(timezone.utc).timestamp() * 1000))
    
    # ⚡ PHASE 1 OPTIMIZATION: Fire-and-forget AI message save (non-blocking)
    print(f"💾 Saving AI message to history (async): user_id={user_id}, message_length={len(ai_message)}, message_id={ai_message_id}")
    # Save in background - don't block response
    asyncio.create_task(chat_history.save_message(
        user_id=user_id,
        role='assistant',
        content=ai_message,
        metadata=metadata,
        # ✨ Pass expandable fields from chat_response
        summary=chat_response.summary,
        suggestion=chat_response.suggestion,
        details=chat_response.details,
        expandable=chat_response.expandable,
        # 🧠 PHASE 2: Pass confidence & explanation fields
        confidence_score=confidence_score,
        confidence_level=confidence_level,
        confidence_factors=confidence_factors_dict,
        explanation=explanation_dict,
        alternatives=alternatives_list,
        # 🎨 UX FIX: Pass generated messageId
        message_id=ai_message_id
    ))
    
    t14 = time.perf_counter()
    print(f"⏱️ [{request_id}] STEP 7 - Save AI response (fire-and-forget): {(t14-t13)*1000:.0f}ms")
    
    # ⏱️ TOTAL TIME
    t_end = time.perf_counter()
    total_ms = (t_end - t_start) * 1000
    print(f"⏱️ [{request_id}] ✅ TOTAL TIME: {total_ms:.0f}ms")
    print(f"⏱️ [{request_id}] BREAKDOWN: Save msg={((t2-t1)*1000):.0f}ms, Cache={((t4-t3)*1000):.0f}ms, LLM={((t6-t5)*1000):.0f}ms, DB={((t8-t7)*1000):.0f}ms, Context={((t10-t9)*1000):.0f}ms, Response={((t12-t11)*1000):.0f}ms, Save AI={((t14-t13)*1000):.0f}ms")
    
    # ✨ NEW: Return response with expandable fields + Phase 2 explainable AI
    response_obj = ChatResponse(
        items=[],  # Don't return individual cards - summary has everything
        original=text,
        message=ai_message,
        # ✨ Include expandable fields in response
        summary=chat_response.summary,
        suggestion=chat_response.suggestion,
        details=chat_response.details,
        expandable=chat_response.expandable,
        # 🧠 PHASE 2: Include explainable AI fields
        confidence_score=confidence_score,
        confidence_level=confidence_level,
        confidence_factors=confidence_factors_dict,
        explanation=explanation_dict,
        alternatives=alternatives_list,
        # 🎨 UX FIX: Return messageId for feedback matching
        message_id=ai_message_id,
        needs_clarification=False,
        clarification_question=None
    )
    
    # 🔍 DEBUG: Log expandable fields
    print(f"✨ [DEBUG] Expandable fields in response:")
    print(f"   - summary: {response_obj.summary[:50] if response_obj.summary else 'None'}...")
    print(f"   - suggestion: {response_obj.suggestion[:50] if response_obj.suggestion else 'None'}...")
    print(f"   - expandable: {response_obj.expandable}")
    print(f"   - details keys: {list(response_obj.details.keys()) if response_obj.details else 'None'}")
    
    # 🧠 DEBUG: Log Phase 2 fields
    print(f"🧠 [DEBUG] Phase 2 Explainable AI fields:")
    print(f"   - confidence_score: {response_obj.confidence_score}")
    print(f"   - confidence_level: {response_obj.confidence_level}")
    print(f"   - explanation: {'Present' if response_obj.explanation else 'None'}")
    print(f"   - alternatives: {len(response_obj.alternatives) if response_obj.alternatives else 0} alternatives")
    
    return response_obj


@app.get("/chat/history")
async def get_chat_history(
    limit: int = 100,
    current_user: User = Depends(get_current_user),
):
    """Get chat history for the current user"""
    print(f"📜 Loading chat history for user: {current_user.user_id}")
    chat_history = get_chat_history_service()
    messages = chat_history.get_user_history(current_user.user_id, limit=limit)
    print(f"📜 Found {len(messages)} messages")
    
    # Debug: Print role distribution
    user_count = sum(1 for m in messages if m.get('role') == 'user')
    assistant_count = sum(1 for m in messages if m.get('role') == 'assistant')
    other_count = len(messages) - user_count - assistant_count
    print(f"📊 Role distribution: {user_count} user, {assistant_count} assistant, {other_count} other")
    
    # Debug: Print first few messages
    for i, msg in enumerate(messages[:5]):
        role = msg.get('role', 'NONE')
        content_preview = (msg.get('content', '')[:50] + '...') if len(msg.get('content', '')) > 50 else msg.get('content', '')
        print(f"  Message {i+1}: role={role}, content={content_preview}")
    
    # 🎨 UX FIX: Query feedback collection and match to messages
    try:
        print(f"🔍 [FEEDBACK MATCHING] Querying feedback for user: {current_user.user_id}")
        db = firestore.Client()
        feedback_ref = db.collection('chat_feedback') \
            .where('user_id', '==', current_user.user_id)
        feedback_docs = list(feedback_ref.stream())
        print(f"🔍 [FEEDBACK MATCHING] Found {len(feedback_docs)} feedback entries")
        
        # Create feedback lookup map
        feedback_map = {}
        for doc in feedback_docs:
            data = doc.to_dict()
            msg_id = data.get('message_id')
            if msg_id:
                feedback_map[msg_id] = {
                    'rating': data.get('rating'),
                    'feedback_id': doc.id
                }
        print(f"🔍 [FEEDBACK MATCHING] Built feedback map with {len(feedback_map)} entries")
        
        # Match feedback to messages
        matched_count = 0
        for msg in messages:
            msg_id = msg.get('messageId')
            if msg_id and msg_id in feedback_map:
                msg['feedback_given'] = True
                msg['feedback_rating'] = feedback_map[msg_id]['rating']
                matched_count += 1
            else:
                msg['feedback_given'] = False
                msg['feedback_rating'] = None
        
        print(f"✅ [FEEDBACK MATCHING] Matched {matched_count}/{len(messages)} messages with feedback")
        
    except Exception as e:
        print(f"⚠️ [FEEDBACK MATCHING] Error matching feedback: {e}")
        # Don't fail the request - just log and continue without feedback data
        import traceback
        traceback.print_exc()
        # Set default feedback state for all messages
        for msg in messages:
            msg['feedback_given'] = False
            msg['feedback_rating'] = None
    
    return {
        "messages": messages,
        "count": len(messages)
    }


@app.post("/admin/init-llm-config")
async def init_llm_config():
    """
    Admin endpoint to initialize LLM config in Firestore
    """
    try:
        from app.models.llm_config import LLMConfig
        import os
        
        db = dbsvc.get_firestore_client()
        configs_ref = db.collection('llm_configs')
        
        # Check existing
        docs = list(configs_ref.limit(1).stream())
        if len(docs) > 0:
            return {"status": "already_exists", "count": len(docs)}
        
        # Create OpenAI config
        api_key = os.getenv('OPENAI_API_KEY', '')
        if not api_key:
            return {"status": "error", "message": "OPENAI_API_KEY not set"}
        
        config = LLMConfig(
            provider='openai',
            model_name='gpt-4o-mini',
            api_key=api_key,
            priority=1,
            is_active=True,
            temperature=0.7,
            max_tokens=4000,
            cost_per_1k_input_tokens=0.00015,
            cost_per_1k_output_tokens=0.0006
        )
        
        doc_ref = configs_ref.document('openai_gpt4o_mini')
        doc_ref.set(config.model_dump())
        
        return {"status": "created", "provider": "openai", "model": "gpt-4o-mini"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.delete("/user/wipe-logs")
async def wipe_user_logs(
    current_user: User = Depends(get_current_user),
):
    """
    Wipe all logs for the current user (fitness logs, chat history, tasks)
    Keeps profile and goals intact
    Supports both old flat structure and new subcollection structure
    """
    print(f"🗑️ [WIPE LOGS] Starting wipe for user: {current_user.user_id}")
    try:
        from google.cloud import firestore
        db = firestore.Client()
        user_id = current_user.user_id
        print(f"🗑️ [WIPE LOGS] Firestore client initialized for user: {user_id}")
        
        deleted_logs = 0
        deleted_messages = 0
        deleted_tasks = 0
        
        print(f"🗑️ [WIPE LOGS] Starting deletion from NEW structure...")
        # Delete from NEW structure (subcollections)
        try:
            # Delete fitness logs from subcollection
            print(f"🗑️ [WIPE LOGS] Deleting fitness logs from subcollection...")
            fitness_logs_ref = db.collection("users").document(user_id).collection("fitness_logs")
            for doc in fitness_logs_ref.stream():
                doc.reference.delete()
                deleted_logs += 1
            print(f"🗑️ [WIPE LOGS] Deleted {deleted_logs} fitness logs from subcollection")
            
            # Delete chat sessions and messages
            print(f"🗑️ [WIPE LOGS] Deleting chat sessions...")
            sessions_ref = db.collection("users").document(user_id).collection("chat_sessions")
            for session in sessions_ref.stream():
                # Delete messages in this session
                messages_ref = session.reference.collection("messages")
                for msg in messages_ref.stream():
                    msg.reference.delete()
                    deleted_messages += 1
                # Delete the session itself
                session.reference.delete()
            print(f"🗑️ [WIPE LOGS] Deleted {deleted_messages} chat messages from subcollection")
            
            # Delete tasks from subcollection
            print(f"🗑️ [WIPE LOGS] Deleting tasks from subcollection...")
            tasks_ref = db.collection("users").document(user_id).collection("tasks")
            for doc in tasks_ref.stream():
                doc.reference.delete()
                deleted_tasks += 1
            print(f"🗑️ [WIPE LOGS] Deleted {deleted_tasks} tasks from subcollection")
        except Exception as e:
            print(f"❌ [WIPE LOGS] Error deleting from new structure: {e}")
            import traceback
            traceback.print_exc()
        
        # Delete from OLD structure (flat collections) for backward compatibility
        try:
            # Delete fitness logs
            fitness_logs_ref = db.collection("fitness_logs")
            query = fitness_logs_ref.where("user_id", "==", user_id)
            for doc in query.stream():
                doc.reference.delete()
                deleted_logs += 1
            
            # Delete chat history
            chat_ref = db.collection("chat_history")
            query = chat_ref.where("user_id", "==", user_id)
            for doc in query.stream():
                doc.reference.delete()
                deleted_messages += 1
            
            # Delete tasks
            tasks_ref = db.collection("tasks")
            query = tasks_ref.where("user_id", "==", user_id)
            for doc in query.stream():
                doc.reference.delete()
                deleted_tasks += 1
        except Exception as e:
            print(f"Error deleting from old structure: {e}")
        
        total = deleted_logs + deleted_messages + deleted_tasks
        print(f"✅ [WIPE LOGS] Successfully deleted {total} items (logs: {deleted_logs}, messages: {deleted_messages}, tasks: {deleted_tasks})")
        
        return {
            "success": True,
            "deleted": {
                "fitness_logs": deleted_logs,
                "chat_messages": deleted_messages,
                "tasks": deleted_tasks,
                "total": total
            },
            "message": f"Successfully deleted {total} items. Profile and goals preserved."
        }
    except Exception as e:
        print(f"❌ [WIPE LOGS] Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to wipe logs. Please try again."
        }


@app.get("/chat/stats")
async def get_chat_stats(
    current_user: User = Depends(get_current_user),
):
    """Get chat statistics for the current user"""
    chat_history = get_chat_history_service()
    stats = chat_history.get_user_stats(current_user.user_id)
    
    return stats


def _generate_ai_feedback(items: list[ChatItem], user_input: str) -> str:
    """Generate conversational AI feedback based on logged items"""
    import random
    
    if not items:
        return "I'm not sure I understood that. Could you try rephrasing? For example: 'I ate 2 eggs for breakfast' or 'I did 30 minutes of running'"
    
    feedback_parts = []
    
    for item in items:
        if item.category == "meal":
            meal_name = item.data.get("meal") or item.summary or "meal"
            # Handle if items is a list
            if isinstance(meal_name, list):
                meal_name = ", ".join(str(x) for x in meal_name) if meal_name else "meal"
            meal_name = str(meal_name)
            
            calories = item.data.get("calories", 0)
            protein = item.data.get("protein_g", 0)
            
            encouragements = [
                f"Great choice! {meal_name.capitalize()} logged with {calories} kcal",
                f"Awesome! I've tracked your {meal_name} ({calories} kcal)",
                f"Nice! {meal_name.capitalize()} added - {calories} kcal, {protein}g protein",
                f"Perfect! Your {meal_name} is logged ({calories} kcal)",
            ]
            feedback_parts.append(random.choice(encouragements))
            
        elif item.category == "workout":
            workout_name = item.data.get("activity") or item.summary or "workout"
            # Handle if workout_name is a list
            if isinstance(workout_name, list):
                workout_name = ", ".join(str(x) for x in workout_name) if workout_name else "workout"
            workout_name = str(workout_name)
            
            duration = item.data.get("duration_minutes", 0)
            calories = item.data.get("calories", 0)
            
            encouragements = [
                f"Excellent work! {workout_name.capitalize()} for {duration} mins - burned ~{calories} kcal! 💪",
                f"Way to go! {workout_name.capitalize()} logged ({duration} mins, ~{calories} kcal burned)",
                f"Keep it up! Your {workout_name} session is tracked - {duration} mins, ~{calories} kcal",
                f"Amazing effort! {workout_name.capitalize()} completed - {duration} mins 🔥",
            ]
            feedback_parts.append(random.choice(encouragements))
            
        elif item.category in ("task", "reminder"):
            task_title = item.data.get("title") or item.summary or "task"
            
            encouragements = [
                f"Got it! I've added '{task_title}' to your tasks ✅",
                f"Task created: {task_title}. I'll remind you!",
                f"Perfect! '{task_title}' is on your list now",
                f"Done! Added '{task_title}' to your tasks",
            ]
            feedback_parts.append(random.choice(encouragements))
    
    # Add motivational closing
    closings = [
        "Keep up the great work! 🎯",
        "You're doing amazing! 🌟",
        "Stay consistent! 💪",
        "Great progress today! ⭐",
        "",  # Sometimes no closing
    ]
    
    message = " ".join(feedback_parts)
    if len(items) > 0:
        message += " " + random.choice(closings)
    
    return message.strip()


# --- Simple calorie estimator for MVP ---
FOOD_KCAL_PER_100G = {
    "chicken": 165,
    "chicken breast": 165,
    "rice": 130,
    "egg": 155,  # per 100g (~78 kcal per egg)
    "milk": 60,   # per 100ml
    "oats": 389,
    "salad": 20,
    "bread": 265,
}


def _parse_quantity_grams(text: str, quantity: Optional[str]) -> Optional[int]:
    s = (quantity or "").lower()
    t = text.lower()
    import re
    # look for patterns like 200g / 200 gm / 200 grams
    for source in (s, t):
        m = re.search(r"(\d{2,4})\s*(g|gm|grams)", source)
        if m:
            return int(m.group(1))
        m_ml = re.search(r"(\d{2,4})\s*(ml|mL)", source)
        if m_ml:
            return int(m_ml.group(1))  # approximate 1ml ~ 1g for water-based foods
        m_eggs = re.search(r"(\d{1,2})\s*egg", source)
        if m_eggs:
            # ~50g per egg
            return int(m_eggs.group(1)) * 50
    return None


def _estimate_calories(text: str, data: dict) -> Optional[int]:
    grams = _parse_quantity_grams(text, data.get("quantity")) or 200  # default 200g
    # choose food keyword
    lower = text.lower()
    best_key = None
    for k in FOOD_KCAL_PER_100G.keys():
        if k in lower:
            best_key = k
            break
    if not best_key:
        return None
    kcal_per_100g = FOOD_KCAL_PER_100G[best_key]
    return int(round(kcal_per_100g * grams / 100))


# ============================================================================
# 🎨 CHAT FEEDBACK ENDPOINTS
# ============================================================================

class ChatFeedbackRequest(BaseModel):
    message_id: str
    rating: str  # 'helpful' or 'not_helpful'
    corrections: List[str] = []
    comment: Optional[str] = None

class AlternativeSelectionRequest(BaseModel):
    message_id: str
    selected_index: int
    selected_alternative: dict
    rejected_primary: Optional[dict] = None

@app.post("/chat/feedback")
async def submit_chat_feedback(
    feedback_req: ChatFeedbackRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Submit feedback for a chat message (thumbs up/down)
    """
    print("=" * 80)
    print(f"🎯 [FEEDBACK START] Endpoint called")
    print(f"   User: {current_user.user_id}")
    print(f"   Message ID: {feedback_req.message_id}")
    print(f"   Rating: {feedback_req.rating}")
    print(f"   Corrections: {feedback_req.corrections}")
    print(f"   Comment: {feedback_req.comment}")
    sys.stdout.flush()
    
    try:
        print(f"🔵 [FEEDBACK] Step 1: Creating Firestore client...")
        sys.stdout.flush()
        db = firestore.Client()
        print(f"✅ [FEEDBACK] Step 1: Firestore client created")
        sys.stdout.flush()
        
        print(f"🔵 [FEEDBACK] Step 2: Creating document reference...")
        sys.stdout.flush()
        feedback_ref = db.collection('chat_feedback').document()
        print(f"✅ [FEEDBACK] Step 2: Document ref created: {feedback_ref.id}")
        sys.stdout.flush()
        
        feedback_data = {
            'feedback_id': feedback_ref.id,
            'user_id': current_user.user_id,
            'message_id': feedback_req.message_id,
            'rating': feedback_req.rating,
            'corrections': feedback_req.corrections,
            'comment': feedback_req.comment,
            'created_at': firestore.SERVER_TIMESTAMP,
        }
        
        print(f"🔵 [FEEDBACK] Step 3: Saving to Firestore...")
        print(f"   Data: {feedback_data}")
        sys.stdout.flush()
        feedback_ref.set(feedback_data)
        print(f"✅ [FEEDBACK] Step 3: Saved successfully!")
        sys.stdout.flush()
        
        print(f"🎉 [FEEDBACK SUCCESS] Feedback {feedback_ref.id} saved for message {feedback_req.message_id}")
        print("=" * 80)
        sys.stdout.flush()
        
        return {
            'success': True,
            'feedback_id': feedback_ref.id,
            'message': 'Thank you for your feedback!'
        }
        
    except Exception as e:
        print(f"❌❌❌ [FEEDBACK ERROR] Exception caught!")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {str(e)}")
        import traceback
        print(f"   Full traceback:")
        traceback.print_exc()
        print("=" * 80)
        sys.stdout.flush()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save feedback: {str(e)}"
        )

@app.post("/chat/select-alternative")
async def select_alternative(
    selection_req: AlternativeSelectionRequest,
    current_user: User = Depends(get_current_user),
):
    """
    User selects an alternative interpretation
    """
    print("=" * 80)
    print(f"🎯 [ALTERNATIVE START] Endpoint called")
    print(f"   User: {current_user.user_id}")
    print(f"   Message ID: {selection_req.message_id}")
    print(f"   Selected Index: {selection_req.selected_index}")
    print(f"   Alternative: {selection_req.selected_alternative.get('interpretation', 'N/A')}")
    sys.stdout.flush()
    
    try:
        print(f"🔵 [ALTERNATIVE] Step 1: Creating Firestore client...")
        sys.stdout.flush()
        db = firestore.Client()
        print(f"✅ [ALTERNATIVE] Step 1: Firestore client created")
        sys.stdout.flush()
        
        # Save selection as feedback
        print(f"🔵 [ALTERNATIVE] Step 2: Creating feedback document...")
        sys.stdout.flush()
        feedback_ref = db.collection('chat_feedback').document()
        feedback_data = {
            'feedback_id': feedback_ref.id,
            'user_id': current_user.user_id,
            'message_id': selection_req.message_id,
            'rating': 'alternative_selected',
            'selected_index': selection_req.selected_index,
            'selected_alternative': selection_req.selected_alternative,
            'rejected_primary': selection_req.rejected_primary,
            'created_at': firestore.SERVER_TIMESTAMP,
        }
        print(f"🔵 [ALTERNATIVE] Step 3: Saving feedback to Firestore...")
        sys.stdout.flush()
        feedback_ref.set(feedback_data)
        print(f"✅ [ALTERNATIVE] Step 3: Feedback saved: {feedback_ref.id}")
        sys.stdout.flush()
        
        # ✅ Update the original chat message
        print(f"🔵 [ALTERNATIVE] Step 4: Updating original chat message...")
        sys.stdout.flush()
        try:
            messages_ref = db.collection('chat_history') \
                .where('messageId', '==', selection_req.message_id) \
                .limit(1)
            messages = list(messages_ref.stream())
            
            if messages:
                print(f"✅ [ALTERNATIVE] Step 4a: Found message to update")
                sys.stdout.flush()
                msg_doc = messages[0]
                selected_alt = selection_req.selected_alternative
                interpretation = selected_alt.get('interpretation', 'Item')
                calories = selected_alt.get('data', {}).get('calories', 0)
                updated_summary = f"{interpretation} logged! {int(calories)} kcal"
                
                print(f"🔵 [ALTERNATIVE] Step 4b: Updating message with new summary: {updated_summary}")
                sys.stdout.flush()
                msg_doc.reference.update({
                    'alternatives': [],
                    'summary': updated_summary,
                    'selected_alternative_index': selection_req.selected_index,
                    'updated_at': firestore.SERVER_TIMESTAMP
                })
                print(f"✅ [ALTERNATIVE] Step 4b: Message {selection_req.message_id} updated successfully")
                sys.stdout.flush()
            else:
                print(f"⚠️ [ALTERNATIVE] Step 4a: No message found with ID {selection_req.message_id}")
                sys.stdout.flush()
        except Exception as update_err:
            print(f"⚠️⚠️⚠️ [ALTERNATIVE] Error updating message!")
            print(f"   Error: {update_err}")
            import traceback
            traceback.print_exc()
            sys.stdout.flush()
        
        print(f"🎉 [ALTERNATIVE SUCCESS] Alternative selected and saved!")
        print("=" * 80)
        sys.stdout.flush()
        
        return {
            'success': True,
            'feedback_id': feedback_ref.id,
            'message': 'Alternative selected!'
        }
        
    except Exception as e:
        print(f"❌❌❌ [ALTERNATIVE ERROR] Exception caught!")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {str(e)}")
        import traceback
        print(f"   Full traceback:")
        traceback.print_exc()
        print("=" * 80)
        sys.stdout.flush()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save selection: {str(e)}"
        )


# ============================================================================
# ANALYTICS ENDPOINTS (Phase 1 - User-Facing Analytics Dashboard)
# ============================================================================

@app.get("/analytics/feedback-summary")
async def get_feedback_summary(
    current_user: dict = Depends(get_current_user)
):
    """
    Get feedback analytics summary for current user (read-only, no side effects)
    
    Returns:
    - Total feedback count
    - Satisfaction score (% helpful)
    - Feedback rate
    - Category breakdown
    - Recent feedback
    
    Feature: User-facing analytics dashboard
    Risk: VERY LOW (read-only, isolated)
    """
    try:
        user_id = current_user.user_id  # Fixed: User model uses 'user_id' not 'uid'
        
        print(f"📊 [ANALYTICS] Fetching feedback for user: {user_id}")
        sys.stdout.flush()
        
        # Initialize Firestore client
        project = os.getenv("GOOGLE_CLOUD_PROJECT", "productivityai-mvp")
        db = firestore.Client(project=project)
        
        # Query feedback collection (read-only)
        feedback_ref = db.collection('chat_feedback')
        feedback_query = feedback_ref.where('user_id', '==', user_id).stream()
        
        # Aggregate metrics
        total_feedback = 0
        helpful_count = 0
        not_helpful_count = 0
        category_stats = {}
        recent_feedback = []
        
        for doc in feedback_query:
            data = doc.to_dict()
            total_feedback += 1
            
            # Count ratings
            rating = data.get('rating', '')
            if rating == 'helpful':
                helpful_count += 1
            elif rating == 'not_helpful':
                not_helpful_count += 1
            
            # Category breakdown (from message_data)
            message_data = data.get('message_data', {})
            category = message_data.get('category', 'unknown')
            if category not in category_stats:
                category_stats[category] = {'helpful': 0, 'not_helpful': 0, 'total': 0}
            category_stats[category]['total'] += 1
            if rating == 'helpful':
                category_stats[category]['helpful'] += 1
            elif rating == 'not_helpful':
                category_stats[category]['not_helpful'] += 1
            
            # Recent feedback (last 10)
            if len(recent_feedback) < 10:
                recent_feedback.append({
                    'message_id': data.get('message_id'),
                    'rating': rating,
                    'comment': data.get('comment', ''),
                    'timestamp': data.get('timestamp', ''),
                    'user_input': message_data.get('user_input', ''),
                })
        
        # Calculate satisfaction score
        satisfaction_score = (helpful_count / total_feedback * 100) if total_feedback > 0 else 0
        
        # Calculate category satisfaction
        for category, stats in category_stats.items():
            if stats['total'] > 0:
                stats['satisfaction'] = (stats['helpful'] / stats['total'] * 100)
            else:
                stats['satisfaction'] = 0
        
        print(f"✅ [ANALYTICS] Aggregated {total_feedback} feedback entries")
        print(f"   Satisfaction: {satisfaction_score:.1f}%")
        print(f"   Categories: {len(category_stats)}")
        sys.stdout.flush()
        
        return {
            'status': 'success',
            'summary': {
                'total_feedback': total_feedback,
                'helpful_count': helpful_count,
                'not_helpful_count': not_helpful_count,
                'satisfaction_score': round(satisfaction_score, 1),
                'feedback_rate': 42,  # TODO: Calculate from total messages
            },
            'category_breakdown': category_stats,
            'recent_feedback': recent_feedback,
        }
        
    except Exception as e:
        print(f"❌ [ANALYTICS] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.stdout.flush()
        raise HTTPException(status_code=500, detail=str(e))


