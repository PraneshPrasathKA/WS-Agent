from langchain_core.tools import StructuredTool
from langchain_core.tools import tool
from typing import Optional
from state import state_manager
from utils import (
    get_calcom_api_key,
    get_calcom_event_type_id,
    fetch_calcom_availability,
    create_calcom_booking,
    extract_email
)
from datetime import datetime
import json
import asyncio


def _get_session_id_from_context() -> str:
    """Extract session_id from thread-local context."""
    import threading
    context = getattr(threading.current_thread(), 'session_context', None)
    return context.get('session_id') if context else None


def create_tools_with_session(session_id: str):
    """Create tool instances bound to a specific session."""
    
    @tool
    def show_asset(asset_type: str) -> str:
        """Shows a visual asset to the user."""
        valid_types = ["OVERVIEW_VIDEO", "HOW_IT_WORKS_GIF", "PRICING_CARD"]
        if asset_type not in valid_types:
            return f"Invalid asset type. Must be one of: {', '.join(valid_types)}"
        
        state = state_manager.get(session_id)
        if state:
            state.last_asset = asset_type
            state_manager.set(session_id, state)
        
        return "Asset shown."
    
    @tool
    async def check_calcom_slots() -> str:
        """
        Checks available Cal.com time slots for booking. 
        USE THIS TOOL whenever the user asks about:
        - "available slots"
        - "booking a meeting" 
        - "demo slots"
        - "schedule a call"
        - "book a demo"
        - Any request related to availability or scheduling.
        
        Returns:
            JSON string with available slots or a message indicating no slots
        """
        print(f"🔍 check_calcom_slots tool called!")
        try:
            api_key = get_calcom_api_key()
            event_type_id = get_calcom_event_type_id()
            
            print(f"   Event Type ID: {event_type_id}")
            
            # Check availability for next 7 days
            start_time = datetime.utcnow().isoformat()
            
            # Directly await the async function
            availability = await fetch_calcom_availability(event_type_id, api_key, start_time)
            print(f"   Availability response: {availability}")
            
            state = state_manager.get(session_id)
            if not state:
                from state import AgentState
                state = AgentState(session_id=session_id)
                state_manager.set(session_id, state)
            
            # Truncated logging
            slots = []
            if "collection" in availability:
                coll = availability["collection"]
                print(f"   Found {len(coll)} items in collection")
                for item in coll:
                    # utils.py already filters for available and sets start_time
                    s_time = item.get("start_time")
                    if s_time:
                        slots.append(s_time)
                    else:
                        print(f"⚠️ Item missing start_time: {item}")
            
            # Final summary instead of line-by-line
            print(f"   Total available slots found: {len(slots)}")
            if len(slots) > 0:
                print(f"   First slot: {slots[0]}")
            
            if slots:
                # Format slots for display in IST (UTC+5:30) and store mapping
                from datetime import timedelta
                formatted_slots = []
                slot_mapping = []  # Store both UTC and IST for each slot
                
                for slot in slots[:5]:  # Show max 5 slots
                    try:
                        # Parse UTC time
                        dt_utc = datetime.fromisoformat(slot.replace('Z', '+00:00'))
                        # Convert to IST (UTC+5:30)
                        dt_ist = dt_utc + timedelta(hours=5, minutes=30)
                        ist_formatted = dt_ist.strftime("%A, %B %d at %I:%M %p IST")
                        # Add numbering to formatted string
                        numbered_ist = f"{len(formatted_slots) + 1}. {ist_formatted}"
                        formatted_slots.append(numbered_ist)
                        slot_mapping.append({
                            "utc": slot,
                            "ist": ist_formatted,
                            "index": len(slot_mapping)
                        })
                    except Exception as e:
                        formatted_slots.append(slot)
                        slot_mapping.append({
                            "utc": slot,
                            "ist": slot,
                            "index": len(slot_mapping)
                        })
                
                # Update state with available slots
                if state:
                    state.booking.calendar_full = False
                    state.booking.available_slots = slot_mapping
                    state.stage = "BOOKING"
                    state_manager.set(session_id, state)
                
                return json.dumps({
                    "available": True,
                    "slots": slots[:5],  # UTC times for API
                    "formatted": formatted_slots,  # IST times for display
                    "slot_mapping": slot_mapping  # Mapping of UTC to IST
                })
            else:
                if state:
                    state.booking.calendar_full = True
                    state.stage = "WAITLIST"
                    state_manager.set(session_id, state)
                return json.dumps({
                    "available": False,
                    "message": "No available slots this week"
                })
        except Exception as e:
            return json.dumps({
                "available": False,
                "error": str(e)
            })

    @tool
    async def book_calcom_meeting(email: str, slot: Optional[str] = None, name: str = "Lead") -> str:
        """BOOKS A CAL.COM MEETING."""
        if not email:
            return "Email address is required to book a meeting. Please provide your email."
        
        try:
            # Get state to check for available slots if slot not provided
            state = state_manager.get(session_id)
            if not slot and state and state.booking.available_slots:
                # Use first available slot if no slot specified
                slot = state.booking.available_slots[0].get("utc") if state.booking.available_slots else None
            
            # Fuzzy match slot if it looks like a human time (e.g. "1:00 PM" or "1:00 PM - 2:00 PM")
            if slot and state and state.booking.available_slots:
                if not (slot.endswith('Z') or '+' in slot): # Not an ISO string
                    print(f"🔧 Trying to fuzzy match human slot: {slot}")
                    # If it's a range, take the first part
                    slot_to_match = slot.split('-')[0].strip().lower()
                    for s in state.booking.available_slots:
                        ist_lower = s.get("ist", "").lower()
                        if slot_to_match in ist_lower:
                            print(f"✅ Found match in available_slots: {s.get('ist')} -> {s.get('utc')}")
                            slot = s.get("utc")
                            break
            
            if not slot:
                return "No slot provided and no available slots found. Please select a time slot first."
            
            api_key = get_calcom_api_key()
            event_type_id = get_calcom_event_type_id()
            
            result = await create_calcom_booking(event_type_id, api_key, email, name, slot)
            
            # Only update state to DONE if booking was successful
            if result and result.get("resource"):
                if state:
                    state.booking.slot = slot
                    state.booking.event_uri = result.get("resource", {}).get("uri", "")
                    state.user_profile.email = email
                    if name and name != "Lead":
                        state.user_profile.name = name
                    # Stage changes to DONE only after successful booking
                    state.stage = "DONE"
                    state_manager.set(session_id, state)
                    print(f"✅ Booking successful - stage changed to DONE")
                
                return f"Great! I've booked your meeting. You'll receive a confirmation email at {email}."
            else:
                error_msg = "Booking failed - no event created"
                print(f"❌ {error_msg}")
                return f"Sorry, there was an issue booking that slot: {error_msg}. Would you like to try another time?"
        except Exception as e:
            print(f"❌ Booking exception: {str(e)}")
            # Stage remains BOOKING on error - user can try again
            return f"Sorry, there was an issue booking that slot: {str(e)}. Would you like to try another time?"
    
    @tool
    def capture_waitlist(email: str, phone: str = "") -> str:
        """
        Captures user information for the waitlist when no slots are available.
        
        Args:
            email: User's email address
            phone: User's phone number (optional)
            
        Returns:
            A confirmation message
        """
        state = state_manager.get(session_id)
        if not state:
            from state import AgentState
            state = AgentState(session_id=session_id)
            state_manager.set(session_id, state)
        
        if state:
            state.user_profile.email = email
            if phone:
                state.user_profile.phone = phone
            state.stage = "WAITLIST"
            state_manager.set(session_id, state)
        
        return f"Thank you! We've added {email} to our priority waitlist. We'll notify you as soon as a slot opens up."
    
    @tool
    def scroll_to_section(section_id: str) -> str:
        """Scrolls the user's webpage to a specific section."""
        valid_sections = ["hero", "services", "portfolio", "about"]
        
        # We can hijack the 'last_asset' state property to send the scroll command
        # since the frontend already listens to showAsset
        state = state_manager.get(session_id)
        if state:
            state.last_asset = f"scroll:{section_id}"
            state_manager.set(session_id, state)
            
        return f"SCROLL_COMMAND:{section_id}"
    
    return [
        show_asset,
        scroll_to_section,
        check_calcom_slots,
        book_calcom_meeting,
        capture_waitlist
    ]

