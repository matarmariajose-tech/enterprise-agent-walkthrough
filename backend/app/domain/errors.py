class AuthorizationError(PermissionError):
    pass


class InsufficientEvidenceError(RuntimeError):
    pass


class PolicyUnavailableError(RuntimeError):
    pass


class IdempotencyConflictError(ValueError):
    pass
