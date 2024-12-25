from typing import Any

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework import generics
from rest_framework.request import Request
from rest_framework.throttling import UserRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    CustomUserSerializer,
    RegisterSerializer,
    TokenObtainPairSerializer
)


class RegisterView(APIView):
    """
    View для регистрации пользователей
    """
    throttle_classes = [UserRateThrottle]  # settings

    def post(self, request: Request) -> Response:

        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            refresh = RefreshToken.for_user(user)
            data: dict[str, Any] = {
                'user': serializer.data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),  # type: ignore[attr-defined]
            }

            return Response(data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenObtainPairView(APIView):
    """
    View для получения токена
    """
    def post(self, request: Request) -> Response:

        serializer = TokenObtainPairSerializer(data=request.data)

        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomUserProfileView(generics.RetrieveAPIView):
    """
    View для получения информации о пользователе
    """
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
