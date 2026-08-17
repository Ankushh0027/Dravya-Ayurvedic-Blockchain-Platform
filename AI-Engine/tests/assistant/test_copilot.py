"""
Comprehensive Test Suite for Dravya AI Copilot.
Validates Project Knowledge, Live Data, Multi-Intent Mixed Queries, Context-Aware Anaphora Resolution, and Hallucination Protection.
"""
import pytest
from fastapi.testclient import TestClient

from src.api.app import create_app
from src.api.dependencies import get_batch_manager_dependency
from src.assistant import (
    AssistantService,
    AssistantTools,
    ChatRequest,
    ChatResponse,
    IntentAnalyzer,
    KnowledgeRetriever,
    MockLLMProvider,
    get_session_manager,
)
from src.batch import BatchCreate, BatchManager


@pytest.fixture
def seeded_batch_manager():
    manager = get_batch_manager_dependency()
    manager.clear()

    # Create test batches with metadata
    b1 = manager.create_batch(
        BatchCreate(
            herb_species="Ashwagandha",
            farmer_id="F001",
            farmer_name="Ramesh Kumar",
            quantity=150.0,
            quantity_unit="kg",
            harvest_date="2026-08-10",
            metadata={"location": "Madhya Pradesh, India", "moisture_content": "8.5%"},
        ),
        nonce="COPILOT1",
    )
    b2 = manager.create_batch(
        BatchCreate(
            herb_species="Tulsi",
            farmer_id="F002",
            farmer_name="Suresh Singh",
            quantity=75.0,
            quantity_unit="kg",
            harvest_date="2026-08-11",
            metadata={"location": "Uttarakhand, India", "moisture_content": "7.0%"},
        ),
        nonce="COPILOT2",
    )
    yield b1.batch_id, b2.batch_id
    manager.clear()


@pytest.fixture
def copilot_service(seeded_batch_manager):
    bm = get_batch_manager_dependency()
    tools = AssistantTools(batch_manager=bm)
    return AssistantService(tools=tools)


# ==============================================================================
# A. Project Knowledge Tests
# ==============================================================================

def test_knowledge_what_is_dravya(copilot_service):
    req = ChatRequest(message="What is Dravya?")
    resp = copilot_service.process_chat(req)
    assert resp.intent == "project_overview"
    assert "Dravya" in resp.answer
    assert "Ayurvedic" in resp.answer or "botanical" in resp.answer
    assert "traceability" in resp.answer.lower() or "authenticity" in resp.answer.lower()


def test_knowledge_what_is_dravya_hindi(copilot_service):
    req = ChatRequest(message="Dravya kya hai aur ye kya karta hai?")
    resp = copilot_service.process_chat(req)
    assert resp.intent == "project_overview"
    assert "Dravya" in resp.answer
    assert "Ayurvedic" in resp.answer or "blockchain" in resp.answer


def test_knowledge_problem_statement(copilot_service):
    req = ChatRequest(message="What problem does Dravya solve?")
    resp = copilot_service.process_chat(req)
    assert resp.intent in ["project_overview", "project_objective"]
    assert "substitution" in resp.answer.lower() or "adulteration" in resp.answer.lower() or "milawat" in resp.answer.lower()


def test_knowledge_role_of_ai(copilot_service):
    req = ChatRequest(message="What is the role of AI in Dravya?")
    resp = copilot_service.process_chat(req)
    assert resp.intent in ["ai_engine", "herb_identification"]
    assert "EfficientNet" in resp.answer or "98.67%" in resp.answer or "classification" in resp.answer.lower()


def test_knowledge_role_of_blockchain(copilot_service):
    req = ChatRequest(message="What is the role of blockchain in Dravya?")
    resp = copilot_service.process_chat(req)
    assert resp.intent in ["blockchain", "traceability_explanation"]
    assert "Hyperledger Fabric" in resp.answer
    assert "SHA-256" in resp.answer or "hash" in resp.answer.lower()


def test_knowledge_complete_workflow(copilot_service):
    req = ChatRequest(message="Explain the complete workflow of Dravya")
    resp = copilot_service.process_chat(req)
    assert resp.intent == "workflow"
    assert "Phase" in resp.answer or "Registration" in resp.answer or "Harvest" in resp.answer or "Lab" in resp.answer


def test_knowledge_ai_engine_architecture(copilot_service):
    req = ChatRequest(message="Explain the AI Engine architecture and model")
    resp = copilot_service.process_chat(req)
    assert resp.intent == "ai_engine"
    assert "EfficientNet-B0" in resp.answer
    assert "82" in resp.answer
    assert "5.3M" in resp.answer or "16.75 MB" in resp.answer


