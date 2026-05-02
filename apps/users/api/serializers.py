from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserMeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "full_name",
            "avatar",
            "is_active",
        )
        read_only_fields = ("id", "email", "is_active")


class UserRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField(max_length=150)
    full_name = serializers.CharField(max_length=255)
    password = serializers.CharField(write_only=True, min_length=8)