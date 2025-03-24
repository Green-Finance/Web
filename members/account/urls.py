from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import SignupAPIView, LoginAPIView, LogoutAPIView

urlpatterns = [
    path('signup/', SignupAPIView.as_view(), name='signup'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]