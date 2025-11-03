#!/bin/bash

echo "🔍 ENVIRONMENT VERIFICATION"
echo "=========================================="
echo ""

echo "📋 LOCAL ENVIRONMENT (.env.local):"
echo "---"
echo "GOOGLE_CLOUD_PROJECT: $(grep GOOGLE_CLOUD_PROJECT .env.local | cut -d '=' -f2)"
echo "OPENAI_API_KEY: $(grep OPENAI_API_KEY .env.local | cut -d '=' -f2 | cut -c1-20)..."
echo "ADMIN_USERNAME: $(grep ADMIN_USERNAME .env.local | cut -d '=' -f2)"
echo "ADMIN_PASSWORD: $(grep ADMIN_PASSWORD .env.local | cut -d '=' -f2)"
echo ""

echo "📋 PRODUCTION ENVIRONMENT (Cloud Run):"
echo "---"
echo "Getting environment variables from Cloud Run..."
echo ""

# Get Cloud Run environment variables
/Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity/gcloud/google-cloud-sdk/bin/gcloud run services describe aiproductivity-backend \
  --region us-central1 \
  --project productivityai-mvp \
  --format='value(spec.template.spec.containers[0].env)' 2>/dev/null | while IFS= read -r line; do
    if [[ $line == *"name"* ]]; then
        name=$(echo "$line" | grep -o "name=[^,]*" | cut -d'=' -f2 | tr -d "'")
        value=$(echo "$line" | grep -o "value=[^}]*" | cut -d'=' -f2 | tr -d "'")
        
        # Mask sensitive values
        if [[ $name == *"KEY"* ]] || [[ $name == *"PASSWORD"* ]] || [[ $name == *"SECRET"* ]]; then
            masked_value="${value:0:20}..."
        else
            masked_value="$value"
        fi
        
        echo "$name: $masked_value"
    fi
done

echo ""
echo "=========================================="
echo "✅ VERIFICATION COMPLETE"
echo "=========================================="
echo ""
echo "⚠️  NOTE: Using same credentials for local and production"
echo "   This is OK for now, but should be separated later"
echo ""
