from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializer import SignupSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, generics
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework.permissions import IsAuthenticated
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from rest_framework.permissions import AllowAny

User = get_user_model()

# 회원가입 API 뷰
class SignupAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = SignupSerializer

# 로그인 API 뷰 (JWT 토큰 발급)
class LoginAPIView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]

# 로그아웃
class LogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"error": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()  # blacklist 앱이 활성화되어 있어야 합니다.
            return Response({"detail": "Logout successful."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)

# 이메일 인증
class VerifyEmailView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        uidb64 = request.GET.get('uid')
        token = request.GET.get('token')

        if not uidb64 or not token:
            return Response({'message': '잘못된 요청입니다.'}, status=400)

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            return Response({'message': '유효하지 않은 사용자입니다.'}, status=400)

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({'message': '이메일 인증이 완료되었습니다.'})
        else:
            return Response({'message': '유효하지 않거나 만료된 토큰입니다.'}, status=400)

class UserDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.delete()
        return Response({"message": "회원 탈퇴가 완료되었습니다."}, status=status.HTTP_200_OK)