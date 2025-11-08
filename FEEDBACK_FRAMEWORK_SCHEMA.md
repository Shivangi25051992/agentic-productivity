# 📊 USER FEEDBACK FRAMEWORK - COMPLETE SCHEMA

**Date:** November 7, 2025  
**Phase:** Phase 2 - Explainable AI with Feedback Loop  
**Status:** ✅ Implemented & Working

---

## 🗄️ **DATABASE COLLECTIONS**

### **Collection 1: `chat_feedback`**
Stores user ratings (like/dislike) and corrections on AI responses

### **Collection 2: `chat_history`**
Stores all chat messages with feedback state for persistence

---

## 📋 **TABLE 1: `chat_feedback` Collection**

| Field Name | Data Type | Required | Description | Example Values | Purpose |
|------------|-----------|----------|-------------|----------------|---------|
| **feedback_id** | `string` | Auto | Firestore document ID | `"abc123xyz"` | Unique identifier |
| **user_id** | `string` | ✅ Yes | User who gave feedback | `"UWDeaKl4oKc7my94bf8HWaWkCww1"` | Link to user |
| **message_id** | `string` | ✅ Yes | AI message being rated | `"1762522767026"` | Link to chat message |
| **session_id** | `string` | No | Chat session ID | `"2025-11-07"` | Group by session |
| **feedback_type** | `enum` | ✅ Yes | Type of feedback | `"message_rating"`, `"alternative_selection"`, `"correction"` | Categorize feedback |
| **rating** | `enum` | No | Like or dislike | `"helpful"`, `"not_helpful"` | User sentiment |
| **corrections** | `array[string]` | No | What was wrong | `["Wrong item", "Incorrect calories"]` | Structured issues |
| **comment** | `string` | No | Additional feedback | `"I don't like calories"` | Free-form text |
| **message_data** | `object` | No | Original message context | `{ "text": "Rice", "response": "...", "confidence": 0.8 }` | For analysis |
| **created_at** | `timestamp` | ✅ Yes | When feedback given | `"2025-11-07T10:30:00Z"` | Tracking |
| **status** | `enum` | ✅ Yes | Processing status | `"pending"`, `"processed"`, `"used_for_training"` | Workflow |
| **processed** | `boolean` | ✅ Yes | Has been analyzed? | `true`, `false` | Flag |
| **processed_at** | `timestamp` | No | When analyzed | `"2025-11-07T11:00:00Z"` | Tracking |

---

## 📋 **TABLE 2: `chat_history` Collection**

| Field Name | Data Type | Required | Description | Example Values | Purpose |
|------------|-----------|----------|-------------|----------------|---------|
| **message_id** | `string` | ✅ Yes | Unique message ID | `"1762522767026"` | Primary key |
| **user_id** | `string` | ✅ Yes | Message owner | `"UWDeaKl4oKc7my94bf8HWaWkCww1"` | Link to user |
| **role** | `enum` | ✅ Yes | Message sender | `"user"`, `"assistant"` | Chat flow |
| **content** | `string` | ✅ Yes | Message text | `"Rice, white, cooked (1.0 cup) logged! 206 kcal"` | Display |
| **timestamp** | `timestamp` | ✅ Yes | When sent | `"2025-11-07T10:30:00Z"` | Ordering |
| **summary** | `string` | No | One-liner summary | `"🍚 Rice logged! 206 kcal"` | Expandable UI |
| **suggestion** | `string` | No | AI tip | `"Add protein for satiety! 🍗"` | Expandable UI |
| **details** | `object` | No | Nutrition breakdown | `{ "calories": 206, "protein_g": 4.3, ... }` | Expandable UI |
| **expandable** | `boolean` | No | Has expandable UI? | `true`, `false` | UI flag |
| **confidence_score** | `float` | No | AI confidence (0-1) | `0.89` | Phase 2 |
| **confidence_level** | `enum` | No | Confidence category | `"high"`, `"medium"`, `"low"` | Phase 2 |
| **confidence_factors** | `object` | No | Confidence breakdown | `{ "input_clarity": 0.9, "data_completeness": 0.85, ... }` | Phase 2 |
| **explanation** | `object` | No | AI reasoning | `{ "reasoning": "...", "data_sources": [...], ... }` | Phase 2 |
| **alternatives** | `array[object]` | No | Alternative interpretations | `[{ "interpretation": "...", "confidence": 0.7, ... }]` | Phase 2 |
| **feedback_given** | `boolean` | No | User gave feedback? | `true`, `false` | Persistence |
| **feedback_rating** | `enum` | No | Like or dislike | `"helpful"`, `"not_helpful"` | Persistence |

