#!/bin/bash
# Final iOS Setup - Run these commands manually
# This script needs sudo access for Xcode configuration

set -e

echo "🍎 FINAL iOS SETUP"
echo "=================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}📋 Step 1: Configuring Xcode...${NC}"
echo "This will ask for your Mac password..."
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer
echo -e "${GREEN}✅ Xcode configured${NC}"
echo ""

echo -e "${BLUE}📋 Step 2: Accepting Xcode license...${NC}"
sudo xcodebuild -license accept
echo -e "${GREEN}✅ License accepted${NC}"
echo ""

echo -e "${BLUE}📋 Step 3: Running first launch setup...${NC}"
sudo xcodebuild -runFirstLaunch
echo -e "${GREEN}✅ First launch complete${NC}"
echo ""

echo -e "${BLUE}📋 Step 4: Verifying Xcode installation...${NC}"
xcodebuild -version
echo ""

echo -e "${BLUE}📋 Step 5: Installing iOS dependencies (CocoaPods)...${NC}"
cd flutter_app/ios
export LANG=en_US.UTF-8
pod install
echo -e "${GREEN}✅ iOS dependencies installed${NC}"
echo ""

cd ../..

echo -e "${BLUE}📋 Step 6: Running Flutter doctor...${NC}"
flutter doctor
echo ""

echo "========================================"
echo -e "${GREEN}🎉 iOS SETUP COMPLETE!${NC}"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Wait for iOS Simulator download to finish (currently at 11%)"
echo "2. Run: open -a Simulator"
echo "3. Run: cd flutter_app && flutter run"
echo ""
echo -e "${GREEN}Your app will launch on iOS! 🚀${NC}"


