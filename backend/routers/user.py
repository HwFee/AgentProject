from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.responses import ApiResponse
from schemas.user import (
    UserLogin,
    UserLoginResponse,
    UserRegister,
    UserRegisterResponse,
    UserTokenResponse,
)
from utils.dependencies import get_db, get_current_user, oauth2_scheme
from crud.user import (
    authenticate_user,
    create_user,
    refresh_access_token,
)

router = APIRouter(prefix="/api/user", tags=["user"])


class ProfileUpdateRequest(BaseModel):
    username: str
    email: str


class PasswordUpdateRequest(BaseModel):
    old_password: str
    new_password: str
    confirm_password: str


@router.post("/register", response_model=ApiResponse[UserRegisterResponse])
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    new_user = await create_user(db, user_data)
    return ApiResponse(
        status_code=201,
        message="用户注册成功",
        data=UserRegisterResponse.model_validate(new_user),
    )


@router.post("/login", response_model=ApiResponse[UserLoginResponse])
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    user, access_token, refresh_token = await authenticate_user(db, user_data)
    return ApiResponse(
        status_code=200,
        message="登录成功",
        data=UserLoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserRegisterResponse.model_validate(user),
        ),
    )


@router.post("/refresh", response_model=ApiResponse[UserTokenResponse])
async def refresh_token(
    refresh_token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    access_token, refresh_token = await refresh_access_token(db, refresh_token)
    return ApiResponse(
        status_code=200,
        message="Token刷新成功",
        data=UserTokenResponse(access_token=access_token, refresh_token=refresh_token),
    )


@router.get("/profile", response_model=ApiResponse[dict])
async def get_profile(current_user=Depends(get_current_user)):
    return ApiResponse(
        status_code=200,
        message="获取成功",
        data={
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "role": "admin" if current_user.is_admin else "user",
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        },
    )


@router.put("/profile", response_model=ApiResponse)
async def update_profile(
    req: ProfileUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    from crud.user import update_user
    await update_user(db, current_user.id, username=req.username, email=req.email)
    return ApiResponse(status_code=200, message="更新成功")


@router.put("/password", response_model=ApiResponse)
async def update_password(
    req: PasswordUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if req.new_password != req.confirm_password:
        from utils.exceptions import AppException
        raise AppException(status_code=400, message="两次输入的新密码不一致")
    from crud.user import update_password as update_user_password
    success = await update_user_password(
        db, current_user.id, old_password=req.old_password, new_password=req.new_password
    )
    if not success:
        from utils.exceptions import AppException
        raise AppException(status_code=400, message="旧密码错误")
    return ApiResponse(status_code=200, message="密码修改成功")
