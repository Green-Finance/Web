from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from zoneinfo import ZoneInfo
from core.database import Base


# Django에서 넘어오는 유저 데이터
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    profile_pic = Column(String, nullable=True)  # 이미지 URL 등을 저장
    intro = Column(Text, nullable=True)  # 자기소개 텍스트

    boards = relationship("Board", back_populates="user")
    comments = relationship("Comment", back_populates="user")  # 댓글 관계 추가


class Board(Base):
    __tablename__ = "boards"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(ZoneInfo("Asia/Seoul")))
    updated_at = Column(DateTime, default=lambda: datetime.now(ZoneInfo("Asia/Seoul")),
                        onupdate=lambda: datetime.now(ZoneInfo("Asia/Seoul")))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="boards")
    likes = relationship("BoardLike", back_populates="board")
    comments = relationship("Comment", back_populates="board")  # 댓글 관계 추가


class BoardLike(Base):
    __tablename__ = "board_likes"
    id = Column(Integer, primary_key=True, index=True)
    board_id = Column(Integer, ForeignKey("boards.id"), nullable=False)
    user_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(ZoneInfo("Asia/Seoul")))

    board = relationship("Board", back_populates="likes")

    __table_args__ = (
        UniqueConstraint('board_id', 'user_id', name='unique_board_like'),
    )


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    board_id = Column(Integer, ForeignKey("boards.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(ZoneInfo("Asia/Seoul")))
    updated_at = Column(DateTime, default=lambda: datetime.now(ZoneInfo("Asia/Seoul")),
                        onupdate=lambda: datetime.now(ZoneInfo("Asia/Seoul")))

    # 관계 설정: 댓글이 어느 게시글에 달렸는지, 어떤 사용자가 작성했는지
    board = relationship("Board", back_populates="comments")
    user = relationship("User", back_populates="comments")
