from typing import Any
import os
import threading
import re
import time
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from tools import create_tools_with_session
from state import state_manager, AgentState

# Ensure env vars are loaded
load_dotenv()

# Global instances for reuse
_LLM_CACHE = {}
_memory_saver = MemorySaver()





SYSTEM_PROMPT = """You are WS AI, the official AI Assistant for WS. Be friendly, conversational, and helpful.

ABOUT YOURSELF:
- Your name is "WS AI"
- You are the AI web development assistant for WS
- If asked "what is your name" or "who are you": Say "I'm WS AI, the AI assistant for WS. How can I help you today?"
- If asked "who invented you" or "who created you": Say "I was created by the team at WS to help you learn about our web development services and book consultations!"

ABOUT WS:
We offer a range of web development services to help you build a stunning online presence. Our services include Custom Web Applications, Modern Landing Pages, eCommerce Solutions, and UI/UX Design. We transform your digital ideas into reality natively and blazingly fast, ensuring your site looks beautiful and ranks high on SEO.
- Pricing: Custom web applications start at $5,000. Landing pages start at $1,500.

CONVERSATION RULES:

1. BE CONVERSATIONAL FIRST:
   - Start with friendly greetings and normal conversation
   - If user says "hey", "hi", "hello" - respond with simple friendly greeting like "Hey! How can I help you?"
   - DO NOT show any assets or talk heavily about WS unless the user asks about our services, pricing, or wants to see examples.

2. SCROLLING THE WEBSITE (CRITICAL):
   - You have access to a `scroll_to_section` tool.
   - If the user asks "what services do you offer", "show me your services", or "what do you do" -> Give a brief explanation of our services AND YOU MUST call the `scroll_to_section(section_id="services")` tool so the website scrolls for them.
   - If the user asks "show me your portfolio", "past work", "examples" -> Briefly mention our high-performance sites AND YOU MUST call the `scroll_to_section(section_id="portfolio")` tool.
   - If the user asks "about you", "who is WS" -> Call the `scroll_to_section(section_id="about")` tool.
   - If the user asks to "go back to top" or "hero" -> Call the `scroll_to_section(section_id="hero")` tool.

3. BOOKING MEETINGS (CRITICAL):
    - When user asks about availability, slots, booking, or scheduling (phrases like "book a consultation", "available slots", "book a demo", "schedule a meeting", "book a call"):
      * ALWAYS say something like "I'd like to help you schedule a meeting. Let me check our available slots for you."
      * YOU MUST ALWAYS call the `check_calcom_slots` tool immediately after saying that.
      * If slots available: LIST the PRECISE available time slots from the 'formatted' list in the tool output. DO NOT include any dates or times that are not in the tool output. 
      * Format the response exactly as follows: "I found these slots for you:\n1. [Slot 1 from formatted list]\n2. [Slot 2 from formatted list]\n...\nWhich one would you like to book?"
      * When user confirms a slot (by time or number): 
        - YOU MUST FIRST ask for their **full name**. 
        - DO NOT call the booking tool yet. 
        - DO NOT tell the user they are "all set" yet.
        - Phrasing: "That's a great choice! To send you the calendar invite and confirmation, I just need a few details. First, what is your **full name**?"
      * When user provides their name: 
        - YOU MUST then ask for their **email address**.
        - DO NOT call the booking tool yet.
        - Phrasing: "Thanks [Name]! Now, what's your **email address**?"
      * When user provides their email address (message contains "@" and domain like ".com"):
        - You MUST immediately call the `book_calcom_meeting` tool.
        - Extract email and name (or use the stored name if already provided) and call: `book_calcom_meeting(email="extracted_email", name="extracted_name")`
        - **CONFIRMATION**: After the tool returns, you MUST say: "Great! I've booked your meeting. You'll receive a confirmation email at [email]."
        - ONLY then is the booking complete.

4. HANDLING GENERAL QUESTIONS:
   - PRICING QUESTIONS: When user asks about pricing, explain "Custom web applications start at $5,000. Landing pages start at $1,500."
   - Always be friendly and helpful.

5. AFTER SUCCESSFUL BOOKING (DONE STAGE):
   - Once a meeting is booked (you've called `book_calcom_meeting` and it was successful), you are in the "DONE" stage.
   - YOUR GOAL: Say "You're welcome!" or "No problem!", and offer to help with other things about WS (services, projects, about us).
   - **CRITICAL**: DO NOT call `check_calcom_slots` or offer more appointment slots unless the user explicitly asks to "reschedule" or "change" their existing meeting.
   - If the user says "ok", "thanks", "done", or "cool" after booking -> Just say "You're welcome! Is there anything else I can help you with today?"

IMPORTANT EXAMPLES:
- User: "hey" -> You: "Hey! How can I help you today?"
- User: "what services do you provide" -> You: "We offer a wide range of services including Custom Web Apps and UI/UX design. I've scrolled the page so you can see the details!"
- User: "show me your past work" -> You: "We've built some amazing products for our clients. Take a look at the portfolio section I just brought up for you!"

Keep responses concise, friendly, and conversational. Match the user's energy level. Don't be pushy.

CRITICAL: Never include internal technical details, tool names, or code-like syntax in your response. Always speak in natural, friendly language.
CRITICAL: Do not confirm booking until you have collected BOTH name and email.
"""


