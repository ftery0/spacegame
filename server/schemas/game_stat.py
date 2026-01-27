"""게임 통계 스키마"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class GameStatCreate(BaseModel):
    """게임 통계 생성 스키마"""
    difficulty: str = Field(..., description="난이도")
    final_score: int = Field(..., ge=0, description="최종 점수")
    play_time: int = Field(..., ge=0, description="플레이 시간 (초)")
    stones_destroyed: int = Field(default=0, ge=0)
    enemies_destroyed: int = Field(default=0, ge=0)
    missiles_fired: int = Field(default=0, ge=0)
    missiles_hit: int = Field(default=0, ge=0)
    max_combo: int = Field(default=0, ge=0)
    skills_used: int = Field(default=0, ge=0)
    items_collected: int = Field(default=0, ge=0)
    max_stage_reached: int = Field(default=1, ge=1)
    boss_defeated: bool = Field(default=False)


class GameStatResponse(BaseModel):
    """게임 통계 응답 스키마"""
    id: int
    user_id: int
    game_date: datetime
    difficulty: str
    final_score: int
    play_time: int
    stones_destroyed: int
    enemies_destroyed: int
    missiles_fired: int
    missiles_hit: int
    accuracy: float
    max_combo: int
    skills_used: int
    items_collected: int
    max_stage_reached: int
    boss_defeated: bool

    class Config:
        from_attributes = True


class UserStatsSummary(BaseModel):
    """사용자 통계 요약"""
    total_games: int
    total_play_time: int
    highest_score: int
    total_stones_destroyed: int
    total_enemies_destroyed: int
    average_accuracy: float
    best_combo: int
    total_skills_used: int
    total_items_collected: int
    max_stage_ever: int
    bosses_defeated_count: int
