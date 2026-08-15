"""
FastAPI Route for Dravya AI Assistant Chat Endpoint.
"""
from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import get_assistant_service_dependency
from src.assistant.schemas import ChatRequest, ChatResponse
from src.assistant.service import AssistantService

router = APIRouter(tags=["Dravya AI Assistant"])


@router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask Dravya AI Assistant a natural language question",
    description=(
        "Processes user queries in English, Hindi, or Hinglish regarding herb inventory, "
        "batches, farmer contributions, quality verification, and blockchain traceability payloads. "
        "Executes deterministic backend tools without LLM hallucinations."
    ),
)
async def chat_endpoint(
    request: ChatRequest,
    service: AssistantService = Depends(get_assistant_service_dependency),
) -> ChatResponse:
    """
    Executes natural-language assistant query and returns structured response.
    """
    try:
        return service.process_chat(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        import logging
        logging.exception(f"Error processing chat request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the chat request.",
        )
