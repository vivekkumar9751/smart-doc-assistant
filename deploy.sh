#!/bin/bash

# Smart Document Assistant - Server Deployment Script
# This script helps deploy the application on a server

echo "🚀 Starting Smart Document Assistant Server Deployment"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "📝 Creating .env from template..."
    
    if [ -f ".env.template" ]; then
        cp .env.template .env
        echo "✅ .env file created from template"
        echo "⚠️  IMPORTANT: Edit .env file with your actual OpenAI API key before continuing"
        echo "   Your API key should be in format: OPENAI_API_KEY=sk-proj-YOUR_ACTUAL_KEY"
        echo "   Get your key from: https://platform.openai.com/api-keys"
        exit 1
    else
        echo "❌ No .env.template found. Please create .env manually."
        exit 1
    fi
fi

# Validate API key in .env
echo "🔍 Validating OpenAI API key..."
source .env

if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ OPENAI_API_KEY not set in .env file"
    exit 1
fi

if [[ ! "$OPENAI_API_KEY" =~ ^sk- ]]; then
    echo "❌ Invalid API key format. Must start with sk-"
    exit 1
fi

if [ ${#OPENAI_API_KEY} -lt 20 ]; then
    echo "❌ API key seems too short"
    exit 1
fi

echo "✅ API key format looks valid"

# Install requirements
echo "📦 Installing Python requirements..."
pip install -r requirements.txt

# Test OpenAI connectivity
echo "🧪 Testing OpenAI API connectivity..."
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()

try:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv(\"OPENAI_API_KEY\"))
    response = client.chat.completions.create(
        model=\"gpt-3.5-turbo\",
        messages=[{\"role\": \"user\", \"content\": \"Hello\"}],
        max_tokens=5
    )
    print(\"✅ OpenAI API connection successful\")
except Exception as e:
    print(f\"❌ OpenAI API connection failed: {e}\")
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ OpenAI API test failed. Please check your API key and billing."
    exit 1
fi

echo "✅ All checks passed! Ready to start the server."
echo ""
echo "🎯 To start the server, run:"
echo "   Backend:  uvicorn backend.api:app --host 0.0.0.0 --port 8000"
echo "   Frontend: streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0"
echo ""
echo "🔗 Server will be available at:"
echo "   API: http://YOUR_SERVER_IP:8000"
echo "   App: http://YOUR_SERVER_IP:8501"

