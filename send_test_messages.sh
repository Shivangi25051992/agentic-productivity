#!/bin/bash

# Script to send test messages to Alice's account
# You need to provide Alice's Firebase ID token

echo "======================================================================"
echo "🧪 AUTOMATED TEST MESSAGE SENDER"
echo "======================================================================"
echo ""

# Check if token is provided
if [ -z "$1" ]; then
    echo "⚠️  No token provided"
    echo ""
    echo "📋 TO GET ALICE'S TOKEN:"
    echo "1. Open http://localhost:3000 in Chrome"
    echo "2. Login as alice.test@aiproductivity.app"
    echo "3. Open DevTools (F12) → Console tab"
    echo "4. Run this command:"
    echo "   firebase.auth().currentUser.getIdToken().then(t => console.log(t))"
    echo "5. Copy the token and run:"
    echo "   ./send_test_messages.sh YOUR_TOKEN_HERE"
    echo ""
    exit 1
fi

TOKEN="$1"
BASE_URL="http://localhost:8000"

echo "✅ Token provided"
echo "🚀 Sending 8 test messages..."
echo ""

# Function to send message
send_message() {
    local message="$1"
    local test_name="$2"
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📤 $test_name"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Input: $message"
    echo ""
    
    response=$(curl -s -X POST "$BASE_URL/chat" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"text\": \"$message\", \"type\": \"auto\"}" \
        2>&1)
    
    status=$?
    
    if [ $status -eq 0 ]; then
        # Check if response contains "message" field
        if echo "$response" | grep -q '"message"'; then
            echo "✅ Message sent successfully"
            # Extract and show first 150 chars of response
            preview=$(echo "$response" | jq -r '.message' 2>/dev/null | head -c 150)
            echo "Preview: $preview..."
        else
            echo "❌ Unexpected response:"
            echo "$response" | head -c 200
        fi
    else
        echo "❌ Failed to send message"
        echo "$response"
    fi
    
    echo ""
    sleep 2
}

# Test 1: Breakfast
send_message "2 eggs for breakfast" "TEST 1: Breakfast Classification"

# Test 2: Multi-line
send_message "ran 5km
1 multivitamin" "TEST 2: Multi-line (Workout + Supplement)"

# Test 3: Lunch
send_message "chicken breast with rice and broccoli for lunch" "TEST 3: Lunch with Details"

# Test 4: Snack
send_message "chocolate bar" "TEST 4: Chocolate Bar (Smart Assumption)"

# Test 5: Dinner
send_message "salmon with vegetables for dinner" "TEST 5: Dinner Explicit"

# Test 6: Workout
send_message "30 minutes yoga" "TEST 6: Workout Only"

# Test 7: Task
send_message "remind me to call doctor at 3pm" "TEST 7: Task/Reminder"

# Test 8: Complex
send_message "oatmeal for breakfast
walked 3km
protein shake
call mom at 5pm" "TEST 8: Complex Multi-Category"

echo "======================================================================"
echo "✅ ALL 8 TEST MESSAGES SENT!"
echo "======================================================================"
echo ""
echo "🎯 NOW VERIFY IN UI:"
echo "1. Go to http://localhost:3000"
echo "2. Navigate to 'Assistant' tab"
echo "3. You should see all 8 messages with responses"
echo ""
echo "✅ CHECK FOR:"
echo "  • No duplication in responses"
echo "  • 'Breakfast' labeled correctly (not as dinner)"
echo "  • 'Lunch' labeled correctly"
echo "  • 'Dinner' labeled correctly"
echo "  • Workouts in 'Exercise' section (not Food)"
echo "  • No ** asterisks in responses"
echo "  • Clean, ChatGPT-style formatting"
echo ""
echo "✅ CHAT PERSISTENCE TEST:"
echo "  1. Navigate to Home page"
echo "  2. Navigate back to Assistant"
echo "  3. All messages should still be there!"
echo ""
echo "======================================================================"

