"""
LLM Provider abstraction layer supporting Mock, OpenAI, and Generic HTTP LLM endpoints for Dravya AI Copilot.
Handles environment configuration, project knowledge grounding, and graceful fallback.
"""
from abc import ABC, abstractmethod
import json
import logging
import os
from typing import Any, Dict, List, Optional, Tuple, Union

import httpx

from src.assistant.exceptions import LLMProviderError
from src.assistant.intent import IntentAnalyzer, IntentResult
from src.assistant.knowledge import KnowledgeRetriever
from src.assistant.schemas import ToolCall
from src.assistant.tools import get_tool_definitions

logger = logging.getLogger(__name__)

COPILOT_SYSTEM_PROMPT = """You are Dravya AI Copilot, an expert AI assistant for the Dravya Ayurvedic Blockchain Platform.
Your mission is providing authoritative, accurate, and structured answers across two main domains:
1. LIVE DRAVYA DATA: Querying real-time Ayurvedic herb inventory, batches, farmer records, quality verification statuses, and blockchain traceability payloads.
2. DRAVYA PROJECT KNOWLEDGE: Explaining Dravya's mission, problem statement, 5-phase supply chain workflow, deep learning AI Engine (EfficientNet-B0), and Hyperledger Fabric blockchain architecture.

STRICT POLICY & GUIDELINES:
1. NEVER INVENT OR HALLUCINATE DATA.
   - Do not manufacture herb quantities, batch IDs, farmer IDs, locations, verification statuses, or blockchain hashes.
   - If a batch, farmer, or herb is not found in the live data, clearly state: "I couldn't find a matching record in the current Dravya data."
   - If a question asks about unverified or undocumented features, clearly state: "I don't have enough verified information in the current Dravya documentation to answer that accurately."
2. RELY STRICTLY ON RETRIEVED DATA AND GROUNDED KNOWLEDGE.
3. Keep technical identifiers such as Batch IDs (e.g. DRAVYA-ASH-20260810-346DA7) and Farmer IDs (e.g. F001) intact.
4. Deliver polished, professional, well-structured responses with markdown headings/bullets when appropriate.
5. Fluently match the user's language (English, Hindi, or Hinglish).
6. Do NOT provide medical diagnosis or unsafe medical advice. You are a platform data and supply chain copilot.
"""


class LLMProvider(ABC):
    """Abstract base class for Dravya AI Copilot LLM Providers."""

    @abstractmethod
    def generate_with_tools(
        self,
        user_message: str,
        system_prompt: str = COPILOT_SYSTEM_PROMPT,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        context_entities: Optional[Dict[str, Optional[str]]] = None,
    ) -> Tuple[Optional[ToolCall], Optional[str], Optional[IntentResult]]:
        """
        Processes user query. Returns (ToolCall, thought/answer, IntentResult).
        """
        pass

    @abstractmethod
    def synthesize_answer(
        self,
        user_message: str,
        tool_name: str,
        tool_data: Dict[str, Any],
        system_prompt: str = COPILOT_SYSTEM_PROMPT,
        intent_result: Optional[IntentResult] = None,
    ) -> str:
        """
        Synthesizes structured tool response and knowledge into natural language.
        """
        pass


