from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag , Ingredient, Recipe
from recipe import serializers

class BaseRecepieAttrViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):

    """base viewset for user owned recipe atrs."""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """return objects for curent auth. use ronly"""

        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """create new object"""
        serializer.save(user=self.request.user)

class TagViewSets(BaseRecepieAttrViewSet):
    """manage tags in the database"""

    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer



class IngredientViewSet(BaseRecepieAttrViewSet):


    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer

class RecipeViewSet(viewsets.ModelViewSet):
    """manage recipe in data base"""

    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """retrive the recipe for the aut. user"""

        return self.queryset.filter(user=self.request.user)
    def get_serializer_class(self):
        """return apropriate serializer class"""
        if self.action=='retrieve':
            return serializers.RecipeDetailSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """create new recipe"""
        serializer.save(user = self.request.user)



