import asyncio
import os
import sys
# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agent import process_message
from state import state_manager

async def test_scroll():
    session_id = "test_scroll_session"
    message = "what services do you offer"
    
    print(f"Testing message: {message}")
    result = await process_message(message, session_id)
    
    print("\nResult:")
    print(f"Reply: {result['reply']}")
    print(f"ShowAsset: {result['showAsset']}")
    
    state = state_manager.get(session_id)
    if state:
        print(f"Final State last_asset: {state.last_asset}")

if __name__ == "__main__":
    asyncio.run(test_scroll())
