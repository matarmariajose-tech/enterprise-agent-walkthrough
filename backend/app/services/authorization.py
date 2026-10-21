from app.domain.errors import AuthorizationError
from app.domain.models import ExecutionContext, Permission, Region


class AuthorizationService:
    @staticmethod
    def require(context: ExecutionContext, permission: Permission) -> None:
        if permission not in context.permissions:
            raise AuthorizationError(f"Missing required permission: {permission}")

    @staticmethod
    def require_region(context: ExecutionContext, region: Region) -> None:
        if region not in context.allowed_regions:
            raise AuthorizationError("Region is outside the authorized scope")
