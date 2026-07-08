class AIPlatformError(Exception):
    """Base exception for the platform."""


class ValidationError(AIPlatformError):
    """Raised when input is invalid."""


class ProviderError(AIPlatformError):
    """Raised when an LLM provider fails."""


class DatabaseConnectionError(AIPlatformError):
    """Raised when a database connector cannot connect."""
