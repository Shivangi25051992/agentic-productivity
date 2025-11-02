# 🧪 Test Prompts & Expected Results

## How to Test

1. Open: **http://localhost:3000**
2. Login: `alice.test@aiproductivity.app` / `TestPass123!`
3. Go to: **Chat Assistant** tab
4. Copy-paste each test prompt below
5. Compare actual results with expected results

---

## Test 1: Multi-Line Mixed Categories (CRITICAL TEST)

### Prompt:
```
2 eggs for breakfast
2 egg omlet
ran 5 km
1 multivitamin tablet
chocolate bar
```

### Expected Results:
- ✅ **5 separate meal cards** (not 1 combined card)
- ✅ **Categories**:
  - Item 1: Meal (breakfast) - "2 eggs"
  - Item 2: Meal (breakfast) - "2 egg omelet" (typo corrected)
  - Item 3: Workout - "5 km run"
  - Item 4: Supplement - "1 multivitamin tablet"
  - Item 5: Meal (snack) - "chocolate bar"
- ✅ **Calories**: Different for each item (NOT all 200 kcal)
  - 2 eggs: ~140 kcal
  - 2 egg omelet: ~200 kcal
  - 5 km run: ~300 kcal burned
  - Multivitamin: 0 kcal
  - Chocolate bar: Should ask for clarification OR estimate
- ✅ **Clarification**: Should ask "What size was the chocolate bar?"
- ✅ **Macros**: Each meal should have different protein/carbs/fat values

---

## Test 2: Typos and Wrong English

### Prompt:
```
2 egg omlet
i ate 1 banan
had some rice and dal
eated 2 roti with curry
drinked 1 glass milk
```

### Expected Results:
- ✅ **5 separate items**
- ✅ **Typos corrected**:
  - "omlet" → "omelet"
  - "banan" → "banana"
  - "eated" → "ate" (grammar corrected)
  - "drinked" → "drank" (grammar corrected)
- ✅ **All categorized as meals**
- ✅ **Accurate macros** for each food
- ✅ **No clarification needed** (all clear)

---

## Test 3: Workouts Only

### Prompt:
```
ran 5 km
walked 10000 steps
30 minutes of yoga
worked legs at gym
```

### Expected Results:
- ✅ **4 separate workout cards**
- ✅ **Activity types**:
  - Running
  - Walking
  - Yoga
  - Gym/Strength
- ✅ **Calories burned** estimated for each
- ✅ **Duration** estimated where applicable
- ✅ **Intensity** assigned (low/moderate/high)

---

## Test 4: Supplements and Drinks

### Prompt:
```
1 multivitamin tablet
1 omega 3 capsule
1 protien shake
2 cups of coffe
1 glass of water
```

### Expected Results:
- ✅ **5 separate items**
- ✅ **Categories**:
  - Supplement: multivitamin
  - Supplement: omega-3
  - Supplement/Meal: protein shake
  - Meal/Drink: coffee (typo corrected: "coffe" → "coffee")
  - Meal/Drink: water
- ✅ **Typo corrected**: "protien" → "protein"
- ✅ **Calories**: 0 for vitamins, ~120-150 for protein shake, minimal for coffee/water

---

## Test 5: Complex Multi-Food (Original Test Case)

### Prompt:
```
2 egg omlet + 1 bowl of rice + beans curry 100gm + 1.5 litre water + 1 Multivitamin, 1 omega 3 capsule, 1 probiotics
```

### Expected Results:
- ✅ **7 separate items** (split by `+` and `,`)
- ✅ **Categories**:
  - 3 meals: egg omelet, rice, beans curry
  - 1 drink: water
  - 3 supplements: multivitamin, omega-3, probiotics
- ✅ **Quantities preserved**:
  - 2 eggs
  - 1 bowl rice
  - 100gm beans curry
  - 1.5 litre water
  - 1 tablet each supplement
- ✅ **Accurate macros** for each food item

---

## Test 6: Ambiguous Inputs (Should Ask Clarification)

### Prompt:
```
chocolate bar
had lunch
ate something
protein shake
```

### Expected Results:
- ✅ **4 items created**
- ✅ **Clarification requested** for:
  - "chocolate bar" → "What size?"
  - "had lunch" → "What did you have for lunch?"
  - "ate something" → "What did you eat?"
  - "protein shake" → Maybe ask for brand/size OR estimate
