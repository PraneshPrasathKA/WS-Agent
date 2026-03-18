from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from agent import process_message
from state import state_manager
from utils import get_calcom_api_key, get_calcom_event_type_id, create_calcom_booking
import uvicorn
import os
import uuid
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="WS AI Assistant API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    showAsset: Optional[str] = None
    stage: str
    session_id: str
    availableSlots: Optional[list] = None


class VoiceWebhookRequest(BaseModel):
    message: Optional[str] = None
    transcript: Optional[str] = None
    session_id: Optional[str] = None


class BookMeetingRequest(BaseModel):
    slot: str
    email: str
    name: Optional[str] = None
    session_id: Optional[str] = None


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ws-sales-agent"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a chat message and return agent response with optional asset.
    """
    try:
        # Generate session_id if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Process message through agent
        result = await process_message(request.message, session_id)
        
        return ChatResponse(
            reply=result["reply"],
            showAsset=result["showAsset"],
            stage=result["stage"],
            session_id=session_id,
            availableSlots=result.get("availableSlots")
        )
    except Exception as e:
        import traceback
        error_detail = str(e)
        if os.getenv("DEBUG", "false").lower() == "true":
            error_detail += f"\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)


@app.post("/book-meeting")
async def book_meeting(request: BookMeetingRequest):
    """
    Book a Cal.com meeting with provided slot and email.
    """
    try:
        session_id = request.session_id or str(uuid.uuid4())
        
        api_key = get_calcom_api_key()
        event_type_id = get_calcom_event_type_id()
        
        # Create the booking
        result = await create_calcom_booking(
            event_type_id, 
            api_key, 
            request.email, 
            request.name or "Lead", 
            request.slot
        )
        
        # Update state
        state = state_manager.get(session_id)
        if state:
            state.booking.slot = request.slot
            state.booking.event_uri = result.get("resource", {}).get("uri", "")
            state.user_profile.email = request.email
            state.stage = "DONE"
            state_manager.set(session_id, state)
        
        event_uri = result.get("resource", {}).get("uri", "")
        return {
            "success": True,
            "message": "Meeting booked successfully!",
            "event_uri": event_uri,
            "session_id": session_id
        }
    except Exception as e:
        import traceback
        error_detail = str(e)
        if os.getenv("DEBUG", "false").lower() == "true":
            error_detail += f"\n{traceback.format_exc()}"
        return {
            "success": False,
            "error": error_detail
        }



if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)

