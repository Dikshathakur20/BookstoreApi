from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.user import UserResponse, UserUpdate, ChangePassword
from app.services.user_service import UserService
from app.api.deps import get_current_active_user
from app.core.exceptions import NotFoundException, ConflictException, BadRequestException

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def get_current_user(current_user = Depends(get_current_active_user)):
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    update_data: UserUpdate,
    current_user = Depends(get_current_active_user)
):
    try:
        return UserService.update_user(current_user["id"], update_data)
    except (NotFoundException, ConflictException) as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/me/change-password")
async def change_password(
    password_data: ChangePassword,
    current_user = Depends(get_current_active_user)
):
    try:
        return UserService.change_password(current_user["id"], password_data)
    except BadRequestException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))