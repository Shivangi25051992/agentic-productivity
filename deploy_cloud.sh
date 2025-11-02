#!/bin/bash

# Cloud Deployment Script (Alias for auto_deploy.sh)
# This is a convenience wrapper

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  ☁️  CLOUD DEPLOYMENT STARTING         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Check if auto_deploy.sh exists
if [ ! -f "auto_deploy.sh" ]; then
    echo "❌ auto_deploy.sh not found!"
    exit 1
fi

# Make sure it's executable
chmod +x auto_deploy.sh

# Run the deployment
./auto_deploy.sh

echo ""
echo -e "${GREEN}✅ Cloud deployment complete!${NC}"
echo ""
echo "🌐 Frontend: https://productivityai-mvp.web.app"
echo "🔧 Backend: https://aiproductivity-backend-rhwrraai2a-uc.a.run.app"
echo ""

