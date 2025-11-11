#!/bin/bash

# 🔍 Live Chat Monitoring Script
# Monitors backend health and chat requests in real-time

echo "🔍 Starting Live Chat Monitoring..."
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check backend health
check_backend() {
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend: HEALTHY${NC}"
        return 0
    else
        echo -e "${RED}❌ Backend: DOWN${NC}"
        return 1
    fi
}

# Function to monitor chat requests
monitor_chat() {
    echo ""
    echo "📊 Monitoring chat requests (last 10 lines):"
    echo "============================================"
    tail -f backend.log | grep --line-buffered -E "POST /chat|GET /chat/history|⏱️|✅|❌|ERROR" | while read line; do
        if [[ $line == *"ERROR"* ]] || [[ $line == *"❌"* ]]; then
            echo -e "${RED}$line${NC}"
        elif [[ $line == *"✅"* ]]; then
            echo -e "${GREEN}$line${NC}"
        elif [[ $line == *"⏱️"* ]]; then
            echo -e "${YELLOW}$line${NC}"
        else
            echo "$line"
        fi
    done
}

# Main monitoring loop
while true; do
    clear
    echo "🔍 Live Chat Monitoring - $(date '+%H:%M:%S')"
    echo "=================================="
    echo ""
    
    # Check backend health
    check_backend
    
    # Show recent chat activity
    echo ""
    echo "📊 Recent Chat Activity (last 20 lines):"
    echo "========================================"
    tail -20 backend.log | grep -E "POST /chat|GET /chat/history|⏱️|STEP|TOTAL TIME" | tail -10
    
    echo ""
    echo "Press Ctrl+C to stop monitoring"
    echo ""
    
    sleep 5
done

