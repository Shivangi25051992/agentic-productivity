#!/bin/bash

# Automated iOS App Reload Script
# This script kills, cleans, and restarts the iOS app automatically

echo "🔄 Starting iOS app reload..."

# Step 1: Kill existing Flutter processes
echo "1️⃣ Killing existing Flutter processes..."
pkill -f "flutter run" 2>/dev/null
sleep 2

# Step 2: Clean Flutter build (optional, comment out for faster reloads)
# echo "2️⃣ Cleaning Flutter build..."
# cd /Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity/flutter_app
# flutter clean

# Step 3: Start Flutter app in background
echo "2️⃣ Starting iOS app..."
cd /Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity/flutter_app
flutter run -d D4F4433D-10A6-4B44-904C-150818724C45 --dart-define=API_BASE_URL=http://192.168.0.115:8000 > /tmp/flutter_reload.log 2>&1 &

FLUTTER_PID=$!
echo "✅ Flutter started (PID: $FLUTTER_PID)"

# Step 4: Monitor build progress
echo "3️⃣ Monitoring build progress..."
sleep 5

# Tail the log to show progress
tail -f /tmp/flutter_reload.log &
TAIL_PID=$!

# Wait for "Flutter run key commands" or error
timeout=120
elapsed=0
while [ $elapsed -lt $timeout ]; do
    if grep -q "Flutter run key commands" /tmp/flutter_reload.log; then
        kill $TAIL_PID 2>/dev/null
        echo ""
        echo "🎉 App launched successfully!"
        exit 0
    fi
    
    if grep -q "BUILD FAILED\|Error" /tmp/flutter_reload.log; then
        kill $TAIL_PID 2>/dev/null
        echo ""
        echo "❌ Build failed! Check /tmp/flutter_reload.log for details"
        tail -30 /tmp/flutter_reload.log
        exit 1
    fi
    
    sleep 2
    elapsed=$((elapsed + 2))
done

kill $TAIL_PID 2>/dev/null
echo ""
echo "⏱️ Build timeout after ${timeout}s"
echo "Check /tmp/flutter_reload.log for details"
exit 1

