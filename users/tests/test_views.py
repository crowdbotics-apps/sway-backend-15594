import pytest
from django.conf import settings
from django.test import RequestFactory, TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from users.views import (
    UserRedirectView,
    UserUpdateView,
    UserActivationView,
)

pytestmark = pytest.mark.django_db


class TestUserUpdateView:
    """
    TODO:
        extracting view initialization code as class-scoped fixture
        would be great if only pytest-django supported non-function-scoped
        fixture db access -- this is a work-in-progress for now:
        https://github.com/pytest-dev/pytest-django/pull/258
    """

    def test_get_success_url(
        self, user: settings.AUTH_USER_MODEL, request_factory: RequestFactory
    ):
        view = UserUpdateView()
        request = request_factory.get("/fake-url/")
        request.user = user

        view.request = request

        assert view.get_success_url() == f"/users/{user.username}/"

    def test_get_object(
        self, user: settings.AUTH_USER_MODEL, request_factory: RequestFactory
    ):
        view = UserUpdateView()
        request = request_factory.get("/fake-url/")
        request.user = user

        view.request = request

        assert view.get_object() == user


class TestUserRedirectView:
    def test_get_redirect_url(
        self, user: settings.AUTH_USER_MODEL, request_factory: RequestFactory
    ):
        view = UserRedirectView()
        request = request_factory.get("/fake-url")
        request.user = user

        view.request = request

        assert view.get_redirect_url() == f"/users/{user.username}/"


class TestUserActivationView(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_endpoint_access_fail(self):
        """Test endpoint access invalid `uid` and `token` fails."""
        url = reverse('users:activate-from-email', args=(1, 1))
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
