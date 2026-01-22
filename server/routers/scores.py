"""점수 관련 API 라우트"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.user import User
from schemas.score import (
    ScoreCreate, ScoreResponse, RankingResponse, UserStatsResponse
)
from services.score_service import ScoreService
from .auth import get_current_user

router = APIRouter(prefix="/api/scores", tags=["점수"])
limiter = Limiter(key_func=get_remote_address)


@router.post("", response_model=ScoreResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
async def create_score(
    request: Request,
    score_data: ScoreCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    새로운 점수 저장 (로그인 필요)

    - **score**: 게임 점수 (0 이상)
    """
    score_service = ScoreService(db)
    return score_service.create_score(current_user.id, score_data.score)


@router.get("/top", response_model=List[RankingResponse])
async def get_top_scores(limit: int = 10, db: Session = Depends(get_db)):
    """
    상위 점수 조회 (각 사용자의 최고 점수 기준)

    - **limit**: 조회할 개수 (기본값: 10, 최대: 100)
    """
    if limit > 100:
        limit = 100

    score_service = ScoreService(db)
    return score_service.get_top_scores(limit)


@router.get("/recent", response_model=List[ScoreResponse])
async def get_recent_scores(limit: int = 20, db: Session = Depends(get_db)):
    """
    최근 점수 조회

    - **limit**: 조회할 개수 (기본값: 20, 최대: 100)
    """
    if limit > 100:
        limit = 100

    score_service = ScoreService(db)
    return score_service.get_recent_scores(limit)


@router.get("/my", response_model=List[ScoreResponse])
async def get_my_scores(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    내 점수 기록 조회 (로그인 필요)
    """
    score_service = ScoreService(db)
    return score_service.get_user_scores(current_user.id)


@router.get("/stats", response_model=UserStatsResponse)
async def get_my_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    내 통계 조회 (로그인 필요)
    """
    score_service = ScoreService(db)
    stats = score_service.get_user_statistics(current_user.id)

    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="아직 플레이 기록이 없습니다"
        )

    return stats


@router.delete("/{score_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_score(
    score_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    점수 삭제 (본인의 점수만 삭제 가능)

    - **score_id**: 삭제할 점수 ID
    """
    score_service = ScoreService(db)
    success = score_service.delete_score(current_user.id, score_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="점수를 찾을 수 없거나 본인의 점수가 아닙니다"
        )

    return None
