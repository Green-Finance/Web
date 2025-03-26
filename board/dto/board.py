from pydantic import BaseModel, Field
from datetime import datetime

class BoardCreate(BaseModel):
    title: str = Field(..., example="첫 번째 게시글")
    content: str = Field(..., example="이 게시글은 예시입니다.")


class BoardResponse(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
    user_id: int

    class Config:
        from_attributes = True


class BoardLikeResponse(BaseModel):
    id: int
    board_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True