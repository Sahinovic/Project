from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe
from recipe.serializers import RecipeSerializer

RECIPES_URL=reverse('recipe:recipe-list')

def sample_recipe(user, **params):
    """create and return sample recipe"""
    defaults = {
        'title':'sample recipe',
        'time_minutes':10,
        'price':5
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)

class PublicRecipeApiTests(TestCase):
    """test unauth. reciper API access"""
    def setUp(self):
        self.client=APIClient()

    def test_auth_required(self):
        """test auth. is required"""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)

class PrivatRecipeApiTests(TestCase):
    """test unauth. recipe Api access"""
    def setUp(self):
        self.client=APIClient()
        self.user = get_user_model().objects.create_user(
            'test@gmail.com',
            'test1234'
        )
        self.client.force_authenticate(self.user)


    def test_retrive_recipe(self):
        """test retrivinig a list of recipe"""
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res =self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')

        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_reciper_limited_to_user(self):
        """test retriving recipe for user"""

        user2 = get_user_model().objects.create_user(
            'mirza@gmail.com',
            "testtesttest"
        )
        sample_recipe(user = user2)
        sample_recipe(user = self.user)
        res = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.filter(user = self.user)

        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)