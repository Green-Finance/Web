from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (SignupAPIView,
                    LoginAPIView,
                    LogoutAPIView,
                    VerifyEmailView,
                    UserDeleteView,
                    PasswordResetConfirmAPIView,
                    PasswordResetRequestAPIView
                    )

urlpatterns = [
    path('signup/', SignupAPIView.as_view(), name='signup'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # 인증
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),

    # 회원 탈퇴
    path('delete_id', UserDeleteView.as_view(), name='delete_user'),

    # 비밀번호 재설정
    path('password-reset-request/', PasswordResetRequestAPIView.as_view(), name='password-reset-request'),
    path('password-reset-confirm/', PasswordResetConfirmAPIView.as_view(), name='password-reset-confirm'),
]