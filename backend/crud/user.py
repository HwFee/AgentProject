from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import UserToken
from schemas.user import UserLogin, UserRegister
from models import User
from utils.exceptions import (
    EmailAlreadyExistsException,
    PasswordErrorException,
    TokenInvalidException,
    UserAlreadyExistsException,
)
from utils.security import (
    decode_token,
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)


async def create_user(db: AsyncSession, user_data: UserRegister):
    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalars().first():
        raise UserAlreadyExistsException()

    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalars().first():
        raise EmailAlreadyExistsException()

    hashed_password = hash_password(user_data.password)
    new_user = User(
        username=user_data.username, email=user_data.email, password=hashed_password
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def authenticate_user(db: AsyncSession, user_data: UserLogin):
    result = await db.execute(select(User).where(User.username == user_data.username))
    user = result.scalars().first()
    if not user or not verify_password(user_data.password, user.password):
        raise PasswordErrorException()
    await db.execute(delete(UserToken).where(UserToken.user_id == user.id))
    access_token = create_access_token({"user_id": user.id})
    refresh_token = create_refresh_token({"user_id": user.id})
    user_token = UserToken(user_id=user.id, refresh_token=refresh_token)
    db.add(user_token)
    await db.commit()
    await db.refresh(user_token)
    return user, access_token, refresh_token


async def refresh_access_token(db: AsyncSession, refresh_token: str):
    _payload = decode_token(refresh_token, expected_type="refresh")
    result = await db.execute(
        select(UserToken).where(UserToken.refresh_token == refresh_token)
    )
    user_token = result.scalars().first()
    if not user_token:
        raise TokenInvalidException()
    access_token = create_access_token({"user_id": user_token.user_id})
    new_refresh_token = create_refresh_token({"user_id": user_token.user_id})
    user_token.refresh_token = new_refresh_token
    await db.commit()
    await db.refresh(user_token)
    return access_token, new_refresh_token


async def update_user(db: AsyncSession, user_id: int, username: str = None, email: str = None):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if user:
        if username:
            user.username = username
        if email:
            user.email = email
        await db.commit()


async def update_password(db: AsyncSession, user_id: int, old_password: str, new_password: str) -> bool:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user or not verify_password(old_password, user.password):
        return False
    user.password = hash_password(new_password)
    await db.commit()
    return True
