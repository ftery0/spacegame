"""점수 관련 Pydantic 스키마"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ScoreCreate(BaseModel):
    """점수 생성 요청"""
    score: int = Field(..., ge=0, description="점수")


class ScoreResponse(BaseModel):
    """점수 응답"""
    id: int
    user_id: int
    score: int
    created_at: datetime
    username: Optional[str] = None  # 조인으로 추가되는 필드

    class Config:
        from_attributes = True


class RankingResponse(BaseModel):
    """랭킹 응답"""
    rank: int
    user_id: int
    username: str
    score: int
    created_at: datetime


class UserStatsResponse(BaseModel):
    """사용자 통계 응답"""
    user_id: int
    username: str
    total_games: int
    best_score: int
    average_score: float
    rank: Optional[int] = None
