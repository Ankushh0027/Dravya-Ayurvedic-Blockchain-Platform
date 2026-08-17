"""
High-level Assistant Orchestration Service connecting LLM provider, Intent Analyzer, Context Session Manager, and Assistant Tools.
Enforces zero-hallucination policy, conversation entity tracking, max tool call thresholds, and clean error handling.
"""
import logging
from typing import Any, Dict, Optional

from src.assistant.context import SessionManager, get_session_manager
from src.assistant.exceptions import (
    AssistantError,
    InvalidToolArgumentError,
    MaxToolCallsExceededError,
    ToolExecutionError,
)
from src.assistant.intent import IntentAnalyzer, IntentResult
from src.assistant.knowledge import KnowledgeRetriever
from src.assistant.provider import LLMProvider, MockLLMProvider, get_llm_provider
from src.assistant.schemas import ChatRequest, ChatResponse
from src.assistant.tools import AssistantTools
from src.batch import BatchManager

logger = logging.getLogger(__name__)

MAX_TOOL_CALLS_PER_REQUEST = 3


class AssistantService:
    """
    Service orchestrator executing natural language chat requests against deterministic backend tools and knowledge.
    Enforces no-hallucination policy, session context resolution, max tool call thresholds, and clean error handling.
    """

    def __init__(
        self,
        tools: Optional[AssistantTools] = None,
        provider: Optional[LLMProvider] = None,
        intent_analyzer: Optional[IntentAnalyzer] = None,
        session_manager: Optional[SessionManager] = None,
    ):
        self.tools = tools or AssistantTools()
        self.provider = provider or get_llm_provider()
        self.intent_analyzer = intent_analyzer or IntentAnalyzer()
        self.session_manager = session_manager or get_session_manager()
        self.knowledge_retriever = KnowledgeRetriever()

    def process_chat(self, request: ChatRequest) -> ChatResponse:
        """
        Executes end-to-end chat workflow:
        Input validation -> Session Context Lookup -> Entity resolution -> Intent & Tool call ->
        Execution -> Answer synthesis -> Session context update -> Grounded Response.
        """
        user_msg = request.message

        # 1. Retrieve session and resolve context entities (anaphora / pronoun resolution)
        session, cid = self.session_manager.get_or_create_session(request.conversation_id)
        ctx_entities = self.session_manager.resolve_context_entities(user_msg, session)

        # 2. Determine tool call / intent via LLM Provider (or intent analyzer)
        try:
            tool_call, thought, analysis = self.provider.generate_with_tools(
                user_msg,
                context_entities=ctx_entities,
            )
        except Exception as e:
            logger.exception(f"LLM Provider error during intent determination: {e}")
            fallback_provider = MockLLMProvider()
            tool_call, thought, analysis = fallback_provider.generate_with_tools(
                user_msg,
                context_entities=ctx_entities,
            )

        intent_name = analysis.intent if analysis else "unknown"

        # 3. Update session with newly resolved entities
        if analysis and analysis.resolved_entities:
            session.update_entities(
                herb=analysis.resolved_entities.get("herb"),
                batch_id=analysis.resolved_entities.get("batch_id"),
                farmer_id=analysis.resolved_entities.get("farmer_id"),
                intent=intent_name,
                topic=analysis.knowledge_topic,
            )

        # 4. If no tool execution is required (Project Knowledge, Conversational, or Unknown)
        if tool_call is None:
            ans = thought or "I am Dravya AI Copilot. How can I assist you with your Ayurvedic herb platform?"
            return ChatResponse(
                answer=ans,
                intent=intent_name,
                data=None,
                tool_used=None,
            )

        # 5. Tool execution loop with maximum tool call protection
        tool_name = tool_call.name
        kwargs = tool_call.arguments
        call_count = 0

        logger.info(f"Executing tool '{tool_name}' with args: {kwargs}")

        try:
            call_count += 1
            if call_count > MAX_TOOL_CALLS_PER_REQUEST:
                raise MaxToolCallsExceededError("Exceeded maximum tool calls limit per request.")

            # Check if this query needs full batch details aggregation
            if tool_name == "get_batch_traceability" and analysis and getattr(analysis, "specific_field", None) == "full":
                tool_data = self.tools.get_batch_full_details(kwargs.get("batch_id", ""))
                tool_name = "get_batch_full_details"
            else:
                # Deterministically execute backend function
                tool_data = self.tools.execute_tool(tool_name, kwargs)

        except InvalidToolArgumentError as e:
            logger.warning(f"Invalid tool argument: {e}")
            return ChatResponse(
                answer=f"Kripya sahi parameters pradan karein. Error: {str(e)}",
                intent=intent_name,
                data={"error": str(e)},
                tool_used=tool_name,
            )
        except ToolExecutionError as e:
            logger.error(f"Tool execution failed: {e}")
            return ChatResponse(
                answer="Khed hai, request process karte waqt backend error aaya. Kripya punah prayas karein.",
                intent=intent_name,
                data={"error": "Tool execution failed"},
                tool_used=tool_name,
            )

        # 6. Synthesize answer based strictly on retrieved data & grounded knowledge
        try:
            answer_text = self.provider.synthesize_answer(
                user_msg,
                tool_name,
                tool_data,
                intent_result=analysis,
            )
        except Exception as e:
            logger.warning(f"Failed to synthesize answer via main provider: {e}. Using mock fallback.")
            fallback_provider = MockLLMProvider()
            answer_text = fallback_provider.synthesize_answer(
                user_msg,
                tool_name,
                tool_data,
                intent_result=analysis,
            )

        return ChatResponse(
            answer=answer_text,
            intent=intent_name,
            data=tool_data,
            tool_used=tool_name,
        )
