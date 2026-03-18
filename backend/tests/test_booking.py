import asyncio
import os
from dotenv import load_dotenv
import sys

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools import create_tools_with_session
from state import state_manager

async def test_booking():
    load_dotenv()
    session_id = "test_session_123"
    
    # 1. Check slots
    print("--- Checking Slots ---")
    tools = create_tools_with_session(session_id)
    slot_tool = next(t for t in tools if t.name == "check_calcom_slots")
    slots_res = await slot_tool.ainvoke({})
    print(f"Slots result: {slots_res}")
    
    # 2. Book meeting
    print("\n--- Booking Meeting ---")
    book_tool = next(t for t in tools if t.name == "book_calcom_meeting")
    # We'll use a dummy email for testing
    res = await book_tool.ainvoke({
        "email": "test@example.com",
        "name": "Test User"
    })
    print(f"Booking result: {res}")

if __name__ == "__main__":
    asyncio.run(test_booking())
