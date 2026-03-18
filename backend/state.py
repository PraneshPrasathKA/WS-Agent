from typing import TypedDict, Literal, Optional, List
from dataclasses import dataclass, asdict, field
from datetime import datetime


@dataclass
class UserProfile:
    email: str = ""
    name: str = ""
    crm: str = ""
    phone: str = ""


@dataclass
class Booking:
    calendar_full: bool = False
    slot: Optional[str] = None
    event_uri: Optional[str] = None
    available_slots: List[dict] = field(default_factory=list)  # Store available slots [{utc: "...", ist: "..."}]
    selected_slot_index: Optional[int] = None


@dataclass
class AgentState:
    session_id: str
    stage: Literal["INTRO", "EXPLAINED", "QUALIFYING", "BOOKING", "WAITLIST", "DONE"] = "INTRO"
    user_intent: str = ""
    user_profile: UserProfile = None
    last_asset: Optional[str] = None
    booking: Booking = None
    created_at: str = ""
    
    def __post_init__(self):
        if self.user_profile is None:
            self.user_profile = UserProfile()
        if self.booking is None:
            self.booking = Booking()
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()
    
    def to_dict(self):
        return {
            "session_id": self.session_id,
            "stage": self.stage,
            "user_intent": self.user_intent,
            "user_profile": asdict(self.user_profile),
            "last_asset": self.last_asset,
            "booking": asdict(self.booking),
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        state = cls(
            session_id=data.get("session_id", ""),
            stage=data.get("stage", "INTRO"),
            user_intent=data.get("user_intent", ""),
            last_asset=data.get("last_asset"),
            created_at=data.get("created_at", "")
        )
        if "user_profile" in data:
            state.user_profile = UserProfile(**data["user_profile"])
        if "booking" in data:
            state.booking = Booking(**data["booking"])
        return state


class StateManager:
    def __init__(self):
        self._states: dict[str, AgentState] = {}
    
    def get(self, session_id: str) -> Optional[AgentState]:
        return self._states.get(session_id)
    
    def set(self, session_id: str, state: AgentState):
        self._states[session_id] = state
    
    def update(self, session_id: str, **kwargs):
        state = self.get(session_id)
        if state is None:
            state = AgentState(session_id=session_id)
        for key, value in kwargs.items():
            if hasattr(state, key):
                setattr(state, key, value)
        self.set(session_id, state)
    
    def delete(self, session_id: str):
        if session_id in self._states:
            del self._states[session_id]


state_manager = StateManager()

