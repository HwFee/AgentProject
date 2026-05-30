"""开发环境默认用户 seed 脚本

用法:
    cd backend
    venv\Scripts\python.exe scripts\seed_dev_user.py

环境变量:
    DEV_USERNAME (default: HwFee)
    DEV_PASSWORD (default: devpassword123)
    DEV_EMAIL    (default: shujiehe26@gmail.com)
"""

import asyncio
import os
import sys

# 将 backend 目录加入路径，以便导入项目模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from config.database import worker_engine
from models.user import User
from utils.security import hash_password


async def seed_dev_user():
    username = os.environ.get("DEV_USERNAME", "HwFee")
    password = os.environ.get("DEV_PASSWORD", "devpassword123")
    email = os.environ.get("DEV_EMAIL", "shujiehe26@gmail.com")

    if not password:
        print("错误: DEV_PASSWORD 不能为空")
        sys.exit(1)

    SessionLocal = async_sessionmaker(bind=worker_engine, expire_on_commit=False)
    async with SessionLocal() as session:
        # 检查用户是否已存在
        result = await session.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()

        if user:
            # 更新现有用户
            user.email = email
            user.password = hash_password(password)
            await session.commit()
            print(f"已更新开发用户: {username} ({email})")
        else:
            # 创建新用户
            new_user = User(
                username=username,
                email=email,
                password=hash_password(password),
            )
            session.add(new_user)
            await session.commit()
            print(f"已创建开发用户: {username} ({email})")

    await worker_engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_dev_user())
