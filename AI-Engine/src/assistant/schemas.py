"""
Pydantic schemas for Dravya AI Assistant chat API and tool calling.
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    """Input payload for POST /chat endpoint."""

    message: str = Field(
        ...,
        description="Natural language user query in English, Hindi, or Hinglish.",
        min_length=1,
        max_length=1000,
        examples=["Ashwagandha ki total quantity kitni hai?"],
    )
    conversation_id: Optional[str] = Field(
        default=None,
        description="Optional tracking identifier for multi-turn conversation sessions.",
    )

    @field_validator("message")
    @classmethod
    def validate_message_not_empty(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Chat message cannot be empty or whitespace only.")
        return cleaned


class ChatResponse(BaseModel):
    """Response payload returned by POST /chat endpoint."""

    answer: str = Field(
        ...,
        description="Natural language answer synthesized by Dravya AI Assistant.",
    )
    intent: str = Field(
        ...,
        description="Detected or resolved user intent classification.",
        examples=["herb_summary", "farmer_summary", "batch_lookup", "inventory_summary"],
    )
    data: Optional[Any] = Field(
        default=None,
        description="Structured data retrieved from backend APIs/tools (if applicable).",
    )
    tool_used: Optional[str] = Field(
        default=None,
        description="Name of the deterministic tool executed to fetch structured data.",
    )


class ToolCall(BaseModel):
    """Represents a tool call selected by LLM or intent parser."""

    name: str = Field(..., description="Name of tool to execute.")
    arguments: Dict[str, Any] = Field(
        default_factory=dict,
        description="Keyword arguments for the tool execution.",
    )


class ToolDefinition(BaseModel):
    """OpenAI / generic tool declaration model."""

    name: str
    description: str
    parameters: Dict[str, Any]
