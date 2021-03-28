from django.contrib.auth import authenticate, login, logout
from django.db.transaction import atomic
import json

# Create your views here.
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User, Group
from rest_framework.views import APIView

from tiporagphy_users import redis_pi
from tiporagphy_users.permissions import CheckAccessPermission
from tiporagphy_users.serializers import (
    UserCreationSerializer,
    AuthenticateUserSerializer,
    UserInGroupSerializer,
    UserManagementSerializer,
)


class CreateUserView(CreateAPIView):
    queryset = User.objects
    serializer_class = UserCreationSerializer

    def perform_create(self, serializer):
        serializer.create(serializer.validated_data)
        groups = serializer.validated_data["profile"]["group"]
        redis_pi.set(
            name=serializer.validated_data["username"],
            value=json.dumps({"groups": [gr.name for gr in groups]}),
            ex=10,
        )

    @atomic
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class LoginPlatformView(APIView):
    serializer_class = AuthenticateUserSerializer

    queryset = User.objects

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        content = dict(status_logged=True)
        if request.user.is_authenticated:
            return Response(data=content, status=status.HTTP_200_OK)
        user = authenticate(request, **serializer.validated_data)
        if user:
            login(request, user)
            return Response(data=content, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutPlatformView(APIView):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logout(request)
        return Response(data=dict(status_logged=False), status=status.HTTP_200_OK)


class CheckUserInGroup(APIView):
    serializer_class = UserInGroupSerializer
    permission_classes = [CheckAccessPermission]
    groups_check_list = [Group.objects.all().values_list("name", flat=True)]

    def redis_check(self, serializer):
        if is_cached := redis_pi.get(name=serializer.validated_data["username"]):
            groups = json.loads(is_cached)["groups"]
            return groups

    def get_serializer_context(self):
        return {"request": self.request, "format": self.format_kwarg, "view": self}

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        groups = self.redis_check(serializer)
        if not groups:
            # serializer.validated_data["username"] - request.user.id . e.p 3 or 4
            groups = Group.objects.filter(
                user=serializer.validated_data["username"]
            ).values_list("name", flat=True)
            redis_pi.set(
                name=serializer.validated_data["username"],
                value=json.dumps({"groups": list(groups)}),
                ex=100,
            )
        return Response(
            data=dict(status="OK", groups=[groups]), status=status.HTTP_200_OK
        )


class UserManagementView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserManagementSerializer
    queryset = User.objects

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        """validate cache here"""
        redis_pi.delete(instance.id)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        """validate cache here"""
        redis_pi.delete(instance.id)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
