from fastapi import FastAPI, Request, HTTPException
from fastapi import Body, Depends
from typing import Any, List, Optional
from pydantic import BaseModel
import json
import time
import logging
from datetime import datetime, timezone, timedelta
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from dotenv import load_dotenv
import os
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

app = FastAPI(title="AI Fitness & Task Tracker API", version="0.1.0")

# Add error handler middleware
from app.utils.error_handler import ErrorHandlerMiddleware
app.add_middleware(ErrorHandlerMiddleware)

# HTTPS Enforcement Middleware (Production only)
# DISABLED - Cloud Run already handles HTTPS enforcement
# class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next):
#         return await call_next(request)

# CORS configuration - Only allow HTTPS origins in production
cors_origins_env = os.getenv("CORS_ORIGINS", "*")
if cors_origins_env.strip() == "*":
    # In production, restrict to HTTPS only
    allowed_origins = [
        "https://productivityai-mvp.web.app",
        "https://productivityai-mvp.firebaseapp.com",
        "http://localhost:3000",  # Allow local dev
        "http://localhost:8080",
    ]
else:
    allowed_origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
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

# Import models/services for persistence
from app.services import database as dbsvc  # noqa: E402
from app.models.fitness_log import FitnessLog, FitnessLogType  # noqa: E402
from app.models.task import Task, TaskPriority, TaskStatus  # noqa: E402
from app.models.user import User  # noqa: E402
from app.services.nutrition_db import get_nutrition_info, estimate_meal_nutrition  # noqa: E402
from app.services.chat_history_service import get_chat_history_service  # noqa: E402

app.include_router(users_router)
app.include_router(tasks_router)
app.include_router(fitness_logs_router)
app.include_router(auth_router)
app.include_router(fitness_router)
app.include_router(admin_auth_router)
app.include_router(admin_config_router)
from app.routers.admin_feedback import router as admin_feedback_router
app.include_router(admin_feedback_router)
app.include_router(profile_router)
app.include_router(feedback_router)

# Meal management router
from app.routers.meals import router as meals_router
app.include_router(meals_router)

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
    
    # Get goals from profile
    goals = profile.daily_goals
    calories_goal = goals.calories
    protein_goal = goals.protein_g
    carbs_goal = goals.carbs_g
    fat_goal = goals.fat_g
    
    # Calculate streak (simplified - just check if logged today)
    streak_days = 1 if len(logs) > 0 else 0
    
    # Get user's fitness goal
    user_goal = "lose_weight"  # Default
    if hasattr(profile, 'fitness_goal'):
        goal_map = {
            "lose_weight": "lose_weight",
            "gain_muscle": "gain_weight",
            "maintain": "maintain"
        }
        user_goal = goal_map.get(profile.fitness_goal, "lose_weight")
    
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


class ChatItem(BaseModel):
    category: str  # meal | workout | supplement | task | reminder | other
    summary: str
    data: dict


class ChatResponse(BaseModel):
    items: List[ChatItem]
    original: str
    message: str
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


