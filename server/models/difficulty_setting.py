"""난이도 설정 모델"""
from sqlalchemy import Column, Integer, String, Float, TIMESTAMP
from sqlalchemy.sql import func
from database import Base


class DifficultySetting(Base):
    """난이도 설정 테이블"""
    __tablename__ = "difficulty_settings"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(20), unique=True, nullable=False, index=True)  # 'easy', 'medium', 'hard'
    display_name = Column(String(50), nullable=False)  # '초급', '중급', '고급'

    # 게임 설정
    stone_speed = Column(Float, nullable=False)
    stone_spawn_interval = Column(Integer, nullable=False)
    enemy_spawn_chance = Column(Float, nullable=False)  # 0.0 ~ 1.0

    # AI 설정
    enemy_speed = Column(Float, nullable=False)
    enemy_evasion_skill = Column(Float, nullable=False)  # 회피 성공률
    enemy_attack_rate = Column(Integer, nullable=False)  # 공격 간격 (프레임)

    # 점수 배율
    score_multiplier = Column(Float, default=1.0)

    # 플레이어 설정
    player_health = Column(Integer, default=3)

    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
