#!/bin/bash

# GovernmentGPT Development Startup Script
# This script helps set up the development environment quickly

set -e  # Exit on any error

echo "🚀 Starting GovernmentGPT Development Environment"
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: Please run this script from the GovernmentGPT root directory"
    exit 1
fi

# Start database services
echo "📦 Starting database services..."
docker-compose up -d postgres redis

# Wait for postgres to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
for i in {1..30}; do
    if docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
        echo "✅ PostgreSQL is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ PostgreSQL failed to start within 30 seconds"
        exit 1
    fi
    sleep 1
done

# Check if backend virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    cd ..
fi

# Activate virtual environment and run database setup
echo "🗄️  Setting up database..."
cd backend
source venv/bin/activate

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit backend/.env with your API keys before proceeding"
fi

# Run database migrations
echo "🔄 Running database migrations..."
alembic upgrade head

# Seed database with sample data
echo "🌱 Seeding database with sample data..."
python seed_data.py

cd ..

# Check if frontend dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

# Create frontend .env if it doesn't exist
if [ ! -f "frontend/.env.local" ]; then
    echo "📝 Creating frontend .env.local..."
    cd frontend
    cp .env.example .env.local
    cd ..
fi

echo ""
echo "✅ Development environment setup complete!"
echo ""
echo "🎯 Next steps:"
echo "   1. Edit backend/.env with your API keys (optional for basic testing)"
echo "   2. Start the backend: cd backend && source venv/bin/activate && uvicorn main:app --reload"
echo "   3. Start the frontend: cd frontend && npm run dev"
echo "   4. Visit http://localhost:3000 to see the application"
echo ""
echo "📊 Database includes sample data:"
echo "   - 4 legislators (Schumer, Markey, Abraham, Pelosi)"
echo "   - 4 documents (HR-1, Climate Emergency Act, Infrastructure Act, EO-14008)"
echo "   - 5 popular search terms"
echo ""
echo "🔍 API available at: http://localhost:8000"
echo "📖 API docs at: http://localhost:8000/docs"