def clean_output(text: str) -> str:
    """Safe cleaning of technical tags without corrupting legitimate words."""
    if not text:
        return text
    
    # Use a safer regex that explicitly looks for our tags and ensures it starts with < and ends with >
    # Specifically catching section_id=, function=, etc.
    text = re.sub(r'<(?:function|tool_call|section_id|booking|scroll_to)=[^>]*>.*?</(?:function|tool_call|section_id|booking|scroll_to)>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<(?:function|tool_call|section_id|booking|scroll_to)=[^>]*>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'</(?:function|tool_call|section_id|booking)[^>]*>', '', text, flags=re.IGNORECASE)
    
    # Remove Action/Thought/etc only at start of lines
    text = re.sub(r'^\s*(?:Action|Thought|Observation|AI|System):.*?\n?', '', text, flags=re.MULTILINE | re.IGNORECASE)
    
    return text.strip()


from typing import Any

# Global executor cache per session
_executor_cache: dict[str, Any] = {}
_memory_saver = MemorySaver()


def build_system_prompt_with_state(session_id: str) -> str:
    """Build system prompt with current state information."""
    state = state_manager.get(session_id)
    
    state_context = ""
    if state and state.user_profile:
        # Build context if we have user info or booking status
        has_info = False
        if state.user_profile.name or state.user_profile.email or state.stage in ["DONE", "BOOKING"]:
            state_context = "\n\nCURRENT SESSION INFORMATION:\n"
            has_info = True
            
        if state.user_profile.name:
            state_context += f"- User's name: {state.user_profile.name}\n"
        if state.user_profile.email:
            state_context += f"- User's email: {state.user_profile.email}\n"
        if state.stage == "DONE":
            state_context += "- Booking status: Meeting has been successfully booked!\n"
            state_context += "- IMPORTANT: Do not offer more slots or check for slots unless user asks to reschedule.\n"
        elif state.stage == "BOOKING":
            state_context += "- Booking status: User is in the process of booking a meeting\n"
        
        if not has_info:
            state_context = ""
    
    if state and state.stage == "DONE":
        # Extra reinforcement for the DONE stage
        return SYSTEM_PROMPT + state_context + "\n\nCRITICAL: The user has already booked a meeting. Focus on answering other questions and avoid the booking flow unless asked to reschedule."
    
    return SYSTEM_PROMPT + state_context


# Pre-initialize LLM chain at module level for maximum speed
def _initialize_llm_chain():
    start_llm = time.time()
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        return None
        
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=groq_api_key,
        temperature=0.7
    )
    
    fallbacks = []
    
    # Groq 8B (Fast fallback)
    llm_groq_8b = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=groq_api_key,
        temperature=0.7
    )
    fallbacks.append(llm_groq_8b)
    
    # Gemini Fallbacks (VERIFIED MODELS ONLY)
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if api_key:
        # Gemini 1.5 Flash
        llm_gemini_15 = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.7,
            google_api_key=api_key
        )
        fallbacks.append(llm_gemini_15)
        
        # Gemini 2.0 Flash
        llm_gemini_20 = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.7,
            google_api_key=api_key
        )
        fallbacks.append(llm_gemini_20)

    if fallbacks:
        llm = llm.with_fallbacks(fallbacks)
    
    return llm

_CACHED_LLM_CHAIN = _initialize_llm_chain()


