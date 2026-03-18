import requests
import json
import time
import os
import sys
# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

url = "http://localhost:8000/chat"
payload = {
    "message": "hi",
    "session_id": "test_timing"
}
headers = {
    "Content-Type": "application/json"
}

try:
    print(f"Sending request to {url}...")
    start = time.time()
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    end = time.time()
    print(f"External Time taken: {end - start:.2f} seconds")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
