import json

from django import apps
from django.core.management import call_command
from .permissions import CrowboticsExclusive

from rest_framework import generics, status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from home.api.v1.serializers import (
    CustomTextSerializer,
    HomePageSerializer,
)
from home.models import CustomText, HomePage


class CustomTextViewSet(ModelViewSet):
    serializer_class = CustomTextSerializer
    queryset = CustomText.objects.all()
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = [IsAdminUser]
    http_method_names = ['get', 'put', 'patch']


class HomePageViewSet(ModelViewSet):
    serializer_class = HomePageSerializer
    queryset = HomePage.objects.all()
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = [IsAdminUser]
    http_method_names = ['get', 'put', 'patch']


class AppReportView(APIView):
    """
    DO NOT REMOVE THIS CODE SNIPPET, YOUR DASHBOARD MAY NOT REFLECT THE CORRECT
    RESOURCES IN YOUR APP.
    """
    permission_classes = [CrowboticsExclusive]

    def _get_models(self):
        project_models = apps.apps.get_models(
            include_auto_created=True, include_swapped=True
        )
        parsed_data = [
            str(model).split(".")[-1].replace("'", "").strip(">") for model in
            project_models
        ]
        return parsed_data

    def _get_urls(self):
        parsed_data = json.loads(call_command("show_urls", format="json"))
        return parsed_data

    def get(self, request):
        return Response({
            "models": self._get_models(),
            "urls": self._get_urls()
        }, status=status.HTTP_200_OK)
