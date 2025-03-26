from django.urls import path
from .views import (UserProfileView,
                    UserUpdateView,
                    PasswordChangeView,
                    SyncPostFromFastAPIView,
                    SyncPostDeleteAPIView,
                    SyncPostUpdateAPIView,
                    SyncBoardLikeAPIView,
                    SyncCommentAPIView,
                    SyncCommentDeleteAPIView,
                    SyncCommentUpdateAPIView
                    )

urlpatterns = [
    path('views/', UserProfileView.as_view(), name='profile'),
    path('update_profile/', UserUpdateView.as_view(), name='update_profile'),
    path('change_password/', PasswordChangeView.as_view(), name='change_password'),
    path('sync/', SyncPostFromFastAPIView.as_view(), name='sync-post-from-fastapi'), # Celery로 받은 데이터

    # post
    path("sync/delete/<int:post_id>/", SyncPostDeleteAPIView.as_view(), name="sync-post-delete-fastapi"),
    path('sync/update/<int:post_id>/', SyncPostUpdateAPIView.as_view(), name="sync-post-update-fastapi"),
    path("sync/<int:post_id>/board_like/", SyncBoardLikeAPIView.as_view(), name="toggle-post-like"),

    # comment
    path("sync/comment/", SyncCommentAPIView.as_view(), name="sync-comment"),
    path("sync/comment/update/<int:comment_id>/", SyncCommentUpdateAPIView.as_view(), name="sync_comment_update"),
    path("sync/comment/delete/<int:comment_id>/", SyncCommentDeleteAPIView.as_view(), name="sync_comment_delete"),

]