---

## 🔄 **FEEDBACK FLOW DIAGRAM**

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER INTERACTION                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  1. User types: "Rice"                                           │
│  2. AI responds: "🍚 Rice logged! 206 kcal"                      │
│  3. Shows: Confidence 89%, Alternatives, Like/Dislike buttons    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    USER GIVES FEEDBACK                           │
│                                                                  │
│  Option A: Click 👍 (Like)                                       │
│  Option B: Click 👎 (Dislike) → Opens form                      │
│  Option C: Select alternative → Click Confirm                   │
│  Option D: Click "Something else" → Type correction             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FRONTEND (Flutter)                             │
│                                                                  │
│  1. Capture feedback data:                                       │
│     - message_id: "1762522767026"                                │
│     - rating: "helpful" or "not_helpful"                         │
│     - corrections: ["Wrong item", "Incorrect calories"]          │
│     - comment: "I don't like calories"                           │
│                                                                  │
│  2. Call API: POST /chat/feedback                                │
│     Body: { message_id, rating, corrections, comment }           │
│                                                                  │
│  3. Update UI:                                                   │
│     - Hide like/dislike buttons                                  │
│     - Show badge: "✓ Helpful" or "✗ Not helpful"                │
│     - Hide alternative picker                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   BACKEND (FastAPI)                              │
│                                                                  │
│  Endpoint: POST /chat/feedback                                   │
│                                                                  │
│  1. Receive feedback data                                        │
│  2. Validate: message_id exists, rating valid                    │
│  3. Create feedback document:                                    │
│     {                                                            │
│       "user_id": "UWDeaKl4oKc7my94bf8HWaWkCww1",                 │
│       "message_id": "1762522767026",                             │
│       "rating": "helpful",                                       │
│       "corrections": [],                                         │
│       "comment": null,                                           │
│       "created_at": SERVER_TIMESTAMP,                            │
│       "status": "pending"                                        │
│     }                                                            │
│  4. Save to Firestore: chat_feedback collection                  │
│  5. Return: { "success": true, "feedback_id": "abc123" }         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FIRESTORE DATABASE                             │
│                                                                  │
│  Collection: chat_feedback                                       │
│  Document ID: abc123xyz (auto-generated)                         │
│                                                                  │
│  {                                                               │
│    "feedback_id": "abc123xyz",                                   │
│    "user_id": "UWDeaKl4oKc7my94bf8HWaWkCww1",                    │
│    "message_id": "1762522767026",                                │
│    "feedback_type": "message_rating",                            │
│    "rating": "helpful",                                          │
│    "corrections": [],                                            │
│    "comment": null,                                              │
│    "created_at": "2025-11-07T10:30:00Z",                         │
│    "status": "pending",                                          │
│    "processed": false                                            │
│  }                                                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              FEEDBACK PERSISTENCE (On Reload)                    │
│                                                                  │
│  Endpoint: GET /chat/history                                     │
│                                                                  │
│  1. Load messages from chat_history                              │
│  2. Query chat_feedback for user's feedback                      │
│  3. Build feedback_map: { message_id → rating }                  │
│  4. Inject feedback state into messages:                         │
│     message["feedback_given"] = true                             │
│     message["feedback_rating"] = "helpful"                       │
│  5. Return messages with feedback state                          │
│                                                                  │
│  Frontend displays:                                              │
│  - If feedback_given = true → Show badge                         │
│  - If feedback_given = false → Show buttons                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 **FEEDBACK TYPES & EXAMPLES**

