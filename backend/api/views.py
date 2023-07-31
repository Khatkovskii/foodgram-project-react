from django.shortcuts import render


from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status, viewsets, mixins

from .serializers import UserCreateSerializer, UserReadSerializer, RecipeSerializer, IngredientSerializer, IngredientAmountSerializer
from users.models import User
from recipes.models import Recipe, Ingredient, IngredientAmount


class UserViewSet(mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet,):
    '''Вьюсет для работы с пользователями'''
    queryset = User.objects.all()
    
    def get_serializer_class(self):
        return UserCreateSerializer
    
    def me(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer