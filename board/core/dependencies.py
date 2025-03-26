# dependencies.py
from fastapi import Request, Depends, HTTPException, status
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from .config import settings
from .database import get_db
from models.model import User
from .security import verify_jwt

def get_current_user(request: Request, db: Session = Depends(get_db)):
    # 헤더에서 JWT 가져오기
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="헤더에 토큰이 없습니다.")

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="잘못된 인증 수단")

    token = parts[1]

    # 기존 verify_jwt로 user_id 검증
    user_id = verify_jwt(token)

    # DB에서 실제 User 객체 가져오기
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="유저가 없습니다.")

    return user
