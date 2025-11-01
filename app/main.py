from fastapi import FastAPI
from fastapi import Body, Depends
from typing import Any, List, Optional
from pydantic import BaseModel
import json
import time
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from app.services.auth import get_current_user


load_dotenv()
dotenv_local_path = os.path.join(os.getcwd(), '.env.local')
if os.path.exists(dotenv_local_path):
    load_dotenv(dotenv_local_path, override=True)

app = FastAPI(title="AI Fitness & Task Tracker API", version="0.1.0")

# CORS configuration
cors_origins_env = os.getenv("CORS_ORIGINS", "*")
if cors_origins_env.strip() == "*":
    allowed_origins = ["*"]
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
from app.routers.feedback import router as feedback_router  # noqa: E402

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
app.include_router(profile_router)
app.include_router(feedback_router)

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


def _classify_with_llm(text: str) -> tuple[List[ChatItem], bool, Optional[str]]:
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

    default_prompt = '''
You are a friendly, conversational AI fitness and productivity assistant. Your job is to:

1. **Parse user input** naturally - understand meals, workouts, tasks, reminders in any phrasing
2. **Infer meal type** from time of day if not specified:
   - 5am-10am → breakfast
   - 11am-2pm → lunch  
   - 3pm-5pm → snack
   - 6pm-10pm → dinner
   - 11pm-4am → late night snack
3. **Ask clarifying questions** ONLY when truly ambiguous:
   - Food preparation: "Did you have boiled, fried, or scrambled eggs?"
   - Quantity: "How much rice did you have? (e.g., 1 cup, 200g)"
   - Missing details: "When is this task due?" or "What priority?"
4. **Normalize food names** to standard items (e.g., "2 boiled eggs" not "some eggs")
5. **Estimate calories** using realistic portions if not specified
6. **Be positive and encouraging** in your responses

**Response Format (strict JSON):**
{
  "items": [
    {
      "category": "meal|workout|supplement|task|reminder|other",
      "summary": "Friendly confirmation message",
      "data": {
        // For meals:
        "meal_type": "breakfast|lunch|dinner|snack",
        "items": ["food1", "food2"],
        "quantity": "2 eggs, 1 cup rice",
        "preparation": "boiled|fried|grilled|raw",
        "calories": 450,
        // For workouts:
        "workout_type": "cardio|strength|yoga|sports",
        "duration_minutes": 30,
        "calories": 250,
        // For tasks:
        "title": "Task name",
        "due_date": "YYYY-MM-DD",
        "priority": "high|medium|low"
      }
    }
  ],
  "needs_clarification": false,
  "clarification_question": "Optional: Ask ONE specific question if ambiguous"
}

**Examples:**
Input: "I ate 2 eggs"
→ Infer time → breakfast, ask: "Did you have them boiled, fried, or scrambled?"

Input: "2 boiled eggs for breakfast"
→ Perfect! Log: "Logged: 2 boiled eggs for breakfast (140 kcal, 12g protein)! 🍳"

Input: "ran 5k"
→ Log: "Great run! 5K logged (~300 kcal burned). Keep it up! 🏃"

Input: "call mom tomorrow"
→ Create reminder: "Reminder set: Call mom tomorrow ☎️"
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
        for it in items_json:
            items.append(ChatItem(category=it.get("category", "other"), summary=it.get("summary", ""), data=it.get("data") or {}))
        if not items:
            items = [ChatItem(category="task", summary="Task created", data={"title": text})]
        
        # Store clarification info in a global or return it separately
        # For now, we'll handle it in the endpoint
        return items, data.get("needs_clarification", False), data.get("clarification_question")
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
    
    # Get chat history service
    chat_history = get_chat_history_service()
    user_id = current_user.user_id  # Fixed: User model uses 'user_id' not 'uid'
    
    # Save user message to history
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
    
    # If cache miss, try multi-food parser first
    if not cache_hit:
        try:
            from app.services.multi_food_parser import get_parser
            parser = get_parser()
            meal_entries = parser.parse(text)
            
            if len(meal_entries) > 1:
                # Multiple meals detected! Parse each separately
                print(f"🎯 MULTI-FOOD DETECTED: {len(meal_entries)} meals")
                items = []
                for entry in meal_entries:
                    macros = parser.calculate_macros(entry)
                    items.append(ChatItem(
                        category="meal",
                        summary=f"{entry.food} ({entry.meal_type})",
                        data={
                            "meal": entry.food,
                            "meal_type": entry.meal_type,
                            "quantity": entry.quantity,
                            "calories": macros.get("calories", 0),
                            "protein_g": macros.get("protein", 0),
                            "carbs_g": macros.get("carbs", 0),
                            "fat_g": macros.get("fat", 0),
                            "fiber_g": macros.get("fiber", 0),
                            "estimated": macros.get("estimated", False),
                            "multi_food_parsed": True
                        }
                    ))
                cache_hit = True  # Skip LLM
            elif len(meal_entries) == 1:
                # Single meal, but with accurate macros
                entry = meal_entries[0]
                macros = parser.calculate_macros(entry)
                
                # Check if clarification is needed
                if macros.get("needs_clarification"):
                    clarification_msg = macros.get("clarification_question", "Could you provide more details?")
                    
                    # Save AI clarification to history
                    chat_history.save_message(user_id, 'assistant', clarification_msg, {
                        'needs_clarification': True,
                        'category': 'clarification'
                    })
                    
                    return ChatResponse(
                        items=[],
                        original=text,
                        message=clarification_msg,
                        needs_clarification=True,
                        clarification_question=clarification_msg
                    )
                
                items = [ChatItem(
                    category="meal",
                    summary=f"{entry.food} ({entry.meal_type})",
                    data={
                        "meal": entry.food,
                        "meal_type": entry.meal_type,
                        "quantity": entry.quantity or macros.get("assumed_quantity"),
                        "calories": macros.get("calories", 0),
                        "protein_g": macros.get("protein", 0),
                        "carbs_g": macros.get("carbs", 0),
                        "fat_g": macros.get("fat", 0),
                        "fiber_g": macros.get("fiber", 0),
                        "estimated": macros.get("estimated", False),
                        "multi_food_parsed": True
                    }
                )]
                cache_hit = True  # Skip LLM
        except Exception as e:
            print(f"⚠️  Multi-food parser error: {e}")
            cache_hit = False
    
    # If still no items, use LLM as final fallback
    if not cache_hit:
        items, needs_clarification, clarification_question = _classify_with_llm(text)
    
    # If clarification is needed, return early without persisting
    if needs_clarification and clarification_question:
        # Save AI clarification to history
        chat_history.save_message(user_id, 'assistant', clarification_question, {
            'needs_clarification': True,
            'category': 'clarification'
        })
        
        return ChatResponse(
            items=[],
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
    try:
        for it in items:
            if it.category == "meal":
                # Convert list to string for content field
                meal_content = it.data.get("meal")
                if not meal_content:
                    items_list = it.data.get("items")
                    meal_content = ", ".join(items_list) if isinstance(items_list, list) else str(items_list) if items_list else text
                
                log = FitnessLog(
                    user_id=current_user.user_id,
                    log_type=FitnessLogType.meal,
                    content=meal_content,
                    calories=it.data.get("calories"),
                    ai_parsed_data=it.data,
                )
                dbsvc.create_fitness_log(log)
            elif it.category == "workout":
                log = FitnessLog(
                    user_id=current_user.user_id,
                    log_type=FitnessLogType.workout,
                    content=it.summary or text,
                    calories=it.data.get("calories"),
                    ai_parsed_data=it.data,
                )
                dbsvc.create_fitness_log(log)
            elif it.category in ("task", "reminder"):
                t = Task(
                    task_id=None,  # Task model likely autogenerates
                    user_id=current_user.user_id,
                    title=it.data.get("title") or it.summary or text,
                    description=it.data.get("notes", ""),
                    due_date=None,
                    priority=TaskPriority.medium,
                    status=TaskStatus.pending,
                )
                dbsvc.create_task(t)
    except Exception as e:
        # Log the error instead of silently swallowing it
        print(f"ERROR persisting data: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

    # Generate conversational AI feedback
    ai_message = _generate_ai_feedback(items, text)
    
    # Save AI response to history
    metadata = {
        'category': items[0].category if items else 'unknown',
        'items_count': len(items)
    }
    
    # Add meal-specific metadata
    if items and items[0].category == 'meal':
        meal_data = items[0].data or {}
        metadata.update({
            'calories': meal_data.get('calories', 0),
            'protein_g': meal_data.get('protein_g', 0),
            'carbs_g': meal_data.get('carbs_g', 0),
            'fat_g': meal_data.get('fat_g', 0)
        })
    
    chat_history.save_message(user_id, 'assistant', ai_message, metadata)
    
    return ChatResponse(
        items=items,
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
    chat_history = get_chat_history_service()
    messages = chat_history.get_user_history(current_user.user_id, limit=limit)
    
    return {
        "messages": messages,
        "count": len(messages)
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


