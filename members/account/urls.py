from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import SignupAPIView, LoginAPIView, LogoutAPIView, VerifyEmailView, UserDeleteView

urlpatterns = [
    path('signup/', SignupAPIView.as_view(), name='signup'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('delete_id', UserDeleteView.as_view(), name='delete_user')
]