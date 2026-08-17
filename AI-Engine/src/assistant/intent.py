"""
Intent Classification, Category Detection, and Entity Extraction Engine for Dravya AI Copilot.
Supports English, Hindi, and Hinglish queries across Live Data, Project Knowledge, and Multi-Intent Mixed Queries.
"""
from dataclasses import dataclass, field
import re
from typing import Any, Dict, List, Optional, Tuple, Union

from src.assistant.knowledge import KnowledgeRetriever

# Known Ayurvedic herb canonical & common names for entity resolution
KNOWN_HERBS = [
    "Ashwagandha", "Tulsi", "Shatavari", "Neem", "Giloy",
    "Amla", "Brahmi", "Mulethi", "Arjuna", "Haritaki",
    "Guduchi", "Gotu Kola", "Bhringraj", "Aloe Vera", "Turmeric",
    "Ashoka", "Guggulu", "Manjistha", "Bala", "Pippali",
    "Vacha", "Karela", "Senna", "Bael", "Kalmegh",
    "Chirata", "Kutki", "Shankhpushpi", "Vidanga", "Musta"
]


class IntentResult(tuple):
    """
    Tuple subclass (intent, tool_name, tool_kwargs) maintaining backward compatibility
    with existing destructuring while providing rich metadata attributes.
    """
    def __new__(
        cls,
        intent: str,
        tool_name: Optional[str] = None,
        tool_kwargs: Optional[Dict[str, Any]] = None,
        category: str = "LIVE_DATA",
        knowledge_topic: Optional[str] = None,
        multi_tools: Optional[List[Tuple[str, Dict[str, Any]]]] = None,
        multi_topics: Optional[List[str]] = None,
        resolved_entities: Optional[Dict[str, Any]] = None,
        specific_field: Optional[str] = None,
    ):
        kw = tool_kwargs or {}
        instance = super().__new__(cls, (intent, tool_name, kw))
        instance.intent = intent
        instance.tool_name = tool_name
        instance.tool_kwargs = kw
        instance.category = category  # LIVE_DATA, PROJECT_KNOWLEDGE, MIXED_QUERY, CONVERSATIONAL, UNKNOWN
        instance.knowledge_topic = knowledge_topic
        instance.multi_tools = multi_tools or ([] if tool_name is None else [(tool_name, kw)])
        instance.multi_topics = multi_topics or ([] if knowledge_topic is None else [knowledge_topic])
        instance.resolved_entities = resolved_entities or {}
        instance.specific_field = specific_field  # e.g., "farmer", "location", "status", "quantity", "moisture"
        return instance


class IntentAnalyzer:
    """
    Deterministic Intent Classification, Category Detection, and Entity Extraction engine.
    Supports English, Hindi, and Hinglish queries with context-aware entity resolution.
    """

    def __init__(self):
        self.knowledge_retriever = KnowledgeRetriever()

    @staticmethod
    def extract_batch_id(text: str) -> Optional[str]:
        """Extracts deterministic batch ID (e.g. DRAVYA-ASH-20260810-346DA7) or batch identifier."""
        match = re.search(r"\b(DRAVYA-[A-Z0-9]{3,4}-\d{8}-[A-Z0-9]{6,8})\b", text, re.IGNORECASE)
        if match:
            return match.group(1).upper()
        # Generic batch code fallback (e.g. DRAVYA-ASH-001 or DRAVYA-UNKNOWN-000)
        match_gen = re.search(r"\b(DRAVYA-[A-Z0-9\-]+)\b", text, re.IGNORECASE)
        if match_gen:
            return match_gen.group(1).upper()
        # Keyword pattern "batch <id>" e.g. "batch DOES-NOT-EXIST"
        match_kw = re.search(r"\bbatch\s+([A-Za-z0-9\-_]+)\b", text, re.IGNORECASE)
        if match_kw and match_kw.group(1).lower() not in {"details", "traceability", "information", "summary", "status", "ka", "ki", "ke", "hai", "kya", "is", "this", "that"}:
            return match_kw.group(1)
        return None

    @staticmethod
    def extract_farmer_id(text: str) -> Optional[str]:
        """Extracts farmer ID (e.g., F001, F002)."""
        match = re.search(r"\b(F\d{3,5})\b", text, re.IGNORECASE)
        if match:
            return match.group(1).upper()
        match_kw = re.search(r"\bfarmer\s*([A-Z0-9]+)\b", text, re.IGNORECASE)
        if match_kw:
            return match_kw.group(1).upper()
        return None

    @staticmethod
    def extract_herb_name(text: str) -> Optional[str]:
        """Extracts herb species name from natural language query."""
        # 1. Check known herbs
        for herb in KNOWN_HERBS:
            pattern = rf"\b{re.escape(herb)}\b"
            if re.search(pattern, text, re.IGNORECASE):
                return herb

        # 2. Hindi/Hinglish positional pattern: "X ki quantity", "X ke batches"
        match_pos = re.search(
            r"\b([A-Za-z]+)\s+(?:ki|ka|ke)\s+(?:total\s+)?(?:quantity|stock|kitni|kitne|batches|details|herb)\b",
            text,
            re.IGNORECASE,
        )
        if match_pos and match_pos.group(1).lower() not in {"system", "is", "ye", "total", "farmer", "dravya", "all"}:
            return match_pos.group(1).capitalize()

        # 3. English positional pattern: "batches of X", "inventory of X", "how much X"
        match_eng = re.search(
            r"(?:batches|inventory|quantity|stock)\s+(?:of|for)\s+([A-Za-z]+)",
            text,
            re.IGNORECASE,
        )
        if match_eng and match_eng.group(1).lower() not in {"system", "it", "this", "that", "all"}:
            return match_eng.group(1).capitalize()

        match_eng_hm = re.search(
            r"how\s+much\s+([A-Za-z]+)\b",
            text,
            re.IGNORECASE,
        )
        if match_eng_hm and match_eng_hm.group(1).lower() not in {"inventory", "stock", "do", "batches", "of", "it"}:
            return match_eng_hm.group(1).capitalize()

        return None

    def analyze(
        self,
        message: str,
        context_entities: Optional[Dict[str, Optional[str]]] = None,
    ) -> IntentResult:
        """
        Analyzes user message and returns structured IntentResult.
        """
        text = message.strip()
        text_lower = text.lower()
        ctx = context_entities or {}

        # 1. Extract explicit entities
        batch_id = self.extract_batch_id(text) or ctx.get("batch_id")
        farmer_id = self.extract_farmer_id(text) or ctx.get("farmer_id")
        herb_name = self.extract_herb_name(text) or ctx.get("herb")

        resolved_entities = {
            "batch_id": batch_id,
            "farmer_id": farmer_id,
            "herb": herb_name,
        }

        # 2. Check for Specific Attribute Query on a Batch
        specific_field = None
        if batch_id:
            if any(w in text_lower for w in ["who is the farmer", "farmer kaun", "kisan kaun", "farmer of this batch", "farmer details"]):
                specific_field = "farmer"
            elif any(w in text_lower for w in ["location", "kahan hai", "kahan se", "place", "where is"]):
                specific_field = "location"
            elif any(w in text_lower for w in ["verification status", "status kya", "verified", "status"]):
                specific_field = "status"
            elif any(w in text_lower for w in ["quantity", "kitni quantity", "kitna weight", "weight"]):
                specific_field = "quantity"
            elif any(w in text_lower for w in ["moisture", "moisture content", "nami"]):
                specific_field = "moisture"

        # 3. Check for Project Knowledge Intent
        knowledge_topic = self.knowledge_retriever.match_topic(text)

        # 4. Multi-Intent / Mixed Query Detection
        # Case A: Live herb batches + Traceability explanation
        if herb_name and ("traceability" in text_lower or "trace" in text_lower) and any(w in text_lower for w in ["kaise", "how", "maintain", "work", "explain"]):
            return IntentResult(
                intent="mixed_query",
                tool_name="get_herb_summary",
                tool_kwargs={"herb_name": herb_name},
                category="MIXED_QUERY",
                knowledge_topic="traceability_explanation",
                multi_tools=[("get_herb_summary", {"herb_name": herb_name})],
                multi_topics=["traceability_explanation"],
                resolved_entities=resolved_entities,
            )

        # Case B: Project Overview + AI Identification (Must have an explicit conjunction like 'aur', 'and', 'also', 'kaise identify')
        if (
            re.search(r"\b(dravya|system)\b", text_lower)
            and re.search(r"\b(ai|identify|identification|model|efficientnet)\b", text_lower)
            and re.search(r"\b(aur|and|also|plus|identify kaise|kaise identify)\b", text_lower)
        ):
            return IntentResult(
                intent="mixed_query",
                category="MIXED_QUERY",
                knowledge_topic="project_overview",
                multi_topics=["project_overview", "ai_engine"],
                resolved_entities=resolved_entities,
            )

        # Case C: Complete Batch Details + Full Traceability
        if batch_id and any(w in text_lower for w in ["complete", "poori", "all details", "farmer, quantity", "sab kuch", "full details", "traceability aur"]):
            return IntentResult(
                intent="batch_traceability",
                tool_name="get_batch_traceability",
                tool_kwargs={"batch_id": batch_id},
                category="LIVE_DATA",
                multi_tools=[
                    ("get_batch", {"batch_id": batch_id}),
                    ("get_batch_traceability", {"batch_id": batch_id}),
                ],
                resolved_entities=resolved_entities,
                specific_field="full",
            )

        # 5. Live Data Intents

        # Total inventory summary
        if any(w in text_lower for w in [
            "system me total", "total inventory", "overall summary", "all herbs",
            "total stock", "total kitni", "kitni herbs", "total inventory batao",
            "overall inventory", "system me total kitni herbs", "current inventory",
            "what herbs are present", "kaunsi herbs hain", "list all herbs"
        ]):
            return IntentResult(
                intent="inventory_summary",
                tool_name="get_inventory_summary",
                tool_kwargs={},
                category="LIVE_DATA",
                resolved_entities=resolved_entities,
            )

        # Batch Traceability
        if "traceability" in text_lower or "trace" in text_lower or "provenance" in text_lower:
            if batch_id:
                return IntentResult(
                    intent="batch_traceability",
                    tool_name="get_batch_traceability",
                    tool_kwargs={"batch_id": batch_id},
                    category="LIVE_DATA",
                    resolved_entities=resolved_entities,
                    specific_field=specific_field,
                )
            elif not knowledge_topic:
                return IntentResult(
                    intent="batch_traceability",
                    tool_name="get_batch_traceability",
                    tool_kwargs={},
                    category="LIVE_DATA",
                    resolved_entities=resolved_entities,
                )

        # Batch Lookup / Details / Status / Location
        if batch_id:
            return IntentResult(
                intent="batch",
                tool_name="get_batch",
                tool_kwargs={"batch_id": batch_id},
                category="LIVE_DATA",
                resolved_entities=resolved_entities,
                specific_field=specific_field,
            )

        # Farmer Summary & Batches
        if farmer_id:
            if any(w in text_lower for w in ["summary", "total quantity", "total stock", "how much", "kitni quantity", "kitna stock"]):
                return IntentResult(
                    intent="farmer_summary",
                    tool_name="get_farmer_summary",
                    tool_kwargs={"farmer_id": farmer_id},
                    category="LIVE_DATA",
                    resolved_entities=resolved_entities,
                )
            else:
                return IntentResult(
                    intent="farmer_batches",
                    tool_name="get_farmer_batches",
                    tool_kwargs={"farmer_id": farmer_id},
                    category="LIVE_DATA",
                    resolved_entities=resolved_entities,
                )

        # Herb Summary & Batches
        if herb_name and herb_name.lower() not in {"total", "system", "inventory"}:
            if any(w in text_lower for w in ["how many", "all batches", "show me all", "kitne batch", "kitne batches", "list", "batches of"]):
                return IntentResult(
                    intent="herb_batches",
                    tool_name="get_herb_batches",
                    tool_kwargs={"herb_name": herb_name},
                    category="LIVE_DATA",
                    resolved_entities=resolved_entities,
                )
            else:
                return IntentResult(
                    intent="herb_summary",
                    tool_name="get_herb_summary",
                    tool_kwargs={"herb_name": herb_name},
                    category="LIVE_DATA",
                    resolved_entities=resolved_entities,
                )

        # 6. Project Knowledge Intent
        if knowledge_topic:
            return IntentResult(
                intent=knowledge_topic,
                category="PROJECT_KNOWLEDGE",
                knowledge_topic=knowledge_topic,
                resolved_entities=resolved_entities,
            )

        # 7. Conversational / Unknown
        is_greeting = any(w in text_lower for w in ["hello", "hi", "hey", "namaste", "pranam", "who are you", "tum kaun ho", "aap kaun hain"])
        if is_greeting:
            return IntentResult(
                intent="conversational",
                category="CONVERSATIONAL",
                resolved_entities=resolved_entities,
            )

        return IntentResult(
            intent="unknown",
            category="UNKNOWN",
            resolved_entities=resolved_entities,
        )
