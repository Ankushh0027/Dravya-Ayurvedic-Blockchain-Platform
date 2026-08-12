"""
Domain-specific exceptions for Dravya AI Engine Batch Management.
"""

class BatchException(Exception):
    """Base exception class for all batch domain errors."""
    pass


class InvalidQuantityError(BatchException):
    """Raised when quantity is non-positive or unit is unsupported."""
    pass


class UnknownHerbError(BatchException):
    """Raised when an unrecognized herb species is supplied or queried."""
    pass


class InvalidBatchError(BatchException):
    """Raised when batch payload metadata fail validation."""
    pass


class BatchNotFoundError(BatchException):
    """Raised when a requested batch_id does not exist."""
    pass


class LowConfidencePredictionError(BatchException):
    """Raised when an AI prediction confidence falls below mandatory minimum."""
    pass


class DuplicateBatchError(BatchException):
    """Raised when attempting to register a batch with an already existing ID."""
    pass
