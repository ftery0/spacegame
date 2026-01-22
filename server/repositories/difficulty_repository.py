"""난이도 설정 레포지토리"""
from sqlalchemy.orm import Session
from models.difficulty_setting import DifficultySetting
from typing import List, Optional


class DifficultyRepository:
    """난이도 설정 데이터 액세스"""

    @staticmethod
    def get_all(db: Session) -> List[DifficultySetting]:
        """모든 난이도 설정 조회"""
        return db.query(DifficultySetting).all()

    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[DifficultySetting]:
        """이름으로 난이도 설정 조회"""
        return db.query(DifficultySetting).filter(
            DifficultySetting.name == name
        ).first()

    @staticmethod
    def get_default(db: Session) -> Optional[DifficultySetting]:
        """기본 난이도 (중급) 조회"""
        return DifficultyRepository.get_by_name(db, "medium")
