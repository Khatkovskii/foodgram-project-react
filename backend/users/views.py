from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from .models import Follow
from .serializers import (
    FollowAuthorSerializer,
    FollowListSerializer,
    UserCreateSerializer,
    UserReadSerializer,
    SetPasswordSerializer

)

User = get_user_model()


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """Вьюсет для работы с пользователями"""

    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action in ("me", "list", "retrieve"):
            return UserReadSerializer
        if self.action == "set_password":
            return SetPasswordSerializer
        return UserCreateSerializer

    def get_permissions(self):
        if self.action in [
            "me",
            "set_password",
            "retrieve",
            "subscribe",
            "subscriptions",
        ]:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    @action(
        detail=False, methods=["GET"], permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False, methods=["POST"], permission_classes=[IsAuthenticated]
    )
    def set_password(self, request):
        user = request.user
        data = request.data
        serializer = self.get_serializer(user, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response("Пароль успешно изменен", status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, pk):
        """Подписка/отписка на автора"""
        author = get_object_or_404(User, id=pk)
        if request.method == "POST":
            serializer = FollowAuthorSerializer(
                author,
                data=request.data,
                context={"request": request, "author": author},
            )
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=request.user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        get_object_or_404(Follow, user=request.user, author=author).delete()
        return Response("Вы отписались", status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False, methods=["GET"], permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        """Вывод списка подписок"""
        queryset = User.objects.filter(following__user=request.user)
        pagin = self.paginate_queryset(queryset)
        serializer = FollowListSerializer(
            pagin, context={"request": request}, many=True
        )
        return self.get_paginated_response(serializer.data)
