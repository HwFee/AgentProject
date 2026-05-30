from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from config.database import LocalSession
from models.user import User
from utils.security import decode_token
from utils.exceptions import UserNotFoundException, TokenInvalidException


# 数据库会话依赖项
async def get_db():
    async with LocalSession() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


# 自动提取Token的依赖项 tokenUrl参数指定了测试文档获取Token的URL路径，前端登录时会向这个路径发送请求以获取Token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/login")


# 获取当前用户的依赖项
async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    payload = decode_token(token, expected_type="access")
    user_id: int = payload.get("user_id")
    if user_id is None:
        raise TokenInvalidException()
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if user is None:
        raise UserNotFoundException()
    return user
