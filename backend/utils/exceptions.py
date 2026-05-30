from typing import Any, Optional
from fastapi import status


class AppException(Exception):
    def __init__(
        self,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        message: str = "服务内部错误",
        data: Optional[Any] = None,
    ):
        self.status_code = status_code
        self.message = message
        self.data = data
        super().__init__(self.message)


class UserNotFoundException(AppException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, message="该用户不存在")


class UserAlreadyExistsException(AppException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_409_CONFLICT, message="用户已存在")


class EmailAlreadyExistsException(AppException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_409_CONFLICT, message="邮箱已存在")


class PasswordErrorException(AppException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, message="用户名或密码错误"
        )


class TokenInvalidException(AppException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Token无效或已过期或类型不匹配",
        )
