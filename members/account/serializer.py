from django.contrib.auth import get_user_model
from rest_framework import serializers
from .utils import send_verification_email_task, send_user_to_fastapi
from celery import group

User = get_user_model()

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'profile_pic', 'intro', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            profile_pic=validated_data.get('profile_pic'),
            intro=validated_data.get('intro', ''),
            is_active=False
        )
        request = self.context.get('request')
        domain = request.build_absolute_uri('/')[:-1] if request else 'https://yourdomain.com'

        # Group Celery fastapi로 유저 정보 보내면서 이메일 인증도 같이 보내는 queue
        group(
            send_user_to_fastapi.s(
                user.id,
                user.username,
                user.email,
                user.profile_pic.url if user.profile_pic else None,
                user.intro
            ).set(queue='account'),

            send_verification_email_task.s(user.id, domain).set(queue='account')
        ).apply_async()

        return user

