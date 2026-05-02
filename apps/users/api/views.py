from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.services import register_user

from .serializers import UserMeSerializer, UserRegisterSerializer
from apps.common.api_response import success_response, error_response


class UserMeAPIView(APIView):
    def get(self, request):
        return success_response(
            UserMeSerializer(request.user).data,
            message="user detail",
        )

    def patch(self, request):
        serializer = UserMeSerializer(
            request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return success_response(
            serializer.data,
            message="user updated",
        )


class UserRegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = register_user(
            email=serializer.validated_data["email"],
            username=serializer.validated_data["username"],
            full_name=serializer.validated_data["full_name"],
            password=serializer.validated_data["password"],
        )

        return success_response(
            UserMeSerializer(user).data,
            message="user created",
            status=status.HTTP_201_CREATED,
        )