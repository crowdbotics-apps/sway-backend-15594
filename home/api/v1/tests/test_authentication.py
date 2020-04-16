"""
Unit tests for User Authentication Signup and Login.
"""
from django.core import mail
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from allauth.account.models import EmailAddress

from rest_framework.test import APIClient
from rest_framework import status

from users.models import User


SIGNUP_URL = reverse('user-list')


class RegistrationTests(TestCase):
    """Test the users registration API"""

    DEFAULT_PAYLOAD = {
        'first_name': 'Aaa',
        'last_name': 'Aaa',
        'email': 'a@a.com',
        'password': 'Password0978',
        're_password': 'Password0978',
    }
    VENDOR_PAYLOAD = {
        'first_name': 'Aaa',
        'last_name': 'Aaa',
        'email': 'a@a.com',
        'password': 'Password0978',
        're_password': 'Password0978',
        'user_type': 'vendor',

    }
    def setUp(self):
        self.client = APIClient()

    def test_create_valid_customer_email_created(self):
        """Test that an EmailAddress instance is created with the signup."""
        res = self.client.post(SIGNUP_URL, self.DEFAULT_PAYLOAD)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        res_email = res.data['email']
        email = EmailAddress.objects.get(email=res_email)
        self.assertEqual(res_email, email.email)

    def test_create_valid_customer_user_success(self):
        """Test creating customer user with valid payload is successful."""
        res = self.client.post(SIGNUP_URL, self.DEFAULT_PAYLOAD)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        res_data = res.data
        user = get_user_model().objects.get(**res_data)
        self.assertEqual(user.user_type, User.TYPE_CUSTOMER)
        self.assertEqual(user.first_name, res_data['first_name'])
        self.assertEqual(user.last_name, res_data['last_name'])
        self.assertTrue(user.check_password(self.DEFAULT_PAYLOAD['password']))
        self.assertNotIn('password', res_data)

    def test_create_valid_customer_email_sent(self):
        """Test creating customer user with email activation."""
        res = self.client.post(SIGNUP_URL, self.DEFAULT_PAYLOAD)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(bool(len(mail.outbox)))

    def test_create_valid_vendor_user_success(self):
        """Test creating vendor user with valid payload is successful."""

        res = self.client.post(SIGNUP_URL, self.VENDOR_PAYLOAD)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(**res.data)
        self.assertEqual(user.user_type, User.TYPE_VENDOR)

        self.assertTrue(user.check_password(self.VENDOR_PAYLOAD['password']))
        self.assertNotIn('password', res.data)

    def test_create_valid_vendor_no_email_sent(self):
        """Test creating vendor user has no email activation."""
        res = self.client.post(SIGNUP_URL, self.VENDOR_PAYLOAD)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertFalse(bool(len(mail.outbox)))
