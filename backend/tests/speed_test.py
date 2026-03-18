import asyncio
import time
import os
import sys
# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agent import process_message

async def main():
    session_id = f"test_speed_{int(time.time())}"
    
    print("--- FIRST REQUEST (Warm-up) ---")
    start = time.time()
    res1 = await process_message("hi", session_id)
    end = time.time()
    print(f"Time: {end - start:.2f}s")
    print(f"Reply: {res1['reply']}")
    
    print("\n--- SECOND REQUEST (Cached) ---")
    start = time.time()
    res2 = await process_message("tell me about your services", session_id)
    end = time.time()
    print(f"Time: {end - start:.2f}s")
    print(f"Reply: {res2['reply']}")

if __name__ == "__main__":
    asyncio.run(main())
