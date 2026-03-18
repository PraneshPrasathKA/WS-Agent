# WS Sales Agent POC

Full-stack AI Sales Agent with voice and text support, implementing the "Golden Flow" sales process.

## Project Structure

```
WS/
├── backend/          # FastAPI + LangChain backend
│   ├── main.py      # FastAPI application
│   ├── agent.py     # LangChain agent setup
│   ├── tools.py     # Agent tools (Cal.com, assets)
│   ├── state.py     # State management
│   ├── utils.py     # Utilities
│   └── requirements.txt
├── frontend/        # Next.js frontend
│   ├── app/         # Next.js app directory
│   ├── components/  # React components
│   └── package.json
└── README.md
```

## Golden Flow

1. **EXPLAIN** - 2-sentence sales pitch of WS
2. **SHOW** - Trigger visual asset (video, GIF, pricing card)
3. **PIVOT** - Qualify the lead ("Do you use HubSpot?")
4. **CLOSE** - Book meeting via Cal.com or capture email for waitlist

## Backend Setup

### Prerequisites

- Python 3.9+
- Google Gemini API key (Gemini 2.0 Flash supported)
- Groq API key (for fast inference)
- Cal.com API key and event type ID

### Installation

```bash
cd backend
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the `backend/` directory:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash
CALCOM_API_KEY=your_calcom_api_key_here
CALCOM_EVENT_TYPE_ID=your_calcom_event_type_id_here
GROQ_API_KEY=your_groq_api_key_here
XAI_API_KEY=your_xai_api_key_here
PORT=8000
DEBUG=false
```

### Running the Backend

```bash
cd backend
python main.py
```

Or with uvicorn:

```bash
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### API Endpoints

- `POST /chat` - Process chat message
- `POST /voice-webhook` - Handle Vapi voice webhook
- `GET /health` - Health check

## Frontend Setup

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
cd frontend
npm install
```

### Environment Variables

Create a `.env.local` file in the `frontend/` directory:

```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

### Running the Frontend

```bash
cd frontend
npm run dev
```

The app will be available at `http://localhost:3000`

## Features

### Backend

- LangChain agent with LangGraph and fallback logic (Groq -> Gemini)
- 4 essential tools:
  - `show_asset()` - Display visual assets
  - `check_calcom_slots()` - Check available meeting slots
  - `book_calcom_meeting()` - Book a meeting
  - `capture_waitlist()` - Add to waitlist
- In-memory state management with MemorySaver
- Cal.com API v2 integration

### Frontend

- Modern Next.js 14 app with TypeScript
- Chat UI with message bubbles and voice support
- Asset panel for displaying videos, GIFs, and pricing cards
- Responsive design with Tailwind CSS
- Session management

## Usage

1. Start the backend server
2. Start the frontend development server
3. Open `http://localhost:3000` in your browser
4. Start chatting with the sales agent

### Example Flow

1. User: "What does WS do?"
   - Agent explains with 2-sentence pitch
   - Shows OVERVIEW_VIDEO asset

2. Agent: "By the way, do you use HubSpot or any CRM?"

3. User: "Yes, we use HubSpot. I'd like to learn more."
   - Agent checks Cal.com slots
   - Offers available time slots

4. User: "I'll take the first slot."
   - Agent asks for Name and Email
   - Agent books meeting via Cal.com

## Production Deployment

### Backend

- Use a production ASGI server (gunicorn with uvicorn workers)
- Set up proper CORS origins
- Use environment variables for secrets
- Consider using Redis for state management instead of in-memory

### Frontend

- Build for production: `npm run build`
- Deploy to Vercel, Netlify, or your preferred hosting
- Update `NEXT_PUBLIC_BACKEND_URL` to production backend URL

## Notes

- State management is in-memory (not persistent across server restarts)
- Cal.com integration requires valid API credentials
- Asset URLs in AssetPanel need to be updated with actual video/GIF URLs
- Voice webhook endpoint is ready for Vapi integration

