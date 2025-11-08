#!/bin/bash

# ============================================================================
# PRE-DEPLOYMENT CHECKLIST
# ============================================================================
# Run this before deploying to production to catch issues early
# ============================================================================

echo "🔍 PRE-DEPLOYMENT CHECKLIST"
echo "============================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASSED=0
FAILED=0
WARNINGS=0

check_pass() {
    echo -e "${GREEN}✅ $1${NC}"
    ((PASSED++))
}

check_fail() {
    echo -e "${RED}❌ $1${NC}"
    ((FAILED++))
}

check_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    ((WARNINGS++))
}

# ============================================================================
# 1. GIT STATUS
# ============================================================================
echo "📦 Git Status"
echo "-------------"

BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
if [ "$BRANCH" == "main" ] || [ "$BRANCH" == "production" ]; then
    check_pass "On correct branch: $BRANCH"
else
    check_warn "Not on main/production branch: $BRANCH"
fi

if git diff-index --quiet HEAD -- 2>/dev/null; then
    check_pass "No uncommitted changes"
else
    check_warn "Uncommitted changes detected"
fi

echo ""

# ============================================================================
# 2. CONFIGURATION FILES
# ============================================================================
echo "⚙️  Configuration"
echo "----------------"

if [ -f ".env.production" ]; then
    check_pass ".env.production exists"
    
    # Check for placeholder values
    if grep -q "REPLACE_WITH" .env.production 2>/dev/null; then
        check_fail ".env.production contains placeholder values"
    else
        check_pass ".env.production has no placeholders"
    fi
else
    check_fail ".env.production not found"
fi

if [ -f "flutter_app/lib/config/environment_config.dart" ]; then
    check_pass "Frontend config exists"
    
    # Check for TODO markers
    if grep -q "TODO:" flutter_app/lib/config/environment_config.dart; then
        check_warn "Frontend config has TODO markers"
    else
        check_pass "Frontend config complete"
    fi
else
    check_fail "Frontend config missing"
fi

echo ""

# ============================================================================
# 3. BACKEND TESTS
# ============================================================================
echo "🧪 Backend Tests"
echo "---------------"

cd "$(dirname "$0")"
source venv/bin/activate 2>/dev/null

if pytest app/tests/ -v --tb=short -x -q 2>&1 | grep -q "passed"; then
    check_pass "Backend tests passing"
else
    check_fail "Backend tests failing"
fi

echo ""

# ============================================================================
# 4. DEPENDENCIES
# ============================================================================
echo "📚 Dependencies"
echo "--------------"

if [ -f "requirements.txt" ]; then
    check_pass "requirements.txt exists"
    
    if grep -q "pydantic-settings" requirements.txt; then
        check_pass "pydantic-settings in requirements.txt"
    else
        check_fail "pydantic-settings missing from requirements.txt"
    fi
else
    check_fail "requirements.txt missing"
fi

if [ -f "flutter_app/pubspec.yaml" ]; then
    check_pass "pubspec.yaml exists"
else
    check_fail "pubspec.yaml missing"
fi

echo ""

# ============================================================================
# 5. BACKEND URL VERIFICATION
# ============================================================================
echo "🌐 Backend URL"
echo "-------------"

BACKEND_URL=$(gcloud run services describe aiproductivity-backend \
    --region us-central1 \
    --format 'value(status.url)' 2>/dev/null || echo "")

if [ -n "$BACKEND_URL" ]; then
    check_pass "Backend URL retrieved: $BACKEND_URL"
    
    # Check if URL matches frontend config
    if grep -q "$BACKEND_URL" flutter_app/lib/config/environment_config.dart; then
        check_pass "Frontend config matches backend URL"
    else
        check_fail "Frontend config doesn't match backend URL"
    fi
else
    check_warn "Could not retrieve backend URL (gcloud not configured?)"
fi

echo ""

# ============================================================================
# 6. DATABASE
# ============================================================================
echo "💾 Database"
echo "----------"

# Check if GOOGLE_CLOUD_PROJECT is set
if [ -f ".env.production" ]; then
    source .env.production
    if [ -n "$GOOGLE_CLOUD_PROJECT" ]; then
        check_pass "GOOGLE_CLOUD_PROJECT configured: $GOOGLE_CLOUD_PROJECT"
        
        # Try to verify Firestore connection (optional, won't fail deployment)
        if venv/bin/python scripts/verify_firestore_connection.py >/dev/null 2>&1; then
            check_pass "Firestore connection verified locally"
        else
            echo "   ℹ️  Local Firestore connection not verified (will work in Cloud Run)"
        fi
    else
        check_fail "GOOGLE_CLOUD_PROJECT not set in .env.production"
    fi
else
    check_fail ".env.production not found"
fi

echo ""

# ============================================================================
# 7. FEATURE FLAGS
# ============================================================================
echo "🚩 Feature Flags"
echo "---------------"

if python -c "from app.core.config_manager import settings; print(settings.enable_free_tier_limits)" 2>/dev/null | grep -q "True"; then
    check_pass "Free tier limits enabled"
else
    check_warn "Free tier limits disabled"
fi

if python -c "from app.core.config_manager import settings; print(settings.enable_parallel_generation)" 2>/dev/null | grep -q "True"; then
    check_pass "Parallel generation enabled"
else
    check_warn "Parallel generation disabled"
fi

echo ""

# ============================================================================
# SUMMARY
# ============================================================================
echo "================================"
echo "📊 SUMMARY"
echo "================================"
echo -e "${GREEN}✅ Passed:   $PASSED${NC}"
echo -e "${YELLOW}⚠️  Warnings: $WARNINGS${NC}"
echo -e "${RED}❌ Failed:   $FAILED${NC}"
echo ""

if [ $FAILED -gt 0 ]; then
    echo -e "${RED}🔴 DEPLOYMENT BLOCKED${NC}"
    echo "Fix the failed checks before deploying"
    exit 1
elif [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}🟡 WARNINGS DETECTED${NC}"
    echo "Review warnings before deploying"
    exit 0
else
    echo -e "${GREEN}🟢 ALL CHECKS PASSED${NC}"
    echo "Ready for deployment!"
    exit 0
fi
