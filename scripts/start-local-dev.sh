#!/bin/bash

# GovernmentGPT Local Development Setup (NO DOCKER)
# This script sets up development without Docker containers

set -e

echo "🔒 Starting DOCKER-FREE Local Development Environment"
echo "====================================================="

# Check if we're in the right directory
if [ ! -f "backend/requirements.txt" ]; then
    echo "❌ Error: Please run this script from the GovernmentGPT root directory"
    exit 1
fi

echo "⚠️  NOTE: This setup uses SQLite instead of PostgreSQL for local development"
echo "⚠️  This avoids Docker but limits some advanced features"
echo ""

# Backend setup
echo "🐍 Setting up Python backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📥 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install SQLite adapter (lighter than PostgreSQL)
pip install aiosqlite

# Create local .env for SQLite
echo "📝 Creating local development .env..."
cat > .env << EOF
# Local Development Configuration (NO DOCKER)
DEBUG=True
SECRET_KEY=local-development-secret-change-in-production

# SQLite Database (local file)
DATABASE_URL=sqlite+aiosqlite:///./governmentgpt_local.db

# No Redis for local development
REDIS_URL=

# Security Settings (relaxed for local dev)
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Government APIs (add your keys here)
CONGRESS_API_KEY=
GOVTRACK_API_BASE=https://www.govtrack.us/api/v2
FEDERAL_REGISTER_API_BASE=https://www.federalregister.gov/api/v1

# Rate Limiting (relaxed for local dev)
RATE_LIMIT_PER_MINUTE=1000
RATE_LIMIT_PER_HOUR=10000

# AI Services (optional for basic testing)
ANTHROPIC_API_KEY=
VOYAGE_API_KEY=
EOF

cd ..

# Frontend setup
echo "📦 Setting up frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "📥 Installing Node.js dependencies..."
    npm install
fi

# Create local frontend config
echo "📝 Creating frontend .env.local..."
cat > .env.local << EOF
# Frontend Local Development
NEXT_PUBLIC_API_URL=http://localhost:8000
NODE_ENV=development
EOF

cd ..

echo ""
echo "✅ Local development environment setup complete!"
echo ""
echo "🚀 To start development:"
echo "   1. Backend:  cd backend && source venv/bin/activate && python -m uvicorn main:app --reload --port 8000"
echo "   2. Frontend: cd frontend && npm run dev"
echo ""
echo "📊 Database: SQLite file will be created at backend/governmentgpt_local.db"
echo "🔍 URLs:"
echo "   - Frontend: http://localhost:3000"
echo "   - Backend API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo ""
echo "⚠️  This local setup:"
echo "   ✅ No Docker required (secure)"
echo "   ✅ SQLite database (simple, local file)"
echo "   ✅ Government API integration ready"
echo "   ❌ No Redis caching (acceptable for development)"
echo "   ❌ No advanced PostgreSQL features"