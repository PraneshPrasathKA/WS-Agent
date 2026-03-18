import os
import re
from typing import Optional
import httpx


def get_calcom_api_key() -> str:
    """Get Cal.com API key from environment."""
    api_key = os.getenv("CALCOM_API_KEY")
    if not api_key:
        raise ValueError("CALCOM_API_KEY environment variable is required")
    return api_key


def get_calcom_event_type_id() -> str:
    """Get Cal.com event type ID from environment."""
    event_id = os.getenv("CALCOM_EVENT_TYPE_ID")
    if not event_id:
        raise ValueError("CALCOM_EVENT_TYPE_ID environment variable is required")
    return event_id


async def fetch_calcom_availability(event_type_id: str, api_key: str, start_time: Optional[str] = None) -> dict:
    """Fetch available time slots from Cal.com using v2 API."""
    from datetime import datetime, timedelta
    
    base_url = "https://api.cal.com/v2"
    url = f"{base_url}/slots"
    
    # Calculate start and end dates: start = today, end = 7 weeks (49 days) from today
    if not start_time:
        start_dt = datetime.utcnow()
    else:
        try:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        except:
            start_dt = datetime.utcnow()
    
    # Format dates as YYYY-MM-DD
    # Start date is today (current date)
    start_date = start_dt.strftime('%Y-%m-%d')
    # End date is 7 days from start date
    end_date = (start_dt + timedelta(days=7)).strftime('%Y-%m-%d')
    
    print(f"📅 Cal.com availability check:")
    print(f"   Start date: {start_date} (today)")
    print(f"   End date: {end_date} (7 days from today)")
    
    params = {
        "eventTypeId": event_type_id,
        "start": start_date,
        "end": end_date
    }
    
    headers = {
        "authorization": f"Bearer {api_key}",
        "cal-api-version": "2024-09-04",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            print(f"   Making request to: {url}")
            print(f"   With params: {params}")
            response = await client.get(url, headers=headers, params=params, timeout=10.0)
            print(f"   Response status: {response.status_code}")
            response.raise_for_status()
            data = response.json()
            print(f"   Cal.com API response: {data}")
            
            # Cal.com v2 returns {"data": {"YYYY-MM-DD": [{"start": "..."}, ...]}, "status": "success"}
            # Extract all slots from the data object
            collection = []
            if isinstance(data, dict) and "data" in data:
                slots_data = data["data"]
                if isinstance(slots_data, dict):
                    # Iterate through each date key
                    for date_key, slots_list in slots_data.items():
                        if isinstance(slots_list, list):
                            for slot in slots_list:
                                if isinstance(slot, dict) and "start" in slot:
                                    # Calculate end time (assuming 30-minute slots)
                                    start_time = slot.get("start")
                                    # Parse start time and add 30 minutes for end time
                                    from datetime import datetime, timedelta
                                    try:
                                        dt_start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                                        dt_end = dt_start + timedelta(minutes=30)
                                        end_time = dt_end.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
                                    except:
                                        # Fallback: just use start time + 30 min notation
                                        end_time = start_time
                                    
                                    collection.append({
                                        "start_time": start_time,
                                        "end_time": end_time,
                                        "status": "available"
                                    })
                    
                    print(f"   Extracted {len(collection)} slots from response")
                    return {"collection": collection}
            
            print(f"   No 'data' key in response or unexpected format, returning empty collection")
            return {"collection": []}
        except httpx.HTTPStatusError as e:
            # Log the error for debugging
            import logging
            print(f"❌ Cal.com API error: {e.response.status_code} - {e.response.text}")
            # Return empty collection on error
            return {"collection": []}
        except Exception as e:
            print(f"❌ Cal.com unexpected error: {str(e)}")
            return {"collection": []}


async def create_calcom_booking(event_type_id: str, api_key: str, email: str, name: str, start_time: str, duration_minutes: int = 30) -> dict:
    """Create a booking in Cal.com using v2 API."""
    from datetime import datetime, timezone, timedelta
    
    base_url = "https://api.cal.com/v2"
    url = f"{base_url}/bookings"
    
    # Convert start_time to UTC ISO format (ensure it's UTC, not IST)
    start_time_utc = None
    end_time_utc = None
    
    try:
        # Parse the datetime, handling timezone offsets
        if '+' in start_time:
            # Has timezone offset like +05:30
            dt = datetime.fromisoformat(start_time)
            # Convert to UTC
            dt_utc = dt.astimezone(timezone.utc)
        elif start_time.endswith('Z'):
            # Already UTC
            dt_utc = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            if dt_utc.tzinfo is None:
                dt_utc = dt_utc.replace(tzinfo=timezone.utc)
        else:
            # Assume it's UTC already
            dt = datetime.fromisoformat(start_time)
            if dt.tzinfo is None:
                dt_utc = dt.replace(tzinfo=timezone.utc)
            else:
                dt_utc = dt.astimezone(timezone.utc)
        
        # Format start_time in ISO format without milliseconds for Cal.com v2
        # Use isoformat() for maximum compatibility
        start_time_utc = dt_utc.replace(microsecond=0).isoformat().replace('+00:00', 'Z')
        
        # Calculate end_time (add duration)
        end_time_utc_dt = dt_utc + timedelta(minutes=duration_minutes)
        end_time_utc = end_time_utc_dt.replace(microsecond=0).isoformat().replace('+00:00', 'Z')
        
    except Exception as e:
        print(f"Time conversion error: {e}, start_time: {start_time}")
        # Fallback: try to parse and add duration
        try:
            # Remove timezone info and parse
            start_time_clean = start_time.replace('+05:30', '').replace('+00:00', '').replace('Z', '').replace('T', ' ')
            if '.' in start_time_clean:
                dt = datetime.strptime(start_time_clean.split('.')[0], '%Y-%m-%d %H:%M:%S')
            else:
                dt = datetime.strptime(start_time_clean, '%Y-%m-%d %H:%M:%S')
            dt = dt.replace(tzinfo=timezone.utc)
            start_time_utc = dt.strftime('%Y-%m-%dT%H:%M:%SZ')
            end_time_utc_dt = dt + timedelta(minutes=duration_minutes)
            end_time_utc = end_time_utc_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        except Exception as e2:
            print(f"Fallback time conversion error: {e2}")
            # Last resort: try ISO format directly
            try:
                if start_time.endswith('Z'):
                    dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                elif '+' in start_time:
                    dt = datetime.fromisoformat(start_time)
                else:
                    dt = datetime.fromisoformat(start_time)
                
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                else:
                    dt = dt.astimezone(timezone.utc)
                
                start_time_utc = dt.strftime('%Y-%m-%dT%H:%M:%SZ')
                end_time_utc_dt = dt + timedelta(minutes=duration_minutes)
                end_time_utc = end_time_utc_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
            except Exception as e3:
                print(f"Final fallback time conversion error: {e3}")
                # If all fails, use as-is and try to add duration manually
                start_time_utc = start_time
                # Try to add 30 minutes for end_time
                try:
                    # Parse just the date/time part
                    dt_str = start_time.replace('Z', '').replace('+05:30', '').replace('+00:00', '')
                    dt = datetime.fromisoformat(dt_str)
                    dt = dt.replace(tzinfo=timezone.utc)
                    end_dt = dt + timedelta(minutes=duration_minutes)
                    end_time_utc = end_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
                except:
                    # Final fallback - just add 30 minutes to the string (not ideal but works)
                    end_time_utc = start_time_utc
    
    # Ensure start_time_utc and end_time_utc are set
    # Cal.com v2 prefers YYYY-MM-DDTHH:MM:SS.SSSZ format
    if not start_time_utc:
        raise ValueError(f"Could not parse start_time: {start_time}")
    
    # Standardize to exact format (no milliseconds as per documentation)
    start_time_utc = start_time_utc.replace('+00:00', 'Z')
    if '.' in start_time_utc:
        # Strip milliseconds if they somehow got in
        start_time_utc = re.sub(r'\.\d+', '', start_time_utc)
    
    if not end_time_utc:
        try:
            dt_utc = datetime.fromisoformat(start_time_utc.replace('Z', '+00:00'))
            if dt_utc.tzinfo is None:
                dt_utc = dt_utc.replace(tzinfo=timezone.utc)
            end_dt = dt_utc + timedelta(minutes=duration_minutes)
            end_time_utc = end_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        except:
            end_time_utc = start_time_utc
    
    end_time_utc = end_time_utc.replace('+00:00', 'Z')
    if '.' in end_time_utc:
        end_time_utc = re.sub(r'\.\d+', '', end_time_utc)
    
    headers = {
        "authorization": f"Bearer {api_key}",
        "cal-api-version": "2024-08-13",
        "Content-Type": "application/json"
    }
    
    # Cal.com v2 API payload format (matching the curl example)
    payload = {
        "eventTypeId": int(event_type_id),
        "start": start_time_utc,
        "attendee": {
            "name": name or "Guest",
            "email": email,
            "timeZone": "Asia/Kolkata",
            "language": "en"
        },
        "metadata": {}
    }
    
    import json
    print(f"DEBUG: Creating Cal.com booking with payload:")
    print(json.dumps(payload, indent=2))
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=payload, timeout=10.0)
            response.raise_for_status()
            result = response.json()
            print(f"Cal.com API response: {result}")  # Debug log
            # Cal.com v2 returns {"booking": {"uid": "...", "status": "...", "start": "..."}}
            # Normalize to resource format for compatibility
            if "booking" in result:
                return {"resource": {"uri": result["booking"].get("uid", ""), **result["booking"]}}
            return {"resource": result}
        except httpx.HTTPStatusError as e:
            error_detail = f"HTTP {e.response.status_code}: {e.response.text}"
            print(f"Cal.com API error: {error_detail}")  # Debug log
            raise Exception(f"Failed to create Cal.com booking: {error_detail}")
        except httpx.RequestError as e:
            error_detail = f"Request failed: {str(e)}"
            print(f"Cal.com API request error: {error_detail}")  # Debug log
            raise Exception(f"Failed to create Cal.com booking: {error_detail}")
        except Exception as e:
            error_detail = f"Unexpected error: {str(e)}"
            print(f"Cal.com API unexpected error: {error_detail}")  # Debug log
            raise Exception(f"Failed to create Cal.com booking: {error_detail}")


def extract_email(text: str) -> Optional[str]:
    """Extract email from text."""
    import re
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(email_pattern, text)
    return match.group(0) if match else None


def extract_phone(text: str) -> Optional[str]:
    """Extract phone number from text."""
    import re
    phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b|\b\+?1?[-.]?\d{3}[-.]?\d{3}[-.]?\d{4}\b'
    match = re.search(phone_pattern, text)
    return match.group(0) if match else None

