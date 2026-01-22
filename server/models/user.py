"""사용자 데이터베이스 모델"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    """사용자 모델"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 관계 설정
    scores = relationship("Score", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(username={self.username})>"
