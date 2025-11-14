# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PropertyViewSet, InquiryViewSet, PropertyImageViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register("properties", PropertyViewSet, basename="properties")
router.register("inquiries", InquiryViewSet, basename="inquiries")
router.register("property-images", PropertyImageViewSet, basename="property-images")

urlpatterns = [
    path("", include(router.urls)),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
