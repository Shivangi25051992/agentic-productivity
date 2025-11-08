# 🎨 Phase 2 Frontend UI - Implementation Plan

**Goal:** Build intuitive Flutter UI to display confidence, explanations, and alternatives  
**Time Estimate:** 2-3 hours  
**Impact:** Users can see AI reasoning and provide feedback

---

## 🎯 **UI COMPONENTS TO BUILD**

### **1. Confidence Badge** (30 min)
**Location:** Top-right of AI message bubble  
**Design:**
```
┌─────────────────────────────────────┐
│ 🍳 2 eggs logged! 140 kcal         │
│                                     │
│ Great protein! 🥚          [87% ✓] │ ← Confidence badge
└─────────────────────────────────────┘
```

**Colors:**
- High (≥ 0.9): Green `Color(0xFF10B981)`
- Medium (0.7-0.9): Yellow `Color(0xFFF59E0B)`
- Low (< 0.7): Orange `Color(0xFFEF4444)`

**Behavior:**
- Tap to show detailed confidence breakdown
- Icon changes based on level: ✓ (high), ⚠ (medium), ? (low)

---

### **2. "Why?" Button** (45 min)
**Location:** Next to confidence badge  
**Design:**
```
┌─────────────────────────────────────┐
│ 🍳 2 eggs logged! 140 kcal         │
│                                     │
│ [87% ✓] [Why?]                     │ ← Explanation button
└─────────────────────────────────────┘
```

**Behavior:**
- Tap opens bottom sheet with full explanation
- Shows:
  - Step-by-step reasoning
  - Data sources used
  - Assumptions made
  - Confidence breakdown chart

**Bottom Sheet Design:**
```
┌──────────────────────────────────────┐
│ 🧠 How AI Understood This            │
│                                       │
│ Reasoning:                            │
│ 1. You said "2 eggs"                  │
│ 2. Identified eggs as food            │
│ 3. Looked up nutrition data           │
│ 4. Calculated 140 calories            │
│                                       │
│ Data Sources:                         │
│ • USDA FoodData Central               │
│ • Standard serving sizes              │
│                                       │
│ Assumptions:                          │
│ • Medium-sized eggs                   │
│ • Assumed breakfast (8 AM)            │
│                                       │
│ Confidence Factors:                   │
│ Input clarity:     ████████░ 90%     │
│ Data completeness: ███████░░ 85%     │
│ Model certainty:   ███████░░ 85%     │
│                                       │
│             [Got it]                  │
└──────────────────────────────────────┘
```

---

### **3. Alternative Picker** (60 min)
**Location:** Shown inline when confidence < 0.85  
**Design:**
```
┌─────────────────────────────────────┐
│ 🐔 Chicken logged (72% ⚠)          │
│                                     │
│ I'm not 100% sure. Did you mean:   │
│                                     │
│ ○ Small portion (115 kcal)          │
│   70% confidence                    │
│                                     │
│ ● Standard portion (165 kcal) ✓    │ ← Primary (selected)
│   72% confidence                    │
│                                     │
│ ○ Large portion (215 kcal)          │
│   65% confidence                    │
│                                     │
│ ○ Fried chicken (231 kcal)          │
│   63% confidence                    │
│                                     │
│      [Confirm] [Something else]     │
└─────────────────────────────────────┘
```

**Behavior:**
- Radio buttons for selection
- Primary interpretation pre-selected
- Tap alternative to switch
- "Confirm" sends selection to backend
- "Something else" opens text input for correction

---

### **4. Feedback Buttons** (30 min)
**Location:** Bottom of AI message bubble  
**Design:**
```
┌─────────────────────────────────────┐
│ 🍳 2 eggs logged! 140 kcal         │
│                                     │
│ [87% ✓] [Why?]                     │
│                                     │
│ Was this helpful? [👍] [👎]        │ ← Feedback buttons
└─────────────────────────────────────┘
```

**Behavior:**
- 👍 - Logs positive feedback
- 👎 - Opens correction dialog
- Stored in Firestore for Phase 3 learning

---

### **5. Correction Dialog** (30 min)
**Location:** Modal when user taps 👎  
**Design:**
```
┌──────────────────────────────────────┐
│ Help AI Learn                         │
│                                       │
│ What was wrong?                       │
│                                       │
│ ☐ Wrong food item                    │
│ ☐ Wrong quantity                     │
│ ☐ Wrong calories                     │
│ ☐ Wrong meal timing                  │
│ ☐ Other                              │
│                                       │
│ Tell us more (optional):              │
│ ┌──────────────────────────────────┐ │
│ │                                  │ │
│ └──────────────────────────────────┘ │
│                                       │
│      [Cancel]  [Submit Feedback]     │
└──────────────────────────────────────┘
```

---

## 📂 **FILES TO CREATE**

