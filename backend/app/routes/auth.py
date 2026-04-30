from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.user import UserRegister, UserLogin, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    try:
        user = AuthService.register_user(db, user_data)

        token = AuthService.create_access_token({
            "sub": user.email
        })

        return {
            "access_token": token,
            "token_type": "bearer",
            "user": user
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = AuthService.login_user(
        db,
        credentials.email,
        credentials.password
    )

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = AuthService.create_access_token({
        "sub": user.email
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }
