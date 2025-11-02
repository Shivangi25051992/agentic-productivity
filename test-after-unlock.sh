#!/bin/bash

# ============================================================================
# Test GitHub Actions After Account Unlock
# Run this script once your account is unlocked
# ============================================================================

set -e

echo "🔍 Checking GitHub Account Status..."
echo ""

# Check if account is unlocked by trying to trigger workflow
echo "📋 Step 1: Checking if Actions are available..."
if gh workflow run ci-cd-regression.yml 2>&1 | grep -q "billing"; then
    echo "❌ Account still locked due to billing"
    echo ""
    echo "Please wait or contact support:"
    echo "  https://support.github.com/contact"
    echo ""
    echo "Expected unlock time: 1-2 hours after payment"
    exit 1
else
    echo "✅ Account unlocked! Actions are available"
fi

echo ""
echo "📋 Step 2: Triggering test workflow..."
gh workflow run ci-cd-regression.yml

echo ""
echo "✅ Workflow triggered successfully!"
echo ""
echo "📊 Watching workflow run..."
echo "   (Press Ctrl+C to stop watching, workflow will continue)"
echo ""

sleep 5
gh run watch

echo ""
echo "================================================"
echo "✅ Test Complete!"
echo "================================================"
echo ""
echo "View full results:"
echo "  https://github.com/prashantrepocollection/agentic-productivity/actions"
echo ""
echo "Check usage:"
echo "  https://github.com/settings/billing/summary"
echo ""


