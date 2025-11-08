#!/bin/bash

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  🚀 Starting All Services for Feedback Testing          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Set working directory
cd /Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity

# Kill existing processes
echo "🛑 Stopping existing processes..."
pkill -f "uvicorn.*main:app" 2>/dev/null || true
pkill -f "flutter.*run" 2>/dev/null || true
sleep 2
echo "✅ Processes stopped"
echo ""

# Clear caches
echo "🧹 Clearing caches..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
echo "✅ Caches cleared"
echo ""

# Start backend
echo "🚀 Starting backend..."
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKEND_LOG="/tmp/feedback_backend_${TIMESTAMP}.log"
echo "📁 Log: ${BACKEND_LOG}"

nohup uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > "${BACKEND_LOG}" 2>&1 &
BACKEND_PID=$!
echo "   PID: ${BACKEND_PID}"
echo "   Waiting for startup..."

# Wait for backend
for i in {1..15}; do
    sleep 1
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend is READY! (http://localhost:8000)"
        break
    fi
    if [ $i -eq 15 ]; then
        echo "❌ Backend failed to start"
        echo "Check log: ${BACKEND_LOG}"
        exit 1
    fi
done
echo ""

# Start frontend
echo "🚀 Starting frontend..."
cd flutter_app
flutter clean > /dev/null 2>&1 || true
nohup flutter run -d chrome --web-port=9000 > /tmp/flutter_${TIMESTAMP}.log 2>&1 &
FLUTTER_PID=$!
cd ..
echo "   PID: ${FLUTTER_PID}"
echo "   Waiting for Chrome to open..."
echo "   This may take 30-60 seconds..."
echo ""

# Monitor backend for feedback activity
echo "📊 Starting monitoring..."
MONITOR_LOG="/tmp/feedback_monitor_${TIMESTAMP}.log"
tail -f "${BACKEND_LOG}" 2>/dev/null | grep --line-buffered -E "FEEDBACK|ALTERNATIVE|💬|🔀|POST /chat/feedback|POST /chat/select" > "${MONITOR_LOG}" &
MONITOR_PID=$!
echo "   Monitor PID: ${MONITOR_PID}"
echo ""

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  ✅ ALL SERVICES RUNNING!                                ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "🌐 Frontend: http://localhost:9000 (opening in Chrome...)"
echo "🔌 Backend:  http://localhost:8000"
echo ""
echo "📊 MONITORING LOGS:"
echo "   Backend:  ${BACKEND_LOG}"
echo "   Monitor:  ${MONITOR_LOG}"
echo "   Flutter:  /tmp/flutter_${TIMESTAMP}.log"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  🧪 WHEN CHROME OPENS:"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "1. Press Cmd+Shift+R (hard refresh)"
echo "2. Open DevTools (F12) → Console tab"
echo "3. Login → Go to Chat"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  💬 TEST THESE 3 SCENARIOS:"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "TEST 1: Send '2 eggs' → Click 👍"
echo "TEST 2: Send '1 banana' → Click 👎 → Select corrections → Submit"
echo "TEST 3: Send 'a bit of rice' → Select alternative → Confirm"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  👀 WHAT TO WATCH:"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "✅ Green/Blue success messages in browser"
echo "✅ Console logs: 📊 [FEEDBACK CAPTURED]"
echo "✅ This terminal shows: 💬 [FEEDBACK] messages"
echo "✅ Firestore: https://console.firebase.google.com/project/productivityai-mvp/firestore"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "⏳ Monitoring active - I'll show feedback activity below..."
echo ""

# Display monitoring feed
tail -f "${MONITOR_LOG}"




