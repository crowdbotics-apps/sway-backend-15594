from allauth.account.utils import setup_user_email

from djoser.conf import settings as djoser_settings
from djoser.serializers import (
    UserCreatePasswordRetypeSerializer,
)

from rest_framework.serializers import Serializer

from phonenumber_field.serializerfields import PhoneNumberField

from .models import User


DEFAULT_USER_FIELDS = (
    User._meta.pk.name,
    djoser_settings.LOGIN_FIELD,
    'password',
    'first_name',
    'last_name',
    'user_type',
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
    """Custom CreateUserSerializer with fields specific for a Vendor User."""

    class Meta(CreateUserSerializer.Meta):
        fields = tuple(DEFAULT_USER_FIELDS) + (
            'phone_number',
            'address',
            'business_name',
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }
