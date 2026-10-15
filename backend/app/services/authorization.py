from app.domain.errors import AuthorizationError
from app.domain.models import ExecutionContext, Permission


class AuthorizationService:
    @staticmethod
    def require(context: ExecutionContext, permission: Permission) -> None:
        if permission not in context.permissions:
            raise AuthorizationError(f"Missing required permission: {permission}")
