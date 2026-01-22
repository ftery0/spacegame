"""게임 통계 모델"""
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class GameStat(Base):
    """게임 통계 테이블"""
    __tablename__ = "game_stats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # 기본 정보
    game_date = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    difficulty = Column(String(20), nullable=False)  # 'easy', 'medium', 'hard'
    final_score = Column(Integer, nullable=False)

    # 플레이 통계
    play_time = Column(Integer, nullable=False)  # 초 단위
    stones_destroyed = Column(Integer, default=0)
    enemies_destroyed = Column(Integer, default=0)

    # 전투 통계
    missiles_fired = Column(Integer, default=0)
    missiles_hit = Column(Integer, default=0)
    accuracy = Column(Float, default=0.0)  # 명중률 (%)

    # 콤보/스킬 통계
    max_combo = Column(Integer, default=0)
    skills_used = Column(Integer, default=0)
    items_collected = Column(Integer, default=0)

    # 스테이지 정보
    max_stage_reached = Column(Integer, default=1)
    boss_defeated = Column(Boolean, default=False)

    # 관계
    user = relationship("User", back_populates="game_stats")

    def calculate_accuracy(self):
        """명중률 계산"""
        if self.missiles_fired > 0:
            self.accuracy = (self.missiles_hit / self.missiles_fired) * 100
        else:
            self.accuracy = 0.0
