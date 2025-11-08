# ✅ Bug #15 Root Cause - FOUND!

**Bug:** "1 litre of water" logged as 250ml  
**Root Cause:** LLM prompt doesn't specify litre→ml conversion + backend defaults to 250ml  
**Location:** `app/main.py` line 1083 + LLM prompt line 454

---

## 🔍 Root Cause Details

### Problem 1: LLM Prompt Missing Unit Conversion
**File:** `app/main.py` line 454  
**Current:**
```
- Water: 1 glass=250ml, calories=0
```

**Issue:**
- Prompt only mentions "glass" unit
- Doesn't tell LLM how to handle "litre", "liter", "l"
- LLM doesn't know to convert litres to ml

### Problem 2: Backend Default Value
**File:** `app/main.py` line 1083  
**Current:**
```python
"quantity_ml": it.data.get("quantity_ml", 250),  # Defaults to 250ml!
```

**Issue:**
- If LLM doesn't return `quantity_ml`, backend defaults to 250ml
- This is why "1 litre" becomes 250ml

---

## 🎯 The Fix (Two-Part)

### Part 1: Update LLM Prompt
**File:** `app/main.py` line 454  
**Change:**
```python
# BEFORE:
- Water: 1 glass=250ml, calories=0

# AFTER:
- Water: 1 glass=250ml, 1 litre=1000ml, 1 liter=1000ml, 1l=1000ml, calories=0. ALWAYS return quantity_ml in data.
```

### Part 2: Add Fallback Parsing (Safety Net)
**File:** `app/main.py` after line 1083  
**Add:**
```python
# Parse quantity_ml from text if LLM didn't provide it
quantity_ml = it.data.get("quantity_ml")
if not quantity_ml:
    # Fallback: parse from text
    text_lower = text.lower()
    if "litre" in text_lower or "liter" in text_lower:
        # Extract number before litre/liter
        match = re.search(r'(\d+\.?\d*)\s*(litre|liter|l)\b', text_lower)
        if match:
            quantity_ml = float(match.group(1)) * 1000
        else:
            quantity_ml = 1000  # Default to 1 litre
    elif "glass" in text_lower:
        match = re.search(r'(\d+\.?\d*)\s*glass', text_lower)
        if match:
            quantity_ml = float(match.group(1)) * 250
        else:
            quantity_ml = 250  # Default to 1 glass
    elif "ml" in text_lower:
        match = re.search(r'(\d+\.?\d*)\s*ml', text_lower)
        if match:
            quantity_ml = float(match.group(1))
        else:
            quantity_ml = 250  # Default
    else:
        quantity_ml = 250  # Default to 1 glass

"quantity_ml": quantity_ml,
```

---

## ✅ Why This Fix Works

### Primary Fix (LLM Prompt)
- LLM will now know to convert litres to ml
- LLM will return `quantity_ml: 1000` for "1 litre"
- Backend will use the correct value

### Fallback Fix (Parsing)
- If LLM fails, backend parses the text directly
- Handles: litre, liter, l, glass, ml
- Provides safety net for edge cases

---

## 🧪 Test Cases

### Test 1: Litre Variations
```python
assert parse_water("1 litre of water") == 1000
assert parse_water("2 litres of water") == 2000
assert parse_water("1 liter of water") == 1000
assert parse_water("1.5 litres") == 1500
assert parse_water("1l water") == 1000
```

### Test 2: Glass (Unchanged)
```python
assert parse_water("1 glass of water") == 250
assert parse_water("2 glasses") == 500
assert parse_water("water") == 250  # Default
```

### Test 3: ML (Direct)
```python
assert parse_water("500 ml water") == 500
assert parse_water("750ml") == 750
```

---

## 📋 Implementation Checklist

- [ ] Update LLM prompt (line 454)
- [ ] Add fallback parsing (after line 1083)
- [ ] Add `import re` if not present
- [ ] Write unit tests
- [ ] Test with real inputs
- [ ] Verify no regression

---

**Ready to implement!**


