import asyncio
import os
import json
import sys
# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tools import create_tools_with_session
from dotenv import load_dotenv

async def test_slot_numbering():
    load_dotenv()
    session_id = f"test_numbering_{os.urandom(4).hex()}"
    print(f"--- Testing Slot Numbering (Session: {session_id}) ---")
    
    tools = create_tools_with_session(session_id)
    check_slots_tool = next((t for t in tools if t.name == "check_calcom_slots"), None)
    
    if not check_slots_tool:
        print("❌ Error: check_calcom_slots tool not found.")
        return

    try:
        # Run the tool
        result_json = await check_slots_tool.ainvoke({})
        result = json.loads(result_json)
        
        if not result.get("available"):
            print("ℹ️ No slots available for testing right now. Please ensure there are available slots on Cal.com.")
            return

        formatted_slots = result.get("formatted", [])
        print(f"Found {len(formatted_slots)} formatted slots:")
        
        all_numbered = True
        for i, slot in enumerate(formatted_slots):
            print(f"  Slot {i+1}: {slot}")
            if not slot.startswith(f"{i+1}. "):
                all_numbered = False
                print(f"  ❌ Slot {i+1} is NOT correctly numbered!")
        
        if all_numbered:
            print("✅ Success: All slots are correctly numbered (1., 2., 3., etc.).")
        else:
            print("❌ Failure: Some slots are not correctly numbered.")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_slot_numbering())
