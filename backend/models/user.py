from sqlalchemy import String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class User(Base):
    __tablename__ = "users"
    username: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, comment="用户名"
    )
    email: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, comment="邮箱"
    )
    bio: Mapped[str] = mapped_column(
        Text, nullable=True, comment="个人简介", default="这个人很懒,还没有任何介绍"
    )
    gender: Mapped[str] = mapped_column(String(10), default="unknown", comment="性别")
    avatar_url: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="头像URL", default="/static/default.png"
    )
    password: Mapped[str] = mapped_column(String(255), nullable=False, comment="密码")
    is_admin: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, comment="是否管理员"
    )


class UserToken(Base):
    __tablename__ = "user_tokens"
    user_id: Mapped[int] = mapped_column(nullable=False, comment="用户ID")
    refresh_token: Mapped[str] = mapped_column(
        String(512), nullable=False, comment="RefreshToken"
    )
