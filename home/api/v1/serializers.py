from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.utils.translation import ugettext_lazy as _
from allauth.account import app_settings as allauth_settings
from allauth.utils import email_address_exists, generate_unique_username
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from rest_framework import serializers
from rest_auth.serializers import PasswordResetSerializer

from djoser.conf import settings as djoser_settings
from djoser.serializers import (
    UserCreatePasswordRetypeSerializer
)

from home.models import CustomText, HomePage

User = get_user_model()


class CreateUserSerializer(UserCreatePasswordRetypeSerializer):
    """Serializer for User Signup."""

    class Meta(UserCreatePasswordRetypeSerializer.Meta):
        fields = (
            User._meta.pk.name,
            djoser_settings.LOGIN_FIELD,
            'password',
            'first_name',
            'last_name',
            'user_type',
        )
        extra_kwargs = {
            'email': {
                'required': True,
                'allow_blank': False,
            },
        }

    def create(self, validated_data):
        """
        Performs the creation of a User and a related EmailAddress instance
        used for `allauth`.
        """
        user = super(CreateUserSerializer, self).create(validated_data)
        setup_user_email(self.context['request'], user, [])
        return user


class CustomTextSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomText
        fields = '__all__'


class HomePageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomePage
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name']
