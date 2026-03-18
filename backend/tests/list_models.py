import os
import asyncio
import httpx
import sys
# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dotenv import load_dotenv

async def list_xai_models():
    print("\n--- Listing xAI Models ---")
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        print("❌ XAI_API_KEY not found")
        return
    
    url = "https://api.x.ai/v1/models"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200:
                models = resp.json().get("data", [])
                for m in models:
                    print(f"- {m.get('id')}")
            else:
                print(f"❌ Failed: {resp.status_code} - {resp.text}")
        except Exception as e:
            print(f"❌ Error: {e}")

async def list_gemini_models():
    print("\n--- Listing Gemini Models ---")
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found")
        return
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url)
            if resp.status_code == 200:
                models = resp.json().get("models", [])
                for m in models:
                    print(f"- {m.get('name')}")
            else:
                print(f"❌ Failed: {resp.status_code} - {resp.text}")
        except Exception as e:
            print(f"❌ Error: {e}")

async def main():
    load_dotenv()
    await list_xai_models()
    await list_gemini_models()

if __name__ == "__main__":
    asyncio.run(main())
