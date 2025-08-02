# Congress.gov API Key Documentation

## API Key Information

**Provider**: Congress.gov  
**Purpose**: Fetching real-time congressional bills, member information, and legislative data  
**Documentation**: https://api.congress.gov/  
**Rate Limit**: 5,000 requests per hour  

## Security Notes

- ✅ API key stored in `backend/.env` file
- ✅ `.env` file is excluded from git via `.gitignore`
- ✅ Key is loaded via environment variables in application
- ⚠️ Never commit API keys to version control
- ⚠️ Regenerate key if accidentally exposed

## Usage

The API key is automatically loaded by the application from the environment variable:

```python
from app.core.config import settings
congress_api_key = settings.CONGRESS_API_KEY
```

## Testing Connectivity

Test API connectivity with:

```bash
cd backend
source venv/bin/activate
python ingest_data.py --test-apis
```

## Key Features Available

- **Bills**: Current and historical congressional bills
- **Members**: Current House and Senate member information  
- **Committees**: Committee structure and membership
- **Nominations**: Presidential nominations requiring Senate confirmation
- **Treaties**: Treaties submitted to the Senate
- **Congressional Records**: Floor proceedings and debates

## Data Refresh Schedule

- **Recent**: Every 6 hours (automated)
- **Historical**: Weekly backfill (manual)
- **Emergency**: On-demand via CLI tool