# 🚨 Timeline Bug - Quick Reference

## Problem
**Fast-path logs saved but not visible in Timeline UI (80% failure rate)**

---

## Files to Review

### Backend (Python)
```
app/main.py                    Lines: 739-761, 763-810, 813-847, 850-1003, 1215-1221, 1503-1654
app/services/database.py       Lines: 193-204, 270-340
app/routers/timeline.py        Lines: 130-210, 179-189, 220-260
app/services/cache_service.py Lines: 47-90
```

### Frontend (Dart)
```
flutter_app/lib/providers/timeline_provider.dart       Lines: 73-180, 225-230, 400-480
flutter_app/lib/screens/timeline/timeline_screen.dart  Lines: 150-167, 169-250
flutter_app/lib/services/api_service.dart              Lines: 277-296
flutter_app/lib/screens/main_navigation.dart           Lines: 52-78
```

---

## Key Differences: Fast vs LLM Path

| Field | Fast-Path | LLM-Path |
|-------|-----------|----------|
| `ai_parsed_data.source` | ✅ "fast_path" | ❌ Not set |
| `ai_parsed_data.items` | ❌ Not set | ✅ Array of items |
| Processing time | 800ms | 3-5s |
| LLM call | No | Yes |

---

## Confirmed Working ✅
- Fast-path detection
- Firestore save (both paths)
- Cache invalidation
- Backend API response
- LLM-path display (100% success)

## Confirmed Broken ❌
- Fast-path display in UI (0-20% success)

---

## Most Likely Root Cause

**Frontend state management or UI rendering issue**

Possible causes:
1. Timeline grouping logic filters out fast-path logs
2. Section collapse state hides activities
3. UI expects `ai_parsed_data.items` array (missing in fast-path)
4. Client cache returns stale data

---

## Quick Fixes to Test

### Fix 1: Add "items" field (Match LLM format)
```python
# app/main.py:791
"items": [f"{log_data['quantity']} {log_data['food_name']}"],
```

### Fix 2: Force section expansion
```dart
// timeline_provider.dart:60
bool isSectionExpanded(String sectionKey) {
  return true;  // Force all expanded
}
```

### Fix 3: Add debug logging
```dart
// timeline_provider.dart:130
print('📊 Fetched ${response.activities.length} activities');
for (var activity in response.activities) {
  print('  - ${activity.title} (${activity.details?['source']})');
}
```

---

## Debug Commands

### Check Firestore
```bash
gcloud firestore documents list \
  --collection-ids=fitness_logs \
  --filter="ai_parsed_data.source=fast_path"
```

### Check Backend API
```bash
curl "http://localhost:8000/timeline?types=meal&limit=50" \
  -H "Authorization: Bearer TOKEN"
```

### Check Backend Logs
```bash
tail -100 /tmp/backend.log | grep -E "FAST-PATH|Food log saved"
```

---

## Test Inputs

**Fast-Path (should work but doesn't)**:
- "1 apple"
- "2 bananas"
- "3 eggs"

**LLM-Path (works 100%)**:
- "I had a delicious grilled chicken salad"
- "Ate pasta with tomato sauce"

---

## Priority Actions

1. ✅ **Verify API response** includes fast-path logs
2. ✅ **Add frontend logging** to see where logs disappear
3. ✅ **Test Fix 1** (add items field)
4. ✅ **Test Fix 2** (force expansion)

