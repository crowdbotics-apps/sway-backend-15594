"""
Unit tests for API Serializers.
"""
from rest_framework.test import APIRequestFactory
from rest_framework.test import APITestCase

from phonenumber_field.serializerfields import PhoneNumberField

from ..serializers import (
    CreateUserSerializer,
    CreateVendorUserSerializer
)
from ..models import User


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
        """Tests that the serializer validates the data fails."""
        serializer = CreateUserSerializer(data=self.PAYLOAD)
        self.assertTrue(serializer.is_valid())

    def test_user_customer_created(self):
        """Tests that the `customer` user is created."""
        payload = self.PAYLOAD.copy()
        payload.update({
            'user_type': User.TYPE_CUSTOMER,
        })
        serializer = CreateUserSerializer(data=payload,
                        context={'request': self.request})
        self.assertTrue(serializer.is_valid())
        serializer.save()
        user = User.objects.get(email=payload['email'])
        self.assertEqual(user.user_type, payload['user_type'])

    def test_user_vendor_created(self):
        """Tests that the `vendor` user is created."""
        payload = self.PAYLOAD.copy()
        payload.update({
            'user_type': User.TYPE_VENDOR,
        })
        serializer = CreateUserSerializer(data=payload,
                        context={'request': self.request})
        self.assertTrue(serializer.is_valid())
        serializer.save()
        user = User.objects.get(email=payload['email'])
        self.assertEqual(user.user_type, payload['user_type'])

    def test_invalid_email_blank(self):
        """
        Tests that no email data on serializer. Asserts that `blank`
        email is not allowed.
        """
        email_field = 'email'
        payload = self.PAYLOAD.copy()
        payload.update({
            email_field: '',
        })
        serializer = CreateUserSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        email_errors = serializer.errors[email_field]
        self.assertEqual(len(email_errors), 1)
        # Assert email may not be blank
        self.assertEqual(str(email_errors[0]),
            serializer.fields[email_field].error_messages['blank'])

    def test_invalid_email_null(self):
        """
        Tests that no email data on serializer. Asserts that `null`
        email is not allowed.
        """
        email_field = 'email'
        payload = self.PAYLOAD.copy()
        payload.update({
            email_field: None,
        })
        serializer = CreateUserSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        email_errors = serializer.errors[email_field]
        self.assertEqual(len(email_errors), 1)
        # Assert email may not be null
        self.assertEqual(str(email_errors[0]),
            serializer.fields[email_field].error_messages['null'])

    def test_allowed_empty_fields(self):
        """Tests allowed empty fields."""
        payload = self.PAYLOAD.copy()
        payload.update({
            'first_name': '',
            'last_name': '',
        })
        serializer = CreateUserSerializer(data=payload)
        self.assertTrue(serializer.is_valid())

    def test_password_field(self):
        """Tests for password field."""
        password_field = 'password'
        payload = self.PAYLOAD.copy()
        # Test password is required.
        payload.update({
            password_field: '',
        })
        serializer = CreateUserSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        password_errors = serializer.errors[password_field]
        self.assertEqual(len(password_errors), 1)
        self.assertEqual(str(password_errors[0]),
            serializer.fields[password_field].error_messages['blank'])
        # Test password and re_password should match.
        payload.update({
            'password': 'Password0978',
            're_password': 'Password7809',
        })
        serializer = CreateUserSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertEqual('password_mismatch',
            serializer.errors['non_field_errors'].pop().code)


class CreateVendorUserSerializerTests(APITestCase):

    PAYLOAD = {
        'first_name': 'Aaa',
        'last_name': 'Aaa',
        'email': 'a@a.com',
        'country_code': '+48',
        'phone_number': '123456789',
        'address': 'Aaa',
        'business_name': 'Aaa',
        'password': 'Password0978',
        're_password': 'Password0978',
    }

    def setUp(self):
        self.request = APIRequestFactory().get('/')
        self.request.session = {}

    def test_valid_payload_success(self):
        """Tests that the serializer with valid data."""
        payload = self.PAYLOAD.copy()
        serializer = CreateVendorUserSerializer(data=self.PAYLOAD)
        self.assertTrue(serializer.is_valid())

    def test_country_code_errors(self):
        """Tests that invalid `country_code` validates the `phone_number`."""
        country_code = 'country_code'
        payload = self.PAYLOAD.copy()
        payload.update({
            country_code: '1',
        })
        serializer = CreateVendorUserSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        phone_errors = serializer.errors['phone_number']
        self.assertEqual(len(phone_errors), 1)
        self.assertEqual(str(phone_errors[0]),
            PhoneNumberField.default_error_messages['invalid'])

    def test_phone_number_errors(self):
        """Tests that phone_number field errors."""
        phone_field = 'phone_number'
        payload = self.PAYLOAD.copy()
        payload.update({
            phone_field: None,
        })
        serializer = CreateVendorUserSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        phone_errors = serializer.errors[phone_field]
        self.assertEqual(len(phone_errors), 1)
        self.assertEqual(str(phone_errors[0]),
            serializer.fields[phone_field].error_messages['null'])

        payload = self.PAYLOAD.copy()
        payload.update({
            phone_field: '1',
        })
        serializer = CreateVendorUserSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        phone_errors = serializer.errors[phone_field]
        self.assertEqual(len(phone_errors), 1)
        self.assertEqual(str(phone_errors[0]),
            PhoneNumberField.default_error_messages['invalid'])
