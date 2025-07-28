# GovernmentGPT Development Guide

Quick setup guide for local development and testing.

## Quick Start (Automated)

Run the development setup script:

```bash
./scripts/start-dev.sh
```

This script will:
- Start PostgreSQL and Redis with Docker
- Create Python virtual environment
- Run database migrations
- Seed sample data
- Install frontend dependencies
- Create environment files

## Manual Setup

### 1. Start Database Services

```bash
docker-compose up -d postgres redis
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your settings (optional for basic testing)

# Run migrations
alembic upgrade head

# Seed sample data
python seed_data.py
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Setup environment
cp .env.example .env.local
```

### 4. Start Development Servers

**Backend (Terminal 1):**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend (Terminal 2):**
```bash
cd frontend
npm run dev
```

## Testing the Application

### API Testing (localhost:8000)

1. **Health Check**: http://localhost:8000/health
2. **API Documentation**: http://localhost:8000/docs
3. **Search Documents**: 
   ```bash
   curl -X POST "http://localhost:8000/api/v1/search" \
     -H "Content-Type: application/json" \
     -d '{"query": "climate change", "search_type": "hybrid"}'
   ```
4. **Recent Documents**: http://localhost:8000/api/v1/search/recent

### Frontend Testing (localhost:3000)

1. **Home Page**: http://localhost:3000
2. **Search Interface**: Try searching for "climate", "infrastructure", or "voting"
3. **Document Details**: Click on any document card

## Sample Data Included

The seed script creates:

### Legislators
- **Chuck Schumer** (D-NY, Senate)
- **Ed Markey** (D-MA, Senate)  
- **Ralph Abraham** (R-LA-5, House)
- **Nancy Pelosi** (D-CA-11, House)

### Documents
- **HR-1-118**: For the People Act of 2023
- **S-1-118**: Climate Emergency Act
- **HR-3684-117**: Infrastructure Investment and Jobs Act (signed)
- **EO-14008**: Executive Order on Climate Crisis

### Popular Searches
- climate change, infrastructure bill, voting rights, healthcare reform, immigration policy

## Development URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **API Health**: http://localhost:8000/health

## Troubleshooting

### Database Connection Issues
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Reset database
docker-compose down
docker-compose up -d postgres redis
cd backend && alembic upgrade head && python seed_data.py
```

### Port Conflicts
- Backend uses port 8000
- Frontend uses port 3000  
- PostgreSQL uses port 5432
- Redis uses port 6379

### Python Environment Issues
```bash
# Recreate virtual environment
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Next Steps for Production

1. **Add Government APIs**: Implement Congress.gov, GovTrack data ingestion
2. **AI Integration**: Add Claude Sonnet 4 for summarization
3. **Vector Search**: Implement semantic search with embeddings
4. **Authentication**: Add user accounts and personalization
5. **Monitoring**: Set up Prometheus/Grafana monitoring

## Architecture Notes

- **Backend**: FastAPI with async PostgreSQL and Redis
- **Frontend**: Next.js 14 with TypeScript and Tailwind CSS
- **Database**: PostgreSQL with full-text search indexes
- **Caching**: Redis for search results and session storage
- **Deployment**: Docker containers with Kubernetes support