#!/bin/bash

# Focused debugging monitor for chat → dashboard flow

echo "🔍 DEBUG MONITOR - Chat → Dashboard Flow"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "📋 This will monitor:"
echo "   1. Chat requests (user input)"
echo "   2. Backend classification (LLM response)"
echo "   3. Items array in response"
echo "   4. Dashboard data updates"
echo "   5. Feedback captures"
echo ""
echo "⏳ Waiting for activity... (send a chat message to see logs)"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Find most recent backend log
BACKEND_LOG=$(ls -t /tmp/backend*.log 2>/dev/null | head -1)
if [ -z "$BACKEND_LOG" ]; then
  echo "❌ No backend log file found in /tmp/"
  exit 1
fi

echo "📁 Monitoring: $BACKEND_LOG"
echo ""

# Monitor backend in real-time
tail -f "$BACKEND_LOG" 2>/dev/null | grep --line-buffered -E "POST /chat|MONITOR|items=|calories|dashboard|fitness|ERROR|Exception" | while read line; do
  timestamp=$(date +"%H:%M:%S")
  
  if echo "$line" | grep -qi "POST /chat"; then
    echo -e "${CYAN}[$timestamp] 📨 CHAT REQUEST${NC}"
    echo "   $line"
    echo ""
    
  elif echo "$line" | grep -qi "items="; then
    # Extract items count if possible
    echo -e "${GREEN}[$timestamp] 📦 ITEMS ARRAY${NC}"
    echo "   $line"
    echo ""
    
  elif echo "$line" | grep -qi "calories.*logged\|fitness.*log"; then
    echo -e "${YELLOW}[$timestamp] 🍽️  NUTRITION LOGGED${NC}"
    echo "   $line"
    echo ""
    
  elif echo "$line" | grep -qi "dashboard"; then
    echo -e "${CYAN}[$timestamp] 📊 DASHBOARD UPDATE${NC}"
    echo "   $line"
    echo ""
    
  elif echo "$line" | grep -qi "error\|exception"; then
    echo -e "${RED}[$timestamp] ❌ ERROR DETECTED${NC}"
    echo "   $line"
    echo ""
  fi
done

