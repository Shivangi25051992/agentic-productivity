#!/bin/bash

# ============================================================================
# Local Regression Test Runner
# Runs all critical E2E tests before committing/deploying
# ============================================================================

set -e  # Exit on error

echo "🧪 AI Productivity App - Regression Test Suite"
echo "================================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if servers are running
echo "🔍 Checking services..."

if ! curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${RED}❌ Backend not running at http://localhost:8000${NC}"
    echo "   Start with: ./start-dev.sh"
    exit 1
fi
echo -e "${GREEN}✅ Backend running${NC}"

if ! curl -s http://localhost:8080 > /dev/null; then
    echo -e "${RED}❌ Frontend not running at http://localhost:8080${NC}"
    echo "   Start with: ./start-dev.sh"
    exit 1
fi
echo -e "${GREEN}✅ Frontend running${NC}"

echo ""
echo "🧪 Running regression tests..."
echo ""

# Create reports directory
mkdir -p test-reports

# Run E2E tests
pytest tests/test_e2e_critical_flows.py \
    -v \
    --html=test-reports/e2e-report.html \
    --self-contained-html \
    --json-report \
    --json-report-file=test-reports/e2e-report.json \
    --tb=short \
    --maxfail=5 \
    || TEST_FAILED=1

echo ""
echo "================================================"

if [ -z "$TEST_FAILED" ]; then
    echo -e "${GREEN}✅ ALL TESTS PASSED${NC}"
    echo ""
    echo "📊 Test report: test-reports/e2e-report.html"
    echo "🚀 Safe to commit and deploy"
    exit 0
else
    echo -e "${RED}❌ TESTS FAILED${NC}"
    echo ""
    echo "📊 Test report: test-reports/e2e-report.html"
    echo "🚫 DO NOT DEPLOY until tests pass"
    echo ""
    echo "🔧 Next steps:"
    echo "   1. Open test-reports/e2e-report.html for details"
    echo "   2. Fix failing tests"
    echo "   3. Run this script again"
    exit 1
fi


