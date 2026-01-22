"""업적 스키마"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class AchievementResponse(BaseModel):
    """업적 응답 스키마"""
    id: int
    code: str
    name: str
    description: str
    icon: Optional[str]
    category: Optional[str]
    condition_type: str
    condition_value: Optional[int]
    reward_type: Optional[str]
    reward_value: Optional[int]
    rarity: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserAchievementResponse(BaseModel):
    """사용자 업적 응답 스키마"""
    id: int
    user_id: int
    achievement_id: int
    achievement: AchievementResponse
    achieved_at: datetime
    progress: int
    completed: bool

    class Config:
        from_attributes = True


class AchievementUnlockRequest(BaseModel):
    """업적 언락 요청 스키마"""
    achievement_code: str
    progress: int = 100
