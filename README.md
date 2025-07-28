# GovernmentGPT

A modern civic information platform that ingests, summarizes, and enables intelligent search across congressional bills and executive orders.

## Project Structure

```
GovernmentGPT/
├── backend/              # FastAPI backend application
├── frontend/             # Next.js frontend application  
├── Documentation/        # Implementation guides and documentation
├── scripts/             # Deployment and utility scripts
├── docker-compose.yml   # Development environment
└── README.md           # This file
```

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15+ with vector extensions (pgvector)
- **Cache**: Redis 7+
- **Authentication**: Session-based with PostgreSQL storage

### Frontend
- **Framework**: Next.js 14+ with TypeScript
- **Styling**: Tailwind CSS with shadcn/ui components
- **State Management**: React Query

### AI Integration
- **Primary LLM**: Anthropic Claude Sonnet 4 via API
- **Embeddings**: Voyage-law-2 for legal text
- **Search**: Hybrid semantic + BM25 using Reciprocal Rank Fusion

## Development Setup

1. **Clone and setup environment**:
   ```bash
   cd GovernmentGPT
   ```

2. **Backend setup**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install -r requirements.txt
   ```

3. **Frontend setup**:
   ```bash
   cd frontend
   npm install
   ```

4. **Database setup**:
   ```bash
   # Start PostgreSQL and Redis with Docker
   docker-compose up -d postgres redis
   
   # Run database migrations
   cd backend
   alembic upgrade head
   ```

5. **Environment variables**:
   Copy `.env.example` to `.env` and configure:
   - Database connection strings
   - API keys (Congress.gov, Anthropic, etc.)
   - JWT secrets

## Running the Application

### Development
```bash
# Terminal 1: Backend
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2: Frontend  
cd frontend
npm run dev
```

### Production
```bash
docker-compose up -d
```

## Key Features

- **Intelligent Search**: Hybrid semantic and keyword search across government documents
- **AI Summarization**: Plain-language summaries of complex legislation
- **Real-time Updates**: Daily ingestion of new bills and executive orders
- **Accessibility**: WCAG 2.1 Level AA compliant
- **Mobile-First**: Responsive design optimized for all devices

## Data Sources

- **Congress.gov API**: House and Senate bills, voting records
- **GovTrack API**: Historical bill tracking and member information
- **Federal Register API**: Executive orders and presidential documents
- **GovInfo API**: Full-text congressional documents

## Contributing

1. Review the implementation guide in `Documentation/`
2. Follow the development setup instructions
3. Create feature branches from `main`
4. Ensure tests pass and maintain code coverage
5. Submit pull requests with comprehensive descriptions

## License

This project is designed for civic transparency and public benefit.