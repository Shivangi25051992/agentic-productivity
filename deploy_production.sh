#!/bin/bash
set -e  # Exit on error

# Non-interactive mode (set to 'true' for automated deployment)
NON_INTERACTIVE=${NON_INTERACTIVE:-false}

# ============================================================================
# PRODUCTION DEPLOYMENT SCRIPT
# ============================================================================
# This script deploys the AI Productivity app to production
# - Runs pre-deployment checks
# - Builds frontend with production config
# - Deploys backend to Cloud Run
# - Deploys frontend to Firebase Hosting
# - Runs post-deployment verification
# ============================================================================

echo "🚀 PRODUCTION DEPLOYMENT SCRIPT"
echo "================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# CONFIGURATION
# ============================================================================
PROJECT_ROOT="/Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity"
BACKEND_SERVICE="aiproductivity-backend"
REGION="us-central1"
FRONTEND_URL="https://productivityai-mvp.web.app"

# ============================================================================
# PRE-DEPLOYMENT CHECKS
# ============================================================================
echo -e "${BLUE}📋 Running pre-deployment checks...${NC}"
echo ""

# Check if on correct branch
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
if [ "$CURRENT_BRANCH" != "main" ] && [ "$CURRENT_BRANCH" != "production" ]; then
    echo -e "${YELLOW}⚠️  WARNING: Not on 'main' or 'production' branch${NC}"
    echo "   Current branch: $CURRENT_BRANCH"
    if [ "$NON_INTERACTIVE" = "false" ]; then
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        echo "   (Non-interactive mode: continuing...)"
    fi
fi

# Check for uncommitted changes (excluding .venv and cache files)
UNCOMMITTED=$(git diff-index HEAD -- 2>/dev/null | grep -v "\.venv/" | grep -v "__pycache__" | grep -v "\.pyc$" || true)
if [ -n "$UNCOMMITTED" ]; then
    echo -e "${YELLOW}⚠️  WARNING: Uncommitted changes detected (excluding .venv)${NC}"
    if [ "$NON_INTERACTIVE" = "false" ]; then
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        echo "   (Non-interactive mode: continuing...)"
    fi
fi

# Check if .env.production exists
if [ ! -f "$PROJECT_ROOT/.env.production" ]; then
    echo -e "${RED}❌ ERROR: .env.production not found${NC}"
    echo "   Create it from: cp env.production.template .env.production"
    exit 1
fi

echo -e "${GREEN}✅ Pre-deployment checks passed${NC}"
echo ""

# ============================================================================
# RUN TESTS
# ============================================================================
echo -e "${BLUE}🧪 Running tests...${NC}"
cd "$PROJECT_ROOT"
source venv/bin/activate

# Run Python tests
if pytest tests/ -v --tb=short -x 2>&1 | tee /tmp/test_output.log; then
    echo -e "${GREEN}✅ All tests passed${NC}"
else
    echo -e "${RED}❌ Tests failed!${NC}"
    echo "   Check /tmp/test_output.log for details"
    read -p "Continue deployment anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi
echo ""

# ============================================================================
# BUILD FRONTEND
# ============================================================================
echo -e "${BLUE}🔨 Building Flutter web (production)...${NC}"
cd "$PROJECT_ROOT/flutter_app"

# Clean previous build
flutter clean
flutter pub get

# Get backend URL
BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE \
    --region $REGION \
    --format 'value(status.url)' 2>/dev/null || echo "")

if [ -z "$BACKEND_URL" ]; then
    echo -e "${RED}❌ ERROR: Could not get backend URL${NC}"
    exit 1
fi

echo "   Backend URL: $BACKEND_URL"

# Build with production config
flutter build web --release \
    --dart-define=ENVIRONMENT=production \
    --dart-define=API_BASE_URL=$BACKEND_URL

echo -e "${GREEN}✅ Frontend built successfully${NC}"
echo ""

# ============================================================================
# DEPLOY BACKEND
# ============================================================================
echo -e "${BLUE}🚀 Deploying backend to Cloud Run...${NC}"
cd "$PROJECT_ROOT"

# Convert .env.production to YAML format for gcloud
echo "   Converting .env.production to YAML..."
./scripts/convert_env_to_yaml.sh .env.production .env.production.yaml

# Deploy to Cloud Run
gcloud run deploy $BACKEND_SERVICE \
    --source . \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --env-vars-file .env.production.yaml \
    --max-instances 10 \
    --min-instances 0 \
    --memory 512Mi \
    --cpu 1 \
    --timeout 120s \
    --concurrency 80

# Get deployed URL
BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE \
    --region $REGION \
    --format 'value(status.url)')

echo -e "${GREEN}✅ Backend deployed: $BACKEND_URL${NC}"
echo ""

# ============================================================================
# DEPLOY FRONTEND
# ============================================================================
echo -e "${BLUE}🚀 Deploying frontend to Firebase Hosting...${NC}"
cd "$PROJECT_ROOT/flutter_app"

firebase deploy --only hosting --project productivityai-mvp

echo -e "${GREEN}✅ Frontend deployed: $FRONTEND_URL${NC}"
echo ""

# ============================================================================
# POST-DEPLOYMENT VERIFICATION
# ============================================================================
echo -e "${BLUE}🔍 Running post-deployment checks...${NC}"
echo ""

# Check backend health
echo "Checking backend health..."
if curl -f -s "$BACKEND_URL/health" > /dev/null; then
    echo -e "${GREEN}✅ Backend health check passed${NC}"
else
    echo -e "${RED}❌ Backend health check failed!${NC}"
    exit 1
fi

# Check backend configuration
echo "Checking backend configuration..."
CONFIG_RESPONSE=$(curl -s "$BACKEND_URL/" | grep -o '"status":"ok"' || echo "")
if [ -n "$CONFIG_RESPONSE" ]; then
    echo -e "${GREEN}✅ Backend responding correctly${NC}"
else
    echo -e "${YELLOW}⚠️  Backend response unexpected${NC}"
fi

# Check frontend
echo "Checking frontend..."
if curl -f -s "$FRONTEND_URL" > /dev/null; then
    echo -e "${GREEN}✅ Frontend accessible${NC}"
else
    echo -e "${RED}❌ Frontend not accessible!${NC}"
    exit 1
fi

echo ""

# ============================================================================
# SUCCESS!
# ============================================================================
echo -e "${GREEN}✅ DEPLOYMENT SUCCESSFUL!${NC}"
echo "================================"
echo ""
echo -e "${GREEN}Backend:${NC}  $BACKEND_URL"
echo -e "${GREEN}Frontend:${NC} $FRONTEND_URL"
echo ""
echo -e "${BLUE}🎉 Your app is now live in production!${NC}"
echo ""
echo -e "${YELLOW}📊 Next steps:${NC}"
echo "1. Test the app thoroughly"
echo "2. Monitor logs for errors"
echo "3. Check analytics dashboard"
echo ""
echo -e "${YELLOW}📝 Monitoring commands:${NC}"
echo "Backend logs:  gcloud run services logs read $BACKEND_SERVICE --region $REGION"
echo "Frontend logs: firebase hosting:channel:list"
echo ""

