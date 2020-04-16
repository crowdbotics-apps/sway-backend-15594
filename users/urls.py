from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import (
    SwayUserViewSet,
    user_activation_view,
)

app_name = "users"

router = DefaultRouter()
router.register('', SwayUserViewSet)

urlpatterns = [
    path('activate/<str:uid>/<str:token>', user_activation_view),
    path('', include(router.urls)),
]
