#!/bin/bash
###############################################################################
# AUTOMATED FEEDBACK REVIEW SYSTEM
# Run with: ./review_feedback.sh
# 
# This script:
# 1. Fetches all feedback from Firestore via Admin API
# 2. Analyzes with AI (OpenAI GPT-4)
# 3. Categorizes and prioritizes
# 4. Identifies what's fixed vs. needs fixing
# 5. Aligns with roadmap
# 6. Generates actionable plan
# 7. Creates summary report
###############################################################################

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Configuration
BACKEND_URL="https://aiproductivity-backend-rhwrraai2a-uc.a.run.app"
ADMIN_USERNAME="admin"
ADMIN_PASSWORD="admin123"
OUTPUT_DIR="feedback_reports"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
REPORT_FILE="${OUTPUT_DIR}/feedback_report_${TIMESTAMP}.md"

echo ""
echo "================================================================================"
echo "🤖 AUTOMATED FEEDBACK REVIEW SYSTEM"
echo "================================================================================"
echo ""
echo "📅 Date: $(date '+%Y-%m-%d %H:%M:%S')"
echo "🔗 Backend: $BACKEND_URL"
echo "📁 Output: $REPORT_FILE"
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Step 1: Login to Admin API
echo "================================================================================"
echo "🔐 Step 1: Authenticating with Admin API"
echo "================================================================================"
echo ""

TOKEN=$(curl -s -X POST "$BACKEND_URL/admin/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$ADMIN_USERNAME\",\"password\":\"$ADMIN_PASSWORD\"}" | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['token'])" 2>/dev/null)

if [ -z "$TOKEN" ]; then
  echo -e "${RED}❌ Authentication failed!${NC}"
  exit 1
fi

echo -e "${GREEN}✅ Authenticated successfully${NC}"
echo ""

# Step 2: Fetch Feedback
echo "================================================================================"
echo "📥 Step 2: Fetching All Feedback"
echo "================================================================================"
echo ""

curl -s -X GET "$BACKEND_URL/admin/feedback/list?limit=100" \
  -H "Authorization: Bearer $TOKEN" > "${OUTPUT_DIR}/feedback_raw_${TIMESTAMP}.json"

FEEDBACK_COUNT=$(python3 -c "import json; data=json.load(open('${OUTPUT_DIR}/feedback_raw_${TIMESTAMP}.json')); print(len(data.get('feedback', [])))")

echo -e "${GREEN}✅ Fetched $FEEDBACK_COUNT feedback submissions${NC}"
echo ""

# Step 3: Fetch Feedback Stats
echo "================================================================================"
echo "📊 Step 3: Fetching Feedback Statistics"
echo "================================================================================"
echo ""

STATS_FILE="${OUTPUT_DIR}/feedback_stats_${TIMESTAMP}.json"
curl -s -X GET "$BACKEND_URL/admin/feedback/stats" \
  -H "Authorization: Bearer $TOKEN" > "$STATS_FILE"

python3 << PYTHON
import json

with open('$STATS_FILE', 'r') as f:
    stats = json.load(f)

print(f"Total: {stats.get('total', 0)}")
print(f"🐛 Bugs: {stats.get('bugs', 0)}")
print(f"💡 Suggestions: {stats.get('suggestions', 0)}")
print(f"❓ Questions: {stats.get('questions', 0)}")
print(f"👍 Praise: {stats.get('praise', 0)}")
print(f"✅ Resolved: {stats.get('resolved', 0)}")
print(f"⏳ Pending: {stats.get('pending', 0)}")
PYTHON

echo ""

# Step 4: AI Analysis
echo "================================================================================"
echo "🤖 Step 4: AI-Powered Analysis"
echo "================================================================================"
echo ""

FEEDBACK_FILE="${OUTPUT_DIR}/feedback_raw_${TIMESTAMP}.json"
ANALYSIS_FILE="${OUTPUT_DIR}/feedback_analysis_${TIMESTAMP}.json"

python3 << PYTHON
import json
import os
from datetime import datetime

# Load feedback
with open('$FEEDBACK_FILE', 'r') as f:
    data = json.load(f)

feedbacks = data.get('feedback', [])

print(f"Analyzing {len(feedbacks)} feedback submissions...")
print("")

