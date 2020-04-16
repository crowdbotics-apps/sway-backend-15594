from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import DetailView, RedirectView, UpdateView

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
