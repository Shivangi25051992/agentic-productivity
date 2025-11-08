#!/bin/bash
# Convert .env file to YAML format for gcloud

INPUT_FILE="${1:-.env.production}"
OUTPUT_FILE="${2:-.env.production.yaml}"

echo "# Generated from $INPUT_FILE" > "$OUTPUT_FILE"

# Read .env file and convert to YAML
while IFS='=' read -r key value || [ -n "$key" ]; do
    # Skip comments and empty lines
    [[ "$key" =~ ^#.*$ ]] && continue
    [[ -z "$key" ]] && continue
    
    # Remove leading/trailing whitespace
    key=$(echo "$key" | xargs)
    value=$(echo "$value" | xargs)
    
    # Skip if key is empty
    [[ -z "$key" ]] && continue
    
    # Write to YAML format
    echo "$key: \"$value\"" >> "$OUTPUT_FILE"
done < "$INPUT_FILE"

echo "✅ Converted $INPUT_FILE to $OUTPUT_FILE"