- ✅ **Confidence scores < 0.8** for these items
- ✅ **Message**: "I need more details. [Clarification questions]"

---

## Test 7: Time-Based Meal Type Inference

### Prompt (Test at different times of day):
```
2 eggs
1 bowl oatmeal
chicken sandwich
```

### Expected Results (varies by time):
- ✅ **Morning (5-10am)**: All tagged as "breakfast"
- ✅ **Noon (11am-2pm)**: All tagged as "lunch"
- ✅ **Afternoon (3-5pm)**: All tagged as "snack"
- ✅ **Evening (6-10pm)**: All tagged as "dinner"

---

## Test 8: Mixed Everything (ULTIMATE TEST)

### Prompt:
```
2 eggs for breakfast
ran 5km in the morning
1 multivitamin tablet
had rice and dal for lunch
worked out at gym for 1 hour
1 protien shake after workout
chocolate bar
walked 10000 steps
2 cups of coffe
todo: call doctor tomorrow
```

### Expected Results:
- ✅ **10 separate items**
- ✅ **Categories**:
  - 4 meals: eggs, rice+dal, chocolate bar, coffee
  - 3 workouts: 5km run, gym, 10000 steps walk
  - 2 supplements: multivitamin, protein shake
  - 1 task: call doctor
- ✅ **Meal types assigned**: breakfast, lunch, snack
- ✅ **Workout types**: run, gym, walk
- ✅ **Task with due date**: tomorrow
- ✅ **Clarification**: For chocolate bar

---

## Test 9: Edge Cases

### Prompt:
```
v
```

### Expected Results:
- ❌ **Rejected**: "Please provide more details"
- ✅ **No items logged**

### Prompt:
```
ate food
```

### Expected Results:
- ✅ **1 item created**
- ✅ **Clarification requested**: "What food did you eat?"
- ✅ **Low confidence** (<0.5)

---

## Test 10: Single Items (Should Work Fast)

### Prompt:
```
2 eggs
```

### Expected Results:
- ✅ **1 meal card**
- ✅ **Fast response** (< 2 seconds)
- ✅ **Accurate macros**: ~140 kcal, 12g protein
- ✅ **Meal type inferred** from current time

---

## Success Criteria

### ✅ PASS if:
1. Multi-line inputs split into separate items
2. Typos are corrected automatically
3. Mixed categories (meals + workouts + supplements) handled correctly
4. Each food has different, accurate macros (NOT flat 200 kcal)
5. Clarification asked only when truly ambiguous
6. Response time < 3 seconds for most inputs
7. Confidence scores logged in backend (check `backend.log`)

### ❌ FAIL if:
1. Multi-line input treated as single item
2. All items show same calories (200 kcal)
3. Workouts logged as meals
4. Typos not corrected
5. No clarification for ambiguous inputs
6. Response time > 5 seconds
7. App crashes or shows errors

---

## How to Check Backend Logs

```bash
cd /Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity
tail -50 backend.log
```

Look for:
- `⚠️  Low confidence items detected:` - Shows items with confidence < 0.8
- `❌ CACHE MISS:` - Shows when OpenAI is called
- `🎯 MULTI-FOOD DETECTED:` - Should NOT appear (we disabled multi-food parser)

---

## Quick Test Checklist

Copy this and test each one:

```
☐ Test 1: Multi-line mixed (2 eggs\nran 5km\n1 multivitamin\nchocolate bar)
☐ Test 2: Typos (2 egg omlet\ni ate 1 banan)
☐ Test 3: Workouts (ran 5km\nwalked 10000 steps)
☐ Test 4: Supplements (1 multivitamin\n1 omega 3\n1 protien shake)
☐ Test 5: Complex multi-food (2 egg omlet + 1 bowl rice + beans curry)
☐ Test 6: Ambiguous (chocolate bar\nhad lunch)
☐ Test 7: Time inference (2 eggs - check meal type matches time)
☐ Test 8: Mixed everything (all categories in one input)
☐ Test 9: Edge cases (v, ate food)
☐ Test 10: Single items (2 eggs)
```

---

## Report Format

After testing, report like this:

```
Test 1: ✅ PASS - 5 items, typos corrected, accurate macros
Test 2: ❌ FAIL - All showing 200 kcal
Test 3: ✅ PASS - Workouts logged correctly
...
```

---

**Start with Test 1 (Multi-line mixed) - this is the most critical!**