def _classify_with_llm(text: str, user_id: Optional[str] = None) -> tuple[List[ChatItem], bool, Optional[str]]:
    # Get user's local time for meal classification
    user_local_time = None
    user_timezone = "UTC"
    if user_id:
        try:
            from app.services.timezone_service import get_user_local_time, get_user_timezone
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
        timezone_context = f"\n\n**USER CONTEXT:**\n- Current time in user's timezone ({user_timezone}): {user_local_time.strftime('%Y-%m-%d %H:%M:%S')}\n- Current hour: {user_local_time.hour}\n- Use this time for meal type classification if user doesn't specify!\n"
    
    default_prompt = f'''
You are an expert fitness/nutrition/activity assistant and entity extractor.
{timezone_context}
⚠️ **CRITICAL: FEATURE BOUNDARIES** ⚠️
You ONLY support these features:
1. Logging meals/snacks and calculating macros
2. Logging tasks and reminders
3. Logging workouts
4. Answering questions about logged data
5. Summarizing daily progress

You DO NOT support (yet):
❌ Creating diet plans or meal plans
❌ Suggesting meals or recipes
❌ Creating workout plans or exercise routines
❌ Investment tracking or stock analysis
❌ Generating weekly schedules

If user asks for unsupported features, respond with:
"I love that question! 🎯 Right now, I'm focused on helping you log meals and track your macros. 
[Feature name] is coming soon - we're building something exciting! 
For now, I can help you log what you eat and track your progress. What would you like to log today?"

Your job is to:
- Parse ANY free-form text (even with typos, multi-line, multiple categories, wrong English)
- For EVERY line/item, identify and extract:
  
  **Category Classification:**
  - category: "meal", "snack", "workout", "supplement", "task", "reminder", "other"
  - meal_type: "breakfast", "lunch", "dinner", "snack", "unknown" (infer from time/context or mark unknown)
  - activity_type (if workout): "run", "walk", "cycle", "gym", "yoga", "sport", "swim", "other"
  - supplement_type (if supplement): vitamin name/type (e.g., "multivitamin", "omega-3", "protein")
  
  **Entity Extraction:**
  - item: normalized, spell-corrected name (e.g., "omlet" → "omelet", "banan" → "banana")
  - quantity: smart guess with units if missing (e.g., "2", "1 cup", "100g", "5 km")
  - preparation: for meals, if mentioned (e.g., "boiled", "fried", "grilled", "raw")
  - time: if explicitly mentioned or can be inferred
  
  **Nutrition/Activity Data:**
  - For meals: calories, protein_g, carbs_g, fat_g, fiber_g (use realistic values based on food database knowledge)
  - For workouts: duration_minutes, intensity ("low", "moderate", "high"), calories_burned
  - For supplements: dosage, nutrients provided
  
  **Confidence Scoring:**
  - confidence_category: 0.0-1.0 (how confident about the category)
  - confidence_meal_type: 0.0-1.0 (how confident about meal type)
  - confidence_macros: 0.0-1.0 (how confident about nutrition values)

**Critical Rules:**
1. **Split multi-line inputs**: Each line is a SEPARATE item in the array
2. **Handle typos**: Correct common misspellings automatically (omlet→omelet, banan→banana)
3. **Smart Assumptions (BE INTELLIGENT LIKE CHATGPT)**:
   - If quantity/size is reasonable to assume, ASSUME IT (e.g., "chocolate bar" = 40-50g regular size)
   - If preparation is common, ASSUME IT (e.g., eggs = boiled unless stated, omelet = light oil)
   - If calorie range is appropriate, provide RANGE (e.g., "5km run" = 350-450 kcal depending on pace)
   - Default to standard portions: 1 egg=70kcal, 1 cup rice=200kcal, 1 chocolate bar=200kcal
4. **Meal type inference (CRITICAL - MOST IMPORTANT RULE)**:
   - **PRIORITY 1**: If user explicitly says "for breakfast", "at breakfast", "breakfast time", etc. → meal_type="breakfast" (confidence=1.0)
   - **PRIORITY 2**: If user says "for lunch", "at lunch" → meal_type="lunch" (confidence=1.0)
   - **PRIORITY 3**: If user says "for dinner", "at dinner" → meal_type="dinner" (confidence=1.0)
   - **PRIORITY 4**: ONLY if NO explicit mention, use current time to guess (5-10am=breakfast, 11am-2pm=lunch, 3-5pm=snack, 6-10pm=dinner) with confidence=0.8
   - **NEVER EVER override explicit user input!** If they say "2 eggs for breakfast", it's breakfast regardless of time!
5. **Confidence scoring rules**:
   - confidence_category: 1.0 if category is clear (meal/workout/supplement), 0.5-0.8 if ambiguous
   - confidence_meal_type: 1.0 if explicitly stated (e.g., "for breakfast"), 0.9 if inferred from time, 0.5 if unknown
   - confidence_macros: 0.9-1.0 if you know the food well OR made smart assumption, 0.5-0.8 if rough estimate, 0.3 if very uncertain
6. **Clarification threshold**: ONLY set needs_clarification=true if:
   - Input is too vague (e.g., "had lunch" with NO food details)
   - Quantity is critical and completely unknown (e.g., "ate rice" - could be 50g or 500g)
   - DO NOT ask for chocolate bar size, protein shake brand, etc. - make smart assumptions!

**Output Format (strict JSON):**
{
  "items": [
    {
      "category": "meal|snack|workout|supplement|task|reminder|other",
      "summary": "Friendly confirmation (e.g., '2 boiled eggs for breakfast (140 kcal)')",
      "data": {
        "item": "normalized name",
        "quantity": "with units",
        "preparation": "if applicable",
        "meal_type": "breakfast|lunch|dinner|snack|unknown",
        "activity_type": "if workout",
        "supplement_type": "if supplement",
        "calories": number,
        "protein_g": number,
        "carbs_g": number,
        "fat_g": number,
        "fiber_g": number,
        "duration_minutes": number (for workouts),
        "intensity": "low|moderate|high" (for workouts),
        "calories_burned": number (for workouts),
        "confidence_category": 0.0-1.0,
        "confidence_meal_type": 0.0-1.0,
        "confidence_macros": 0.0-1.0
      }
    }
  ],
  "needs_clarification": false,
  "clarification_questions": ["Array of specific questions, max 2"]
}

**Examples:**

Input: "2 eggs for breakfast"
Output: {
  "items": [{
    "category": "meal",
    "summary": "2 eggs for breakfast (140 kcal, 12g protein)",
    "data": {
      "item": "eggs",
      "quantity": "2",
      "meal_type": "breakfast",
      "calories": 140,
      "protein_g": 12,
      "carbs_g": 1,
      "fat_g": 10,
      "fiber_g": 0,
      "confidence_category": 1.0,
      "confidence_meal_type": 1.0,
      "confidence_macros": 0.95
    }
  }],
  "needs_clarification": false,
  "clarification_questions": []
}

Input: "2 egg omlet\\nran 5km\\n1 multivitamin tablet\\nchocolate bar"
Output: {
  "items": [
    {
      "category": "meal",
      "summary": "2 egg omelet with light oil (200 kcal)",
      "data": {
        "item": "egg omelet",
        "quantity": "2 eggs",
        "preparation": "light oil",
        "meal_type": "breakfast",
        "calories": 200,
        "protein_g": 14,
        "carbs_g": 2,
        "fat_g": 15,
        "confidence_category": 1.0,
        "confidence_meal_type": 0.9,
        "confidence_macros": 0.9
      }
    },
    {
      "category": "workout",
      "summary": "5K run (350-450 kcal burned)",
      "data": {
        "item": "running",
        "quantity": "5 km",
        "activity_type": "run",
        "duration_minutes": 30,
        "intensity": "moderate",
        "calories_burned": 400,
        "calories_burned_range": "350-450",
        "confidence_category": 1.0
      }
    },
    {
      "category": "supplement",
      "summary": "1 multivitamin tablet (5 kcal)",
      "data": {
        "item": "multivitamin",
        "quantity": "1 tablet",
        "supplement_type": "multivitamin",
        "calories": 5,
        "confidence_category": 1.0
      }
    },
    {
      "category": "meal",
      "summary": "Chocolate bar regular 40g (200 kcal)",
      "data": {
        "item": "chocolate bar",
        "quantity": "40g",
        "meal_type": "snack",
        "calories": 200,
        "protein_g": 2,
        "carbs_g": 25,
        "fat_g": 10,
        "confidence_category": 1.0,
        "confidence_meal_type": 0.9,
        "confidence_macros": 0.85
      }
    }
  ],
  "needs_clarification": false,
  "clarification_questions": []
}

**Always split each food/activity/supplement onto its own item in the array. Be smart, accurate, and only ask for clarification when truly needed.**
'''

    system_prompt = template_from_admin or default_prompt
    
    # Add current time context for meal type inference
    from datetime import datetime
    current_time = datetime.now()
    time_context = f"Current time: {current_time.strftime('%I:%M %p')} ({current_time.strftime('%A')})"
    user_prompt = f"{time_context}\nInput: {text}"
    
    try:
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


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    req: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    started = time.time()
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
    
    # Save user message to history
    print(f"💾 Saving user message to history: user_id={user_id}, text={text[:50]}...")
    chat_history.save_message(user_id, 'user', text)
    
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
            items = [ChatItem(
                category="meal",
                summary=f"{match_result.food_macro.display_name} ({portion_result.quantity} {portion_result.unit})",
                data={
                    "meal": match_result.food_macro.display_name,
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
    
    # If cache miss, ALWAYS use OpenAI for intelligent parsing
    # OpenAI can handle mixed categories (meals + workouts + supplements) properly
    
    # If still no items, use LLM as final fallback
    if not cache_hit:
        items, needs_clarification, clarification_question = _classify_with_llm(text, user_id)
    
    # If clarification is needed, still return the parsed items (don't persist them yet)
    # This allows the user to see what was understood before answering clarification
    if needs_clarification and clarification_question:
        # Save AI clarification to history
        chat_history.save_message(user_id, 'assistant', clarification_question, {
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
            
            elif it.category in ("task", "reminder"):
                # Create task immediately
                t = Task(
                    task_id=None,
                    user_id=current_user.user_id,
                    title=it.data.get("title") or it.summary or text,
                    description=it.data.get("notes", ""),
                    due_date=None,
                    priority=TaskPriority.medium,
                    status=TaskStatus.pending,
                )
                dbsvc.create_task(t)
        
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

    # Generate ChatGPT-style summary format with context awareness
    from app.services.response_formatter import get_response_formatter
    from app.services.context_service import get_context_service
    
    formatter = get_response_formatter()
    context_service = get_context_service(dbsvc)
    
    # Get user context for intelligent feedback
    user_context = context_service.get_user_context(current_user.user_id)
    
    # Convert items to dict format for formatter
    items_dict = []
    for item in items:
        items_dict.append({
            'category': item.category,
            'summary': item.summary,
            'data': item.data
        })
    
    # Format response
    formatted = formatter.format_response(
        items=items_dict,
        user_goal=user_context.fitness_goal,
        daily_calorie_goal=user_context.daily_calorie_goal
    )
    
    # Generate context-aware personalized message
    context_message = context_service.generate_context_aware_message(user_context, items_dict)
    
    # Use ONLY the formatted summary (no duplication, no asterisks)
    ai_message = formatted.summary_text
    
    # Append context-aware feedback if available (clean format, no markdown)
    if context_message:
        ai_message = f"{ai_message}\n\n💬 Personal Insights:\n{context_message}"
    
    # Save AI response to history
    metadata = {
        'category': items[0].category if items else 'unknown',
        'items_count': len(items),
        'net_calories': formatted.net_calories,
        'formatted': True  # Mark as using new format
    }
    
    print(f"💾 Saving AI message to history: user_id={user_id}, message_length={len(ai_message)}")
    chat_history.save_message(user_id, 'assistant', ai_message, metadata)
    
    return ChatResponse(
        items=[],  # Don't return individual cards - summary has everything
        original=text,
        message=ai_message,
        needs_clarification=False,
        clarification_question=None
    )


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
    
    return {
        "messages": messages,
        "count": len(messages)
    }


@app.delete("/user/wipe-logs")
async def wipe_user_logs(
    current_user: User = Depends(get_current_user),
):
    """
    Wipe all logs for the current user (fitness logs, chat history, tasks)
    Keeps profile and goals intact
    Supports both old flat structure and new subcollection structure
    """
    try:
        from google.cloud import firestore
        db = firestore.Client()
        user_id = current_user.user_id
        
        deleted_logs = 0
        deleted_messages = 0
        deleted_tasks = 0
        
        # Delete from NEW structure (subcollections)
        try:
            # Delete fitness logs from subcollection
            fitness_logs_ref = db.collection("users").document(user_id).collection("fitness_logs")
            for doc in fitness_logs_ref.stream():
                doc.reference.delete()
                deleted_logs += 1
            
            # Delete chat sessions and messages
            sessions_ref = db.collection("users").document(user_id).collection("chat_sessions")
            for session in sessions_ref.stream():
                # Delete messages in this session
                messages_ref = session.reference.collection("messages")
                for msg in messages_ref.stream():
                    msg.reference.delete()
                    deleted_messages += 1
                # Delete the session itself
                session.reference.delete()
            
            # Delete tasks from subcollection
            tasks_ref = db.collection("users").document(user_id).collection("tasks")
            for doc in tasks_ref.stream():
                doc.reference.delete()
                deleted_tasks += 1
        except Exception as e:
            print(f"Error deleting from new structure: {e}")
        
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
        
        return {
            "success": True,
            "deleted": {
                "fitness_logs": deleted_logs,
                "chat_messages": deleted_messages,
                "tasks": deleted_tasks,
                "total": deleted_logs + deleted_messages + deleted_tasks
            },
            "message": f"Successfully deleted {deleted_logs + deleted_messages + deleted_tasks} items. Profile and goals preserved."
        }
    except Exception as e:
        print(f"Error wiping user logs: {e}")
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


