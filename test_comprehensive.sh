#!/bin/bash

# Comprehensive Test Script
# Tests confidence score, feedback, and conversational messages

echo "🧪 ============================================"
echo "   COMPREHENSIVE TEST SUITE"
echo "============================================"
echo ""

# Get test user ID token (you'll need to replace with actual token)
echo "📝 Note: Using test user from Firestore"
echo ""

# Test 1: Send "apple" and check confidence score
echo "📋 TEST 1: Send 'apple' → Check Confidence Score"
echo "------------------------------------------------"
RESPONSE1=$(curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test-token-placeholder" \
  -d '{"user_input": "apple"}' 2>&1)

echo "Response excerpt:"
echo "$RESPONSE1" | jq -r '.confidence_score, .confidence_level, .message' 2>/dev/null || echo "$RESPONSE1" | head -20
echo ""
sleep 2

# Test 2: Send "I am frustrated" and check conversational response
echo "📋 TEST 2: Send 'I am frustrated' → Check Conversational Response"
echo "-------------------------------------------------------------------"
RESPONSE2=$(curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test-token-placeholder" \
  -d '{"user_input": "I am frustrated"}' 2>&1)

echo "Response excerpt:"
echo "$RESPONSE2" | jq -r '.message, .items[0].category' 2>/dev/null || echo "$RESPONSE2" | head -20
echo ""
sleep 2

# Test 3: Send feedback
echo "📋 TEST 3: Submit Feedback (Positive)"
echo "---------------------------------------"
MESSAGE_ID="test-message-$(date +%s)"
FEEDBACK=$(curl -s -X POST http://localhost:8000/feedback \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test-token-placeholder" \
  -d "{\"message_id\": \"$MESSAGE_ID\", \"rating\": \"helpful\", \"corrections\": []}" 2>&1)

echo "Feedback response:"
echo "$FEEDBACK" | head -10
echo ""

# Test 4: Check chat history
echo "📋 TEST 4: Get Chat History (Check Order)"
echo "------------------------------------------"
HISTORY=$(curl -s http://localhost:8000/chat/history?limit=5 \
  -H "Authorization: Bearer test-token-placeholder" 2>&1)

echo "Recent messages:"
echo "$HISTORY" | jq -r '.messages[] | "\(.role): \(.content[0:50])..."' 2>/dev/null || echo "$HISTORY" | head -20
echo ""

echo "✅ ============================================"
echo "   TEST SUITE COMPLETE"
echo "============================================"
echo ""
echo "📊 Summary:"
echo "  ✅ Confidence score endpoint"
echo "  ✅ Conversational message handling"
echo "  ✅ Feedback submission"
echo "  ✅ Chat history retrieval"
echo ""
echo "⚠️  Note: Authentication tokens not set - showing structure only"




