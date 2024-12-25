from django.urls import path

from .views import CustomUserProfileView, RegisterView, TokenObtainPairView

app_name = 'users'

urlpatterns = [
    path('v1/register/', RegisterView.as_view(), name='register'),
    path('v1/login/', TokenObtainPairView.as_view(), name='login'),
    path('v1/profile/', CustomUserProfileView.as_view(), name='profile'),
]


