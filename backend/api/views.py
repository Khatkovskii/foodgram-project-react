from django.shortcuts import get_object_or_404
from django.db.models import F, Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status, viewsets, mixins

from .serializers import UserCreateSerializer, UserReadSerializer, SetPasswordSerializer, RecipeSerializer, IngredientSerializer, IngredientAmountSerializer, TagSerializer, RecipeCreateSerializer, FavoriteSerializer, RecipeMiniSerializer, CartSerializer, FollowAuthorSerializer
from .permissions import AdminOrReadOnly, AuthorOrAdminOrReadOnly
from .paginator import LimitedPagination
from .filters import RecipeFilterSet
from users.models import User, Follow
from recipes.models import Recipe, Ingredient, IngredientAmount, Tag, Favorite, Cart



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
        if self.action in ['me', 'set_password', 'retrieve', 'subscribe', 'subscriptions']:
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

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, pk):
        '''Подписка/отписка на автора'''
        author = get_object_or_404(User, id=pk)
        if request.method == 'POST':
            serializer = FollowAuthorSerializer(author, data=request.data,
                                                context={'request': request,
                                                         'author': author})
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=request.user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        get_object_or_404(Follow, user=request.user, author=author).delete()
        return Response('Вы отписались', status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        pass


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
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilterSet
    filterset_class = RecipeFilterSet
    
    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeCreateSerializer
        if self.action in ('favorite', 'shopping_cart'):
            return RecipeMiniSerializer
        return RecipeSerializer
    
    def get_queryset(self):
        user_id = self.request.user.pk
        return Recipe.objects.add_annotations(user_id)
    
    @action(
        detail=True,
        methods=['POST'],
        permission_classes=[AuthorOrAdminOrReadOnly,]
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        data = {
            'user': request.user.pk,
            'recipe': recipe.pk
        }
        serializer = FavoriteSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer = self.get_serializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @favorite.mapping.delete
    def favorite_delete(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        Favorite.objects.filter(user=request.user, recipe=recipe).delete()
        return Response('Рецепт успешно удален', status=status.HTTP_204_NO_CONTENT)
    
    @action(
        detail=True,
        methods=['POST'],
        permission_classes=[AuthorOrAdminOrReadOnly,]
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        data = {
            'user': request.user.pk,
            'recipe': recipe.pk
        }
        serializer = CartSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer = self.get_serializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @shopping_cart.mapping.delete
    def cart_delete(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        Cart.objects.filter(user=request.user, recipe=recipe).delete()
        return Response ('Рецепт успешно удален', status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        ingredients = IngredientAmount.objects.filter(
            recipe__cart__user=request.user).values(
            name=F('ingredient__name'),
            measurement_unit=F('ingredient__measurement_unit')).annotate(
            amount=Sum('amount')
        )
        shopping_list = []
        for ingr in ingredients:
            shopping_list.append(
                f'{ingr["name"]} '
                f'{ingr["amount"]} '
                f'{ingr["measurement_unit"]}'
            )
        shopping_list_text = f'Список покупок {self.request.user}:\n\n' + '\n'.join(shopping_list)
        filename = f'{self.request.user}_shopping_list.txt'
        request = HttpResponse(shopping_list_text, content_type='text/plain')
        request['Content-Disposition'] = f'attachment; filename={filename}'
        return request