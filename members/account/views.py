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

from .utils import send_password_reset_email_task

from django.utils.encoding import force_str
from django.conf import settings



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
            return Response({"error": "리프레시 토큰이 만료됨"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()  # blacklist 앱이 활성화되어 있어야 합니다.
            return Response({"detail": "로그인 성공."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": "토큰이 잘못됨."}, status=status.HTTP_400_BAD_REQUEST)

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


# 회원탈퇴 맨
class UserDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.delete()
        return Response({"message": "회원 탈퇴가 완료되었습니다."}, status=status.HTTP_200_OK)

# 비밀번호 재설정 요청
class PasswordResetRequestAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        domain = request.get_host()

        try:
            user = User.objects.get(email=email)
            send_password_reset_email_task.delay(user.id, domain)
            return Response({'detail': '비밀번호 재설정 링크가 전송되었습니다.'}, status=200)
        except User.DoesNotExist:
            if settings.DEBUG:
                return Response({'detail': '해당 이메일은 존재하지 않습니다.'}, status=400)
            # 실제 운영 환경에서는 이메일 존재 여부를 알려주지 않음
            return Response({'detail': '비밀번호 재설정 링크가 전송되었습니다.'}, status=200)


# 비밀번호 변경 후 컨펌
class PasswordResetConfirmAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        uid = request.data.get('uid')
        token = request.data.get('token')
        new_password = request.data.get('new_password')

        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            return Response({'detail': '유효하지 않은 링크입니다.'}, status=400)

        if not default_token_generator.check_token(user, token):
            return Response({'detail': '유효하지 않은 토큰입니다.'}, status=400)

        user.set_password(new_password)
        user.save()
        return Response({'detail': '비밀번호가 성공적으로 변경되었습니다.'}, status=200)



