# RCA: Bug #15 - Water Logging Quantity Parsing

**Bug ID:** #15  
**Priority:** P0 (CRITICAL)  
**Status:** In Progress  
**Date:** November 7, 2025

---

## 🐛 Bug Description

**User Input:** "1 litre of water"  
**Expected:** Log 1000ml (1 litre = 1000ml)  
**Actual:** Logged only 250ml  
**Impact:** Critical - Incorrect hydration tracking

### User Feedback
> "Another bug - when i said 1 litre of water..it is logged only 250 ml- can you see it scrrenshot"

---

## 🔍 Root Cause Analysis

### Hypothesis 1: Unit Conversion Issue
**Likelihood:** HIGH  
**Evidence:**
- User said "1 litre" but system logged "250ml"
- 250ml is exactly 1/4 of 1 litre
- Suggests conversion factor is wrong or missing

### Hypothesis 2: Default Serving Size
**Likelihood:** MEDIUM  
**Evidence:**
- 250ml is a common "glass" of water
- System might be defaulting to "1 glass" instead of parsing "1 litre"
- Possible that "litre" is not recognized as a unit

### Hypothesis 3: Quantity Parsing Logic
**Likelihood:** HIGH  
**Evidence:**
- System might be parsing "1" correctly but ignoring "litre"
- Then defaulting to standard water serving (250ml)
- Need to check water quantity parsing code

---

## 📂 Files to Investigate

### Backend Files (Priority Order)

1. **`app/services/nutrition_service.py`**
   - Water logging logic
   - Quantity parsing
   - Unit conversion

2. **`app/services/food_parser.py`**
   - Input parsing
   - Unit recognition
   - Quantity extraction

3. **`app/services/chat_response_generator.py`**
   - Water category detection
   - Response generation
   - Logging logic

4. **`app/main.py`**
   - Water logging endpoint
   - Request handling

### Frontend Files (Lower Priority)

5. **`flutter_app/lib/screens/chat/chat_screen.dart`**
   - User input handling
   - Display logic

---

## 🎯 Investigation Plan

### Step 1: Find Water Logging Code
```bash
grep -r "water" app/services/*.py | grep -i "log\|quantity\|litre\|ml"
```

### Step 2: Check Unit Conversion
```bash
grep -r "litre\|liter" app/services/*.py
grep -r "250" app/services/*.py | grep -i water
```

### Step 3: Review Water Parser
- Find where water quantity is parsed
- Check unit conversion table
- Verify default values

### Step 4: Check Test Coverage
```bash
find . -name "*test*.py" | xargs grep -l water
```

---

## 🔧 Expected Fix

### Root Cause (Predicted)
- Missing or incorrect unit conversion for "litre" → "ml"
- System defaulting to 250ml (1 glass) when unit not recognized
- Quantity parser not handling "litre" unit properly

### Fix Strategy
1. **Add/Fix Unit Conversion:**
   ```python
   WATER_UNITS = {
       'ml': 1,
       'litre': 1000,
       'liter': 1000,
       'l': 1000,
       'glass': 250,
       'cup': 240,
   }
   ```

2. **Update Quantity Parser:**
   - Recognize "litre", "liter", "l" as valid units
   - Apply correct conversion factor
   - Handle variations (litre, litres, liter, liters)

3. **Add Validation:**
   - Log warning if unit not recognized
   - Show user what was logged
   - Allow correction

---

## ✅ Testing Strategy

### Unit Tests (Automated)
```python
def test_water_quantity_parsing():
    assert parse_water("1 litre") == 1000  # ml
    assert parse_water("2 litres") == 2000
    assert parse_water("1 liter") == 1000
    assert parse_water("1 l") == 1000
    assert parse_water("500 ml") == 500
    assert parse_water("1 glass") == 250
    assert parse_water("2 glasses") == 500
```

### Integration Tests
```python
def test_water_logging_endpoint():
    response = client.post("/chat", json={"text": "1 litre of water"})
    assert response.status_code == 200
    
    # Check logged amount
    logs = get_fitness_logs(user_id)
    water_log = [l for l in logs if l['type'] == 'water'][0]
    assert water_log['quantity_ml'] == 1000
```

### Regression Tests
- Test all existing water logging scenarios
- Verify meal/workout logging still works
- Check chat response format unchanged
- Verify timeline display correct

---

## 🚫 Zero Regression Strategy

### Isolation
- ✅ Changes limited to water quantity parsing
- ✅ No changes to meal/workout/supplement logic
- ✅ No database schema changes
- ✅ No API contract changes

### Backward Compatibility
- ✅ Existing "glass" unit still works
- ✅ "ml" unit still works
- ✅ Default behavior preserved for unrecognized units
- ✅ No breaking changes to frontend

### Rollback Plan
- Git branch: `fix/water-quantity-parsing`
- Can revert single commit
- No data migration needed
- Instant rollback possible

---

## 📊 Success Criteria

### Functional
- [ ] "1 litre of water" logs 1000ml
- [ ] "2 litres of water" logs 2000ml
- [ ] "500 ml of water" logs 500ml
- [ ] "1 glass of water" logs 250ml (unchanged)
- [ ] All unit variations work (litre, liter, l)

### Technical
- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] Regression tests pass
- [ ] No console errors
- [ ] No backend errors

### User Experience
- [ ] Chat response shows correct amount
- [ ] Timeline displays correct amount
- [ ] Dashboard shows correct total
- [ ] User can verify what was logged

---

## 📝 Implementation Checklist

### Phase 1: Investigation (Current)
- [ ] Find water logging code
- [ ] Identify quantity parsing logic
- [ ] Check unit conversion table
- [ ] Review test coverage

### Phase 2: Fix Implementation
- [ ] Add/fix unit conversion for litre
- [ ] Update quantity parser
- [ ] Add validation and logging
- [ ] Update chat response to show logged amount

### Phase 3: Testing
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Run regression tests
- [ ] Manual testing with various inputs

### Phase 4: Deployment
- [ ] Code review
- [ ] Commit with detailed message
- [ ] Update defect log
- [ ] Mark bug as resolved

---

## 🎯 Next Steps

1. **Investigate:** Find water logging code
2. **Analyze:** Identify root cause
3. **Fix:** Implement unit conversion
4. **Test:** Automated + manual testing
5. **Deploy:** Commit and verify

**Starting investigation now...**


