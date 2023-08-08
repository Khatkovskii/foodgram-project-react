from django.shortcuts import render

from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status, viewsets, mixins

from .serializers import UserCreateSerializer, UserReadSerializer, SetPasswordSerializer, RecipeSerializer, IngredientSerializer, IngredientAmountSerializer, TagSerializer, RecipeCreateSerializer, FavoriteSerializer
from .permissions import AdminOrReadOnly, AuthorOrAdminOrReadOnly
from .paginator import LimitedPagination
from users.models import User
from recipes.models import Recipe, Ingredient, IngredientAmount, Tag, Favorite



class UserViewSet(mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet,):
    '''Вьюсет для работы с пользователями'''
    queryset = User.objects.all()
    
    def get_serializer_class(self):
        if self.action in ('me', 'list', 'retrieve'):
            return UserReadSerializer
        if self.action == 'set_password':
            return SetPasswordSerializer
        return UserCreateSerializer
    
    def get_permissions(self):
        if self.action in ['me', 'set_password', 'retrieve']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]
    
    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['POST'],
            permission_classes=[IsAuthenticated])
    def set_password(self, request):
        user = request.user
        data = request.data
        serializer = self.get_serializer(user, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response('Пароль успешно изменен',
                        status=status.HTTP_200_OK)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly,)
    pagination_class = None


class TagViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AuthorOrAdminOrReadOnly,)
    pagination_class = LimitedPagination
    
    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeCreateSerializer
        return RecipeSerializer


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = None