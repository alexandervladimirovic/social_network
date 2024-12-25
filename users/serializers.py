from typing import Any

from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для представления данных пользователя.
    """

    class Meta:
        model = CustomUser
        fields = ("id", "username", "email", "avatar", "bio")


class RegisterSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации нового пользователя.
    """

    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ("username", "email", "password", "password2")

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:

        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(_("Passwords do not match"))

        if CustomUser.objects.filter(username=attrs["username"]).exists():
            raise serializers.ValidationError(_("The username is already in use"))

        if CustomUser.objects.filter(email=attrs["email"]).exists():
            raise serializers.ValidationError(_("The email address is already in use"))

        return attrs

    def create(self, validated_data: dict[str, Any]) -> CustomUser:
        """
        Создает нового пользователя.
        """
        validated_data.pop("password2")

        user = CustomUser.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )

        return user


class TokenObtainPairSerializer(serializers.Serializer):
    """
    Сериализатор для получения JWT токенов (доступ и обновление).
    """

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs: dict[str, Any]) -> dict[str, str]:
        user = authenticate(username=attrs["username"], password=attrs["password"])

        if user is None or not user.is_active:
            raise serializers.ValidationError(_("Invalid username or password"))


        refresh = RefreshToken.for_user(user)

        return {
            "access": str(refresh.access_token),  # type: ignore[attr-defined]
            "refresh": str(refresh),
        }

    def create(self, validated_data: dict[str, Any]) -> None:
        pass

    def update(self, instance: Any, validated_data: dict[str, Any]) -> None:
        pass
