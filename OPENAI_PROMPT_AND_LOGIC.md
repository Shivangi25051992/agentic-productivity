# 🤖 OpenAI Prompt & Parsing Logic

## Current System Prompt (Lines 276-334 in `app/main.py`)

```
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
```

---

## How It Works (Parsing Flow)

### Step 1: User Input Received
```python
# Example: "2 eggs for breakfast\n2 egg omlet\nran 5 km"
text = req.user_input.strip()
```

### Step 2: Input Validation
```python
# Reject meaningless inputs (< 2 characters)
if len(text) < 2:
    return "Please provide more details..."
```

### Step 3: Cache-First Approach (Single Food Only)
```python
# Try fuzzy match against food database
match_result = await food_service.fuzzy_match_food(text)

if match_result.matched:
    # CACHE HIT! Use database macros
    return cached_nutrition_data
else:
    # CACHE MISS! Fall through to OpenAI
    pass
```

### Step 4: OpenAI Classification (Multi-Item & Complex Inputs)
```python
# Add time context for meal type inference
current_time = datetime.now()
time_context = f"Current time: {current_time.strftime('%I:%M %p')} ({current_time.strftime('%A')})"
user_prompt = f"{time_context}\nInput: {text}"

# Call OpenAI
response = client.chat.completions.create(
    model="gpt-4o-mini",  # Fast & cheap
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ],
    temperature=0.2,  # Low = more consistent
    response_format={"type": "json_object"}  # Structured output
)
```

### Step 5: Parse OpenAI Response
```python
# OpenAI returns JSON like:
{
  "items": [
    {
      "category": "meal",
      "summary": "2 eggs for breakfast",
      "data": {
        "meal_type": "breakfast",
        "items": ["eggs"],
        "quantity": "2",
        "calories": 140,
        "protein_g": 12
      }
    },
    {
      "category": "meal",
      "summary": "2 egg omelet",
      "data": {
        "meal_type": "breakfast",
        "items": ["egg omelet"],
        "quantity": "2",
        "calories": 200
      }
    },
    {
      "category": "workout",
      "summary": "5K run",
      "data": {
        "workout_type": "cardio",
        "duration_minutes": 30,
        "calories": 300
      }
    }
  ],
  "needs_clarification": false
}

# Convert to ChatItem objects
items = []
for item_json in response["items"]:
    items.append(ChatItem(
        category=item_json["category"],
        summary=item_json["summary"],
        data=item_json["data"]
    ))
```

### Step 6: Post-Processing (Enhance with Database)
```python
# For meals without calories, try to enhance with database
for item in items:
    if item.category == "meal" and "calories" not in item.data:
        nutrition = get_nutrition_info(item.data["meal"])
        if nutrition:
            item.data.update(nutrition)  # Add accurate macros
```

### Step 7: Save to Database
```python
# Save each item to Firestore
for item in items:
    if item.category == "meal":
        FitnessLog(
            user_id=user_id,
            log_type="meal",
            content=item.summary,
            calories=item.data.get("calories"),
            ai_parsed_data=item.data
        ).save()
    elif item.category == "workout":
        FitnessLog(
            user_id=user_id,
            log_type="workout",
            content=item.summary,
            calories=item.data.get("calories")
        ).save()
```

### Step 8: Return Response to Frontend
```python
return ChatResponse(
    items=items,
    original=text,
    message="Great! Logged all items.",
    needs_clarification=False
)
```

---

## Key Configuration

### Model Settings (Line 346)
```python
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # Default: gpt-4o-mini
temperature = 0.2  # Low = consistent, High = creative
response_format = {"type": "json_object"}  # Structured JSON output
```

### Fallback Logic (No OpenAI)
If OpenAI key is missing or API fails, use basic keyword matching:
```python
if "breakfast" or "lunch" or "egg" in text:
    → category = "meal"
elif "workout" or "run" or "gym" in text:
    → category = "workout"
else:
    → category = "task"
```

---

