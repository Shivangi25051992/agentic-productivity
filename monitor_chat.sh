#!/bin/bash
# Monitor chat request in real-time

echo "================================================"
echo "🔍 MONITORING SETUP"
echo "================================================"
echo ""
echo "✅ Ready to monitor!"
echo ""
echo "📝 Please send '2 eggs' in the chat NOW..."
echo ""
echo "Monitoring for 15 seconds..."
echo ""

# Monitor backend logs (look for Phase 2 related output)
timeout 15 tail -f /Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity/backend.log 2>/dev/null &
TAIL_PID=$!

sleep 15

# Kill tail if still running
kill $TAIL_PID 2>/dev/null

echo ""
echo "================================================"
echo "✅ Monitoring complete"
echo "================================================"




