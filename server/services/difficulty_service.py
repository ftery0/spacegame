"""난이도 설정 서비스"""
from sqlalchemy.orm import Session
from repositories.difficulty_repository import DifficultyRepository
from schemas.difficulty import DifficultySettingResponse
from typing import List, Optional


class DifficultyService:
    """난이도 설정 비즈니스 로직"""

    @staticmethod
    def get_all_difficulties(db: Session) -> List[DifficultySettingResponse]:
        """모든 난이도 설정 조회"""
        difficulties = DifficultyRepository.get_all(db)
        return [DifficultySettingResponse.model_validate(d) for d in difficulties]

    @staticmethod
    def get_difficulty_by_name(db: Session, name: str) -> Optional[DifficultySettingResponse]:
        """이름으로 난이도 설정 조회"""
        difficulty = DifficultyRepository.get_by_name(db, name)
        if difficulty:
            return DifficultySettingResponse.model_validate(difficulty)
        return None

    @staticmethod
    def get_default_difficulty(db: Session) -> Optional[DifficultySettingResponse]:
        """기본 난이도 조회"""
        difficulty = DifficultyRepository.get_default(db)
        if difficulty:
            return DifficultySettingResponse.model_validate(difficulty)
        return None