## Current Issues & Limitations

### ❌ Problems:
1. **Multi-line inputs not parsed correctly** (FIXED in latest code)
   - Before: Only split by `,`, `+`, `and`
   - Now: OpenAI handles newlines naturally

2. **Mixed categories not handled** (FIXED)
   - Before: Multi-food parser only handled meals
   - Now: OpenAI categorizes meals, workouts, supplements separately

3. **Prompt could be better**
   - Current prompt doesn't explicitly handle:
     - Supplements/vitamins
     - Typos and wrong English
     - Multi-line inputs
     - Micronutrients

### ✅ Strengths:
- Time-aware meal type inference
- Clarification questions for ambiguous inputs
- Positive, encouraging tone
- Structured JSON output
- Fast model (gpt-4o-mini)

---

## Recommended Improvements

### 1. Enhanced Prompt (Add These Sections)

```
**Additional Capabilities:**
7. **Handle typos gracefully** - "2 egg omlet" → "2 egg omelet"
8. **Parse multi-line inputs** - Each line is a separate item
9. **Recognize supplements** - vitamins, protein shakes, etc.
10. **Support micronutrients** - calcium, iron, vitamin C, etc.

**Multi-Item Input Handling:**
- If input has multiple lines or items separated by newlines, parse EACH as a separate item
- Example: "2 eggs\nran 5 km\n1 multivitamin" → 3 separate items (meal, workout, supplement)

**Typo Correction:**
- "omlet" → "omelet"
- "banan" → "banana"
- "protien" → "protein"
- "coffe" → "coffee"
```

### 2. Better Category Handling

Add "supplement" as a distinct category:
```json
{
  "category": "supplement",
  "summary": "1 multivitamin tablet",
  "data": {
    "supplement_type": "multivitamin",
    "quantity": "1 tablet",
    "nutrients": ["vitamin A", "vitamin C", "zinc"]
  }
}
```

### 3. Micronutrient Support

Extend meal data structure:
```json
{
  "category": "meal",
  "data": {
    "calories": 140,
    "protein_g": 12,
    "carbs_g": 1,
    "fat_g": 10,
    "fiber_g": 0,
    // Add micronutrients:
    "calcium_mg": 50,
    "iron_mg": 1.2,
    "vitamin_c_mg": 0,
    "vitamin_d_mcg": 1.1
  }
}
```

---

## Testing the Prompt

### Test Inputs:
1. `2 eggs for breakfast` → Should log 2 eggs (breakfast)
2. `2 egg omlet` → Should correct to "omelet"
3. `ran 5 km` → Should log workout
4. `1 multivitamin tablet` → Should log supplement
5. `2 eggs\nran 5 km\n1 multivitamin` → Should parse as 3 separate items

### Expected OpenAI Response:
```json
{
  "items": [
    {
      "category": "meal",
      "summary": "2 eggs for breakfast (140 kcal)",
      "data": {
        "meal_type": "breakfast",
        "items": ["eggs"],
        "quantity": "2",
        "calories": 140,
        "protein_g": 12
      }
    },
    {
      "category": "workout",
      "summary": "5K run (300 kcal burned)",
      "data": {
        "workout_type": "cardio",
        "duration_minutes": 30,
        "calories": 300
      }
    },
    {
      "category": "supplement",
      "summary": "1 multivitamin tablet",
      "data": {
        "supplement_type": "multivitamin",
        "quantity": "1 tablet"
      }
    }
  ],
  "needs_clarification": false
}
```

---

## Files to Review

1. **`app/main.py`** (Lines 240-368) - `_classify_with_llm()` function
2. **`app/main.py`** (Lines 371-600) - `/chat` endpoint
3. **`.env.local`** - `OPENAI_API_KEY` and `OPENAI_MODEL` settings

---

**Current Status**: OpenAI is now being used for ALL complex inputs (multi-line, mixed categories). The multi-food parser has been disabled.

**Next Steps**: Test with real inputs and refine the prompt based on results.


