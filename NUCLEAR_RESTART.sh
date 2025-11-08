#!/bin/bash

# 🧹 NUCLEAR RESTART SCRIPT - Complete Fresh Start
# Run this AFTER laptop restart for cleanest possible state

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         🧹 NUCLEAR RESTART - COMPLETE CLEAN START             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Project directory
PROJECT_DIR="/Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity"

echo "📍 Working directory: $PROJECT_DIR"
echo ""

# ============================================================================
# STEP 1: KILL ALL PROCESSES (just in case)
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔪 STEP 1: Killing any remaining processes..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Kill backend (port 8000)
if lsof -ti:8000 > /dev/null 2>&1; then
  lsof -ti:8000 | xargs kill -9 2>/dev/null
  echo "${GREEN}✅ Killed backend on port 8000${NC}"
else
  echo "${BLUE}ℹ️  No process on port 8000${NC}"
fi

# Kill Flutter (port 9001)
if lsof -ti:9001 > /dev/null 2>&1; then
  lsof -ti:9001 | xargs kill -9 2>/dev/null
  echo "${GREEN}✅ Killed Flutter on port 9001${NC}"
else
  echo "${BLUE}ℹ️  No process on port 9001${NC}"
fi

# Kill any Flutter processes
pkill -f "flutter run" 2>/dev/null
echo "${GREEN}✅ Killed all Flutter processes${NC}"

# Kill any Python uvicorn processes
pkill -f "uvicorn" 2>/dev/null
echo "${GREEN}✅ Killed all Uvicorn processes${NC}"

echo ""
sleep 2

# ============================================================================
# STEP 2: CLEAN FLUTTER
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧼 STEP 2: Cleaning Flutter build cache..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd "$PROJECT_DIR/flutter_app" || exit

echo "${YELLOW}⏳ Running flutter clean...${NC}"
flutter clean

echo "${YELLOW}⏳ Removing build directories...${NC}"
rm -rf build/ .dart_tool/ .flutter-plugins .flutter-plugins-dependencies

echo "${YELLOW}⏳ Getting Flutter dependencies...${NC}"
flutter pub get

echo "${GREEN}✅ Flutter cleaned and dependencies installed${NC}"
echo ""
sleep 2

# ============================================================================
# STEP 3: START BACKEND
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 STEP 3: Starting Backend (port 8000)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd "$PROJECT_DIR" || exit

# Start backend in background
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > backend_live.log 2>&1 &
BACKEND_PID=$!

echo "${YELLOW}⏳ Waiting for backend to start (5 seconds)...${NC}"
sleep 5

# Check if backend is running
if lsof -ti:8000 > /dev/null 2>&1; then
  echo "${GREEN}✅ Backend running on http://localhost:8000 (PID: $BACKEND_PID)${NC}"
  echo "${BLUE}📝 Backend logs: $PROJECT_DIR/backend_live.log${NC}"
else
  echo "${RED}❌ Backend failed to start! Check backend_live.log${NC}"
  tail -20 backend_live.log
  exit 1
fi

echo ""
sleep 2

# ============================================================================
# STEP 4: START FLUTTER
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 STEP 4: Starting Flutter (port 9001)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd "$PROJECT_DIR/flutter_app" || exit

# Start Flutter in background
nohup flutter run -d chrome --web-port 9001 --no-cache-sksl > ../flutter_live.log 2>&1 &
FLUTTER_PID=$!

echo "${YELLOW}⏳ Flutter is starting (this takes 30-60 seconds)...${NC}"
echo "${BLUE}📝 Flutter logs: $PROJECT_DIR/flutter_live.log${NC}"

# Wait and monitor
for i in {1..60}; do
  if grep -q "Application finished" ../flutter_live.log 2>/dev/null; then
    echo "${GREEN}✅ Flutter started successfully!${NC}"
    break
  fi
  echo -n "."
  sleep 1
done

echo ""

# Final check
if grep -q "Application finished" ../flutter_live.log 2>/dev/null; then
  echo "${GREEN}✅ Flutter running at http://localhost:9001 (PID: $FLUTTER_PID)${NC}"
else
  echo "${YELLOW}⚠️  Flutter may still be starting. Check flutter_live.log${NC}"
fi

echo ""
sleep 2

# ============================================================================
# STEP 5: VERIFY EVERYTHING IS RUNNING
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ STEP 5: Verification"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "📊 Service Status:"
echo "  └─ Backend:  $(lsof -ti:8000 > /dev/null 2>&1 && echo "${GREEN}✅ Running${NC}" || echo "${RED}❌ Down${NC}")"
echo "  └─ Flutter:  $(lsof -ti:9001 > /dev/null 2>&1 && echo "${GREEN}✅ Running${NC}" || echo "${YELLOW}⏳ Starting...${NC}")"

echo ""
echo "📝 Log Files:"
echo "  └─ Backend:  tail -f $PROJECT_DIR/backend_live.log"
echo "  └─ Flutter:  tail -f $PROJECT_DIR/flutter_live.log"

echo ""
echo "🌐 URLs:"
echo "  └─ Backend:  ${BLUE}http://localhost:8000${NC}"
echo "  └─ Frontend: ${BLUE}http://localhost:9001${NC}"

echo ""
sleep 2

# ============================================================================
# STEP 6: BROWSER INSTRUCTIONS
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 STEP 6: BROWSER CACHE CLEAR (MANUAL STEPS)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "${YELLOW}⚠️  IMPORTANT: You MUST clear browser cache manually!${NC}"
echo ""
echo "Follow these steps IN YOUR BROWSER:"
echo ""
echo "  1️⃣  Open Chrome (or your browser)"
echo "  2️⃣  Go to: ${BLUE}http://localhost:9001${NC}"
echo "  3️⃣  Press F12 (or Cmd+Option+I on Mac)"
echo "  4️⃣  Click 'Application' tab at top"
echo "  5️⃣  Left sidebar → 'Storage' → 'Clear site data'"
echo "  6️⃣  Check ALL boxes"
echo "  7️⃣  Click 'Clear site data' button"
echo "  8️⃣  Left sidebar → 'Service Workers' → Unregister all"
echo "  9️⃣  Close DevTools"
echo "  🔟  Hard refresh: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)"
echo "  1️⃣1️⃣  Close browser COMPLETELY (Cmd+Q or Alt+F4)"
echo "  1️⃣2️⃣  Wait 10 seconds"
echo "  1️⃣3️⃣  Reopen browser → ${BLUE}http://localhost:9001${NC}"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 SCRIPT COMPLETE!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "${GREEN}✅ Backend and Flutter are running!${NC}"
echo ""
echo "Next steps:"
echo "  1. Follow browser cache clear steps above"
echo "  2. Login to app at http://localhost:9001"
echo "  3. Check if user messages appear as chat bubbles (not green pills)"
echo ""
echo "${BLUE}💡 TIP: Keep this terminal open to see logs${NC}"
echo ""




