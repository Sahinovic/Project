from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL= reverse('user:create')
TOKEN_URL=reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**param):
    return get_user_model().objects.create_user(**param)

class PublicUserApiTests(TestCase):
    """test user api public """
    def setUp(self):
        self.client=APIClient()

    def test_create_valid_user_success(self):
        """test creating user with valid payload """
        payload = {
            'email':'mirza@gamil.com',
            'password':'test12345',
            'name':'test name'
        }
        res = self.client.post(CREATE_USER_URL,payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """test creating user that already exists"""
        payload = {'email':'mirza@gamil.com',
            'password':'test12345'}
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_shor(self):
        """Test that password is too short"""
        payload = {'email': 'mirza@gamil.com',
                   'password': 'tes',
                   'name': 'test'}


        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']).exists()
        self.assertFalse(user_exists)

    def test_crate_token_for_user(self):
        """test that token is created for user"""
        payload={'email': 'mirza@gamil.com',
                   'password': 'tes'}
        create_user(**payload)

        res=self.client.post(TOKEN_URL, payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """test that token is not created if invalid credentials are given"""

        create_user(email='test@gmail.com', password="testpassss")
        payload = {'email' :'test1234@test.com', 'password' :'wrong'}

        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        '''Test that token is not created if user dos not exist'''
        payload = {'email' :'test1234@test.com', 'password' :'wrong'}
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_fied(self):
        """test that email and pass are requried"""
        res = self.client.post(TOKEN_URL, {'email':'one', 'password':''})

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrive_user_unautherised(self):
        """test that auth is required for user"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivatUserApiTests(TestCase):
    """test api request thtat required auth."""

    def setUp(self):
        self.user = create_user(
            email= 'test@gmail.com',
            password='test123456',
            name='test',
        )

        self.client=APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrive_profile_succ(self):
        """test retrive profile for logged in user"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name':self.user.name,
            'email':self.user.email,
        })

    def test_post_me_not_allowed(self):
        """test that post in not alloved on the me url"""

        res=self.client.post(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for authenticated user"""
        payload = {'name': 'new name', 'password': 'newpassword123'}

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)