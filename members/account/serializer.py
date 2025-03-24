from django.contrib.auth import get_user_model
from rest_framework import serializers


User = get_user_model()


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'profile_pic', 'intro', 'password')

    def create(self, validated_data):
        # create_user를 사용하면 비밀번호 해싱 등이 처리됩니다.
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            profile_pic=validated_data.get('profile_pic'),
            intro=validated_data.get('intro', '')
        )





