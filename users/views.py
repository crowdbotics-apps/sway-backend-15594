import json
import phonenumbers
import requests

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.views.generic import DetailView, RedirectView, UpdateView

from authy.api import AuthyApiClient

from djoser import signals
from djoser.compat import get_user_email
from djoser.conf import settings as djoser_settings
from djoser.views import UserViewSet

from phonenumbers.phonenumberutil import NumberParseException

from rest_framework import (
    generics,
    status,
    views,
    viewsets,
    permissions,
)
from rest_framework.response import Response

from .models import User
from .serializers import (
    CreateUserSerializer,
    CreateVendorUserSerializer,
    PhoneSerializer,
    PhoneVerificationCodeSerializer,
)


class SwayUserViewSet(UserViewSet):
    """Provides the endpoints for registering and managing the User account."""

    def perform_create(self, serializer):
        """
        Method for executing `create` requests. Only Customers are sent with
        activation emails while Vendors require phone 2FA.
        """
        user = serializer.save()
        # Dispatch signal for successful User registration.
        signals.user_registered.send(
            sender=self.__class__,
            user=user,
            request=self.request
        )
        if djoser_settings.SEND_ACTIVATION_EMAIL and user.is_customer:
            context = {'user': user}
            to = [get_user_email(user)]
            djoser_settings.EMAIL.activation(self.request, context).send(to)


class VendorUserView(generics.CreateAPIView):
    """Create a new Vendor user in the system."""
    serializer_class = CreateVendorUserSerializer
    queryset = User.objects.all()
    permission_classes = djoser_settings.PERMISSIONS.user_create
    token_generator = default_token_generator

    def perform_create(self, serializer):
        user = serializer.save()
        user.user_type = User.TYPE_VENDOR
        user.save()
        # Dispatch signal for successful User registration.
        signals.user_registered.send(
            sender=self.__class__,
            user=user,
            request=self.request
        )


class PhoneVerificationView(generics.GenericAPIView):
    """Handles the Twilio phone verification."""

    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]
    serializer_class = PhoneSerializer

    def post(self, request):

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)


class PhoneRegistrationView(generics.GenericAPIView):
    """Handles the Twilio phone registration.

    Validates the 4 digit token sent to the user phone number.
    If successful, user instance will be updated with verified authy_id
    received from Twilio API authy_id
    """
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]
    serializer_class = PhoneVerificationCodeSerializer
    queryset = User.objects.all()

    def get_object(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = str(serializer.validated_data['phone_number'])
        user = User.objects.get(phone_number=phone_number)
        phone = phonenumbers.parse(phone_number, None)
        authy_api = AuthyApiClient(settings.ACCOUNT_SECURITY_API_KEY)
        authy_user = authy_api.users.create(
            user.email,
            str(phone.national_number),
            phone.country_code,
            True
        )
        if authy_user.ok():
            # Successful verifying `phone_number` and `verification_code`
            # TODO: Move to method
            user.authy_id = authy_user.id
            user.is_active = True
            user.save()
            signals.user_activated.send(
                sender=self.__class__,
                user=user,
                request=self.request
            )
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(authy_user.errors(),
                        status=status.HTTP_400_BAD_REQUEST)


class UserActivationView(views.APIView):
    """
    Custom view to handle GET request on registration User activation.
    """
    def get (self, request, uid, token):
        site = get_current_site(self.request)
        domain = getattr(settings, 'DOMAIN', '') or site.domain
        protocol = 'https://' if request.is_secure() else 'http://'
        activation_url = reverse('user-activation')
        activation_url = f'{protocol}{domain}{activation_url}'

        post_data = {'uid': uid, 'token': token}
        result = requests.post(activation_url, data=post_data)
        content = json.dumps(result.text)
        return Response(content, status=result.status_code)

user_activation_view = UserActivationView.as_view()


class UserDetailView(LoginRequiredMixin, DetailView):

    model = User
    slug_field = "username"
    slug_url_kwarg = "username"


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, UpdateView):

    model = User
    fields = ["name"]

    def get_success_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})

    def get_object(self):
        return User.objects.get(username=self.request.user.username)


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):

    permanent = False

    def get_redirect_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})


user_redirect_view = UserRedirectView.as_view()
