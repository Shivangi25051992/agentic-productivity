#!/bin/bash

# ══════════════════════════════════════════════════════════════
# 💬 Feedback System Testing Script
# Full monitoring with clean restart
# ══════════════════════════════════════════════════════════════

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${CYAN}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  💬 FEEDBACK SYSTEM - FULL TESTING SETUP                         ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ════════════════════════════════════════════════════════════════
# STEP 1: KILL EXISTING PROCESSES
# ════════════════════════════════════════════════════════════════

echo -e "${YELLOW}📋 STEP 1: Killing Existing Processes...${NC}"
echo ""

# Kill backend
echo -e "   ${BLUE}→${NC} Stopping backend (uvicorn)..."
pkill -f "uvicorn.*main:app" 2>/dev/null || echo "   ℹ️  No backend running"
sleep 1

# Kill frontend
echo -e "   ${BLUE}→${NC} Stopping frontend (flutter)..."
pkill -f "flutter.*run" 2>/dev/null || echo "   ℹ️  No frontend running"
pkill -f "dart.*tool.*run" 2>/dev/null || true
sleep 1

echo -e "   ${GREEN}✅ All processes stopped${NC}"
echo ""

# ════════════════════════════════════════════════════════════════
# STEP 2: CLEAR CACHES
# ════════════════════════════════════════════════════════════════

echo -e "${YELLOW}📋 STEP 2: Clearing Caches...${NC}"
echo ""

# Clear Python cache
echo -e "   ${BLUE}→${NC} Clearing Python __pycache__..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Clear Flutter cache
echo -e "   ${BLUE}→${NC} Clearing Flutter build cache..."
cd flutter_app
flutter clean > /dev/null 2>&1 || true
cd ..

# Clear old log files
echo -e "   ${BLUE}→${NC} Clearing old log files..."
rm -f /tmp/backend_*.log 2>/dev/null || true
rm -f /tmp/frontend_*.log 2>/dev/null || true
rm -f /tmp/feedback_test_*.log 2>/dev/null || true

echo -e "   ${GREEN}✅ All caches cleared${NC}"
echo ""

# ════════════════════════════════════════════════════════════════
# STEP 3: START BACKEND WITH MONITORING
# ════════════════════════════════════════════════════════════════

echo -e "${YELLOW}📋 STEP 3: Starting Backend with Full Monitoring...${NC}"
echo ""

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKEND_LOG="/tmp/feedback_backend_${TIMESTAMP}.log"

echo -e "   ${BLUE}→${NC} Log file: ${BACKEND_LOG}"
echo -e "   ${BLUE}→${NC} Starting uvicorn on port 8000..."

cd /Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity

# Start backend in background with logging
nohup uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > "${BACKEND_LOG}" 2>&1 &
BACKEND_PID=$!

echo -e "   ${BLUE}→${NC} Backend PID: ${BACKEND_PID}"
echo -e "   ${BLUE}→${NC} Waiting for backend to start..."

# Wait for backend to be ready
for i in {1..20}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "   ${GREEN}✅ Backend is running!${NC}"
        break
    fi
    if [ $i -eq 20 ]; then
        echo -e "   ${RED}❌ Backend failed to start${NC}"
        echo -e "   ${RED}Check log: ${BACKEND_LOG}${NC}"
        exit 1
    fi
    sleep 1
done

echo -e "   ${GREEN}✅ Backend health check passed${NC}"
echo ""

# ════════════════════════════════════════════════════════════════
# STEP 4: START MONITORING
# ════════════════════════════════════════════════════════════════

echo -e "${YELLOW}📋 STEP 4: Starting Real-Time Monitoring...${NC}"
echo ""

MONITOR_LOG="/tmp/feedback_monitor_${TIMESTAMP}.log"

echo -e "   ${BLUE}→${NC} Monitor log: ${MONITOR_LOG}"
echo -e "   ${BLUE}→${NC} Starting background monitor..."

# Monitor backend logs for feedback activity
tail -f "${BACKEND_LOG}" 2>/dev/null | grep --line-buffered -E "FEEDBACK|ALTERNATIVE|POST /chat/feedback|POST /chat/select|💬|🔀|✅|❌" > "${MONITOR_LOG}" &
MONITOR_PID=$!

echo -e "   ${GREEN}✅ Monitoring active (PID: ${MONITOR_PID})${NC}"
echo ""

# ════════════════════════════════════════════════════════════════
# STEP 5: DISPLAY TESTING INSTRUCTIONS
# ════════════════════════════════════════════════════════════════

echo -e "${CYAN}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  🎯 READY FOR TESTING!                                           ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${GREEN}✅ Backend: Running on http://localhost:8000${NC}"
echo -e "${GREEN}✅ Monitoring: Active${NC}"
echo -e "${YELLOW}⏳ Frontend: Start manually (see instructions below)${NC}"
echo ""

echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${MAGENTA}  📋 FRONTEND STARTUP INSTRUCTIONS${NC}"
echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${CYAN}Open a NEW terminal and run:${NC}"
echo ""
echo -e "${BLUE}cd /Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity/flutter_app${NC}"
echo -e "${BLUE}flutter run -d chrome --web-port=9000${NC}"
echo ""
echo -e "${YELLOW}Then in Chrome:${NC}"
echo -e "   1. Open http://localhost:9000"
echo -e "   2. Press ${GREEN}Cmd+Shift+R${NC} (hard refresh)"
echo -e "   3. Open DevTools (F12)"
echo -e "   4. Check Console tab for logs"
echo ""

echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${MAGENTA}  🧪 TEST SCENARIOS${NC}"
echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${CYAN}TEST 1: Positive Feedback (👍)${NC}"
echo -e "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${YELLOW}Actions:${NC}"
echo -e "   1. Go to Chat tab"
echo -e "   2. Send message: ${GREEN}\"2 eggs\"${NC}"
echo -e "   3. Wait for AI response"
echo -e "   4. Click ${GREEN}👍 thumbs up${NC} button"
echo ""
echo -e "${YELLOW}Expected Results:${NC}"
echo -e "   ${GREEN}✓${NC} Success message: \"Thank you for your feedback!\""
echo -e "   ${GREEN}✓${NC} Green SnackBar appears for 2 seconds"
echo ""
echo -e "${YELLOW}Backend Log (watch this terminal):${NC}"
echo -e "   ${GREEN}✓${NC} ${CYAN}POST /chat HTTP/1.1${NC} 200"
echo -e "   ${GREEN}✓${NC} ${CYAN}💬 [FEEDBACK] User: wQHjQvwt... | Rating: helpful${NC}"
echo -e "   ${GREEN}✓${NC} ${CYAN}   Feedback ID: [some-id]${NC}"
echo ""
echo -e "${YELLOW}Frontend Console (F12):${NC}"
echo -e "   ${GREEN}✓${NC} ${CYAN}📊 [FEEDBACK CAPTURED] Positive feedback for message: ...${NC}"
echo -e "   ${GREEN}✓${NC} ${CYAN}✅ [API] Positive feedback saved: feedback_...${NC}"
echo ""
echo -e "${YELLOW}Firestore Verification:${NC}"
echo -e "   ${GREEN}✓${NC} Go to: ${BLUE}https://console.firebase.google.com/project/productivityai-mvp/firestore${NC}"
echo -e "   ${GREEN}✓${NC} Collection: ${CYAN}user_feedback${NC}"
echo -e "   ${GREEN}✓${NC} Should see new document with:"
echo -e "      • rating: \"helpful\""
echo -e "      • corrections: []"
echo -e "      • message_id: timestamp"
echo ""
echo ""

echo -e "${CYAN}TEST 2: Negative Feedback with Corrections (👎)${NC}"
echo -e "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${YELLOW}Actions:${NC}"
echo -e "   1. Send message: ${GREEN}\"1 banana\"${NC}"
echo -e "   2. Wait for AI response"
echo -e "   3. Click ${RED}👎 thumbs down${NC} button"
echo -e "   4. In dialog, check:"
echo -e "      ${GREEN}✓${NC} Wrong calories"
echo -e "      ${GREEN}✓${NC} Wrong quantity"
echo -e "   5. Type comment: ${GREEN}\"Should be 150 calories not 105\"${NC}"
echo -e "   6. Click ${GREEN}Submit${NC}"
echo ""
echo -e "${YELLOW}Expected Results:${NC}"
echo -e "   ${GREEN}✓${NC} Dialog appears with correction options"
echo -e "   ${GREEN}✓${NC} Checkboxes are clickable"
echo -e "   ${GREEN}✓${NC} Success message: \"Feedback received. AI will learn from this!\""
echo -e "   ${GREEN}✓${NC} Blue SnackBar appears"
echo -e "   ${GREEN}✓${NC} Form clears automatically"
echo ""
echo -e "${YELLOW}Backend Log:${NC}"
echo -e "   ${GREEN}✓${NC} ${CYAN}POST /chat/feedback HTTP/1.1${NC} 200"
echo -e "   ${GREEN}✓${NC} ${CYAN}💬 [FEEDBACK] User: wQHjQvwt... | Rating: not_helpful${NC}"
echo -e "   ${GREEN}✓${NC} ${CYAN}   Corrections: ['calories', 'quantity']${NC}"
echo -e "   ${GREEN}✓${NC} ${CYAN}   Comment: Should be 150 calories not 105${NC}"
echo -e "   ${GREEN}✓${NC} ${CYAN}   Feedback ID: [some-id]${NC}"
echo ""
echo -e "${YELLOW}Frontend Console:${NC}"
echo -e "   ${GREEN}✓${NC} ${CYAN}📊 [FEEDBACK CAPTURED] Negative feedback for message: ...${NC}"
echo -e "   ${GREEN}✓${NC} ${CYAN}   Corrections selected: [calories, quantity]${NC}"
echo -e "   ${GREEN}✓${NC} ${CYAN}   Comment: Should be 150 calories not 105${NC}"
echo -e "   ${GREEN}✓${NC} ${CYAN}✅ [API] Negative feedback saved: feedback_...${NC}"
echo ""
echo -e "${YELLOW}Firestore Verification:${NC}"
echo -e "   ${GREEN}✓${NC} New document in ${CYAN}user_feedback${NC} with:"
echo -e "      • rating: \"not_helpful\""
echo -e "      • corrections: [\"calories\", \"quantity\"]"
echo -e "      • comment: \"Should be 150 calories not 105\""
echo ""
echo ""