def test_knowledge_explain_in_detail(copilot_service):
    req = ChatRequest(message="Explain Dravya in detail")
    resp = copilot_service.process_chat(req)
    assert resp.intent == "project_overview"
    assert "What is Dravya?" in resp.answer or "Dravya Kya Hai?" in resp.answer
    assert "Role of AI" in resp.answer or "AI ka Role" in resp.answer
    assert "Role of Blockchain" in resp.answer or "Blockchain ka Role" in resp.answer


def test_knowledge_tech_stack(copilot_service):
    req = ChatRequest(message="What technologies and frameworks are used in Dravya?")
    resp = copilot_service.process_chat(req)
    assert resp.intent == "technology_stack"
    assert "Next.js" in resp.answer or "React" in resp.answer
    assert "FastAPI" in resp.answer or "PyTorch" in resp.answer


def test_knowledge_model_versioning(copilot_service):
    req = ChatRequest(message="How does model versioning and promotion work?")
    resp = copilot_service.process_chat(req)
    assert resp.intent == "model_versioning"
    assert "active_model.json" in resp.answer or "rollback" in resp.answer.lower()


# ==============================================================================
# B. Live Data Tests
# ==============================================================================

def test_live_herb_summary(copilot_service):
    req = ChatRequest(message="How much Ashwagandha do we have?")
    resp = copilot_service.process_chat(req)
    assert resp.intent == "herb_summary"
    assert resp.tool_used == "get_herb_summary"
    assert "150.00 kg" in resp.answer or "150" in resp.answer
    assert resp.data["total_quantity"] == 150.0


def test_live_herb_batches(copilot_service, seeded_batch_manager):
    b1_id, _ = seeded_batch_manager
    req = ChatRequest(message="Show me all batches of Ashwagandha")
    resp = copilot_service.process_chat(req)
    assert resp.intent == "herb_batches"
    assert resp.tool_used == "get_herb_batches"
    assert b1_id in resp.answer
    assert resp.data["total_count"] == 1


def test_live_batch_details(copilot_service, seeded_batch_manager):
    b1_id, _ = seeded_batch_manager
    req = ChatRequest(message=f"Show details of batch {b1_id}")
    resp = copilot_service.process_chat(req)
    assert resp.intent == "batch"
    assert resp.tool_used == "get_batch"
    assert "Ashwagandha" in resp.answer
    assert "150" in resp.answer
    assert "F001" in resp.answer


def test_live_batch_specific_farmer(copilot_service, seeded_batch_manager):
    b1_id, _ = seeded_batch_manager
    req = ChatRequest(message=f"Who is the farmer for batch {b1_id}?")
    resp = copilot_service.process_chat(req)
    assert resp.intent == "batch"
    assert "Ramesh Kumar" in resp.answer or "F001" in resp.answer


def test_live_batch_specific_location(copilot_service, seeded_batch_manager):
    b1_id, _ = seeded_batch_manager
    req = ChatRequest(message=f"Where is batch {b1_id} located?")
    resp = copilot_service.process_chat(req)
    assert resp.intent == "batch"
    assert "Madhya Pradesh" in resp.answer


def test_live_batch_specific_status(copilot_service, seeded_batch_manager):
    b1_id, _ = seeded_batch_manager
    req = ChatRequest(message=f"What is the verification status of batch {b1_id}?")
    resp = copilot_service.process_chat(req)
    assert resp.intent == "batch"
    assert "status" in resp.answer.lower() or "AI_PREDICTED" in resp.answer or "AI_CONFIRMED" in resp.answer


def test_live_batch_traceability(copilot_service, seeded_batch_manager):
    b1_id, _ = seeded_batch_manager
    req = ChatRequest(message=f"What is the traceability information for batch {b1_id}?")
    resp = copilot_service.process_chat(req)
    assert resp.intent == "batch_traceability"
    assert resp.tool_used == "get_batch_traceability"
    assert "payload_hash" in resp.data
    assert len(resp.data["payload_hash"]) == 64
    assert "SHA-256" in resp.answer or "Hash" in resp.answer or "Traceability" in resp.answer


def test_live_farmer_summary(copilot_service):
    req = ChatRequest(message="Give me summary for farmer F001")
    resp = copilot_service.process_chat(req)
    assert resp.intent in ["farmer_summary", "farmer_batches"]
    assert "150.00 kg" in resp.answer or "150" in resp.answer
    assert resp.data["farmer_id"] == "F001"


def test_live_inventory_summary(copilot_service):
    req = ChatRequest(message="What is the current inventory summary?")
    resp = copilot_service.process_chat(req)
    assert resp.intent == "inventory_summary"
    assert resp.tool_used == "get_inventory_summary"
    assert resp.data["total_batches"] == 2
    assert resp.data["total_quantity_kg"] == 225.0


