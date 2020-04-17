import phonenumbers

from django.conf import settings

from allauth.account.utils import setup_user_email
from authy.api import AuthyApiClient

from djoser.conf import settings as djoser_settings
from djoser.serializers import (
    UserCreatePasswordRetypeSerializer,
)

from rest_framework import (
    exceptions,
    serializers,
)

from phonenumber_field.serializerfields import PhoneNumberField
from phonenumber_field.phonenumber import to_python

from .models import User


DEFAULT_USER_FIELDS = (
    User._meta.pk.name,
    djoser_settings.LOGIN_FIELD,
    'password',
    'first_name',
    'last_name',
)

class CreateUserSerializer(UserCreatePasswordRetypeSerializer):
    """Serializer for User Signup."""

    class Meta(UserCreatePasswordRetypeSerializer.Meta):
        fields = DEFAULT_USER_FIELDS
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        """
        Performs the creation of a User and a related EmailAddress instance
        used for `allauth`.
        """
        user = super(CreateUserSerializer, self).create(validated_data)
        setup_user_email(self.context['request'], user, [])
        return user


class CreateVendorUserSerializer(CreateUserSerializer):
    """
    Custom CreateUserSerializer with fields specific for a Vendor User.
    """
    country_code = serializers.CharField(max_length=3,
                    read_only=True,
                    help_text='Phone number country code with optional `+` prefix')
    phone_number = serializers.CharField(required=True,
                    help_text='Phone number')
    is_phone_verified = serializers.ReadOnlyField()

    class Meta(CreateUserSerializer.Meta):
        fields = tuple(DEFAULT_USER_FIELDS) + (
            'country_code',
            'phone_number',
            'address',
            'business_name',
            'is_phone_verified',
        )
        read_only_fields = (
            'country_code',
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }


    def validate_phone_number(self, value):
        """
        Validate `country_code` with `phone_number` using the
        `phonenumber_field` validation methods.
        """
        # Format country_code with + sign.
        country_code = self.initial_data['country_code']
        if not country_code.startswith('+'):
            country_code = f'+{country_code}'

        phone_number = self.initial_data['phone_number']
        phone_number = f'{country_code}{phone_number}'
        phone_number = to_python(phone_number)
        if phone_number and not phone_number.is_valid():
            raise exceptions.ValidationError(
                     PhoneNumberField.default_error_messages['invalid'])
        return phone_number


class PhoneSerializer(serializers.Serializer):
    """
    Serializer for `phone_number` verification.
    """
    phone_number = PhoneNumberField(required=True)

    def validate(self, data):
        """
        Validate the phone number on the Authy API Server. If valid,
        Twilio API will send 4 digit verification token via SMS.
        """
        phone_number = phonenumbers.parse(
                        str(data.get('phone_number')), None)
        authy_api = AuthyApiClient(settings.ACCOUNT_SECURITY_API_KEY)
        authy_phone = authy_api.phones.verification_start(
            phone_number.national_number,
            phone_number.country_code
        )
        if authy_phone.ok():
            # authy_phone.response
            return data
        else:
            raise exceptions.ValidationError(authy_phone.errors())


class PhoneVerificationSerializer(serializers.Serializer):
    phone_number = PhoneNumberField(required=True)
    verification_code = serializers.CharField(min_length=4,
                            required=True,
                            write_only=True)

    def validate(self, data):
        # TODO: move to field validation
        phone_number = phonenumbers.parse(
                    str(data.get('phone_number')), None)
        authy_api = AuthyApiClient(settings.ACCOUNT_SECURITY_API_KEY)
        authy_phone = authy_api.phones.verification_check(
            phone_number.national_number,
            phone_number.country_code,
            data.get('verification_code')
        )
        if authy_phone.ok():
            return data
        else:
            raise exceptions.ValidationError(authy_phone.errors())
