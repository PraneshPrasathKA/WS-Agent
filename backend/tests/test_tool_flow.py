import asyncio
import os
import sys
# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agent import process_message
from dotenv import load_dotenv

async def test_tool_calling():
    load_dotenv()
    session_id = f"test_tool_{os.urandom(4).hex()}"
    print(f"--- Testing Tool Calling Logic (Session: {session_id}) ---")
    
    # Message that should trigger check_calcom_slots
    message = "book me an appointment please"
    print(f"User: {message}")
    
    try:
        result = await process_message(message, session_id)
        print(f"AI: {result['reply']}")
        
        # Check if slots are present in result
        if result.get("availableSlots"):
            print(f"✅ Success! Found {len(result['availableSlots'])} slots in response.")
        else:
            print("❌ Failure: No slots found in response.")
            
        # Check if raw function tags are in reply
        if "<function" in result['reply']:
            print("❌ Failure: Raw function tags visible in reply.")
        else:
            print("✅ Success: No raw function tags in reply.")
            
    except Exception as e:
        import traceback
        print(f"❌ Error during test: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_tool_calling())
