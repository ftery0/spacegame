"""공통 Pydantic 스키마"""
from pydantic import BaseModel
from .user import UserResponse


class Token(BaseModel):
    """토큰 응답"""
    access_token: str
    token_type: str
    user: UserResponse