# ==============================================================================
# C. Multi-Intent / Mixed Query Tests
# ==============================================================================

def test_mixed_query_project_plus_ai(copilot_service):
    req = ChatRequest(message="Dravya kya hai aur AI herb ko identify kaise karta hai?")
    resp = copilot_service.process_chat(req)
    assert resp.intent == "mixed_query"
    assert "Dravya" in resp.answer
    assert "EfficientNet" in resp.answer or "Image" in resp.answer or "Patti" in resp.answer or "identify" in resp.answer.lower()


def test_mixed_query_herb_plus_traceability(copilot_service):
    req = ChatRequest(message="Ashwagandha ke kitne batches hain aur unki traceability kaise maintain hoti hai?")
    resp = copilot_service.process_chat(req)
    assert resp.intent in ["mixed_query", "herb_summary", "herb_batches"]
    assert "Ashwagandha" in resp.answer
    assert "150" in resp.answer or "batch" in resp.answer.lower()
    assert "Traceability" in resp.answer or "SHA-256" in resp.answer or "Hyperledger" in resp.answer or "payload" in resp.answer.lower()


def test_mixed_query_complete_batch_traceability(copilot_service, seeded_batch_manager):
    b1_id, _ = seeded_batch_manager
    req = ChatRequest(message=f"Is batch {b1_id} ka farmer, quantity, verification status aur complete traceability batao.")
    resp = copilot_service.process_chat(req)
    assert resp.intent in ["batch_traceability", "batch"]
    assert b1_id in resp.answer
    assert "Ashwagandha" in resp.answer
    assert "150" in resp.answer
    assert "F001" in resp.answer or "Ramesh" in resp.answer


# ==============================================================================
# D. Anti-Hallucination & Unknown Query Tests
# ==============================================================================

def test_anti_hallucination_unknown_batch(copilot_service):
    req = ChatRequest(message="Give me details of batch DRAVYA-FAKE-999999")
    resp = copilot_service.process_chat(req)
    assert resp.data.get("found") is False
    assert "not found" in resp.answer.lower() or "nahi mila" in resp.answer.lower()


def test_anti_hallucination_unknown_herb(copilot_service):
    req = ChatRequest(message="How much DragonFruit do we have in inventory?")
    resp = copilot_service.process_chat(req)
    assert resp.data["total_batches"] == 0
    assert "No inventory records found" in resp.answer or "nahi mili" in resp.answer


def test_anti_hallucination_undocumented_topic(copilot_service):
    req = ChatRequest(message="Does Dravya support quantum crypto entanglement mining on Mars?")
    resp = copilot_service.process_chat(req)
    assert "verified information" in resp.answer.lower() or "paryapt jankari" in resp.answer.lower()


# ==============================================================================
# E. Multi-Turn Follow-Up & Context Entity Handling Tests
# ==============================================================================

def test_context_followup_herb(copilot_service):
    sess_id = "test_sess_herb_followup"
    # Turn 1: Ask about herb
    req1 = ChatRequest(message="Tell me about Ashwagandha inventory.", conversation_id=sess_id)
    resp1 = copilot_service.process_chat(req1)
    assert resp1.intent == "herb_summary"
    assert "150" in resp1.answer

    # Turn 2: Follow-up using pronoun "it"
    req2 = ChatRequest(message="How many batches does it have?", conversation_id=sess_id)
    resp2 = copilot_service.process_chat(req2)
    assert resp2.intent in ["herb_batches", "herb_summary"]
    assert "Ashwagandha" in resp2.answer
    assert "1" in resp2.answer


def test_context_followup_batch(copilot_service, seeded_batch_manager):
    b1_id, _ = seeded_batch_manager
    sess_id = "test_sess_batch_followup"

    # Turn 1: Lookup batch
    req1 = ChatRequest(message=f"Show batch {b1_id}", conversation_id=sess_id)
    resp1 = copilot_service.process_chat(req1)
    assert resp1.intent == "batch"

    # Turn 2: Follow-up question asking for farmer
    req2 = ChatRequest(message="Who is the farmer?", conversation_id=sess_id)
    resp2 = copilot_service.process_chat(req2)
    assert resp2.intent == "batch"
    assert "Ramesh Kumar" in resp2.answer or "F001" in resp2.answer

    # Turn 3: Follow-up question asking for verification status
    req3 = ChatRequest(message="What is the verification status?", conversation_id=sess_id)
    resp3 = copilot_service.process_chat(req3)
    assert resp3.intent == "batch"
    assert "status" in resp3.answer.lower() or "AI_PREDICTED" in resp3.answer or "AI_CONFIRMED" in resp3.answer
