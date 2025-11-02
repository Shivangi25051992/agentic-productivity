#!/bin/bash

# AI Productivity App - Deployment Script
# Deploys to Google Cloud Platform (Free Tier)

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 AI Productivity App - Deployment Script${NC}"
echo "=============================================="

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI not found. Please install: https://cloud.google.com/sdk/docs/install${NC}"
    exit 1
fi

# Check if firebase is installed
if ! command -v firebase &> /dev/null; then
    echo -e "${RED}❌ Firebase CLI not found. Installing...${NC}"
    npm install -g firebase-tools
fi

# Get project ID
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    echo -e "${YELLOW}⚠️  No project selected${NC}"
    read -p "Enter your Google Cloud Project ID: " PROJECT_ID
    gcloud config set project $PROJECT_ID
fi

echo -e "${GREEN}📦 Project: $PROJECT_ID${NC}"

# Get region
REGION=${REGION:-"us-central1"}
echo -e "${GREEN}🌍 Region: $REGION${NC}"

# Service name
SERVICE_NAME="aiproductivity-backend"

echo ""
echo "=============================================="
echo "Step 1: Deploy Backend to Cloud Run"
echo "=============================================="

# Build and deploy backend
echo -e "${YELLOW}🔨 Building backend container...${NC}"
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

echo -e "${YELLOW}🚀 Deploying to Cloud Run...${NC}"
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
  --set-env-vars="OPENAI_MODEL=gpt-3.5-turbo" \
  --max-instances=1 \
  --min-instances=0 \
  --memory=512Mi \
  --cpu=1 \
  --timeout=60s \
  --concurrency=80

# Get backend URL
BACKEND_URL=$(gcloud run services describe $SERVICE_NAME \
  --region $REGION \
  --format='value(status.url)')

echo -e "${GREEN}✅ Backend deployed: $BACKEND_URL${NC}"

echo ""
echo "=============================================="
echo "Step 2: Update Frontend Configuration"
echo "=============================================="

# Update API URL in Flutter constants
CONSTANTS_FILE="flutter_app/lib/utils/constants.dart"
if [ -f "$CONSTANTS_FILE" ]; then
    echo -e "${YELLOW}📝 Updating API URL in Flutter...${NC}"
    
    # Backup original file
    cp $CONSTANTS_FILE ${CONSTANTS_FILE}.bak
    
    # Update API URL
    sed -i.tmp "s|static const String apiBaseUrl = .*|static const String apiBaseUrl = '$BACKEND_URL';|" $CONSTANTS_FILE
    rm ${CONSTANTS_FILE}.tmp
    
    echo -e "${GREEN}✅ API URL updated${NC}"
else
    echo -e "${RED}❌ Constants file not found: $CONSTANTS_FILE${NC}"
    exit 1
fi

echo ""
echo "=============================================="
echo "Step 3: Build Flutter Web"
echo "=============================================="

cd flutter_app

# Check if Flutter is installed
if ! command -v flutter &> /dev/null; then
    echo -e "${RED}❌ Flutter not found. Please install: https://flutter.dev/docs/get-started/install${NC}"
    exit 1
fi

echo -e "${YELLOW}🔨 Building Flutter web...${NC}"
flutter build web --release

cd ..

echo -e "${GREEN}✅ Flutter web built${NC}"

echo ""
echo "=============================================="
echo "Step 4: Deploy Frontend to Firebase Hosting"
echo "=============================================="

echo -e "${YELLOW}🚀 Deploying to Firebase Hosting...${NC}"
firebase deploy --only hosting

# Get hosting URL
HOSTING_URL=$(firebase hosting:channel:list | grep -o 'https://[^ ]*' | head -1)
if [ -z "$HOSTING_URL" ]; then
    HOSTING_URL="https://$PROJECT_ID.web.app"
fi

echo -e "${GREEN}✅ Frontend deployed: $HOSTING_URL${NC}"

echo ""
echo "=============================================="
echo "Step 5: Deploy Firestore Rules & Indexes"
echo "=============================================="

echo -e "${YELLOW}🔒 Deploying Firestore rules...${NC}"
firebase deploy --only firestore:rules

echo -e "${YELLOW}📊 Deploying Firestore indexes...${NC}"
firebase deploy --only firestore:indexes

echo -e "${GREEN}✅ Firestore rules and indexes deployed${NC}"

echo ""
echo "=============================================="
echo "🎉 Deployment Complete!"
echo "=============================================="
echo ""
echo -e "${GREEN}Frontend URL:${NC} $HOSTING_URL"
echo -e "${GREEN}Backend URL:${NC} $BACKEND_URL"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Test the application: $HOSTING_URL"
echo "2. Check backend health: $BACKEND_URL/health"
echo "3. Monitor logs: gcloud run services logs read $SERVICE_NAME --region $REGION"
echo "4. View metrics: https://console.cloud.google.com/run/detail/$REGION/$SERVICE_NAME"
echo ""
echo -e "${GREEN}Test Credentials:${NC}"
echo "Email: alice.test@aiproductivity.app"
echo "Password: Test@123"
echo ""
echo "=============================================="