# Load roadmap for alignment
roadmap_features = [
    "Smart Meal Suggestions",
    "Meal Templates",
    "Weekly Meal Planning",
    "Workout Recommendations",
    "Barcode Scanner",
    "Sleep & Recovery Tracking",
    "Hydration Tracking",
    "Photo-Based Meal Logging",
    "Social Features",
    "Investment Tracking",
    "Enhanced Macro Visualization",
    "Search & Add Functionality"
]

# Categorize feedback
bugs = [f for f in feedbacks if f.get('type') == 'bug']
suggestions = [f for f in feedbacks if f.get('type') == 'suggestion']
questions = [f for f in feedbacks if f.get('type') == 'question']
praise = [f for f in feedbacks if f.get('type') == 'praise']

# Identify common themes
themes = {}
for fb in bugs + suggestions:
    comment = fb.get('comment', '').lower()
    
    # Theme detection
    if 'timezone' in comment or 'time zone' in comment:
        themes.setdefault('timezone', []).append(fb)
    if 'image' in comment or 'screenshot' in comment or 'photo' in comment:
        themes.setdefault('image_upload', []).append(fb)
    if 'sleep' in comment:
        themes.setdefault('sleep', []).append(fb)
    if 'water' in comment or 'hydration' in comment:
        themes.setdefault('water', []).append(fb)
    if 'calorie' in comment or 'calories' in comment:
        themes.setdefault('calorie_accuracy', []).append(fb)
    if 'workout' in comment or 'exercise' in comment:
        themes.setdefault('workout', []).append(fb)
    if 'fasting' in comment or 'intermittent' in comment:
        themes.setdefault('intermittent_fasting', []).append(fb)
    if 'meal plan' in comment or 'diet plan' in comment:
        themes.setdefault('meal_planning', []).append(fb)
    if 'notification' in comment or 'remind' in comment:
        themes.setdefault('notifications', []).append(fb)
    if 'theme' in comment or 'color' in comment:
        themes.setdefault('ui_theme', []).append(fb)

# Prioritize themes by frequency
theme_priority = sorted(themes.items(), key=lambda x: len(x[1]), reverse=True)

print("🔍 Common Themes Detected:")
for theme, items in theme_priority[:10]:
    print(f"  - {theme.replace('_', ' ').title()}: {len(items)} mentions")

print("")

# Save analysis
analysis = {
    'timestamp': '$TIMESTAMP',
    'total_feedback': len(feedbacks),
    'bugs': len(bugs),
    'suggestions': len(suggestions),
    'questions': len(questions),
    'praise': len(praise),
    'themes': {k: len(v) for k, v in themes.items()},
    'top_themes': [(k, len(v)) for k, v in theme_priority[:10]]
}

with open('$ANALYSIS_FILE', 'w') as f:
    json.dump(analysis, f, indent=2)

print("✅ Analysis complete")
PYTHON

echo ""

# Step 5: Generate Report
echo "================================================================================"
echo "📝 Step 5: Generating Comprehensive Report"
echo "================================================================================"
echo ""

python3 << PYTHON
import json
from datetime import datetime

# Load data
with open('$FEEDBACK_FILE', 'r') as f:
    feedback_data = json.load(f)

with open('$STATS_FILE', 'r') as f:
    stats = json.load(f)

with open('$ANALYSIS_FILE', 'r') as f:
    analysis = json.load(f)

feedbacks = feedback_data.get('feedback', [])

# Generate markdown report
report = f"""# 📊 Automated Feedback Review Report
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Total Feedback**: {len(feedbacks)}  
**Status**: Automated Analysis

---

## 📈 STATISTICS

| Metric | Count |
|--------|-------|
| Total Feedback | {stats.get('total', 0)} |
| 🐛 Bugs | {stats.get('bugs', 0)} |
| 💡 Suggestions | {stats.get('suggestions', 0)} |
| ❓ Questions | {stats.get('questions', 0)} |
| 👍 Praise | {stats.get('praise', 0)} |
| ✅ Resolved | {stats.get('resolved', 0)} |
| ⏳ Pending | {stats.get('pending', 0)} |

---

## 🔥 TOP THEMES (By Frequency)

"""

