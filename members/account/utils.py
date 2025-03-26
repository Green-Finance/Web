from config.celery import app
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import get_user_model
import requests


# 로그인과 동시에 인증을 보낼 때 동기 형식으로 인해 가입이 너무 오래걸림

User = get_user_model()

@app.task
def send_verification_email_task(user_id, domain):
    print("send_verification_email_task 실행됨")
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        print(f"User ID {user_id} not found.")
        return

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    verify_url = f"{domain}{reverse('verify-email')}?uid={uid}&token={token}"

    subject = '이메일 인증을 완료해주세요'
    message = f'{user.username}님, 아래 링크를 클릭하여 이메일 인증을 완료해주세요:\n\n{verify_url}'

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])



@app.task
def send_password_reset_email_task(user_id, domain):
    try:
        user = get_user_model().objects.get(pk=user_id)
    except User.DoesNotExist:
        print(f"User ID {user_id} not found.")
        return

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    reset_url = f"{domain}{reverse('password-reset-confirm')}?uid={uid}&token={token}"

    subject = '비밀번호 재설정 링크입니다'
    message = f'{user.username}님, 아래 링크를 클릭하여 비밀번호를 재설정하세요:\n\n{reset_url}'
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])


@app.task
def send_user_to_fastapi(user_id, username, email, profile_pic, intro):
    url = f"{settings.FASTAPI_SERVER_URL}/sync-user/"
    data = {
        'id': user_id,
        'username': username,
        'email': email,
        'profile_pic': profile_pic,
        'intro': intro,
    }
    try:
        response = requests.post(url, json=data, timeout=5)  # 👈 timeout 추가!
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"FastAPI 유저 전송 실패, 실패 사유 : {e}")