echo -e "${CYAN}TEST 3: Alternative Selection (Low Confidence)${NC}"
echo -e "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${YELLOW}Actions:${NC}"
echo -e "   1. Send message: ${GREEN}\"rice\"${NC} or ${GREEN}\"a bit of rice\"${NC}"
echo -e "   2. Wait for AI response (should show alternatives)"
echo -e "   3. Select an alternative (not the first one)"
echo -e "   4. Click ${GREEN}Confirm${NC}"
echo ""
echo -e "${YELLOW}Expected Results:${NC}"
echo -e "   ${GREEN}✓${NC} Alternative picker shows multiple options"
echo -e "   ${GREEN}✓${NC} Can select one option (radio button)"
echo -e "   ${GREEN}✓${NC} Confirm button shows loading spinner"
echo -e "   ${GREEN}✓${NC} Success message: \"Updated! Thanks for the feedback.\""
echo -e "   ${GREEN}✓${NC} Green SnackBar appears"
echo ""
echo -e "${YELLOW}Backend Log:${NC}"
echo -e "   ${GREEN}✓${NC} ${CYAN}POST /chat/select-alternative HTTP/1.1${NC} 200"
echo -e "   ${GREEN}✓${NC} ${CYAN}🔀 [ALTERNATIVE] User: wQHjQvwt... | Selected: Index 1${NC}"
echo -e "   ${GREEN}✓${NC} ${CYAN}   Alternative: Small portion of Rice (144 kcal)...${NC}"
echo -e "   ${GREEN}✓${NC} ${CYAN}   Selection ID: [some-id]${NC}"
echo ""
echo -e "${YELLOW}Frontend Console:${NC}"
echo -e "   ${GREEN}✓${NC} ${CYAN}📊 [ALTERNATIVE SELECTED] Index: 1${NC}"
echo -e "   ${GREEN}✓${NC} ${CYAN}   Interpretation: Small portion of Rice${NC}"
echo -e "   ${GREEN}✓${NC} ${CYAN}✅ [API] Alternative selection saved: selection_...${NC}"
echo ""
echo -e "${YELLOW}Firestore Verification:${NC}"
echo -e "   ${GREEN}✓${NC} New document in ${CYAN}alternative_selections${NC} with:"
echo -e "      • selected_index: 1"
echo -e "      • selected_alternative: {...}"
echo ""
echo ""

echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${MAGENTA}  📊 MONITORING COMMANDS${NC}"
echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${CYAN}Watch Backend Logs:${NC}"
echo -e "${BLUE}tail -f ${BACKEND_LOG}${NC}"
echo ""

echo -e "${CYAN}Watch Feedback Activity Only:${NC}"
echo -e "${BLUE}tail -f ${MONITOR_LOG}${NC}"
echo ""

echo -e "${CYAN}Check Backend Health:${NC}"
echo -e "${BLUE}curl http://localhost:8000/health${NC}"
echo ""

echo -e "${CYAN}View Firestore Console:${NC}"
echo -e "${BLUE}https://console.firebase.google.com/project/productivityai-mvp/firestore${NC}"
echo ""

echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${MAGENTA}  🛑 CLEANUP COMMANDS${NC}"
echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${CYAN}Stop Backend:${NC}"
echo -e "${BLUE}kill ${BACKEND_PID}${NC}"
echo ""

echo -e "${CYAN}Stop Monitor:${NC}"
echo -e "${BLUE}kill ${MONITOR_PID}${NC}"
echo ""

echo -e "${CYAN}Stop All:${NC}"
echo -e "${BLUE}pkill -f \"uvicorn.*main:app\"${NC}"
echo -e "${BLUE}pkill -f \"flutter.*run\"${NC}"
echo ""

echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${GREEN}✅ SETUP COMPLETE - READY FOR TESTING!${NC}"
echo ""
echo -e "${YELLOW}⏳ Waiting for you to start frontend and begin testing...${NC}"
echo ""
echo -e "${CYAN}I'm watching the logs - send your messages and I'll report what I see!${NC}"
echo ""

# Keep monitoring active
tail -f "${BACKEND_LOG}" | grep --line-buffered --color=always -E "FEEDBACK|ALTERNATIVE|POST /chat/feedback|POST /chat/select|💬|🔀|✅|❌"