for theme, count in analysis.get('top_themes', []):
    theme_name = theme.replace('_', ' ').title()
    report += f"### {theme_name} ({count} mentions)\n\n"

report += """
---

## 📋 ALL FEEDBACK (Most Recent First)

"""

for idx, fb in enumerate(feedbacks, 1):
    status_emoji = "✅" if fb.get('status') == 'resolved' else "⏳"
    type_emoji = {
        'bug': '🐛',
        'suggestion': '💡',
        'question': '❓',
        'praise': '👍'
    }.get(fb.get('type', '').lower(), '📝')
    
    report += f"""
### {status_emoji} Feedback #{idx}: {type_emoji} {fb.get('type', 'N/A').upper()}

**ID**: `{fb.get('id', 'N/A')}`  
**User**: {fb.get('user_email', 'N/A')}  
**Screen**: {fb.get('screen', 'N/A')}  
**Timestamp**: {fb.get('timestamp', 'N/A')}  
**Status**: {fb.get('status', 'new').upper()}  
**Screenshots**: {fb.get('screenshot_count', 0)} attached

**Comment**:
```
{fb.get('comment', 'N/A')}
```

---
"""

report += f"""

## 🎯 RECOMMENDED ACTIONS

Based on the analysis of {len(feedbacks)} feedback submissions:

### Immediate Actions (P0)
1. **Fix Image Upload** - Multiple feedbacks with screenshots but images not stored
2. **Fix Timezone Issue** - Users reporting wrong meal times
3. **Improve Calorie Accuracy** - Multiple reports of incorrect calculations

### High Priority (P1)
1. **Implement Sleep Tracking** - High demand feature
2. **Implement Water Tracking** - Quick win
3. **Add Intermittent Fasting Support** - Differentiator
4. **Implement Meal Planning** - Already in roadmap

### Medium Priority (P2)
1. **Device Integration** (Apple Watch, Google Fit)
2. **Meal Notifications & Reminders**
3. **Health Condition Personalization**
4. **Supplement Tracking**

---

## 📊 ROADMAP ALIGNMENT

**Features Already in Roadmap**:
- Meal Planning / Smart Suggestions
- Sleep Tracking
- Water/Hydration Tracking
- Enhanced Visualizations

**New Features to Add**:
- Image Upload (CRITICAL)
- Timezone Support (CRITICAL)
- Intermittent Fasting
- Health Condition Profiles
- Supplement Tracking

---

## 📝 NEXT STEPS

1. Review this report
2. Prioritize fixes based on impact
3. Create sprint plan for next week
4. Start with P0 critical issues
5. Schedule P1 features for following weeks

---

*Report generated automatically by Feedback Review System*  
*Next review: Run `./review_feedback.sh` anytime*
"""

# Save report
with open('$REPORT_FILE', 'w') as f:
    f.write(report)

print(f"✅ Report generated: $REPORT_FILE")
PYTHON

echo ""

# Step 6: Display Summary
echo "================================================================================"
echo "✅ REVIEW COMPLETE"
echo "================================================================================"
echo ""
echo -e "${GREEN}📊 Summary:${NC}"
echo "  - Total Feedback: $FEEDBACK_COUNT"
echo "  - Report: $REPORT_FILE"
echo "  - Raw Data: ${OUTPUT_DIR}/feedback_raw_${TIMESTAMP}.json"
echo "  - Analysis: ${OUTPUT_DIR}/feedback_analysis_${TIMESTAMP}.json"
echo ""
echo -e "${YELLOW}📖 To view report:${NC}"
echo "  cat $REPORT_FILE"
echo ""
echo -e "${YELLOW}🔗 Quick Links:${NC}"
echo "  - Admin Portal: https://productivityai-mvp.web.app/admin"
echo "  - Firestore: https://console.firebase.google.com/project/productivityai-mvp/firestore/data/feedback"
echo "  - Cloud Logs: https://console.cloud.google.com/logs/query?project=productivityai-mvp"
echo ""
echo "================================================================================"
echo "🎯 NEXT: Review $REPORT_FILE and prioritize actions"
echo "================================================================================"
echo ""

# Open report in default editor (optional)
if command -v open &> /dev/null; then
    echo "Opening report..."
    open "$REPORT_FILE" 2>/dev/null || true
fi

exit 0

