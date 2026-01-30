"""의존성 주입 설정"""
from functools import lru_cache
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from .config import Settings
from database import get_db


@lru_cache()
def get_settings() -> Settings:
    """
    애플리케이션 설정 싱글톤 제공

    Returns:
        Settings: 애플리케이션 설정
    """
    return Settings()


async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> "User":
    """
    현재 로그인한 사용자 조회

    Args:
        request: HTTP 요청
        db: 데이터베이스 세션

    Returns:
        User: 현재 사용자

    Raises:
        HTTPException: 인증 실패 시
    """
    from models.user import User
    from .security import decode_token

    # Bearer 토큰 추출
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증 정보가 유효하지 않습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth_header.split(" ")[1]
    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증 정보가 유효하지 않습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증 정보가 유효하지 않습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자를 찾을 수 없습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