### **Type 1: Message Rating (Like/Dislike)**

#### **Example: User Clicks 👍 (Like)**
```json
{
  "message_id": "1762522767026",
  "rating": "helpful",
  "corrections": [],
  "comment": null
}
```

**Saved to Firestore:**
```json
{
  "feedback_id": "abc123",
  "user_id": "UWDeaKl4oKc7my94bf8HWaWkCww1",
  "message_id": "1762522767026",
  "feedback_type": "message_rating",
  "rating": "helpful",
  "corrections": [],
  "comment": null,
  "created_at": "2025-11-07T10:30:00Z",
  "status": "pending",
  "processed": false
}
```

#### **Example: User Clicks 👎 (Dislike) with Comment**
```json
{
  "message_id": "1762522790899",
  "rating": "not_helpful",
  "corrections": [],
  "comment": "I don't like calories"
}
```

**Saved to Firestore:**
```json
{
  "feedback_id": "xyz789",
  "user_id": "UWDeaKl4oKc7my94bf8HWaWkCww1",
  "message_id": "1762522790899",
  "feedback_type": "message_rating",
  "rating": "not_helpful",
  "corrections": [],
  "comment": "I don't like calories",
  "created_at": "2025-11-07T10:35:00Z",
  "status": "pending",
  "processed": false
}
```

---

### **Type 2: Alternative Selection**

#### **Example: User Selects Alternative #1**
```json
{
  "message_id": "1762522767026",
  "selected_index": 1,
  "selected_alternative": {
    "interpretation": "Small portion of Rice, White, Cooked",
    "confidence": 0.65,
    "explanation": "If you meant a small serving (70% of standard)",
    "data": {
      "meal": "Rice, White, Cooked",
      "quantity": 1,
      "unit": "cup",
      "calories": 144,
      "portion_size": "small"
    }
  },
  "rejected_primary": null
}
```

**Saved to Firestore (chat_feedback):**
```json
{
  "feedback_id": "alt456",
  "user_id": "UWDeaKl4oKc7my94bf8HWaWkCww1",
  "message_id": "1762522767026",
  "feedback_type": "alternative_selection",
  "rating": "helpful",
  "corrections": [],
  "comment": "User selected alternative interpretation",
  "message_data": {
    "selected_index": 1,
    "selected_alternative": { ... },
    "rejected_primary": null
  },
  "created_at": "2025-11-07T10:40:00Z",
  "status": "pending",
  "processed": false
}
```

---

### **Type 3: User Correction ("Something Else")**

#### **Example: User Types Custom Correction**
```json
{
  "message_id": "1762522767026",
  "rating": "not_helpful",
  "corrections": ["15 gm of rice and 50 gm of chicken"],
  "comment": "User provided alternative interpretation"
}
```

**Saved to Firestore:**
```json
{
  "feedback_id": "corr999",
  "user_id": "UWDeaKl4oKc7my94bf8HWaWkCww1",
  "message_id": "1762522767026",
  "feedback_type": "correction",
  "rating": "not_helpful",
  "corrections": ["15 gm of rice and 50 gm of chicken"],
  "comment": "User provided alternative interpretation",
  "created_at": "2025-11-07T10:45:00Z",
  "status": "pending",
  "processed": false
}
```

---

## 🔍 **FEEDBACK ANALYTICS QUERIES**

### **Query 1: Get All Feedback for a User**
```python
db.collection('chat_feedback') \
  .where('user_id', '==', 'UWDeaKl4oKc7my94bf8HWaWkCww1') \
  .order_by('created_at', direction='DESCENDING') \
  .stream()
```

### **Query 2: Get Feedback for Specific Message**
```python
db.collection('chat_feedback') \
  .where('message_id', '==', '1762522767026') \
  .get()
```

### **Query 3: Get All "Not Helpful" Feedback (For Analysis)**
```python
db.collection('chat_feedback') \
  .where('rating', '==', 'not_helpful') \
  .where('processed', '==', False) \
  .stream()
```

