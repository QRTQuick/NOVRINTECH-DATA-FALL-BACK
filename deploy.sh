#!/bin/bash

echo "🚀 Novrintech Data Fall Back - Production Deployment"

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please create it from .env.example"
    exit 1
fi

# Check if Firebase credentials exist
if [ ! -f firebase-credentials.json ]; then
    echo "❌ firebase-credentials.json not found. Please download from Firebase Console"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads logs

# Initialize database
echo "🗄️ Initializing database..."
python -c "from app.core.database import init_db; init_db()"

# Generate first API key
echo "🔑 Generate your first API key:"
echo "python app/utils/api_key_generator.py 'My First App'"

echo "✅ Deployment complete!"
echo ""
echo "🚀 Start the server:"
echo "uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo ""
echo "📊 Admin panel (change the admin key in production):"
echo "GET /admin/stats?admin_key=admin_super_secret_key_change_this"