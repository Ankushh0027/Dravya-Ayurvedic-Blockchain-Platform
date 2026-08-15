"""
Exceptions for Dravya AI Assistant domain.
"""


class AssistantError(Exception):
    """Base exception for Dravya AI Assistant."""
    pass


class LLMProviderError(AssistantError):
    """Raised when the LLM provider fails or is unreachable."""
    pass


class ToolExecutionError(AssistantError):
    """Raised when a tool execution fails."""
    pass


class InvalidToolArgumentError(AssistantError):
    """Raised when tool arguments fail validation."""
    pass


class MaxToolCallsExceededError(AssistantError):
    """Raised when tool call count exceeds maximum limit."""
    pass