### **Query 4: Get Feedback with Corrections (For Training)**
```python
db.collection('chat_feedback') \
  .where('feedback_type', '==', 'correction') \
  .where('status', '==', 'pending') \
  .stream()
```

### **Query 5: Get Helpful vs Not Helpful Ratio**
```python
# Count helpful
helpful_count = db.collection('chat_feedback') \
  .where('rating', '==', 'helpful') \
  .count()

# Count not helpful
not_helpful_count = db.collection('chat_feedback') \
  .where('rating', '==', 'not_helpful') \
  .count()

# Calculate ratio
ratio = helpful_count / (helpful_count + not_helpful_count)
```

---

## 📈 **FEEDBACK METRICS & KPIs**

### **Metric 1: Feedback Rate**
```
Feedback Rate = (Messages with Feedback / Total Messages) × 100%
```

### **Metric 2: Satisfaction Score**
```
Satisfaction = (Helpful Feedback / Total Feedback) × 100%
```

### **Metric 3: Confidence Accuracy**
```
Accuracy = (Helpful High-Confidence / Total High-Confidence) × 100%
```

### **Metric 4: Alternative Selection Rate**
```
Alt Selection Rate = (Alternative Selections / Low-Confidence Messages) × 100%
```

### **Metric 5: Correction Rate**
```
Correction Rate = (User Corrections / Total Feedback) × 100%
```

---

## 🎯 **USE CASES**

### **Use Case 1: Improve AI Classification**
- Analyze "not_helpful" feedback
- Identify common misclassifications
- Retrain LLM with corrected examples

### **Use Case 2: Improve Confidence Scoring**
- Compare confidence scores with feedback
- If high confidence + not helpful → adjust scoring
- If low confidence + helpful → boost confidence

### **Use Case 3: Improve Alternative Generation**
- Track which alternatives users select
- Generate better alternatives based on patterns
- Remove alternatives that are never selected

### **Use Case 4: Personalization**
- Learn user preferences from feedback
- Adjust portion sizes based on corrections
- Remember meal types user prefers

### **Use Case 5: Quality Assurance**
- Monitor satisfaction scores daily
- Alert if satisfaction drops below 80%
- Identify problematic categories (e.g., water, tasks)

---

## 🔧 **IMPLEMENTATION FILES**

### **Backend:**
- `app/models/user_feedback.py` - Data models
- `app/main.py` (lines 1670-1740) - Feedback endpoints
- `app/main.py` (lines 1326-1368) - Feedback matching in history

### **Frontend:**
- `flutter_app/lib/widgets/chat/feedback_buttons.dart` - Like/dislike UI
- `flutter_app/lib/widgets/chat/alternative_picker.dart` - Alternative selection
- `flutter_app/lib/widgets/chat/expandable_message_bubble.dart` - Feedback integration
- `flutter_app/lib/screens/chat/chat_screen.dart` - Feedback state management

---

## ✅ **CURRENT STATUS**

| Feature | Status | Notes |
|---------|--------|-------|
| Like/Dislike Buttons | ✅ Working | Shows on all AI messages |
| Feedback Form | ⚠️ Partial | Comment works, checkboxes broken (BUG-003) |
| Alternative Selection | ✅ Working | Tracks user selections |
| "Something Else" Dialog | ✅ Working | Captures corrections |
| Feedback Persistence | ✅ Working | Shows badges after reload |
| Feedback Analytics | 🟡 Pending | Queries ready, dashboard needed |

---

## 🚀 **NEXT STEPS**

1. **Fix BUG-003:** Make checkboxes clickable in dislike form
2. **Add Analytics Dashboard:** Visualize feedback metrics
3. **Implement Learning Loop:** Use feedback to improve AI
4. **Add Feedback Export:** Allow users to see their feedback history
5. **Build Training Pipeline:** Retrain models with corrected data

---

**Last Updated:** November 7, 2025  
**Version:** 1.0 (Phase 2 Complete)  
**Next Review:** After analytics dashboard implementation


