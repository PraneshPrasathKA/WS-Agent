# WS Sales Agent Backend

FastAPI backend with LangChain agent for AI-powered sales conversations.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash
CALCOM_API_KEY=your_calcom_api_key_here
CALCOM_EVENT_TYPE_ID=your_calcom_event_type_id_here
GROQ_API_KEY=your_groq_api_key_here
PORT=8000
DEBUG=false
```

3. Run the server:
```bash
python main.py
```

Or with uvicorn:
```bash
uvicorn main:app --reload --port 8000
```

## API Endpoints

- `POST /chat` - Process chat message
  - Body: `{"message": "text", "session_id": "optional"}`
  - Returns: `{"reply": "...", "showAsset": "...", "stage": "...", "session_id": "...", "availableSlots": [...]}`

- `POST /voice-webhook` - Handle Vapi voice webhook
  - Body: Vapi webhook format
  - Returns: `{"message": "...", "showAsset": "...", "session_id": "..."}`

- `GET /health` - Health check

## Architecture

- `main.py` - FastAPI application and routes
- `agent.py` - LangChain agent setup and message processing
- `tools.py` - Agent tools (Cal.com, assets)
- `state.py` - Session state management
- `utils.py` - Utility functions for Cal.com API v2

## State Management

State is stored in-memory per session using `MemorySaver`. Each session tracks:
- Current stage (INTRO, EXPLAINED, QUALIFYING, BOOKING, WAITLIST, DONE)
- User profile (name, email, phone)
- Last shown asset
- Booking information (available slots, selected slot)

## Cal.com Integration

Requires:
- Cal.com API key (Personal Access Token)
- Event Type ID

The agent checks for available slots (truncated to top 5) and books meetings programmatically using the v2 API.

