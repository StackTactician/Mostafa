from django.urls import path, include
from . import api_views
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'restaurants', api_views.RestaurantViewSet)
router.register(r'orders', api_views.OrderViewSet, basename='order')
router.register(r'profile', api_views.UserProfileViewSet, basename='profile')

urlpatterns = [
    # API Routes
    path('api/', include(router.urls)),
    path('api/register/', api_views.RegisterView.as_view(), name='api_register'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