class MockLLMProvider(LLMProvider):
    """
    Deterministic rule-based LLM Provider for offline use, unit testing, and fallback.
    Provides complete project knowledge, live data formatting, and zero hallucinations.
    """

    def __init__(self):
        self.intent_analyzer = IntentAnalyzer()
        self.knowledge_retriever = KnowledgeRetriever()

    def generate_with_tools(
        self,
        user_message: str,
        system_prompt: str = COPILOT_SYSTEM_PROMPT,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        context_entities: Optional[Dict[str, Optional[str]]] = None,
    ) -> Tuple[Optional[ToolCall], Optional[str], Optional[IntentResult]]:
        analysis = self.intent_analyzer.analyze(user_message, context_entities=context_entities)
        is_hindi = any(w in user_message.lower() for w in ["hai", "kya", "batao", "kaise", "ke", "ki", "ka", "main", "kahan", "kaun"])

        # 1. Project Knowledge Queries
        if analysis.category == "PROJECT_KNOWLEDGE" and analysis.knowledge_topic:
            is_deep_dive = any(w in user_message.lower() for w in ["detail", "deep dive", "vistrit", "explain dravya in detail", "poora"])
            if is_deep_dive or (analysis.knowledge_topic == "project_overview" and "detail" in user_message.lower()):
                ans = self.knowledge_retriever.get_structured_deep_dive(is_hindi=is_hindi)
            else:
                ans = self.knowledge_retriever.get_answer(analysis.knowledge_topic, is_hindi=is_hindi, detailed=True)
            return None, ans, analysis

        # 2. Mixed Query with Live Tool
        if analysis.category == "MIXED_QUERY":
            if analysis.tool_name:
                return ToolCall(name=analysis.tool_name, arguments=analysis.tool_kwargs), "Executing live data tool for mixed query", analysis
            # Pure knowledge mixed query
            topics = analysis.multi_topics or ["project_overview", "ai_engine"]
            answers = [self.knowledge_retriever.get_answer(t, is_hindi=is_hindi) for t in topics]
            ans = "\n\n---\n\n".join(answers)
            return None, ans, analysis

        # 3. Live Data Queries
        if analysis.tool_name is not None:
            return ToolCall(name=analysis.tool_name, arguments=analysis.tool_kwargs), f"Selected tool {analysis.tool_name}", analysis

        # 4. Conversational
        if analysis.category == "CONVERSATIONAL":
            if is_hindi:
                ans = (
                    "Namaste! Main Dravya AI Copilot hoon. Aap mujhse Ayurvedic herb inventory, batches, "
                    "farmer details, blockchain traceability aur Dravya platform ke bare me pooch sakte hain."
                )
            else:
                ans = (
                    "Hello! I am Dravya AI Copilot. You can ask me about Ayurvedic herb inventory, "
                    "batch details, farmer contributions, blockchain traceability, or Dravya system architecture."
                )
            return None, ans, analysis

        # 5. Unknown / Ungrounded queries
        if is_hindi:
            ans = "Dravya ke uplabdh documentation me is bare me paryapt jankari uplabdh nahi hai."
        else:
            ans = "I don't have enough verified information in the current Dravya documentation to answer that accurately."
        return None, ans, analysis

    def synthesize_answer(
        self,
        user_message: str,
        tool_name: str,
        tool_data: Dict[str, Any],
        system_prompt: str = COPILOT_SYSTEM_PROMPT,
        intent_result: Optional[IntentResult] = None,
    ) -> str:
        is_hindi = any(w in user_message.lower() for w in [
            "ki", "ka", "ke", "kitni", "kitne", "hai", "paas", "kya", "dikhao", "batao", "se", "main", "kahan", "kaun"
        ])
        specific_field = intent_result.specific_field if intent_result else None

        # 1. get_herb_summary
        if tool_name == "get_herb_summary":
            herb = tool_data.get("canonical_species") or tool_data.get("herb", "Herb")
            qty = tool_data.get("total_quantity", 0.0)
            count = tool_data.get("total_batches", 0)
            farmers = tool_data.get("farmers_count", 0)

            if count == 0:
                base_msg = (
                    f"Dravya system me '{herb}' ki koi active inventory record nahi mili."
                    if is_hindi
                    else f"No inventory records found for '{herb}' in the Dravya system."
                )
            else:
                if is_hindi:
                    base_msg = (
                        f"Dravya system me **{herb}** ki total recorded quantity **{qty:.2f} kg** hai. "
                        f"Isme total **{count}** batch(es) aur **{farmers}** farmer(s) registered hain."
                    )
                else:
                    base_msg = (
                        f"The Dravya platform has a total recorded quantity of **{qty:.2f} kg** for **{herb}** "
                        f"across **{count}** batch(es) from **{farmers}** farmer(s)."
                    )

            # If this was part of a mixed query with traceability explanation
            if intent_result and intent_result.category == "MIXED_QUERY" and intent_result.knowledge_topic:
                k_expl = self.knowledge_retriever.get_answer(intent_result.knowledge_topic, is_hindi=is_hindi)
                return f"{base_msg}\n\n---\n\n{k_expl}"
            return base_msg

        # 2. get_farmer_summary
        elif tool_name == "get_farmer_summary":
            farmer_id = tool_data.get("farmer_id", "")
            farmer_name = tool_data.get("farmer_name")
            qty = tool_data.get("total_quantity", 0.0)
            count = tool_data.get("total_batches", 0)
            herbs = tool_data.get("herbs_supplied", [])
            herbs_str = ", ".join(herbs) if herbs else "None"
            f_display = f"{farmer_name} ({farmer_id})" if farmer_name else f"Farmer {farmer_id}"

            if count == 0:
                return (
                    f"Farmer ID {farmer_id} ke paas Dravya system me koi active batches recorded nahi hain."
                    if is_hindi
                    else f"No batch records found for farmer ID {farmer_id} in the Dravya system."
                )

            if is_hindi:
                return (
                    f"**{f_display}** ke paas total **{qty:.2f} kg** stock recorded hai, "
                    f"jisme **{count}** batch(es) hain. Herbs: {herbs_str}."
                )
            else:
                return (
                    f"**{f_display}** has a total inventory of **{qty:.2f} kg** across **{count}** batch(es). "
                    f"Herbs: {herbs_str}."
                )

        # 3. get_herb_batches
        elif tool_name == "get_herb_batches":
            herb = tool_data.get("herb_name", "Herb")
            batches = tool_data.get("batches", [])
            count = len(batches)

            if count == 0:
                return (
                    f"Dravya system me '{herb}' ke koi batches nahi mile."
                    if is_hindi
                    else f"No batches found for herb '{herb}'."
                )

            batch_ids = [b.get("batch_id") for b in batches[:5]]
            ids_str = ", ".join(batch_ids)

            if is_hindi:
                return f"Dravya system me **{herb}** ke total **{count}** batches hain: {ids_str}."
            else:
                return f"There are **{count}** batch(es) recorded for **{herb}** in Dravya: {ids_str}."

        # 4. get_farmer_batches
        elif tool_name == "get_farmer_batches":
            farmer_id = tool_data.get("farmer_id", "")
            batches = tool_data.get("batches", [])
            count = len(batches)

            if count == 0:
                return (
                    f"Farmer {farmer_id} ke paas koi batches nahi hain."
                    if is_hindi
                    else f"No batches found for farmer {farmer_id}."
                )

            batch_list = [f"{b.get('batch_id')} ({b.get('herb_species')}, {b.get('quantity')} kg)" for b in batches[:5]]
            b_str = "; ".join(batch_list)

            if is_hindi:
                return f"Farmer **{farmer_id}** ke paas total **{count}** batches hain: {b_str}."
            else:
                return f"Farmer **{farmer_id}** has **{count}** recorded batch(es): {b_str}."

        # 5. get_inventory_summary
        elif tool_name == "get_inventory_summary":
            total_batches = tool_data.get("total_batches", 0)
            total_qty = tool_data.get("total_quantity_kg", 0.0)
            herbs_count = tool_data.get("unique_herbs_count", 0)
            farmers_count = tool_data.get("unique_farmers_count", 0)
            herbs_summary = tool_data.get("herbs_summary", [])
            top_herbs = ", ".join([f"{h.get('canonical_species', h.get('herb'))} ({h.get('total_quantity', 0):.1f} kg)" for h in herbs_summary[:4]])

            if is_hindi:
                msg = (
                    f"Dravya platform me total **{herbs_count}** herb species, **{farmers_count}** farmers, "
                    f"aur **{total_batches}** batches hain, jinki kul quantity **{total_qty:.2f} kg** hai."
                )
                if top_herbs:
                    msg += f"\n\n**Herbs Summary**: {top_herbs}."
                return msg
            else:
                msg = (
                    f"The Dravya platform contains a total of **{herbs_count}** herb species, **{farmers_count}** farmers, "
                    f"and **{total_batches}** batches with a combined quantity of **{total_qty:.2f} kg**."
                )
                if top_herbs:
                    msg += f"\n\n**Herbs Breakdown**: {top_herbs}."
                return msg

        # 6. get_batch (or specific field answers)
        elif tool_name == "get_batch":
            if tool_data.get("found") is False:
                b_id = tool_data.get("batch_id", "")
                return (
                    f"Batch ID '{b_id}' Dravya system me nahi mila."
                    if is_hindi
                    else f"Batch ID '{b_id}' was not found in the Dravya system."
                )

            b_id = tool_data.get("batch_id", "")
            herb = tool_data.get("herb_species", "")
            canon = tool_data.get("canonical_species", herb)
            sci = tool_data.get("scientific_name", "")
            qty = tool_data.get("quantity", 0.0)
            unit = tool_data.get("quantity_unit", "kg")
            farmer = tool_data.get("farmer_id", "")
            farmer_name = tool_data.get("farmer_name", "")
            h_date = tool_data.get("harvest_date", "")
            meta = tool_data.get("metadata", {}) or {}
            location = meta.get("location", "Not specified in metadata")
            moisture = meta.get("moisture_content", "Not specified")
            status_val = tool_data.get("verification_status", "UNVERIFIED")
            if hasattr(status_val, "value"):
                status_val = status_val.value

            # Targeted field query handling
            if specific_field == "farmer":
                f_str = f"{farmer_name} ({farmer})" if farmer_name else farmer
                return (
                    f"Batch **{b_id}** ka farmer **{f_str}** hai (Herb: {canon}, Harvest Date: {h_date})."
                    if is_hindi
                    else f"The farmer associated with batch **{b_id}** is **{f_str}**."
                )
            elif specific_field == "location":
                return (
                    f"Batch **{b_id}** ki location: **{location}** (Farmer: {farmer})."
                    if is_hindi
                    else f"The recorded location for batch **{b_id}** is **{location}**."
                )
            elif specific_field == "status":
                return (
                    f"Batch **{b_id}** ka verification status **{status_val}** hai."
                    if is_hindi
                    else f"The verification status for batch **{b_id}** is **{status_val}**."
                )
            elif specific_field == "quantity":
                return (
                    f"Batch **{b_id}** ki quantity **{qty} {unit}** hai."
                    if is_hindi
                    else f"The quantity of batch **{b_id}** is **{qty} {unit}**."
                )
            elif specific_field == "moisture":
                return (
                    f"Batch **{b_id}** ka moisture content **{moisture}** hai."
                    if is_hindi
                    else f"The moisture content for batch **{b_id}** is **{moisture}**."
                )

            # Full batch details
            f_str = f"{farmer_name} ({farmer})" if farmer_name else farmer
            sci_str = f" (*{sci}*)" if sci else ""
            if is_hindi:
                return (
                    f"### Batch Details: {b_id}\n"
                    f"- **Herb Species**: {canon}{sci_str}\n"
                    f"- **Quantity**: {qty} {unit}\n"
                    f"- **Farmer**: {f_str}\n"
                    f"- **Harvest Date**: {h_date}\n"
                    f"- **Verification Status**: `{status_val}`\n"
                    f"- **Location**: {location}"
                )
            else:
                return (
                    f"### Batch Details: {b_id}\n"
                    f"- **Herb Species**: {canon}{sci_str}\n"
                    f"- **Quantity**: {qty} {unit}\n"
                    f"- **Farmer**: {f_str}\n"
                    f"- **Harvest Date**: {h_date}\n"
                    f"- **Verification Status**: `{status_val}`\n"
                    f"- **Location**: {location}"
                )

        # 7. get_batch_traceability
        elif tool_name == "get_batch_traceability":
            if tool_data.get("found") is False:
                b_id = tool_data.get("batch_id", "")
                return (
                    f"Batch ID '{b_id}' ke liye traceability data uplabdh nahi hai (Batch not found)."
                    if is_hindi
                    else f"Traceability data unavailable for Batch ID '{b_id}' (Batch not found)."
                )

            b_id = tool_data.get("batch_id", "")
            h_hash = tool_data.get("payload_hash", "")
            status_val = tool_data.get("verification_status", "")
            origin = tool_data.get("origin", {})
            f_id = origin.get("farmer_id", "")
            f_name = origin.get("farmer_name", "")
            f_disp = f"{f_name} ({f_id})" if f_name else f_id
            herb_info = tool_data.get("herb", {})
            h_name = herb_info.get("canonical_species") or herb_info.get("common_name", "")
            qty_info = tool_data.get("quantity", {})
            q_val = qty_info.get("value", "")
            q_unit = qty_info.get("unit", "kg")

            if is_hindi:
                return (
                    f"### Blockchain Traceability: {b_id}\n"
                    f"- **Herb**: {h_name}\n"
                    f"- **Origin**: {f_disp}\n"
                    f"- **Quantity**: {q_val} {q_unit}\n"
                    f"- **Verification Status**: `{status_val}`\n"
                    f"- **Tamper-Evident SHA-256 Hash**: `{h_hash}`\n\n"
                    f"Yeh batch Hyperledger Fabric blockchain par anchored hai aur cryptographically authentic hai."
                )
            else:
                return (
                    f"### Blockchain Traceability: {b_id}\n"
                    f"- **Herb**: {h_name}\n"
                    f"- **Origin**: {f_disp}\n"
                    f"- **Quantity**: {q_val} {q_unit}\n"
                    f"- **Verification Status**: `{status_val}`\n"
                    f"- **Tamper-Evident SHA-256 Hash**: `{h_hash}`\n\n"
                    f"This batch is anchored to Hyperledger Fabric blockchain with verified cryptographic integrity."
                )

        # 8. get_batch_full_details
        elif tool_name == "get_batch_full_details":
            if tool_data.get("found") is False:
                b_id = tool_data.get("batch_id", "")
                return (
                    f"Batch ID '{b_id}' Dravya system me nahi mila."
                    if is_hindi
                    else f"Batch ID '{b_id}' was not found in the Dravya system."
                )
            b = tool_data.get("batch", {})
            t = tool_data.get("traceability", {})
            b_id = b.get("batch_id", "")
            canon = b.get("canonical_species", "")
            qty = b.get("quantity", 0.0)
            unit = b.get("quantity_unit", "kg")
            f_str = f"{b.get('farmer_name')} ({b.get('farmer_id')})" if b.get('farmer_name') else b.get('farmer_id')
            status_val = b.get("verification_status", "")
            payload_hash = t.get("payload_hash", "")

            if is_hindi:
                return (
                    f"### Complete Batch & Traceability Record: {b_id}\n"
                    f"- **Herb Species**: {canon}\n"
                    f"- **Farmer**: {f_str}\n"
                    f"- **Quantity**: {qty} {unit}\n"
                    f"- **Harvest Date**: {b.get('harvest_date')}\n"
                    f"- **Verification Status**: `{status_val}`\n"
                    f"- **Blockchain SHA-256 Hash**: `{payload_hash}`\n\n"
                    f"Dravya platform is batch ki authenticity aur seed-to-shelf provenance guarantee karta hai."
                )
            else:
                return (
                    f"### Complete Batch & Traceability Record: {b_id}\n"
                    f"- **Herb Species**: {canon}\n"
                    f"- **Farmer**: {f_str}\n"
                    f"- **Quantity**: {qty} {unit}\n"
                    f"- **Harvest Date**: {b.get('harvest_date')}\n"
                    f"- **Verification Status**: `{status_val}`\n"
                    f"- **Blockchain SHA-256 Hash**: `{payload_hash}`\n\n"
                    f"The Dravya platform guarantees verified authenticity and tamper-evident provenance for this batch."
                )

        # 9. get_project_knowledge
        elif tool_name == "get_project_knowledge":
            return tool_data.get("content", str(tool_data))

        return f"Retrieved data: {tool_data}"


