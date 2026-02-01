#!/bin/bash

# 1. Check API Key (Prompt if not set in environment variables)
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  GEMINI_API_KEY environment variable is not set."
    echo -n "🔑 Please enter your Google Gemini API Key: "
    read -s GEMINI_API_KEY
    echo "" # Newline
fi

echo "🚀 Starting Local Test for SwitchLang..."

# 2. Clean up existing container if it exists (Prevent conflict)
# 2>/dev/null suppresses error messages if the container doesn't exist
echo "🧹 Cleaning up old containers..."
docker rm -f switchlang-test 2>/dev/null || true

# 3. Build Docker Image
# Use ./app folder as context
echo "🔨 Building Docker Image..."
docker build -t switchlang-local ./app

# Exit script if build fails
if [ $? -ne 0 ]; then
    echo "❌ Docker Build Failed!"
    exit 1
fi

# 4. Run Container
# --rm: Automatically remove container when stopped
# --name: Assign a name for easy management
echo "🏃 Running Container..."
echo "🌐 Open your browser at: http://localhost:8501"
echo "🛑 Press Ctrl+C to stop."

docker run --rm \
  -p 8501:8501 \
  --name switchlang-test \
  -e GEMINI_API_KEY="$GEMINI_API_KEY" \
  switchlang-local