from allauth.account.utils import setup_user_email

from djoser.conf import settings as djoser_settings
from djoser.serializers import (
    UserCreatePasswordRetypeSerializer
)

from .models import User


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