class OpenAILLMProvider(LLMProvider):
    """
    OpenAI / Generic HTTP LLM Provider calling external REST API with fallback to MockLLMProvider.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        base_url: str = "https://api.openai.com/v1",
        timeout: float = 15.0,
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.fallback = MockLLMProvider()

    def generate_with_tools(
        self,
        user_message: str,
        system_prompt: str = COPILOT_SYSTEM_PROMPT,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        context_entities: Optional[Dict[str, Optional[str]]] = None,
    ) -> Tuple[Optional[ToolCall], Optional[str], Optional[IntentResult]]:
        analysis = self.fallback.intent_analyzer.analyze(user_message, context_entities=context_entities)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        messages = [{"role": "system", "content": system_prompt}]
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_message})

        payload = {
            "model": self.model,
            "messages": messages,
            "tools": get_tool_definitions(),
            "tool_choice": "auto",
            "temperature": 0.1,
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
                if resp.status_code != 200:
                    logger.warning(f"LLM Provider API status {resp.status_code}. Using fallback provider.")
                    return self.fallback.generate_with_tools(user_message, system_prompt, conversation_history, context_entities)

                data = resp.json()
                choice = data["choices"][0]["message"]

                if "tool_calls" in choice and choice["tool_calls"]:
                    tc = choice["tool_calls"][0]["function"]
                    args = json.loads(tc.get("arguments", "{}"))
                    return ToolCall(name=tc["name"], arguments=args), choice.get("content"), analysis

                return None, choice.get("content", ""), analysis

        except Exception as e:
            logger.warning(f"Error communicating with LLM Provider: {e}. Using fallback provider.")
            return self.fallback.generate_with_tools(user_message, system_prompt, conversation_history, context_entities)

    def synthesize_answer(
        self,
        user_message: str,
        tool_name: str,
        tool_data: Dict[str, Any],
        system_prompt: str = COPILOT_SYSTEM_PROMPT,
        intent_result: Optional[IntentResult] = None,
    ) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        prompt = (
            f"User query: '{user_message}'\n"
            f"Executed tool: '{tool_name}'\n"
            f"Tool returned data: {json.dumps(tool_data)}\n\n"
            f"Synthesize an accurate, grounded, natural language response in the user's language. Never invent data."
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.warning(f"Failed to synthesize with external LLM: {e}. Using fallback synthesizer.")

        return self.fallback.synthesize_answer(user_message, tool_name, tool_data, system_prompt, intent_result)


def get_llm_provider() -> LLMProvider:
    """
    Factory function loading LLM provider from environment variables.
    Defaults to MockLLMProvider if no valid key is configured. Never crashes application startup.
    """
    provider_name = os.getenv("DRAVYA_LLM_PROVIDER", "mock").lower()
    api_key = os.getenv("DRAVYA_LLM_API_KEY", "") or os.getenv("OPENAI_API_KEY", "")
    model = os.getenv("DRAVYA_LLM_MODEL", "gpt-4o-mini")

    if provider_name in ["openai", "generic_http"] and api_key:
        try:
            return OpenAILLMProvider(api_key=api_key, model=model)
        except Exception as e:
            logger.error(f"Failed to instantiate LLM provider '{provider_name}': {e}. Using MockLLMProvider.")
            return MockLLMProvider()

    # Default offline provider
    return MockLLMProvider()
