# Quick Start Guide

## Backend Setup (5 minutes)

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
python main.py
```

## Frontend Setup (3 minutes)

```bash
cd frontend
npm install
# Create .env.local with NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
npm run dev
```

## Environment Variables Needed

### Backend (.env)
- `GEMINI_API_KEY` - Your Google Gemini API key
- `GEMINI_MODEL` - Model name (default: gemini-1.5-flash, or use gemini-2.5-flash when available)
- `CALENDLY_API_TOKEN` - Calendly Personal Access Token
- `CALENDLY_EVENT_TYPE_UUID` - Your Calendly event type UUID
- `PORT` - Server port (default: 8000)

### Frontend (.env.local)
- `NEXT_PUBLIC_BACKEND_URL` - Backend URL (default: http://localhost:8000)

## Testing the Flow

1. Open http://localhost:3000
2. Type: "What does WS do?"
   - Should show overview video
3. Type: "Yes, I use HubSpot"
   - Should check for Calendly slots
4. Follow prompts to book meeting or join waitlist

## Production Notes

- State is in-memory (not persistent across restarts)
- Consider Redis for production state management
- Update CORS origins in main.py for production
- Use environment variables for all secrets

