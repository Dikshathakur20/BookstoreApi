from fastapi import APIRouter, HTTPException, status
from app.schemas.user import UserCreate, UserLogin, TokenResponse
from app.services.auth_service import AuthService
from app.core.exceptions import ConflictException, UnauthorizedException

router = APIRouter()

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    try:
        user = AuthService.register_user(user_data)
        login_data = UserLogin(email=user_data.email, password=user_data.password)
        return AuthService.login_user(login_data)
    except ConflictException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/login", response_model=TokenResponse)
async def login(login_data: UserLogin):
    try:
        return AuthService.login_user(login_data)
    except UnauthorizedException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))