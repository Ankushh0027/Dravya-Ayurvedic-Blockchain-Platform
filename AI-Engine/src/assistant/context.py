"""
Lightweight in-memory conversation session and context resolution manager for Dravya AI Copilot.
Enables multi-turn entity resolution (e.g., resolving 'it', 'this batch', 'that herb') without heavy storage.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
import re
import threading
from typing import Dict, List, Optional, Tuple


@dataclass
class ConversationSession:
    conversation_id: str
    last_herb: Optional[str] = None
    last_batch_id: Optional[str] = None
    last_farmer_id: Optional[str] = None
    last_intent: Optional[str] = None
    last_topic: Optional[str] = None
    turns: List[Dict[str, str]] = field(default_factory=list)
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def update_entities(
        self,
        herb: Optional[str] = None,
        batch_id: Optional[str] = None,
        farmer_id: Optional[str] = None,
        intent: Optional[str] = None,
        topic: Optional[str] = None,
    ) -> None:
        if herb:
            self.last_herb = herb
        if batch_id:
            self.last_batch_id = batch_id
        if farmer_id:
            self.last_farmer_id = farmer_id
        if intent:
            self.last_intent = intent
        if topic:
            self.last_topic = topic
        self.updated_at = datetime.now(timezone.utc)


class SessionManager:
    """
    Thread-safe in-memory session repository with auto-capping to prevent memory leaks.
    """

    def __init__(self, max_sessions: int = 500):
        self._lock = threading.RLock()
        self._sessions: Dict[str, ConversationSession] = {}
        self.max_sessions = max_sessions

    def get_or_create_session(self, conversation_id: Optional[str]) -> Tuple[ConversationSession, str]:
        """
        Retrieves existing session or creates a new one.
        """
        cid = conversation_id.strip() if conversation_id and conversation_id.strip() else f"dravya_sess_{int(datetime.now(timezone.utc).timestamp()*1000)}"
        with self._lock:
            if cid not in self._sessions:
                # Evict oldest if full
                if len(self._sessions) >= self.max_sessions:
                    oldest_key = min(self._sessions.keys(), key=lambda k: self._sessions[k].updated_at)
                    self._sessions.pop(oldest_key, None)
                self._sessions[cid] = ConversationSession(conversation_id=cid)
            return self._sessions[cid], cid

    def resolve_context_entities(
        self,
        text: str,
        session: Optional[ConversationSession],
    ) -> Dict[str, Optional[str]]:
        """
        Resolves pronouns ('it', 'this batch', 'us farmer', 'ye herb') using session context.
        """
        resolved: Dict[str, Optional[str]] = {
            "herb": None,
            "batch_id": None,
            "farmer_id": None,
        }
        if not session:
            return resolved

        text_lower = text.lower().strip()

        # 1. Batch anaphora: "this batch", "is batch", "the batch", "who is the farmer", "verification status", "traceability of this", "location of this batch"
        batch_pronoun_patterns = [
            r"\b(this|that|the|is|ye|us)\s+batch\b",
            r"\b(who is the farmer|farmer kaun hai|kisan kaun hai|status kya hai|verification status|location kya hai|where is it located)\b",
            r"\b(traceability of this|iski traceability|isko kisne ugaya)\b",
            r"\b(tell me about this batch|show details of this batch|is batch ki details)\b",
        ]
        if any(re.search(p, text_lower) for p in batch_pronoun_patterns):
            if session.last_batch_id:
                resolved["batch_id"] = session.last_batch_id

        # 2. Herb anaphora: "about it", "batches does it have", "iski quantity", "iske batches", "how much of it", "this herb", "ye herb"
        herb_pronoun_patterns = [
            r"\b(how many batches does it have|how much of it|batches of it|tell me about it)\b",
            r"\b(iske kitne batch|iski quantity|iske bare me|is herb ke|this herb|that herb|ye herb)\b",
            r"\b(how much do we have of it|total quantity of it)\b",
        ]
        if any(re.search(p, text_lower) for p in herb_pronoun_patterns):
            if session.last_herb:
                resolved["herb"] = session.last_herb

        # 3. Farmer anaphora: "this farmer", "is farmer", "us farmer", "his batches", "unke batches"
        farmer_pronoun_patterns = [
            r"\b(this farmer|that farmer|is farmer|us farmer|his batches|unke batches|unka stock)\b",
        ]
        if any(re.search(p, text_lower) for p in farmer_pronoun_patterns):
            if session.last_farmer_id:
                resolved["farmer_id"] = session.last_farmer_id

        return resolved


# Global singleton instance
_global_session_manager = SessionManager()


def get_session_manager() -> SessionManager:
    return _global_session_manager
