"""게임 통계 API 라우터"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from core.dependencies import get_current_user
from models.user import User
from schemas.game_stat import GameStatCreate, GameStatResponse, UserStatsSummary
from services.game_stat_service import GameStatService
from services.achievement_service import AchievementService
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/stats", tags=["game-stats"])


@router.post("", response_model=GameStatResponse, status_code=status.HTTP_201_CREATED)
def save_game_stats(
    stats: GameStatCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    게임 통계 저장

    게임 종료 후 상세 통계를 저장합니다.
    """
    try:
        # 통계 저장
        game_stat = GameStatService.save_game_stats(db, current_user.id, stats)

        # 업적 체크
        stats_dict = stats.model_dump()
        stats_dict['accuracy'] = (stats.missiles_hit / stats.missiles_fired * 100) if stats.missiles_fired > 0 else 0
        unlocked_achievements = AchievementService.check_and_unlock_achievements(
            db, current_user.id, stats_dict
        )

        if unlocked_achievements:
            logger.info(f"사용자 {current_user.username}이(가) 업적 언락: {unlocked_achievements}")

        return game_stat

    except Exception as e:
        logger.error(f"게임 통계 저장 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="게임 통계 저장에 실패했습니다"
        )


@router.get("/my", response_model=List[GameStatResponse])
def get_my_game_stats(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    내 게임 기록 조회

    최근 게임 기록을 조회합니다.
    """
    return GameStatService.get_user_games(db, current_user.id, limit)


@router.get("/summary", response_model=UserStatsSummary)
def get_my_stats_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    내 통계 요약 조회

    전체 게임 플레이 통계를 요약하여 반환합니다.
    """
    return GameStatService.get_user_summary(db, current_user.id)
