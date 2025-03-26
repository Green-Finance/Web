from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from models.model import User as UserModel
from dto.user import UserCreate, UserResponse

router = APIRouter(
    prefix="/api/users/v1",
    tags=["users"],
    responses={
        404 : {
            "description" : "Not Found"
        }
    }
)

@router.post("/sync-user/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(UserModel).filter(UserModel.id == user.id).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = UserModel(
        id=user.id,
        username=user.username,
        email=user.email,
        profile_pic=user.profile_pic,
        intro=user.intro,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return UserResponse(message="User created", user_id=new_user.id)
