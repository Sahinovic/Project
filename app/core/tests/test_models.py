from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import UserManager
from core import models

def sample_user(email='test@gmail.com', password="test1234"):
    """create sample user """
    return get_user_model().objects.create_user(email,password)
class ModelTests(TestCase):

    def test_create_user_with_email_successefull(self):

        """test creating ne user with email"""
        email = 'test@gmail.com'
        password = "Testpass123"
        user = get_user_model().objects.create_user(
            email=email,
            password = password
        )
        self.assertEqual(user.email , email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalize(self):
        """test email if new user is normalize"""

        email = 'test@GMAIL.com'
        user = get_user_model().objects.create_user(email, 'test123')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """test creating new user with no email raises eror"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_create_new_super_user(self):
        """test creating new super user"""

        user = get_user_model().objects.create_superuser(
            'test@gmail.com',
            'test123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """test tag string representatiom"""

        tag = models.Tag.objects.create(
            user = sample_user(),
            name='vegan'
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingredients_str(self):
        """test the ing. string"""

        ingrediendt = models.Ingredient.objects.create(
            user = sample_user(),
            name = 'kupus'

        )
        self.assertEqual(str(ingrediendt),ingrediendt.name)

    def test_reciper_str(self):
        """test the recipe str repr"""

        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title = 'Kupus sa lukom',
            time_minutes = 5,
            price=5.00
        )
        self.assertEqual(str(recipe),recipe.title)