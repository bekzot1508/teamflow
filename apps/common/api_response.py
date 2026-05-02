from rest_framework.response import Response


def success_response(data=None, message="Success", status=200):
    return Response(
        {
            "success": True,
            "message": message,
            "data": data,
        },
        status=status,
    )


def error_response(message="Error", code="error", details=None, status=400):
    return Response(
        {
            "success": False,
            "error": {
                "code": code,
                "message": message,
                "details": details or {},
            },
        },
        status=status,
    )