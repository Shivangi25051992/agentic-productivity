#!/bin/bash

echo "🔍 MONITORING MEAL PLAN GENERATION"
echo "=================================="
echo ""
echo "Watching backend logs for:"
echo "  - PARALLEL GENERATION messages"
echo "  - Performance metrics"
echo "  - Free tier tracking"
echo ""
echo "Press Ctrl+C to stop"
echo ""

tail -f /Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity/backend.log | grep --line-buffered -E "PARALLEL|PERFORMANCE|FREE TIER|generate_meal_plan|Speed improvement|API call|ERROR"


