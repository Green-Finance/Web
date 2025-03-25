from celery import shared_task
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import get_user_model


# 로그인과 동시에 인증을 보낼 때 동기 형식으로 인해 가입이 너무 오래걸림

User = get_user_model()

@shared_task
def send_verification_email_task(user_id, domain):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.get(pk=user_id)

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    verify_url = f"{domain}{reverse('verify-email')}?uid={uid}&token={token}"

    subject = '이메일 인증을 완료해주세요'
    message = f'{user.username}님, 아래 링크를 클릭하여 이메일 인증을 완료해주세요:\n\n{verify_url}'

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])


@shared_task
def send_password_reset_email_task(user_id, domain):

    user = get_user_model().objects.get(pk=user_id)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    reset_url = f"{domain}{reverse('password-reset-confirm')}?uid={uid}&token={token}"

    subject = '비밀번호 재설정 링크입니다'
    message = f'{user.username}님, 아래 링크를 클릭하여 비밀번호를 재설정하세요:\n\n{reset_url}'
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
