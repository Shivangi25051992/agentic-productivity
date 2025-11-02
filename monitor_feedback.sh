#!/bin/bash

# Feedback Monitor - Checks every 15 minutes for 2 hours
# Created: November 2, 2025

PROJECT_ID="productivityai-mvp"
CHECK_INTERVAL=900  # 15 minutes in seconds
TOTAL_DURATION=7200  # 2 hours in seconds
START_TIME=$(date +%s)
LAST_FEEDBACK_COUNT=0

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  📝 FEEDBACK MONITOR STARTED                              ║"
echo "║  Checking every 15 minutes for the next 2 hours          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "⏰ Started at: $(date '+%H:%M:%S')"
echo "⏰ Will stop at: $(date -v+2H '+%H:%M:%S')"
echo ""

# Function to check feedback
check_feedback() {
    CURRENT_TIME=$(date +%s)
    ELAPSED=$((CURRENT_TIME - START_TIME))
    REMAINING=$((TOTAL_DURATION - ELAPSED))
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔍 Checking feedback at $(date '+%H:%M:%S')"
    echo "⏱️  Time remaining: $((REMAINING / 60)) minutes"
    echo ""
    
    # Use Python to query Firestore
    FEEDBACK_DATA=$(python3 << 'PYTHON_SCRIPT'
import os
import sys
from google.cloud import firestore
from datetime import datetime, timezone, timedelta

try:
    PROJECT_ID = "productivityai-mvp"
    db = firestore.Client(project=PROJECT_ID)
    
    # Get all feedback
    feedback_ref = db.collection('feedback').order_by('timestamp', direction=firestore.Query.DESCENDING).stream()
    
    feedback_list = []
    for doc in feedback_ref:
        data = doc.to_dict()
        data['id'] = doc.id
        feedback_list.append(data)
    
    # Get new feedback (last 15 minutes)
    fifteen_min_ago = datetime.now(timezone.utc) - timedelta(minutes=15)
    new_feedback = []
    for f in feedback_list:
        timestamp = f.get('timestamp')
        if timestamp and hasattr(timestamp, 'replace'):
            if timestamp.replace(tzinfo=timezone.utc) > fifteen_min_ago:
                new_feedback.append(f)
    
    # Print summary
    print(f"TOTAL:{len(feedback_list)}")
    print(f"NEW:{len(new_feedback)}")
    
    # Print new feedback details
    if new_feedback:
        print("NEW_ITEMS:")
        for f in new_feedback:
            print(f"TYPE:{f.get('type', 'unknown')}")
            print(f"USER:{f.get('user_email', 'N/A')}")
            print(f"COMMENT:{f.get('comment', 'N/A')[:100]}")
            print(f"SCREENSHOT:{f.get('has_screenshot', False)}")
            print("---")
    
except Exception as e:
    print(f"ERROR:{str(e)}")
    sys.exit(1)
PYTHON_SCRIPT
)
    
    # Parse output
    TOTAL_COUNT=$(echo "$FEEDBACK_DATA" | grep "TOTAL:" | cut -d':' -f2)
    NEW_COUNT=$(echo "$FEEDBACK_DATA" | grep "NEW:" | cut -d':' -f2)
    
    if [ -z "$TOTAL_COUNT" ]; then
        echo "❌ Error checking feedback"
        return
    fi
    
    echo "📊 Total feedback: $TOTAL_COUNT"
    
    if [ "$NEW_COUNT" -gt 0 ]; then
        echo ""
        echo "🆕 NEW FEEDBACK DETECTED! ($NEW_COUNT new items)"
        echo ""
        
        # Play alert sound (macOS)
        afplay /System/Library/Sounds/Glass.aiff 2>/dev/null || true
        
        # Show notification (macOS)
        osascript -e "display notification \"$NEW_COUNT new feedback items!\" with title \"Feedback Alert\" sound name \"Glass\"" 2>/dev/null || true
        
        # Print details
        echo "$FEEDBACK_DATA" | grep -A 100 "NEW_ITEMS:" | while IFS= read -r line; do
            if [[ $line == TYPE:* ]]; then
                TYPE=$(echo "$line" | cut -d':' -f2)
                echo "  🔸 Type: $TYPE"
            elif [[ $line == USER:* ]]; then
                USER=$(echo "$line" | cut -d':' -f2)
                echo "  👤 User: $USER"
            elif [[ $line == COMMENT:* ]]; then
                COMMENT=$(echo "$line" | cut -d':' -f2-)
                echo "  💬 Comment: $COMMENT"
            elif [[ $line == SCREENSHOT:* ]]; then
                HAS_SCREENSHOT=$(echo "$line" | cut -d':' -f2)
                if [ "$HAS_SCREENSHOT" = "True" ]; then
                    echo "  📷 Screenshot: Yes"
                fi
                echo ""
            fi
        done
        
        echo "🔗 View in admin portal:"
        echo "   https://aiproductivity-backend-rhwrraai2a-uc.a.run.app/admin/admin_dashboard.html"
        echo ""
    else
        echo "✅ No new feedback in the last 15 minutes"
    fi
    
    echo ""
}

# Initial check
check_feedback

# Loop for 2 hours
while true; do
    CURRENT_TIME=$(date +%s)
    ELAPSED=$((CURRENT_TIME - START_TIME))
    
    # Check if 2 hours have passed
    if [ $ELAPSED -ge $TOTAL_DURATION ]; then
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "⏰ 2 HOURS COMPLETE!"
        echo ""
        echo "╔════════════════════════════════════════════════════════════╗"
        echo "║  🛑 TIME TO STOP AND SLEEP!                               ║"
        echo "║  You've been working for 2 hours.                         ║"
        echo "║  Great work today! Rest well! 😴                          ║"
        echo "╚════════════════════════════════════════════════════════════╝"
        
        # Play alert sound
        for i in {1..3}; do
            afplay /System/Library/Sounds/Glass.aiff 2>/dev/null || true
            sleep 1
        done
        
        # Show notification
        osascript -e "display notification \"Time to stop and sleep! 😴\" with title \"2 Hour Timer Complete\" sound name \"Glass\"" 2>/dev/null || true
        
        exit 0
    fi
    
    # Wait 15 minutes
    sleep $CHECK_INTERVAL
    
    # Check feedback again
    check_feedback
done

