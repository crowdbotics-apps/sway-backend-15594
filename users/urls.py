from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import (
    SwayUserViewSet,
)

app_name = "users"

router = DefaultRouter()
router.register('', SwayUserViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
