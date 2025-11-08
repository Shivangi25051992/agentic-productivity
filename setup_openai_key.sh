#!/bin/bash

# Setup OpenAI API Key for Meal Planning
echo "🔐 OpenAI API Key Setup"
echo "================================"
echo ""
echo "The meal planning feature needs an OpenAI API key to generate meal plans."
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Creating .env from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ Created .env file"
    else
        echo "⚠️  No .env.example found, creating new .env file"
        touch .env
    fi
fi

# Check current OpenAI key
current_key=$(grep -E "^OPENAI_API_KEY=" .env | cut -d '=' -f2)

if [ -z "$current_key" ]; then
    echo "⚠️  OPENAI_API_KEY is not set in .env"
else
    echo "✅ OPENAI_API_KEY is set (${#current_key} characters)"
    if [ ${#current_key} -lt 20 ]; then
        echo "⚠️  But the key looks too short! It should be ~50+ characters"
    fi
fi

echo ""
echo "To set up your OpenAI API key:"
echo ""
echo "1. Get your API key from: https://platform.openai.com/api-keys"
echo "2. Run: echo 'OPENAI_API_KEY=your-key-here' >> .env"
echo "3. OR edit .env file directly and add: OPENAI_API_KEY=your-key-here"
echo "4. Then restart the backend"
echo ""
echo "Example:"
echo '  echo "OPENAI_API_KEY=sk-proj-abc123..." >> .env'
echo ""

