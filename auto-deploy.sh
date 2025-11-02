#!/bin/bash

# ============================================================================
# Automated End-to-End Deployment Script
# Handles: Git push, GitHub Actions trigger, monitoring
# ============================================================================

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Automated End-to-End Deployment${NC}"
echo "================================================"
echo ""

# ============================================================================
# STEP 1: Check Prerequisites
# ============================================================================

echo -e "${YELLOW}📋 Step 1: Checking prerequisites...${NC}"

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git is not installed${NC}"
    exit 1
fi

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${YELLOW}⚠️  GitHub CLI (gh) not installed${NC}"
    echo ""
    echo "To enable full automation, install GitHub CLI:"
    echo "  brew install gh"
    echo ""
    echo "Then authenticate:"
    echo "  gh auth login"
    echo ""
    read -p "Continue without gh CLI? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
    GH_CLI_AVAILABLE=false
else
    GH_CLI_AVAILABLE=true
    echo -e "${GREEN}✅ GitHub CLI available${NC}"
fi

# Check if we're in a git repo
if [ ! -d .git ]; then
    echo -e "${RED}❌ Not a git repository${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites checked${NC}"
echo ""

# ============================================================================
# STEP 2: Git Status Check
# ============================================================================

echo -e "${YELLOW}📋 Step 2: Checking git status...${NC}"

# Check if there are uncommitted changes
if [[ -n $(git status -s) ]]; then
    echo -e "${YELLOW}⚠️  Uncommitted changes detected${NC}"
    git status -s
    echo ""
    read -p "Commit all changes? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git add .
        read -p "Enter commit message: " commit_msg
        git commit -m "$commit_msg"
        echo -e "${GREEN}✅ Changes committed${NC}"
    else
        echo -e "${RED}❌ Cannot proceed with uncommitted changes${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ No uncommitted changes${NC}"
fi

echo ""

# ============================================================================
# STEP 3: Push to GitHub
# ============================================================================

echo -e "${YELLOW}📋 Step 3: Pushing to GitHub...${NC}"

# Get current branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "Current branch: $CURRENT_BRANCH"

# Check if remote exists
if ! git remote get-url origin &> /dev/null; then
    echo -e "${RED}❌ No remote 'origin' configured${NC}"
    exit 1
fi

# Push to GitHub
echo "Pushing to origin/$CURRENT_BRANCH..."
if git push -u origin $CURRENT_BRANCH 2>&1; then
    echo -e "${GREEN}✅ Successfully pushed to GitHub${NC}"
else
    echo -e "${RED}❌ Push failed${NC}"
    echo ""
    echo "Common solutions:"
    echo "1. Authenticate with GitHub CLI:"
    echo "   gh auth login"
    echo ""
    echo "2. Or use SSH:"
    echo "   git remote set-url origin git@github.com:prashantrepocollection/agentic-productivity.git"
    echo ""
    echo "3. Or create a Personal Access Token:"
    echo "   https://github.com/settings/tokens"
    exit 1
fi

echo ""

# ============================================================================
# STEP 4: Check/Add GitHub Secrets (if gh CLI available)
# ============================================================================

