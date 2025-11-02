#!/bin/bash

# Automated Deployment Script
# Run with: ./auto_deploy.sh

set -e  # Exit on error

# Add gcloud and firebase to PATH
export PATH=$PATH:/Users/pchintanwar/google-cloud-sdk/bin:/Users/pchintanwar/.nvm/versions/node/v20.19.5/bin

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  🚀 AUTOMATED DEPLOYMENT STARTING     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Configuration
PROJECT_ID="productivityai-mvp"
REGION="us-central1"
SERVICE_NAME="aiproductivity-backend"

echo -e "${YELLOW}📋 Configuration:${NC}"
echo "   Project: $PROJECT_ID"
echo "   Region: $REGION"
echo "   Service: $SERVICE_NAME"
echo ""

# Step 1: Deploy Backend
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${GREEN}Step 1/4: Deploying Backend to Cloud Run${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"

# Load OpenAI API key from .env.local
OPENAI_KEY=$(grep "OPENAI_API_KEY" .env.local | cut -d '=' -f2)

gcloud run deploy $SERVICE_NAME \
  --source . \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --project $PROJECT_ID \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=$PROJECT_ID,OPENAI_MODEL=gpt-4o-mini,OPENAI_API_KEY=$OPENAI_KEY" \
  --max-instances=2 \
  --min-instances=0 \
  --memory=1Gi \
  --cpu=1 \
  --timeout=60s \
  --quiet

# Get backend URL
BACKEND_URL=$(gcloud run services describe $SERVICE_NAME \
  --region $REGION \
  --project $PROJECT_ID \
  --format='value(status.url)')

echo -e "${GREEN}✅ Backend deployed: $BACKEND_URL${NC}"
echo ""

# Step 2: Update Frontend Config
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${GREEN}Step 2/4: Updating Frontend Configuration${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"

# Update API URL in Flutter constants
CONSTANTS_FILE="flutter_app/lib/utils/constants.dart"

if [ -f "$CONSTANTS_FILE" ]; then
    # Backup
    cp $CONSTANTS_FILE ${CONSTANTS_FILE}.backup
    
    # Update both apiBaseUrl occurrences
    sed -i.tmp "s|static const String apiBaseUrl = '.*';|static const String apiBaseUrl = '$BACKEND_URL';|g" $CONSTANTS_FILE
    rm ${CONSTANTS_FILE}.tmp
    
    echo -e "${GREEN}✅ API URL updated in Flutter${NC}"
else
    echo -e "${RED}❌ Constants file not found!${NC}"
    exit 1
fi
echo ""

# Step 3: Build Flutter Web
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${GREEN}Step 3/4: Building Flutter Web${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"

cd flutter_app

# Clean build
flutter clean > /dev/null 2>&1

# Build for web
flutter build web --release

cd ..

echo -e "${GREEN}✅ Flutter web built successfully${NC}"
echo ""

# Step 4: Deploy Frontend to Firebase
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${GREEN}Step 4/4: Deploying Frontend to Firebase${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"

# Set Firebase project
firebase use $PROJECT_ID > /dev/null 2>&1

# Deploy hosting
firebase deploy --only hosting --project $PROJECT_ID

# Get hosting URL
HOSTING_URL="https://$PROJECT_ID.web.app"

echo -e "${GREEN}✅ Frontend deployed: $HOSTING_URL${NC}"
echo ""

# Step 5: Deploy Firestore Rules (if changed)
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${GREEN}Step 5/5: Deploying Firestore Rules & Indexes${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"

firebase deploy --only firestore:rules,firestore:indexes --project $PROJECT_ID

echo -e "${GREEN}✅ Firestore rules deployed${NC}"
echo ""

# Summary
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  🎉 DEPLOYMENT COMPLETE!              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}🌐 Frontend URL:${NC} $HOSTING_URL"
echo -e "${GREEN}🔧 Backend URL:${NC} $BACKEND_URL"
echo ""
echo -e "${YELLOW}📊 Next Steps:${NC}"
echo "1. Test app: $HOSTING_URL"
echo "2. Check logs: gcloud run services logs read $SERVICE_NAME --region $REGION"
echo "3. View feedback: https://console.firebase.google.com/project/$PROJECT_ID/firestore/data/feedback"
echo "4. Manage users: https://console.firebase.google.com/project/$PROJECT_ID/authentication/users"
echo ""
echo -e "${GREEN}✅ All systems deployed and ready!${NC}"
echo ""

