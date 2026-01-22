"""사용자 관련 Pydantic 스키마"""
from pydantic import BaseModel, Field
from datetime import datetime


class UserCreate(BaseModel):
    """회원가입 요청"""
    username: str = Field(..., min_length=3, max_length=20, description="사용자 이름 (3-20자)")
    password: str = Field(..., min_length=4, max_length=50, description="비밀번호 (4자 이상)")


class UserLogin(BaseModel):
    """로그인 요청"""
    username: str = Field(..., description="사용자 이름")
    password: str = Field(..., description="비밀번호")


class UserResponse(BaseModel):
    """사용자 정보 응답"""
    id: int
    username: str
    created_at: datetime

    class Config:
        from_attributes = True
