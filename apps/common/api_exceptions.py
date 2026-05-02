from rest_framework.views import exception_handler
from rest_framework.response import Response



from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.http import Http404

from rest_framework import status
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound
from rest_framework.views import exception_handler

from apps.common.api_response import error_response
from apps.common.exceptions import AppError, BusinessRuleViolation, PermissionDeniedError


def custom_exception_handler(exc, context):
    if isinstance(exc, PermissionDeniedError):
        return error_response(
            message=exc.message,
            code="permission_denied",
            status=status.HTTP_403_FORBIDDEN,
        )

    if isinstance(exc, BusinessRuleViolation):
        return error_response(
            message=exc.message,
            code="business_rule_violation",
            status=status.HTTP_400_BAD_REQUEST,
        )

    if isinstance(exc, AppError):
        return error_response(
            message=exc.message,
            code="app_error",
            status=status.HTTP_400_BAD_REQUEST,
        )

    if isinstance(exc, DjangoPermissionDenied):
        return error_response(
            message=str(exc) or "Permission denied",
            code="permission_denied",
            status=status.HTTP_403_FORBIDDEN,
        )

    if isinstance(exc, Http404):
        return error_response(
            message="Not found",
            code="not_found",
            status=status.HTTP_404_NOT_FOUND,
        )

    response = exception_handler(exc, context)

    if response is None:
        return None

    if isinstance(exc, ValidationError):
        return error_response(
            message="Validation error",
            code="validation_error",
            details=response.data,
            status=response.status_code,
        )

    if isinstance(exc, PermissionDenied):
        return error_response(
            message="Permission denied",
            code="permission_denied",
            status=response.status_code,
        )

    if isinstance(exc, NotFound):
        return error_response(
            message="Not found",
            code="not_found",
            status=response.status_code,
        )

    detail = response.data.get("detail", "Error") if isinstance(response.data, dict) else response.data

    return error_response(
        message=str(detail),
        code="error",
        status=response.status_code,
    )


#
# def custom_exception_handler(exc, context):
#     response = exception_handler(exc, context)
#
#     if response is None:
#         return response
#
#     # default DRF error
#     data = {
#         "success": False,
#         "error": {
#             "message": response.data.get("detail", "Error"),
#         }
#     }
#
#     response.data = data
#     return response
#
#
#
#
#
# def success_response(data=None, message="Success", status=200):
#     return Response({
#         "success": True,
#         "message": message,
#         "data": data,
#     }, status=status)