#!/bin/bash
# iOS Setup Script - Run AFTER Xcode Installation
# This script completes the iOS setup once Xcode is installed

set -e  # Exit on error

echo "🍎 iOS SETUP - POST-XCODE INSTALLATION"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# ============================================================================
# 1. VERIFY XCODE INSTALLATION
# ============================================================================
echo -e "${BLUE}📋 Step 1: Verifying Xcode installation...${NC}"

if ! command -v xcodebuild &> /dev/null; then
    echo -e "${RED}❌ ERROR: Xcode is not installed or not in PATH${NC}"
    echo "Please install Xcode from the App Store first."
    exit 1
fi

XCODE_VERSION=$(xcodebuild -version | head -1)
echo -e "${GREEN}✅ $XCODE_VERSION installed${NC}"
echo ""

# ============================================================================
# 2. CONFIGURE XCODE
# ============================================================================
echo -e "${BLUE}📋 Step 2: Configuring Xcode...${NC}"

# Set Xcode path
echo "Setting Xcode developer directory..."
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer

# Accept license (non-interactive)
echo "Accepting Xcode license..."
sudo xcodebuild -license accept 2>/dev/null || echo "License already accepted"

# Run first launch
echo "Running Xcode first launch setup..."
sudo xcodebuild -runFirstLaunch 2>/dev/null || echo "First launch already completed"

echo -e "${GREEN}✅ Xcode configured${NC}"
echo ""

# ============================================================================
# 3. VERIFY COCOAPODS
# ============================================================================
echo -e "${BLUE}📋 Step 3: Verifying CocoaPods...${NC}"

if ! command -v pod &> /dev/null; then
    echo -e "${YELLOW}⚠️  CocoaPods not found, installing...${NC}"
    brew install cocoapods
fi

POD_VERSION=$(pod --version)
echo -e "${GREEN}✅ CocoaPods $POD_VERSION installed${NC}"
echo ""

# ============================================================================
# 4. INSTALL IOS DEPENDENCIES
# ============================================================================
echo -e "${BLUE}📋 Step 4: Installing iOS dependencies...${NC}"

cd flutter_app/ios

echo "Running pod install..."
export LANG=en_US.UTF-8
pod install

echo -e "${GREEN}✅ iOS dependencies installed${NC}"
echo ""

cd ../..

# ============================================================================
# 5. RUN FLUTTER DOCTOR
# ============================================================================
echo -e "${BLUE}📋 Step 5: Running Flutter doctor...${NC}"

flutter doctor

echo ""

# ============================================================================
# 6. LIST AVAILABLE DEVICES
# ============================================================================
echo -e "${BLUE}📋 Step 6: Listing available iOS devices...${NC}"

flutter devices

echo ""

# ============================================================================
# 7. OPEN SIMULATOR
# ============================================================================
echo -e "${BLUE}📋 Step 7: Opening iOS Simulator...${NC}"

open -a Simulator

echo -e "${GREEN}✅ iOS Simulator launched${NC}"
echo ""

# ============================================================================
# SUMMARY
# ============================================================================
echo "========================================"
echo -e "${GREEN}🎉 iOS SETUP COMPLETE!${NC}"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Wait for iOS Simulator to fully launch"
echo "2. Run: cd flutter_app && flutter run"
echo "3. Your app will build and launch on iOS!"
echo ""
echo "Useful commands:"
echo "  flutter run                    # Run on default device"
echo "  flutter run -d <device-id>     # Run on specific device"
echo "  flutter devices                # List available devices"
echo "  r (while running)              # Hot reload"
echo "  R (while running)              # Hot restart"
echo "  q (while running)              # Quit"
echo ""
echo -e "${GREEN}Happy iOS development! 🚀${NC}"