### **New Flutter Widgets:**
```
flutter_app/lib/widgets/chat/
├── confidence_badge.dart           (NEW - 120 lines)
├── explanation_sheet.dart          (NEW - 200 lines)
├── alternative_picker.dart         (NEW - 180 lines)
├── feedback_buttons.dart           (NEW - 80 lines)
└── correction_dialog.dart          (NEW - 150 lines)
```

### **Modified Files:**
```
flutter_app/lib/
├── models/message.dart             (MODIFY - add Phase 2 fields)
├── providers/chat_provider.dart    (MODIFY - parse Phase 2 data)
└── screens/chat/chat_screen.dart   (MODIFY - integrate new widgets)
```

---

## 🎨 **DESIGN SPECIFICATIONS**

### **Colors:**
- High Confidence: `Color(0xFF10B981)` (Green)
- Medium Confidence: `Color(0xFFF59E0B)` (Yellow)
- Low Confidence: `Color(0xFFEF4444)` (Red)
- Explanation Background: `Color(0xFFF3F4F6)` (Light gray)
- Alternative Selected: `Color(0xFF3B82F6)` (Blue)

### **Typography:**
- Confidence Badge: 14px bold
- Explanation Title: 18px bold
- Reasoning Steps: 14px regular
- Alternative Text: 15px medium

### **Animations:**
- Confidence badge fade-in: 300ms
- Bottom sheet slide-up: 400ms ease-out
- Alternative selection: 200ms scale
- Feedback button press: 100ms

---

## 🔄 **INTEGRATION FLOW**

### **1. Chat Message Received:**
```dart
// In chat_provider.dart
final response = await _apiService.post('/chat', {...});

// Parse Phase 2 fields
final confidenceScore = response['confidence_score'] as double?;
final confidenceLevel = response['confidence_level'] as String?;
final explanation = response['explanation'] as Map?;
final alternatives = response['alternatives'] as List?;

// Create ChatMessage with Phase 2 data
ChatMessage(
  text: response['message'],
  confidenceScore: confidenceScore,
  confidenceLevel: confidenceLevel,
  explanation: explanation,
  alternatives: alternatives,
  ...
);
```

### **2. Render UI Components:**
```dart
// In chat_screen.dart
if (message.confidenceScore != null) {
  // Show confidence badge
  ConfidenceBadge(
    score: message.confidenceScore!,
    level: message.confidenceLevel!,
    onTap: () => _showExplanation(message),
  )
}

if (message.alternatives != null && message.alternatives!.isNotEmpty) {
  // Show alternative picker
  AlternativePicker(
    alternatives: message.alternatives!,
    onSelect: (alt) => _confirmAlternative(alt),
  )
}

// Show feedback buttons
FeedbackButtons(
  messageId: message.id,
  onPositive: () => _logFeedback('helpful'),
  onNegative: () => _showCorrectionDialog(),
)
```

### **3. User Interactions:**
- Tap confidence badge → Show explanation sheet
- Tap "Why?" → Show explanation sheet
- Select alternative → Confirm and update log
- Tap 👍 → Log positive feedback
- Tap 👎 → Show correction dialog → Submit feedback

---

## 📊 **NEW API ENDPOINTS (Optional)**

For Phase 3 feedback collection:

```python
# app/main.py

@app.post("/chat/feedback")
async def submit_feedback(
    message_id: str,
    rating: str,  # "helpful" | "not_helpful"
    correction: Optional[str] = None,
    feedback_type: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Submit user feedback for AI response"""
    # Store in Firestore for Phase 3 learning
    pass

@app.post("/chat/select-alternative")
async def select_alternative(
    message_id: str,
    alternative_index: int,
    current_user: User = Depends(get_current_user)
):
    """User selected an alternative interpretation"""
    # Update fitness log with selected alternative
    # Store selection for learning
    pass
```

---

## ✅ **SUCCESS CRITERIA**

- [ ] Confidence badge displays correctly for all levels
- [ ] Explanation sheet shows complete reasoning
- [ ] Alternatives appear when confidence < 0.85
- [ ] User can select and confirm alternatives
- [ ] Feedback buttons work and log to backend
- [ ] Correction dialog captures user input
- [ ] UI is responsive and performant
- [ ] Animations are smooth
- [ ] Zero regression in existing chat

---

## ⏱️ **TIME BREAKDOWN**

| Component | Time | Priority |
|-----------|------|----------|
| Confidence Badge | 30 min | P0 |
| Explanation Sheet | 45 min | P0 |
| Alternative Picker | 60 min | P0 |
| Feedback Buttons | 30 min | P1 |
| Correction Dialog | 30 min | P1 |
| Integration & Testing | 30 min | P0 |
| **TOTAL** | **3.5 hours** | - |

---

**Next:** Start implementing confidence badge widget!

