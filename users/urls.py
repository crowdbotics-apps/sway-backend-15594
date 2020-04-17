from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import (
    PhoneVerificationView,
    PhoneRegistrationView,
    SwayUserViewSet,
    VendorUserView,
    user_activation_view,
)

app_name = "users"

router = DefaultRouter()
router.register('', SwayUserViewSet)

urlpatterns = [
    path('phone-verify/', PhoneVerificationView.as_view(), name='phone_verify'),
    path('phone-register/', PhoneRegistrationView.as_view(), name='phone_register'),

    path('vendor/', VendorUserView.as_view(), name='vendor'),

    path('', include(router.urls)),
    path('activate/<str:uid>/<str:token>', user_activation_view,
        name='activate-from-email'),
]
