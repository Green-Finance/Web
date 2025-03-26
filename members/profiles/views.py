from .serializer import UserProfileSerializer, UserUpdateSerializer, PasswordChangeSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, permissions

from django.contrib.auth import get_user_model
from .serializer import PostSerializer
from .models import Post

from django.core.exceptions import ObjectDoesNotExist
from django.utils.dateparse import parse_datetime

User = get_user_model()


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)


class UserUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        user = request.user
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "비밀번호가 성공적으로 변경되었습니다."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SyncPostFromFastAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        FastAPI로부터 게시글 데이터를 받아 저장
        """
        data = request.data
        user_id = data.get('user_id')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # datetime 문자열을 파싱 (ISO 포맷 가정)
        created_at = parse_datetime(data.get('created_at'))
        updated_at = parse_datetime(data.get('updated_at'))

        post = Post.objects.create(
            user=user,
            id=data.get('post_id'),
            title=data.get('title'),
            content=data.get('content'),
            created_at=created_at,
            updated_at=updated_at,
        )

        serializer = PostSerializer(post)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SyncPostUpdateAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def put(self, request, post_id):
        """
        FastAPI로부터 게시글 데이터를 받아 기존 게시글을 업데이트
        """
        data = request.data

        try:
            # Django의 기본 id를 사용한다고 가정
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({'detail': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

        # datetime 문자열 파싱 (ISO 포맷)
        created_at = parse_datetime(data.get('created_at'))
        updated_at = parse_datetime(data.get('updated_at'))

        post.title = data.get('title', post.title)
        post.content = data.get('content', post.content)
        post.created_at = created_at or post.created_at
        post.updated_at = updated_at or post.updated_at
        post.save()

        serializer = PostSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)



class SyncPostDeleteAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    def delete(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
            post.delete()
            return Response({"detail": "게시글이 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response({"detail": "해당 게시글을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)