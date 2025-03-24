from django.contrib.auth import get_user_model
from rest_framework import serializers
from .utils import send_verification_email_task

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
        if request:
            domain = request.build_absolute_uri('/')[:-1]  # ex: http://localhost:8000
            send_verification_email_task.delay(user.id, domain)  # 🔥 비동기 처리

        return user




