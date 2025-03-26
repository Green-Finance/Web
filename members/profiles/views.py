from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, permissions

from django.contrib.auth import get_user_model
from .serializer import PostSerializer, CommentSerializer, UserProfileSerializer, UserUpdateSerializer, PasswordChangeSerializer
from .models import Post, PostLike, Comment

from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.utils.dateparse import parse_datetime

from zoneinfo import ZoneInfo
from datetime import datetime

# 기본 유저 모델
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


class SyncBoardLikeAPIView(APIView):
    # 인증 없이 접근하도록 설정 (내부 동기화용)
    permission_classes = [permissions.AllowAny]

    def post(self, request, post_id):
        """
        FastAPI나 Celery Task로부터 게시글 좋아요 토글 요청을 받아 처리합니다.
        요청 본문에 user_id를 포함시켜야 합니다.
        """
        data = request.data
        user_id = data.get("user_id")
        if not user_id:
            return Response({"detail": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        # 해당 게시글을 가져옵니다.
        post = get_object_or_404(Post, id=post_id)

        # 좋아요 토글: 이미 좋아요가 있으면 삭제하고, 없으면 생성합니다.
        like, created = PostLike.objects.get_or_create(user_id=user_id, post=post)
        if not created:
            like.delete()
            action = "Unliked"
        else:
            action = "Liked"

        like_count = post.likes.count()
        return Response({"detail": action, "like_count": like_count}, status=status.HTTP_200_OK)


class SyncCommentAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        FastAPI로부터 댓글 데이터를 받아 저장합니다.
        요청 JSON 예시:
        {
            "user_id": 1,
            "board_id": 3,
            "content": "댓글 내용입니다.",
            "created_at": "2025-03-26T06:58:08.775688",  # (옵션)
            "updated_at": "2025-03-26T06:58:08.775688"   # (옵션)
        }
        """
        data = request.data
        user_id = data.get('user_id')
        board_id = data.get('board_id')
        content = data.get('content')

        if not user_id or not board_id or not content:
            return Response({"detail": "user_id, board_id, content 필드가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 사용자 조회
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # 게시글 조회 (Post 모델; 실제 모델 이름에 맞게 수정)
        try:
            board = Post.objects.get(id=board_id)
        except Post.DoesNotExist:
            return Response({'detail': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

        # datetime 파싱 (옵션: 값이 없으면 현재 시간 사용)
        created_at = parse_datetime(data.get('created_at')) or datetime.now(ZoneInfo("Asia/Seoul"))
        updated_at = parse_datetime(data.get('updated_at')) or datetime.now(ZoneInfo("Asia/Seoul"))

        # 댓글 생성
        comment = Comment.objects.create(
            board=board,
            user=user,
            content=content,
            created_at=created_at,
            updated_at=updated_at
        )

        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SyncCommentUpdateAPIView(APIView):
    permission_classes = [permissions.AllowAny]  # 내부 동기화용, 인증 필요 없음

    def put(self, request, comment_id):
        """
        FastAPI로부터 전달받은 댓글 데이터를 이용해 댓글을 업데이트합니다.
        요청 JSON 예시:
        {
            "content": "새로운 댓글 내용",
            "created_at": "2025-03-26T06:58:08.775688",  # 옵션
            "updated_at": "2025-03-26T06:58:08.775688"   # 옵션
        }
        """
        data = request.data
        comment = get_object_or_404(Comment, id=comment_id)

        # 전달받은 값으로 댓글 업데이트 (값이 없으면 기존 값 유지)
        comment.content = data.get('content', comment.content)
        created_at = parse_datetime(data.get('created_at'))
        updated_at = parse_datetime(data.get('updated_at'))
        if created_at:
            comment.created_at = created_at
        if updated_at:
            comment.updated_at = updated_at

        comment.save()
        return Response({"detail": "Comment updated successfully."}, status=status.HTTP_200_OK)



class SyncCommentDeleteAPIView(APIView):
    permission_classes = [permissions.AllowAny]  # 내부 동기화용, 인증 필요 없음

    def delete(self, request, comment_id):
        """
        FastAPI로부터 전달받은 댓글 삭제 요청을 처리.
        """
        comment = get_object_or_404(Comment, id=comment_id)
        comment.delete()
        return Response({"detail": "Comment deleted successfully."}, status=status.HTTP_200_OK)