def get_llm_chain():
    """Get the cached LLM chain."""
    return _CACHED_LLM_CHAIN


def get_or_create_executor(session_id: str) -> Any:
    """Get or create an agent executor for a session (with persistent memory)."""
    start_all = time.time()
    
    # Check cache first
    if session_id in _executor_cache:
        # Still need the build_system_prompt_with_state for potential dynamic updates,
        # but create_react_agent might not support updating prompt easily after creation.
        # However, for sheer speed, we'll return the cached version.
        return _executor_cache[session_id]

    # Get or create state
    state = state_manager.get(session_id)
    if not state:
        state = AgentState(session_id=session_id)
        state_manager.set(session_id, state)
    
    # Use cached LLM chain
    llm = get_llm_chain()
    
    # Create tools bound to this session
    tools = create_tools_with_session(session_id)
    
    # Create Langgraph React Agent with checkpointer for memory
    system_prompt = build_system_prompt_with_state(session_id)
    executor = create_react_agent(
        llm, 
        tools=tools,
        checkpointer=_memory_saver,
        prompt=system_prompt
    )
    
    # Save to cache
    _executor_cache[session_id] = executor
    
    return executor


async def process_message(message: str, session_id: str) -> dict:
    total_start = time.time()
    """
    Process a user message through the agent and return response with asset info.
    
    Returns:
        {
            "reply": str,
            "showAsset": str | None,
            "stage": str
        }
    """
    # Store session_id in thread-local context for tools
    threading.current_thread().session_context = {"session_id": session_id}
    
    # Get or create executor
    executor = get_or_create_executor(session_id)
    
    # Get state
    state = state_manager.get(session_id)
    if not state:
        state = AgentState(session_id=session_id)
        state_manager.set(session_id, state)
    
    # Check if user is confirming a slot
    message_lower = message.lower()
    # Support "10:00 am", "10:00 a.m.", "10am", "10 a.m.", etc.
    has_time_mention = bool(re.search(r'\d{1,2}(?::\d{2})?\s*(?:am|pm|a\.m\.|p\.m\.)', message_lower))
    # Broader confirmation: removed "book" as it conflicts with initial requests
    is_confirmation = bool(re.search(r'\b(yes|yeah|ok|sure|confirm|works|good|fine|perfect|that one|this one)\b', message_lower))
    # Is it a number selection? (e.g., "1", "I'll take 2")
    digit_match = re.search(r'\b(\d)\b', message)
    # Add ordinal matching
    ordinals = {"first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5}
    ordinal_match = re.search(r'\b(first|second|third|fourth|fifth)\b', message_lower)
    is_number_selection = (bool(digit_match) or bool(ordinal_match)) and state and state.stage == "BOOKING"
    
    # If we have slots and user is confirming, ensure stage is BOOKING
    if state and state.stage == "BOOKING" and state.booking.available_slots:
        if has_time_mention or is_number_selection:
            # User matched a specific slot
            state.stage = "BOOKING"
            
            # If time mention or number selection, try to find and save the specific slot NOW
            if not state.booking.slot:
                selected_slot = None
                
                # Try time matching
                if has_time_mention:
                    for s in state.booking.available_slots:
                        ist_time = s.get("ist", "").lower()
                        time_match = re.search(r'(\d{1,2}(?::\d{2})?\s*(?:am|pm|a\.m\.|p\.m\.))', ist_time)
                        if time_match:
                            time_str = time_match.group(1).replace(".", "")
                            clean_message = message_lower.replace(".", "")
                            if time_str in clean_message:
                                selected_slot = s.get("utc")
                                break
                
                # Try number matching if time didn't work
                if not selected_slot and is_number_selection:
                    idx = -1
                    if digit_match:
                        idx = int(digit_match.group(1)) - 1
                    elif ordinal_match:
                        idx = ordinals[ordinal_match.group(1)] - 1
                        
                    if 0 <= idx < len(state.booking.available_slots):
                        selected_slot = state.booking.available_slots[idx].get("utc")
                
                if selected_slot:
                    state.booking.slot = selected_slot
            
            state_manager.set(session_id, state)
        elif is_confirmation:
            # Generic confirmation, keep stage as BOOKING but don't force a slot yet
            state.stage = "BOOKING"
            state_manager.set(session_id, state)
    
    # AUTO-BOOKING: If stage is BOOKING and message contains email, automatically book
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_match = re.search(email_pattern, message)

    # NAME EXTRACTION: If stage is BOOKING and name is not yet captured, try to extract it from non-email messages
    if state and state.stage == "BOOKING" and not state.user_profile.name and not email_match:
        name_patterns = [
            r'\b(?:my\s+name\s+is\s+|i\'m\s+|i\s+am\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'\bThis\s+is\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'\bName:\s*([A-Za-z]+(?:\s+[A-Za-z]+)*)'
        ]
        for pattern in name_patterns:
            match = re.search(pattern, message, re.IGNORECASE) 
            if match:
                potential_name = match.group(1).strip()
                # Ensure it's not a common greeting or short word
                if len(potential_name.split()) >= 1 and len(potential_name) > 1:
                    # Filter out common false positives
                    common_words = {"The", "This", "That", "It", "Yes", "Ok", "Sure", "Book", "I", "You"}
                    if potential_name not in common_words:
                        state.user_profile.name = potential_name
                        state_manager.set(session_id, state)
                        print(f"👤 [DEBUG] Name captured: {state.user_profile.name}")
                        break
    
    if state and state.stage == "BOOKING" and email_match and state.booking.available_slots:
        email = email_match.group(0)
        print(f"📧 EMAIL DETECTED in BOOKING stage: {email}")
        print(f"   Available slots: {len(state.booking.available_slots)}")
        
        # Extract name from message or use already captured name
        name = state.user_profile.name or "Lead"
        name_patterns = [
            r'\b(?:and\s+)?my\s+name\s+is\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)',
            r'\bname\s+is\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)',
            r'\b([A-Za-z]{2,}(?:\s+[A-Za-z]{2,})*)\s+[a-z0-9._%+-]+@'
        ]
        msg_name = None
        for pattern in name_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                msg_name = match.group(1).strip()
                break
        
        if msg_name:
            name = msg_name
            state.user_profile.name = name
            state_manager.set(session_id, state)
        else:
            # Final fallback: use text before the email as potential name if it's 2+ words
            parts = message.split(email)
            if len(parts) > 0 and not state.user_profile.name:
                pre_text = parts[0].strip().strip(',')
                # Try to extract a name-like structure from pre-text (even lowercase)
                name_match = re.search(r'([A-Za-z]{2,}(?:\s+[A-Za-z]{2,})*)', pre_text)
                if name_match:
                    name = name_match.group(1).strip().title() # Title case it for the email
                    state.user_profile.name = name
                    state_manager.set(session_id, state)
        
        # Get slot from state or try to match message to available slots
        slot = state.booking.slot
        if not slot and state.booking.available_slots:
            # Try to match time in message to available slots IST times
            found_match = False
            if has_time_mention:
                for s in state.booking.available_slots:
                    ist_time = s.get("ist", "").lower()
                    # Extract time part from IST string (e.g. "10:30 AM")
                    time_match = re.search(r'(\d{1,2}:?\d{2}?\s*(am|pm))', ist_time)
                    if time_match:
                        time_str = time_match.group(1)
                        if time_str in message_lower:
                            slot = s.get("utc")
                            found_match = True
                            print(f"🎯 Matched message time to slot: {time_str} -> {slot}")
                            break
            
        if slot:
            print(f"🚀 AUTO-BOOKING: Booking with email={email}, name={name}, slot={slot}")
            # Import and call booking function directly
            from tools import create_tools_with_session
            tools = create_tools_with_session(session_id)
            book_tool = next((t for t in tools if t.name == "book_calcom_meeting"), None)
            
            if book_tool:
                try:
                    # Call booking tool directly - this will update stage to DONE on success
                    booking_result = await book_tool.ainvoke({"email": email, "slot": slot, "name": name})
                    print(f"✅ Booking completed: {booking_result[:100]}")
                    
                    # Get updated state to return correct stage
                    updated_state = state_manager.get(session_id)
                    reply = booking_result
                    if "Great! I've booked" not in reply:
                        reply = f"Great! I've booked your meeting. You'll receive a confirmation email at {email}."
                        
                    return {
                        "reply": reply,
                        "showAsset": None,
                        "stage": updated_state.stage if updated_state else "DONE",
                        "availableSlots": None
                    }
                except Exception as e:
                    print(f"❌ Auto-booking error: {e}")
                    import traceback
                    traceback.print_exc()
        else:
            print("⚠️ Email detected but no slot selected yet. Letting agent handle it.")
    
    try:
        # Pass memory explicitly with langgraph react agent
        config = {"configurable": {"thread_id": session_id}}
        
        # Trim history if it's getting too long to keep latency down
        # We can fetch the current state and only keep the last few messages
        try:
            current_checkpoint = _memory_saver.get(config)
            if current_checkpoint and "channel_values" in current_checkpoint and "messages" in current_checkpoint["channel_values"]:
                msgs = current_checkpoint["channel_values"]["messages"]
                if len(msgs) > 40: # Increase to 40 messages
                    print(f"✂️  Truncating history from {len(msgs)} to 20 messages")
                    current_checkpoint["channel_values"]["messages"] = msgs[-20:]
                    _memory_saver.put(config, current_checkpoint)
        except Exception as e:
            print(f"⚠️  History truncation failed: {e}")
        
        # We need to prepend the system prompt if not done
        system_prompt = build_system_prompt_with_state(session_id)
        
        start_invoke = time.time()
        print(f"🚀 [DEBUG] Calling executor.ainvoke...")
        result = await executor.ainvoke({
            "messages": [
                HumanMessage(content=message)
            ]
        }, config=config)
        end_invoke = time.time()
        print(f"⏱️  Executor invocation took {end_invoke - start_invoke:.2f} seconds")
        
        # Extract the last AI message that isn't just a tool call
        messages = result.get("messages", [])
        reply = ""
        for msg in reversed(messages):
            if msg.type == "ai":
                content = msg.content
                # If there's content and it's not just a tool-calling template
                if content and not (hasattr(msg, 'tool_calls') and msg.tool_calls and len(content) < 100 and ('<function' in content or 'Action:' in content)):
                    reply = content
                    break
        
        # If we still don't have a reply, take the last AI message content anyway
        if not reply and messages:
            for msg in reversed(messages):
                if msg.type == "ai" and msg.content:
                    reply = msg.content
                    break
        
        reply = reply.strip()
        
        # Check for SCROLL_COMMAND in any tool outputs or the final result
        # This is a FAILSAFE for the scroll tool
        asset_shown = None
        for msg in reversed(messages):
            if msg.type == "tool" and msg.content and "SCROLL_COMMAND:" in str(msg.content):
                cmd_match = re.search(r'SCROLL_COMMAND:(\w+)', str(msg.content))
                if cmd_match:
                    asset_shown = f"scroll:{cmd_match.group(1)}"
                    print(f"🎯 TRIGGERED SCROLL DIRECTLY FROM TOOL OUTPUT: {asset_shown}")
                    break

        # Clean the output string to remove any leaked technical tags
        reply = clean_output(reply)
        
        # If reply is empty, provide a fallback
        if not reply:
            print(f"⚠️  Empty reply from agent, result: {result}")
            reply = "I'm here to help! Could you please rephrase your question or let me know what you'd like to know about WS?"
        
        # Force a fresh state read
        updated_state = state_manager.get(session_id)
        if not updated_state:
            updated_state = state
            
        print(f"DEBUG: Final stage in process_message: {updated_state.stage}")
        
        if not asset_shown:
            asset_shown = updated_state.last_asset
        
        # Reset last_asset after reading to avoid showing it multiple times
        if updated_state and updated_state.last_asset:
            updated_state.last_asset = None  # Clear after reading
            state_manager.set(session_id, updated_state)
        
        # Get available slots from state if in BOOKING stage
        available_slots = None
        if updated_state and updated_state.stage == "BOOKING":
            available_slots = updated_state.booking.available_slots
        
        print(f"⏱️  Total process_message took {time.time() - total_start:.2f} seconds")
        return {
            "reply": reply,
            "showAsset": asset_shown,
            "stage": updated_state.stage if updated_state else "INTRO",
            "availableSlots": available_slots if available_slots else None
        }
    except Exception as e:
        import traceback
        error_msg = str(e)
        if os.getenv("DEBUG", "false").lower() == "true":
            error_msg += f"\n{traceback.format_exc()}"
        
        return {
            "reply": f"I apologize, but I encountered an error: {error_msg}. How can I help you today?",
            "showAsset": None,
            "stage": state.stage if state else "INTRO",
            "availableSlots": None
        }

