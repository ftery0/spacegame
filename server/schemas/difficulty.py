"""난이도 설정 스키마"""
from pydantic import BaseModel
from datetime import datetime


class DifficultySettingResponse(BaseModel):
    """난이도 설정 응답 스키마"""
    id: int
    name: str
    display_name: str
    stone_speed: float
    stone_spawn_interval: int
    enemy_spawn_chance: float
    enemy_speed: float
    enemy_evasion_skill: float
    enemy_attack_rate: int
    score_multiplier: float
    player_health: int
    created_at: datetime

    class Config:
        from_attributes = True
