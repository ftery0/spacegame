"""난이도 설정 API 라우터"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schemas.difficulty import DifficultySettingResponse
from services.difficulty_service import DifficultyService
from typing import List

router = APIRouter(prefix="/api/difficulties", tags=["difficulties"])


@router.get("", response_model=List[DifficultySettingResponse])
def get_all_difficulties(db: Session = Depends(get_db)):
    """
    모든 난이도 설정 조회

    게임에서 사용 가능한 모든 난이도 설정을 반환합니다.
    """
    return DifficultyService.get_all_difficulties(db)


@router.get("/{name}", response_model=DifficultySettingResponse)
def get_difficulty_by_name(name: str, db: Session = Depends(get_db)):
    """
    특정 난이도 설정 조회

    이름으로 난이도 설정을 조회합니다.
    - name: 'easy', 'medium', 'hard'
    """
    difficulty = DifficultyService.get_difficulty_by_name(db, name)
    if not difficulty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"난이도 설정을 찾을 수 없습니다: {name}"
        )
    return difficulty


@router.get("/default/settings", response_model=DifficultySettingResponse)
def get_default_difficulty(db: Session = Depends(get_db)):
    """
    기본 난이도 설정 조회

    기본 난이도 (중급)를 반환합니다.
    """
    difficulty = DifficultyService.get_default_difficulty(db)
    if not difficulty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="기본 난이도 설정을 찾을 수 없습니다"
        )
    return difficulty
