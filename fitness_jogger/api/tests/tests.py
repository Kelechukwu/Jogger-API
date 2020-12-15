import datetime

from django.test import TestCase, Client
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from api.models import User, Jog, USER_MANAGER
from unittest.mock import Mock, patch

from api.tests.helpers import MockResponse
from django.utils import timezone

class SignUpTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.super = User.objects.create_superuser(
            'super@test.com', 'password')

    def test_can_create_an_account(self):
        """This verifies that you can successfully create a new account"""
        response = self.client.post(
            reverse('signup'), {'email': 'newUser@test.com', 'password': 'NewPassword'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_cannot_sign_up_using_already_existing_email(self):
        """This verifies that you cannot signup as with a pre-existing email"""
        response = self.client.post(
            reverse('signup'), {'email': 'super@test.com', 'password': 'password'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_sign_up_without_email_and_password_fields(self):
        """This verifies that you cannot signup without providing email
           and password
        """
        response = self.client.post(
            reverse('signup'), {'email': 'super@test.com'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(
            reverse('signup'), {'password': 'password'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PermissionsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            'super@test.com', 'password')
        self.regular_user = User.objects.create_user(
            'regular_user@test.com', 'password1')
        self.manager_user = User.objects.create_user(
            'manager_user@test.com', 'password2')

        self.manager_user.role = USER_MANAGER
        self.manager_user.save()

    def test_regular_user_cannot_CRUD_other_users_information(self):
        """This verifies that a regular user cannot see other users data"""

        # Read
        refresh = RefreshToken.for_user(self.regular_user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = self.client.get('/users')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Update
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = self.client.put(
            f'/users/{self.manager_user.id}', {'email': 'manager_user@test.com', 'password': 'password2'})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Delete
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = self.client.delete(f'/users/{self.manager_user.id}')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_user_can_CRUD_other_users_information(self):
        """This verifies that a regular user cannot see other users data"""

        # Read
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = self.client.get('/users')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Update
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = self.client.put(
            f'/users/{self.regular_user.id}', {'email': 'regular_user@test.com', 'password': 'password2'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Delete
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = self.client.delete(f'/users/{self.regular_user.id}')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_manager_user_can_CRUD_other_users_information(self):
        """This verifies that a regular user cannot see other users data"""

        # Read
        refresh = RefreshToken.for_user(self.manager_user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = self.client.get('/users')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Update
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = self.client.put(
            f'/users/{self.regular_user.id}', {'email': 'regular_user@test.com', 'password': 'password2'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Delete
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = self.client.delete(f'/users/{self.regular_user.id}')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_regular_user_can_CRUD_personal_information(self):
        """This verifies that a regular user can CRUD personal profile"""

        refresh = RefreshToken.for_user(self.regular_user)

        # Update
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = self.client.put(
            f'/users/{self.regular_user.id}', {'email': 'regular_user@test.com', 'role': 3, 'is_active': True})

        self.assertEqual(response.status_code, status.HTTP_200_OK)


        # Read
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = self.client.get(f'/users/{self.regular_user.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Delete
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = self.client.delete(f'/users/{self.regular_user.id}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class JogsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            'super@test.com', 'password')
        self.regular_user = User.objects.create_user(
            'regular_user@test.com', 'password1')
        self.regular_user2 = User.objects.create_user(
            'regular_user2@test.com', 'password1')


    @patch('requests.get')
    def test_regular_user_can_CRUD_personal_jogging_data(self, mock_get):
        """This verifies that a regular user can only CRUD personal data"""

        mock_get.return_value =   MockResponse({'weather': 'conditions'}, 200)
        
        refresh = RefreshToken.for_user(self.regular_user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        # Create  
        response = self.client.post(
            '/myjogs', {'time': 9, 'location': 'POINT(3 4)', 'distance': 300})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


        saved_jog = response.json()

        saved_jog["distance"] = 450
        del saved_jog["weather"]

        # Update
        response = self.client.put(
            f'/myjogs/{saved_jog["id"]}', { **saved_jog })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # read
        response = self.client.get('/myjogs')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 1)

        # delete
        response = self.client.delete(f'/myjogs/{saved_jog["id"]}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


    @patch('requests.get')
    def test_regular_user_cannot_CRUD_other_users_jogging_data(self, mock_get):
        """This verifies that a regular user can only CRUD personal data"""

        mock_get.return_value =   MockResponse({'weather': 'conditions'}, 200)
        
        refresh = RefreshToken.for_user(self.regular_user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        # Create  
        response = self.client.post(
            '/myjogs', {'time': 9, 'location': 'POINT(3 4)', 'distance': 300})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


        saved_jog = response.json()

        saved_jog["distance"] = 450
        del saved_jog["weather"]


        # switch to another user
        refresh = RefreshToken.for_user(self.regular_user2)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        # Update using /myjogs
        response = self.client.put(
            f'/myjogs/{saved_jog["id"]}', { **saved_jog })
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Update /jogs
        response = self.client.put(
            f'/jogs/{saved_jog["id"]}', { **saved_jog })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


        # delete using /myjogs
        response = self.client.delete(f'/myjogs/{saved_jog["id"]}')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # delete using /jogs
        response = self.client.delete(f'/jogs/{saved_jog["id"]}')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    @patch('requests.get')
    def test_admin_user_can_CRUD_users_jogging_data(self, mock_get):
        """This verifies that a regular user can only CRUD personal data"""

        mock_get.return_value =   MockResponse({'weather': 'conditions'}, 200)
        
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        # Create  
        response = self.client.post(
            '/jogs', {'time': 9, 'location': 'POINT(3 4)', 'distance': 300, 'user': self.regular_user.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        saved_jog = response.json()
        saved_jog["distance"] = 450
        del saved_jog["weather"]

        # Update
        response = self.client.put(
            f'/jogs/{saved_jog["id"]}', { **saved_jog })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # read
        response = self.client.get('/jogs')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 1)

        # delete
        response = self.client.delete(f'/jogs/{saved_jog["id"]}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class URLQueryTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            'super@test.com', 'password')
        self.regular_user = User.objects.create_user(
            'regular_user@test.com', 'password1')
        self.regular_user2 = User.objects.create_user(
            'regular_user2@test.com', 'password1')
    
    def test_url_query_works(self):
        query_string =  "(role ne 3)"

        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = self.client.get('/users',{'q':query_string })

        self.assertEqual(response.json()["count"], 1)

class WeeklyReportTestCase(TestCase):
    @patch('requests.get')
    def setUp(self, mock_get):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            'super@test.com', 'password')
        self.regular_user = User.objects.create_user(
            'regular_user@test.com', 'password1')
        self.regular_user2 = User.objects.create_user(
            'regular_user2@test.com', 'password1')
        
        today = timezone.now()
        self.last_week = today - datetime.timedelta(days=8) 

        mock_get.return_value =   MockResponse({'weather': 'conditions'}, 200)

        Jog.objects.create(date=timezone.now(), distance=5, time=100, location="POINT(2 3)", user=self.regular_user)
        jog2 = Jog.objects.create(distance=2, time=50, location="POINT(2 3)", user=self.regular_user)
        jog3 = Jog.objects.create(distance=3, time=50, location="POINT(2 3)", user=self.regular_user)

        jog2.date = self.last_week
        jog3.date = self.last_week

        jog2.save()
        jog3.save()

    def test_weekly_report_returns_accurate_results(self):
        refresh = RefreshToken.for_user(self.regular_user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = self.client.get(f'/weekly_report/{self.regular_user.id}')

        expected = {'average_speed': 0.05, 'average_distance': 5.0}

        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json['average_speed'], expected['average_speed'])
        self.assertEqual(response_json['average_distance'], expected['average_distance'])


    def test_admin_can_view_weekly_report_of_users(self):
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = self.client.get(f'/weekly_report/{self.regular_user.id}', {'date': self.last_week.strftime("%Y-%m-%d")})

        expected = {'average_speed': 0.05, 'average_distance': 2.5}

        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json['average_speed'], expected['average_speed'])
        self.assertEqual(response_json['average_distance'], expected['average_distance'])

    def test_regular_user_cannot_view_weekly_report_of_other_users(self):
        refresh = RefreshToken.for_user(self.regular_user2)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = self.client.get(f'/weekly_report/{self.regular_user.id}', {'date': self.last_week.strftime("%Y-%m-%d")})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
