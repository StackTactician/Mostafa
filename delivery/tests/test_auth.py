from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User

class AuthTests(APITestCase):
    def test_registration(self):
        """Test user registration"""
        url = reverse('api_register')
        data = {
            'username': 'newuser',
            'email': 'new@test.com',
            'password': 'password123',
            'role': 'Customer',
            'phone_number': '1234567890'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertEqual(User.objects.get(username='newuser').userprofile.role, 'Customer')

    def test_login(self):
        """Test user login and token retrieval"""
        user = User.objects.create_user(username='testuser', password='password123')
        user.userprofile.role = 'Customer'
        user.userprofile.save()
        
        url = reverse('token_obtain_pair')
        data = {
            'username': 'testuser',
            'password': 'password123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_profile_creation_signal(self):
        """Test that UserProfile is created via signal"""
        user = User.objects.create_user(username='signaluser', password='password123')
        # refresh from db to check if signal created profile
        self.assertTrue(hasattr(user, 'userprofile'))
