"""게임 통계 서비스"""
from sqlalchemy.orm import Session
from repositories.game_stat_repository import GameStatRepository
from schemas.game_stat import GameStatCreate, GameStatResponse, UserStatsSummary
from typing import List


class GameStatService:
    """게임 통계 비즈니스 로직"""

    @staticmethod
    def save_game_stats(db: Session, user_id: int, stats: GameStatCreate) -> GameStatResponse:
        """게임 통계 저장"""
        stat_data = stats.model_dump()
        game_stat = GameStatRepository.create(db, user_id, stat_data)
        return GameStatResponse.model_validate(game_stat)

    @staticmethod
    def get_user_games(db: Session, user_id: int, limit: int = 10) -> List[GameStatResponse]:
        """사용자의 게임 기록 조회"""
        stats = GameStatRepository.get_by_user(db, user_id, limit)
        return [GameStatResponse.model_validate(stat) for stat in stats]

    @staticmethod
    def get_user_summary(db: Session, user_id: int) -> UserStatsSummary:
        """사용자 통계 요약 조회"""
        summary = GameStatRepository.get_user_summary(db, user_id)
        return UserStatsSummary(**summary)
