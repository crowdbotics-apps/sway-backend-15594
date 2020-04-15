"""
Unit tests for API Serializers.
"""
from rest_framework.test import APIRequestFactory
from rest_framework.test import APITestCase

from home.api.v1.serializers import CreateUserSerializer

from users.models import User


class CreateUserSerializerTests(APITestCase):

    PAYLOAD = {
        'first_name': 'Aaa',
        'last_name': 'Aaa',
        'email': 'a@a.com',
        'password': 'Password0978',
        're_password': 'Password0978',
    }

    def setUp(self):
        self.request = APIRequestFactory().get('/')
        self.request.session = {}

    def test_valid_payload_success(self):
        """Tests that the serializer validates the data passed."""
        serializer = CreateUserSerializer(data=self.PAYLOAD)
        self.assertTrue(serializer.is_valid())

    def test_invalid_payload_fail(self):
        """Tests that the serializer validates the data passed."""
        serializer = CreateUserSerializer(data=self.PAYLOAD)
        self.assertTrue(serializer.is_valid())

    def test_user_customer_created(self):
        """Tests that the `customer` user is created."""
        self.PAYLOAD.update({
            'user_type': User.TYPE_CUSTOMER,
        })
        serializer = CreateUserSerializer(data=self.PAYLOAD,
                        context={'request': self.request})
        self.assertTrue(serializer.is_valid())
        serializer.save()
        user = User.objects.get(email=self.PAYLOAD['email'])
        self.assertEqual(user.user_type, self.PAYLOAD['user_type'])

    def test_user_vendor_created(self):
        """Tests that the `vendor` user is created."""
        self.PAYLOAD.update({
            'user_type': User.TYPE_VENDOR,
        })
        serializer = CreateUserSerializer(data=self.PAYLOAD,
                        context={'request': self.request})
        self.assertTrue(serializer.is_valid())
        serializer.save()
        user = User.objects.get(email=self.PAYLOAD['email'])
        self.assertEqual(user.user_type, self.PAYLOAD['user_type'])
