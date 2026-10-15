class AuthorizationError(PermissionError):
    """Raised when the execution context lacks a required permission."""


class InsufficientEvidenceError(RuntimeError):
    """Raised when a conclusion cannot be supported by retrieved evidence."""


class PolicyUnavailableError(RuntimeError):
    """Raised when a write policy cannot be evaluated safely."""
