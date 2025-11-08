#!/bin/bash

################################################################################
# Configuration Management Script
# 
# Ensures sensitive files are never committed or deployed
# Manages environment-specific configurations
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Sensitive files that should NEVER be committed
SENSITIVE_FILES=(
    ".env"
    ".env.local"
    ".env.production"
    "*.key"
    "*.pem"
    "*credentials*.json"
    "*secret*"
    "firebase-adminsdk-*.json"
    ".firebase/hosting*.cache"
)

# Check if sensitive files are in git
check_sensitive_files() {
    echo -e "${YELLOW}🔍 Checking for sensitive files in git...${NC}"
    
    local found_sensitive=false
    
    for pattern in "${SENSITIVE_FILES[@]}"; do
        # Check if pattern exists in git
        if git ls-files | grep -q "$pattern"; then
            echo -e "${RED}❌ Found sensitive file in git: $pattern${NC}"
            found_sensitive=true
        fi
    done
    
    if [ "$found_sensitive" = true ]; then
        echo -e "${RED}❌ Sensitive files found in git!${NC}"
        echo -e "${YELLOW}Run: git rm --cached <file> to remove them${NC}"
        return 1
    else
        echo -e "${GREEN}✅ No sensitive files in git${NC}"
        return 0
    fi
}

# Ensure .gitignore has sensitive patterns
ensure_gitignore() {
    echo -e "${YELLOW}🔍 Checking .gitignore...${NC}"
    
    if [ ! -f ".gitignore" ]; then
        echo -e "${YELLOW}⚠️  .gitignore not found, creating...${NC}"
        touch .gitignore
    fi
    
    # Add sensitive patterns to .gitignore
    for pattern in "${SENSITIVE_FILES[@]}"; do
        if ! grep -q "^$pattern$" .gitignore; then
            echo "$pattern" >> .gitignore
            echo -e "${GREEN}✅ Added $pattern to .gitignore${NC}"
        fi
    done
    
    echo -e "${GREEN}✅ .gitignore is up to date${NC}"
}

# Create template for environment files
create_env_template() {
    echo -e "${YELLOW}📝 Creating .env.template...${NC}"
    
    cat > .env.template << 'EOF'
# Environment Configuration Template
# Copy this to .env.local for local development
# Copy this to .env.production for production deployment

# Firebase Configuration
GOOGLE_CLOUD_PROJECT=your-project-id
FIREBASE_API_KEY=your-api-key

# OpenAI Configuration
OPENAI_API_KEY=your-openai-key

# Backend Configuration
API_BASE_URL=http://localhost:8000

# Frontend Configuration
FLUTTER_WEB_PORT=9090

# Database
FIRESTORE_EMULATOR_HOST=  # Leave empty for production

# Add your configuration keys here (without values)
EOF
    
    echo -e "${GREEN}✅ Created .env.template${NC}"
}

# Verify configuration files exist
verify_config_files() {
    echo -e "${YELLOW}🔍 Verifying configuration files...${NC}"
    
    local missing_files=()
    
    # Check for local config
    if [ ! -f ".env.local" ]; then
        missing_files+=(".env.local")
    fi
    
    # Check for production config
    if [ ! -f ".env.production" ]; then
        missing_files+=(".env.production")
    fi
    
    if [ ${#missing_files[@]} -gt 0 ]; then
        echo -e "${YELLOW}⚠️  Missing configuration files:${NC}"
        for file in "${missing_files[@]}"; do
            echo -e "  - $file"
        done
        echo -e "${YELLOW}💡 Copy .env.template and fill in your values${NC}"
    else
        echo -e "${GREEN}✅ All configuration files present${NC}"
    fi
}

# Main execution
main() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║          🔐 Configuration Management                       ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    
    ensure_gitignore
    echo ""
    
    check_sensitive_files
    echo ""
    
    create_env_template
    echo ""
    
    verify_config_files
    echo ""
    
    echo -e "${GREEN}✅ Configuration management complete${NC}"
    echo ""
}

main

