from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL=reverse('recipe:recipe-list')

def detail_url(recipe_id):
    """return recipe detail url"""
    return reverse('recipe:recipe-detail', args=[recipe_id])

def sample_tag(user, name='main course'):
    """create and return sample tag"""
    return Tag.objects.create ( user=user, name=name)

def sample_ingredient(user, name='poriluk'):
    """create ang return sample ingredients"""
    return Ingredient.objects.create(user = user, name=name)


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

    def test_view_recipe_detail(self):
        """test viewing recipe detail"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)

        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.data, serializer.data)

    def test_create_recipe_api(self):
        """test creating recipe"""
        payload={
            'title':'ckokoladni kolac',
            'time_minutes': 60,
            'price': 50,
        }
        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """creating recipe with tags"""
        tag1 = sample_tag(user=self.user, name='vegan')
        tag2 = sample_tag(user=self.user, name='dezert')

        payload = {
            'title':'kolac sa sitrom',
            'tags':[tag1.id, tag2.id],
            'time_minutes':60,
            'price':40
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """test creating recipe with ingredients"""
        ingredient1 = sample_ingredient(user=self.user, name='kupus')
        ingredient2 = sample_ingredient(user=self.user, name='mrkva')

        payload = {
            'title':'muckalica',
            'ingredients':[ingredient1.id, ingredient2.id],
            'time_minutes':90,
            'price':40
        }
        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()

        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient2, ingredients)
        self.assertIn(ingredient1, ingredients)


    def test_partial_update_recipe(self):
        """test updating recipe with patch """

        recipe=sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        new_tag= sample_tag(user=self.user, name='cili')
        payload={
            'title':'piletina', 'tags':[new_tag.id]
        }
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_recipe(self):
        """test updating recipe with put"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        payload={
            'title':"bolonjeze",
            'time_minutes':25,
            'price':5.00
        }
        url = detail_url(recipe.id)
        self.client.put(url, payload)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(recipe.price, payload['price'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)