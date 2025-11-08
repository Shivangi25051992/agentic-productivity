#!/bin/bash

echo "🧪 ======================="
echo "   FULL SYSTEM TEST"
echo "======================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Backend Health
echo "📍 Test 1: Backend Health Check"
backend_status=$(curl -s http://localhost:8000/health | jq -r '.status' 2>/dev/null)
if [ "$backend_status" = "healthy" ]; then
  echo -e "   ${GREEN}✅ Backend is healthy${NC}"
else
  echo -e "   ${RED}❌ Backend is down or unhealthy${NC}"
  exit 1
fi
echo ""

# Test 2: Frontend Serving
echo "📍 Test 2: Frontend Serving Check"
frontend_check=$(curl -s -I http://localhost:9000 2>&1 | grep "HTTP/")
if [ -n "$frontend_check" ]; then
  echo -e "   ${GREEN}✅ Frontend is serving${NC}"
else
  echo -e "   ${RED}❌ Frontend is not responding${NC}"
  exit 1
fi
echo ""

# Test 3: Chat Debug Endpoint
echo "📍 Test 3: Chat Debug Endpoint (simulates '2 eggs')"
debug_response=$(curl -s -X POST "http://localhost:8000/test/chat-debug?text=2%20eggs")
debug_status=$(echo "$debug_response" | jq -r '.status' 2>/dev/null)
items_count=$(echo "$debug_response" | jq '.response.items | length' 2>/dev/null)
summary=$(echo "$debug_response" | jq -r '.response.summary' 2>/dev/null)
confidence=$(echo "$debug_response" | jq -r '.response.confidence_score' 2>/dev/null)

if [ "$debug_status" = "success" ]; then
  echo -e "   ${GREEN}✅ Chat endpoint working${NC}"
  echo "   📊 Items returned: $items_count"
  echo "   💬 Summary: $summary"
  echo "   🎯 Confidence: $confidence"
else
  echo -e "   ${RED}❌ Chat endpoint failed${NC}"
fi
echo ""

# Test 4: Check if items are being returned
echo "📍 Test 4: Items Array Verification"
if [ "$items_count" -eq "0" ]; then
  echo -e "   ${RED}❌ CRITICAL: items=[] (dashboard will show 0)${NC}"
  echo "   🔍 This is WHY dashboard isn't updating!"
else
  echo -e "   ${GREEN}✅ Items array has $items_count item(s)${NC}"
fi
echo ""

# Test 5: Phase 2 Fields Present
echo "📍 Test 5: Phase 2 Explainable AI Fields"
explanation=$(echo "$debug_response" | jq -r '.response.explanation' 2>/dev/null)
alternatives=$(echo "$debug_response" | jq '.response.alternatives | length' 2>/dev/null)

if [ "$explanation" != "null" ] && [ "$explanation" != "None" ]; then
  echo -e "   ${GREEN}✅ Explanation present${NC}"
else
  echo -e "   ${YELLOW}⚠️  Explanation missing${NC}"
fi

if [ "$alternatives" != "null" ]; then
  echo -e "   ${GREEN}✅ Alternatives: $alternatives${NC}"
else
  echo "   ℹ️  No alternatives (expected for high confidence)"
fi
echo ""

# Summary
echo "📋 ======================="
echo "   SUMMARY"
echo "======================="
echo ""
echo "Services:"
echo -e "   Backend:  ${GREEN}✅ Running${NC}"
echo -e "   Frontend: ${GREEN}✅ Running${NC}"
echo ""
echo "Chat Response:"
echo "   Items count: $items_count"
echo "   Summary: $summary"
echo "   Confidence: $confidence"
echo ""
echo "🎯 NEXT STEPS FOR USER:"
echo "   1. Hard refresh browser (Cmd+Shift+R)"
echo "   2. Log '2 eggs' in chat"
echo "   3. Check dashboard (should show 140 calories)"
echo "   4. Check browser console (F12) for logs"
echo ""
echo "⚠️  KNOWN LIMITATIONS:"
echo "   - Feedback NOT saved to database (Phase 3)"
echo "   - Checkboxes may need Flutter restart"
echo ""




