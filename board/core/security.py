from jose import JWTError, jwt
from fastapi import HTTPException, status
from .config import settings

def verify_jwt(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_exception()
        return user_id
    except JWTError:
        raise credentials_exception()

def credentials_exception():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="유효한 인증이 아님.",
        headers={"WWW-Authenticate": "Bearer"},
    )
