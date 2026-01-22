"""인증 관련 API 라우트"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from schemas.user import UserCreate, UserLogin, UserResponse
from schemas.common import Token
from services.auth_service import AuthService
from core.security import decode_token

router = APIRouter(prefix="/api/auth", tags=["인증"])
limiter = Limiter(key_func=get_remote_address)


async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
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


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register(
    request: Request,
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    회원가입

    - **username**: 사용자 이름 (3-20자, 고유해야 함)
    - **password**: 비밀번호 (4자 이상)
    """
    auth_service = AuthService(db)

    success, user, error = auth_service.register_user(user_data.username, user_data.password)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    # 토큰 생성
    access_token = auth_service.create_access_token_for_user(user)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
async def login(
    request: Request,
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    로그인

    - **username**: 사용자 이름
    - **password**: 비밀번호
    """
    auth_service = AuthService(db)

    success, user, error = auth_service.login_user(login_data.username, login_data.password)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error,
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 토큰 생성
    access_token = auth_service.create_access_token_for_user(user)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    현재 로그인한 사용자 정보 조회
    """
    return current_user
