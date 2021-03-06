from django.urls import path, include
from rest_framework.routers import DefaultRouter

from home.api.v1.viewsets import (
    HomePageViewSet,
    CustomTextViewSet,
    AppReportView,
)

router = DefaultRouter()
router.register('customtext', CustomTextViewSet)
router.register('homepage', HomePageViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("report", AppReportView.as_view(), name="app_report"),
]
