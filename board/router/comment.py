from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from dto.comment import CommentCreate, CommentResponse
from models.model import Comment
from core.database import get_db
from core.dependencies import get_current_user
from celery_task.tasks import (notify_django_about_comment,
                               notify_django_about_comment_update,
                               notify_django_about_comment_delete
                               )

router = APIRouter(
    prefix="/api/comment/v1",
    tags=["comment"],
    responses={404: {"description": "Not Found"}},
)

@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment_endpoint(
    board_id: int,  # 쿼리 파라미터로 board_id를 전달하거나, URL 경로에 포함시키도록 조정 가능
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # FastAPI에서 댓글을 DB에 저장
    new_comment = Comment(
        board_id=board_id,
        user_id=current_user.id,
        content=comment.content
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    # 동기화용 데이터 준비
    comment_data = {
        "user_id": current_user.id,
        "board_id": board_id,
        "content": new_comment.content,
        "created_at": str(new_comment.created_at),
        "updated_at": str(new_comment.updated_at),
    }

    # 비동기로 보냄
    notify_django_about_comment.apply_async(args=[comment_data], queue="board")

    return new_comment

@router.put("/{comment_id}", response_model=CommentResponse, status_code=status.HTTP_200_OK)
def update_comment_endpoint(
    comment_id: int,
    comment_data: CommentCreate,  # 댓글 수정 시 content 만 전달 (필요에 따라 확장)
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # DB에서 댓글 조회
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No permission to update this comment")

    # 댓글 수정 (여기서는 content만 업데이트)
    comment.content = comment_data.content
    db.commit()
    db.refresh(comment)

    # 업데이트된 댓글 정보를 딕셔너리로 구성합니다.
    updated_data = {
        "content": comment.content,
        "user_id": comment.user_id,
        "board_id": comment.board_id,
        "created_at": str(comment.created_at),
        "updated_at": str(comment.updated_at),
    }

    # Django 동기화용 Celery Task 호출
    notify_django_about_comment_update.apply_async(args=[comment.id, updated_data], queue="board")

    return comment



@router.delete("/{comment_id}", status_code=status.HTTP_200_OK)
def delete_comment_endpoint(
        comment_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    # DB에서 댓글 조회
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No permission to delete this comment")

    db.delete(comment)
    db.commit()

    # 선택 사항: Django 동기화용 Celery Task 호출 (삭제 정보를 전달)
    notify_django_about_comment_delete.apply_async(args=[comment.id], queue="board")

    return {"detail": "Comment deleted successfully."}


