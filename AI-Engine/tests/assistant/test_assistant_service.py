"""
Unit and Integration tests for Dravya AI Assistant service, tools, provider, and intent analyzer.
"""
import pytest
from pydantic import ValidationError

from src.assistant import (
    AssistantService,
    AssistantTools,
    ChatRequest,
    ChatResponse,
    IntentAnalyzer,
    MockLLMProvider,
)
from src.assistant.exceptions import InvalidToolArgumentError, ToolExecutionError
from src.assistant.tools import get_tool_definitions
from src.batch import BatchCreate, BatchManager


@pytest.fixture
def batch_manager():
    bm = BatchManager()
    bm.clear()
    # Seed known test batch data
    bm.create_batch(
        BatchCreate(
            herb_species="Ashwagandha",
            farmer_id="F001",
            farmer_name="Ramesh Kumar",
            quantity=150.0,
            quantity_unit="kg",
            harvest_date="2026-08-10",
        ),
        nonce="TEST01",
    )
    bm.create_batch(
        BatchCreate(
            herb_species="Tulsi",
            farmer_id="F002",
            farmer_name="Suresh Singh",
            quantity=75.0,
            quantity_unit="kg",
            harvest_date="2026-08-11",
        ),
        nonce="TEST02",
    )
    yield bm
    bm.clear()


@pytest.fixture
def assistant_tools(batch_manager):
    return AssistantTools(batch_manager=batch_manager)


@pytest.fixture
def assistant_service(assistant_tools):
    return AssistantService(tools=assistant_tools)


# 1. ChatRequest Validation
def test_chat_request_valid():
    req = ChatRequest(message="Ashwagandha ki quantity?")
    assert req.message == "Ashwagandha ki quantity?"
    assert req.conversation_id is None


def test_chat_request_empty_fails():
    with pytest.raises(ValidationError):
        ChatRequest(message="   ")


def test_chat_request_too_long_fails():
    with pytest.raises(ValidationError):
        ChatRequest(message="A" * 1001)


# 2. ChatResponse Validation
def test_chat_response_schema():
    resp = ChatResponse(
        answer="150 kg Ashwagandha available.",
        intent="herb_summary",
        data={"total_quantity": 150.0},
        tool_used="get_herb_summary",
    )
    assert resp.intent == "herb_summary"
    assert resp.tool_used == "get_herb_summary"


# 3. Tool Schemas
def test_tool_definitions_valid():
    defs = get_tool_definitions()
    assert len(defs) >= 7
    names = [d["function"]["name"] for d in defs]
    assert "get_herb_summary" in names
    assert "get_farmer_summary" in names
    assert "get_inventory_summary" in names
    assert "get_batch" in names
    assert "get_batch_traceability" in names


# 4. Herb Summary Tool
def test_herb_summary_tool(assistant_tools):
    res = assistant_tools.get_herb_summary("Ashwagandha")
    assert res["herb"] == "Ashwagandha"
    assert res["total_quantity"] == 150.0
    assert res["total_batches"] == 1
    assert res["farmers_count"] == 1


# 5. Farmer Summary Tool
def test_farmer_summary_tool(assistant_tools):
    res = assistant_tools.get_farmer_summary("F001")
    assert res["farmer_id"] == "F001"
    assert res["total_quantity"] == 150.0
    assert res["total_batches"] == 1


# 6. Inventory Summary Tool
def test_inventory_summary_tool(assistant_tools):
    res = assistant_tools.get_inventory_summary()
    assert res["total_batches"] == 2
    assert res["total_quantity_kg"] == 225.0
    assert res["unique_herbs_count"] == 2
    assert res["unique_farmers_count"] == 2


# 7. Batch Lookup Tool
def test_batch_lookup_tool(assistant_tools, batch_manager):
    batches = batch_manager.list_batches(herb_species="Ashwagandha")
    b_id = batches[0].batch_id
    res = assistant_tools.get_batch(b_id)
    assert res["batch_id"] == b_id
    assert res["herb_species"] == "Ashwagandha"
    assert res["quantity"] == 150.0


# 8. Traceability Tool
def test_batch_traceability_tool(assistant_tools, batch_manager):
    batches = batch_manager.list_batches(herb_species="Ashwagandha")
    b_id = batches[0].batch_id
    res = assistant_tools.get_batch_traceability(b_id)
    assert res["batch_id"] == b_id
    assert "payload_hash" in res
    assert len(res["payload_hash"]) == 64  # SHA-256 length


# 9. Unknown Batch
def test_unknown_batch_tool(assistant_tools):
    res = assistant_tools.get_batch("DRAVYA-UNKNOWN-000")
    assert res["found"] is False
    assert "not found" in res["error"].lower()


# 10. Unknown Farmer
def test_unknown_farmer_tool(assistant_tools):
    res = assistant_tools.get_farmer_summary("F999")
    assert res["farmer_id"] == "F999"
    assert res["total_batches"] == 0
    assert res["total_quantity"] == 0.0


# 11. Unknown Herb
def test_unknown_herb_tool(assistant_tools):
    res = assistant_tools.get_herb_summary("NonExistentHerb")
    assert res["total_batches"] == 0
    assert res["total_quantity"] == 0.0


# 12. Tool Argument Validation
def test_invalid_tool_args(assistant_tools):
    with pytest.raises(InvalidToolArgumentError):
        assistant_tools.get_herb_summary("   ")

    with pytest.raises(ToolExecutionError):
        assistant_tools.execute_tool("unknown_tool_name", {})


# 13. Max Tool-Call Protection & Process Chat
def test_process_chat_english_query(assistant_service):
    req = ChatRequest(message="How much Ashwagandha do we have?")
    resp = assistant_service.process_chat(req)
    assert resp.intent == "herb_summary"
    assert resp.tool_used == "get_herb_summary"
    assert "150.00 kg" in resp.answer or "150" in resp.answer
    assert resp.data["total_quantity"] == 150.0


# 14. Hindi / Hinglish Intent Handling
def test_process_chat_hinglish_query(assistant_service):
    req = ChatRequest(message="Ashwagandha ki total quantity kitni hai?")
    resp = assistant_service.process_chat(req)
    assert resp.intent == "herb_summary"
    assert "Dravya system me" in resp.answer or "150.00 kg" in resp.answer
    assert resp.data["total_quantity"] == 150.0


def test_process_chat_farmer_hinglish(assistant_service):
    req = ChatRequest(message="F001 ke paas kya hai?")
    resp = assistant_service.process_chat(req)
    assert resp.intent in ["farmer_batches", "farmer_summary"]
    assert "F001" in resp.answer


# 15. Provider Fallback on error
def test_llm_provider_fallback(batch_manager):
    class ErrorLLMProvider(MockLLMProvider):
        def generate_with_tools(self, *args, **kwargs):
            raise RuntimeError("API Error simulation")

    srv = AssistantService(
        tools=AssistantTools(batch_manager=batch_manager),
        provider=ErrorLLMProvider(),
    )
    req = ChatRequest(message="Total inventory batao")
    resp = srv.process_chat(req)
    assert resp.intent == "inventory_summary"
    assert resp.data["total_batches"] == 2


# 16. No-Hallucination behavior check
def test_no_hallucination_empty_inventory(batch_manager):
    bm = BatchManager()
    bm.clear()  # No batches registered
    srv = AssistantService(tools=AssistantTools(batch_manager=bm))
    req = ChatRequest(message="How much Ashwagandha do we have?")
    resp = srv.process_chat(req)
    assert resp.data["total_batches"] == 0
    assert "No inventory records found" in resp.answer or "nahi mili" in resp.answer
