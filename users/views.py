import json
import requests

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.views.generic import DetailView, RedirectView, UpdateView

from rest_framework.views import APIView
from rest_framework.response import Response

from djoser import signals
from djoser.compat import get_user_email
from djoser.conf import settings as djoser_settings
from djoser.views import UserViewSet

from .models import User


class SwayUserViewSet(UserViewSet):
    """User registration viewset."""

    def perform_create(self, serializer):
        """
        Only Customers are sent with activation emails while Vendors
        require phone 2FA.
        """
        user = serializer.save()
        signals.user_registered.send(
            sender=self.__class__,
            user=user,
            request=self.request
        )
        if djoser_settings.SEND_ACTIVATION_EMAIL and user.is_customer:
            context = {'user': user}
            to = [get_user_email(user)]
            djoser_settings.EMAIL.activation(self.request, context).send(to)


class UserActivationView(APIView):
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
