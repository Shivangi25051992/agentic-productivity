# 🚨 QUICK FIX - Use Mock Data First

## Problem
OpenAI integration is causing timeouts. Let's test the UI with mock data FIRST, then add AI later.

## Solution
Replace AI generation with mock data temporarily.

## Run This Command

```bash
cd /Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity

# Create mock meal plan endpoint
cat > test_meal_endpoint.py << 'EOF'
from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:9000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/meal-planning/plans/generate")
async def generate_plan(authorization: str = Header(None)):
    return {
        "id": "test-123",
        "user_id": "test",
        "week_start_date": "2025-11-03",
        "week_end_date": "2025-11-09",
        "dietary_preferences": ["vegetarian"],
        "daily_calorie_target": 2000,
        "daily_protein_target": 150,
        "meals": [
            {
                "day": "sunday",
                "meal_type": "breakfast",
                "recipe_id": "r1",
                "servings": 1,
                "recipe": {
                    "name": "Veggie Omelette",
                    "nutrition": {"calories": 350, "protein_g": 25, "carbs_g": 15, "fat_g": 20}
                }
            },
            {
                "day": "sunday",
                "meal_type": "lunch",
                "recipe_id": "r2",
                "servings": 1,
                "recipe": {
                    "name": "Quinoa Bowl",
                    "nutrition": {"calories": 450, "protein_g": 30, "carbs_g": 55, "fat_g": 18}
                }
            },
            {
                "day": "sunday",
                "meal_type": "dinner",
                "recipe_id": "r3",
                "servings": 1,
                "recipe": {
                    "name": "Lentil Curry",
                    "nutrition": {"calories": 520, "protein_g": 28, "carbs_g": 65, "fat_g": 15}
                }
            }
        ],
        "created_at": "2025-11-05T19:00:00",
        "updated_at": "2025-11-05T19:00:00",
        "is_active": True,
        "created_by_ai": True
    }

@app.get("/meal-planning/plans/current")
async def get_current(authorization: str = Header(None)):
    return {
        "id": "test-123",
        "meals": []
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

# Kill existing backend
kill $(cat backend.pid) 2>/dev/null

# Start mock server
python test_meal_endpoint.py > backend_mock.log 2>&1 &
echo $! > backend.pid

echo "✅ Mock server started!"
echo "Test at: http://localhost:9000"
```

This will:
1. Replace the slow AI backend with instant mock data
2. Return 3 meals to test the UI
3. Let you see if the frontend works

Once the UI works with mock data, we can add AI back.

