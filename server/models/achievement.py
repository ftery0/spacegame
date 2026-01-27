"""업적 모델"""
from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Achievement(Base):
    """업적 정의 테이블"""
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)  # 'first_game', etc.
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=False)
    icon = Column(String(200), nullable=True)  # 아이콘 경로
    category = Column(String(50), nullable=True)  # 'combat', 'survival', 'combo', etc.

    # 달성 조건
    condition_type = Column(String(50), nullable=False)  # 'score', 'combo', 'accuracy', etc.
    condition_value = Column(Integer, nullable=True)

    # 보상
    reward_type = Column(String(50), nullable=True)  # 'badge', 'skin', 'coin'
    reward_value = Column(Integer, nullable=True)

    # 난이도
    rarity = Column(String(20), default="common")  # 'common', 'rare', 'epic', 'legendary'

    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    # 관계
    user_achievements = relationship("UserAchievement", back_populates="achievement")
