from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from models.model import Board as BoardModel
from core.database import get_db
from dto.board import BoardCreate, BoardResponse
from core.dependencies import get_current_user
from dto.user import UserResponse
from celery_task.tasks import (notify_django_about_post,
                               notify_django_about_post_delete,
                               notify_django_about_post_update,
                               notify_django_about_board_like
                               )
from models.model import User, BoardLike, Board

router = APIRouter(
    prefix="/api/boards/v1",
    tags=["boards"],
    responses={404: {"description": "Not Found"}},
)

@router.post("/", response_model=BoardResponse, status_code=status.HTTP_201_CREATED)
def create_board(
    board: BoardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # JWT 인증 및 사용자 식별
):
    new_board = BoardModel(
        title=board.title,
        content=board.content,
        user_id=current_user.id,  # 인증된 사용자 ID 사용
    )
    db.add(new_board)
    db.commit()
    db.refresh(new_board)

    # Celery를 통해 Django로 비동기 데이터 전송
    notify_django_about_post.apply_async(
        args=[{
            "post_id": new_board.id,
            "title": new_board.title,
            "content": new_board.content,
            "user_id": new_board.user_id,
            "created_at": str(new_board.created_at),
            "updated_at": str(new_board.updated_at),
        }],
        queue="board"
    )

    return new_board


@router.get("/", response_model=list[BoardResponse])
def read_boards(db: Session = Depends(get_db)):
    boards = db.query(BoardModel).all()
    return boards

@router.get("/{board_id}", response_model=BoardResponse)
def read_board(board_id: int, db: Session = Depends(get_db)):
    board = db.query(BoardModel).filter(BoardModel.id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return board

@router.put("/{board_id}", response_model=BoardResponse)
def update_board(
    board_id: int,
    updated: BoardCreate,  # BoardCreate에는 title, content만 있어야 함
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    board = db.query(BoardModel).filter(BoardModel.id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    if board.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No permission to update this board")

    board.title = updated.title
    board.content = updated.content
    # 필요하다면 updated_at 갱신 (예: timezone.now() 사용)
    db.commit()
    db.refresh(board)

    notify_django_about_post_update.apply_async(
        args=[
            board.id,
            {
                "title": board.title,
                "content": board.content,
                "user_id": board.user_id,
                "created_at": str(board.created_at),
                "updated_at": str(board.updated_at),
            }
        ],
        queue="board"
    )

    return board

@router.delete("/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_board(
    board_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    board = db.query(BoardModel).filter(BoardModel.id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    if board.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No permission to delete this board")

    db.delete(board)
    db.commit()

    # Celery task 호출 시 매개변수와 큐 지정
    notify_django_about_post_delete.apply_async(args=[board_id], queue="board")

    return {
        "detail" : "삭제가 완료되었습니다."
    }


############################################################################################


# 게시글 좋아요
@router.post("/{board_id}/like", status_code=status.HTTP_200_OK)
def toggle_board_like_endpoint(
        board_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    # 좋아요 상태를 DB에서 직접 확인
    like = db.query(BoardLike).filter(
        BoardLike.board_id == board_id,
        BoardLike.user_id == current_user.id
    ).first()

    if like:
        db.delete(like)
        action = "Unliked"
    else:
        new_like = BoardLike(board_id=board_id, user_id=current_user.id)
        db.add(new_like)
        action = "Liked"

    db.commit()

    # 최신 좋아요 개수를 DB에서 직접 집계 <-- 추가
    like_count = db.query(BoardLike).filter(BoardLike.board_id == board_id).count()

    # 비동기처리 -> django profile로 보내기

    notify_django_about_board_like.apply_async(
        args=[board_id, current_user.id, action],
        queue="board"
    )

    return {"detail": action, "like_count": like_count}

