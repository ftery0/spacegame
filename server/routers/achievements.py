"""업적 API 라우터"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from core.dependencies import get_current_user
from models.user import User
from schemas.achievement import (
    AchievementResponse,
    UserAchievementResponse,
    AchievementUnlockRequest
)
from services.achievement_service import AchievementService
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/achievements", tags=["achievements"])


@router.get("", response_model=List[AchievementResponse])
def get_all_achievements(db: Session = Depends(get_db)):
    """
    모든 업적 조회

    게임에서 사용 가능한 모든 업적을 반환합니다.
    """
    return AchievementService.get_all_achievements(db)


@router.get("/my", response_model=List[UserAchievementResponse])
def get_my_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    내 업적 조회

    현재 사용자가 달성한 업적 목록을 반환합니다.
    """
    return AchievementService.get_user_achievements(db, current_user.id)


@router.post("/unlock", response_model=UserAchievementResponse, status_code=status.HTTP_201_CREATED)
def unlock_achievement(
    request: AchievementUnlockRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    업적 언락

    특정 업적을 언락합니다.
    """
    try:
        return AchievementService.unlock_achievement(
            db, current_user.id, request.achievement_code, request.progress
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"업적 언락 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="업적 언락에 실패했습니다"
        )
