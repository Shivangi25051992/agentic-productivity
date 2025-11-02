# Quick Fixes Needed

## 🐛 Minor Issues (Can be deferred)

### 1. Food Name Formatting & Capitalization
**Issue:** Food names not properly formatted
- "beans curry" → should be "Beans Curry"
- "with dal" → should be "With Dal" or just "Dal"
- Inconsistent capitalization

**Examples from user:**
- ❌ "beans curry" (lowercase)
- ✅ "Beans Curry" (title case)
- ❌ "with dal" (captured literally)
- ✅ "Dal" (cleaned up)

**Solution:**
1. Apply title case to all food names
2. Remove filler words ("with", "and" when not needed)
3. Standardize grammar and formatting
4. Ensure consistency across all entries

**Priority:** LOW (Roadmap item)  
**Estimated Time:** 1 hour

**Implementation:**
```python
def format_food_name(name: str) -> str:
    """Format food name with proper capitalization and cleanup"""
    # Remove filler words
    name = re.sub(r'\b(with|and|of)\b', '', name, flags=re.IGNORECASE)
    # Clean up extra spaces
    name = ' '.join(name.split())
    # Apply title case
    return name.title()
```

---

### 2. "Meal logged!" Message Still Appearing
**Issue:** Black bar with "Meal logged!" still shows after logging
**Status:** Investigating - might be AI response message, not SnackBar
**Priority:** MEDIUM
**Next Step:** Check if it's the AI feedback message being displayed

---

## ✅ What's Working Well

1. **Multi-food parsing** - Correctly extracts multiple items
2. **Macro calculation** - Accurate for most foods
3. **Meal classification** - Time-based inference works
4. **Expandable cards** - UI is functional
5. **Timeline view** - Chronological display works

---

## 🎯 Focus Areas (High Priority)

### Immediate:
1. ✅ Fix "Unknown food" - DONE
2. 🔄 Fix chat history persistence
3. 🔄 Add calorie deficit display
4. 🔄 Add AI insights (DIFFERENTIATOR!)

### Short Term:
5. Food name formatting (this issue)
6. OpenAI fallback for unknown foods
7. 24-hour chat history with edit

---

**Note:** Food formatting is a polish item. Focus on core functionality first (chat history, calorie deficit, AI insights), then come back to this for UI polish.


