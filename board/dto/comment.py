from pydantic import BaseModel, Field
from datetime import datetime


class CommentBase(BaseModel):
    content: str = Field(..., example="예시 댓글~~")

class CommentCreate(CommentBase):
    # 클라이언트에서는 댓글 내용만 보내도록 함.
    pass

class CommentResponse(CommentBase):
    id: int
    board_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
