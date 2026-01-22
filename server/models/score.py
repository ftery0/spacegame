"""점수 데이터베이스 모델"""
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Score(Base):
    """점수 모델"""
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    score = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 관계 설정
    user = relationship("User", back_populates="scores")

    def __repr__(self):
        return f"<Score(user_id={self.user_id}, score={self.score})>"
