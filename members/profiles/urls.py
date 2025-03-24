from django.urls import path
from .views import UserProfileView, UserUpdateView, PasswordChangeView

urlpatterns = [
    path('views/', UserProfileView.as_view(), name='profile'),
    path('update_profile/', UserUpdateView.as_view(), name='update_profile'),
    path('change_password', PasswordChangeView.as_view(), name='change_password')
]