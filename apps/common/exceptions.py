class AppError(Exception):
    default_message = "Application error"

    def __init__(self, message=None):
        self.message = message or self.default_message
        super().__init__(self.message)


class BusinessRuleViolation(AppError):
    default_message = "Business rule violated"


class PermissionDeniedError(AppError):
    default_message = "Permission denied"


class ObjectNotFoundError(AppError):
    default_message = "Object not found"