"""사용자 업적 모델"""
from sqlalchemy import Column, Integer, Boolean, ForeignKey, TIMESTAMP, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class UserAchievement(Base):
    """사용자 업적 테이블"""
    __tablename__ = "user_achievements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    achievement_id = Column(Integer, ForeignKey("achievements.id", ondelete="CASCADE"), nullable=False)

    achieved_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    progress = Column(Integer, default=0)  # 진행도 (%)
    completed = Column(Boolean, default=False)

    # 관계
    user = relationship("User", back_populates="user_achievements")
    achievement = relationship("Achievement", back_populates="user_achievements")

    # 제약조건: 한 사용자가 같은 업적을 중복으로 가질 수 없음
    __table_args__ = (
        UniqueConstraint('user_id', 'achievement_id', name='unique_user_achievement'),
    )