if [ "$GH_CLI_AVAILABLE" = true ]; then
    echo -e "${YELLOW}📋 Step 4: Checking GitHub secrets...${NC}"
    
    # Check if secrets exist
    SECRETS_NEEDED=("FIREBASE_SERVICE_ACCOUNT" "GOOGLE_CLOUD_PROJECT" "OPENAI_API_KEY" "FIREBASE_API_KEY")
    MISSING_SECRETS=()
    
    for secret in "${SECRETS_NEEDED[@]}"; do
        if ! gh secret list | grep -q "$secret"; then
            MISSING_SECRETS+=("$secret")
        fi
    done
    
    if [ ${#MISSING_SECRETS[@]} -eq 0 ]; then
        echo -e "${GREEN}✅ All secrets configured${NC}"
    else
        echo -e "${YELLOW}⚠️  Missing secrets: ${MISSING_SECRETS[*]}${NC}"
        echo ""
        echo "To add secrets, run:"
        echo "  gh secret set FIREBASE_SERVICE_ACCOUNT < agentic-productivity-0017f7241a58.json"
        echo "  gh secret set GOOGLE_CLOUD_PROJECT -b 'productivityai-mvp'"
        echo "  gh secret set OPENAI_API_KEY -b 'your-openai-key'"
        echo "  gh secret set FIREBASE_API_KEY -b 'AIzaSyCWfkKNm9Q6nYBHnldlUtlFBS15NJmCBkg'"
        echo ""
        read -p "Add secrets now? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            # Add secrets
            if [ -f "agentic-productivity-0017f7241a58.json" ]; then
                gh secret set FIREBASE_SERVICE_ACCOUNT < agentic-productivity-0017f7241a58.json
                echo -e "${GREEN}✅ FIREBASE_SERVICE_ACCOUNT added${NC}"
            fi
            
            gh secret set GOOGLE_CLOUD_PROJECT -b "productivityai-mvp"
            echo -e "${GREEN}✅ GOOGLE_CLOUD_PROJECT added${NC}"
            
            if [ -f ".env" ]; then
                OPENAI_KEY=$(grep OPENAI_API_KEY .env | cut -d '=' -f2)
                if [ -n "$OPENAI_KEY" ]; then
                    gh secret set OPENAI_API_KEY -b "$OPENAI_KEY"
                    echo -e "${GREEN}✅ OPENAI_API_KEY added${NC}"
                fi
            fi
            
            gh secret set FIREBASE_API_KEY -b "AIzaSyCWfkKNm9Q6nYBHnldlUtlFBS15NJmCBkg"
            echo -e "${GREEN}✅ FIREBASE_API_KEY added${NC}"
        fi
    fi
    
    echo ""
fi

# ============================================================================
# STEP 5: Trigger GitHub Actions (if gh CLI available)
# ============================================================================

if [ "$GH_CLI_AVAILABLE" = true ]; then
    echo -e "${YELLOW}📋 Step 5: Checking GitHub Actions...${NC}"
    
    # Check if workflow exists
    if gh workflow list | grep -q "CI/CD"; then
        echo -e "${GREEN}✅ CI/CD workflow found${NC}"
        
        # Get latest workflow run
        echo ""
        echo "Latest workflow runs:"
        gh run list --limit 3
        
        echo ""
        read -p "Watch latest workflow run? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo ""
            echo -e "${BLUE}📊 Watching workflow (Ctrl+C to exit)...${NC}"
            gh run watch
        fi
    else
        echo -e "${YELLOW}⚠️  CI/CD workflow not found${NC}"
        echo "Workflow will run automatically after push"
    fi
else
    echo -e "${YELLOW}📋 Step 5: GitHub Actions${NC}"
    echo "Install GitHub CLI for automated monitoring:"
    echo "  brew install gh"
    echo "  gh auth login"
    echo ""
    echo "Or manually check:"
    echo "  https://github.com/prashantrepocollection/agentic-productivity/actions"
fi

echo ""

# ============================================================================
# STEP 6: Summary
# ============================================================================

echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo "📊 Next steps:"
echo ""
echo "1. View GitHub Actions:"
echo "   https://github.com/prashantrepocollection/agentic-productivity/actions"
echo ""
echo "2. Monitor test results:"
if [ "$GH_CLI_AVAILABLE" = true ]; then
    echo "   gh run watch"
else
    echo "   (Install gh CLI: brew install gh)"
fi
echo ""
echo "3. View deployment status:"
echo "   https://github.com/prashantrepocollection/agentic-productivity"
echo ""
echo -e "${BLUE}🎉 All done! Tests will run automatically.${NC}"


