from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from zoneinfo import ZoneInfo
from core.database import Base

# django에서 넘어오는 유저 데이터
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    profile_pic = Column(String, nullable=True)  # 이미지 URL 등을 저장
    intro = Column(Text, nullable=True)          # 자기소개 텍스트

    boards = relationship("Board", back_populates="user")

class Board(Base):
    __tablename__ = "boards"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(ZoneInfo("Asia/Seoul")))
    updated_at = Column(DateTime, default=lambda: datetime.now(ZoneInfo("Asia/Seoul")), onupdate=lambda: datetime.now(ZoneInfo("Asia/Seoul")))

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="boards")


