"""보안 관련 함수"""
import logging
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt

from .config import settings

logger = logging.getLogger(__name__)

# bcrypt는 최대 72바이트까지만 지원
MAX_PASSWORD_BYTES = 72


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    비밀번호 검증

    Args:
        plain_password: 평문 비밀번호
        hashed_password: 해시된 비밀번호

    Returns:
        bool: 일치 여부
    """
    try:
        # bcrypt 제한에 맞게 비밀번호 자르기
        password_bytes = plain_password.encode('utf-8')
        if len(password_bytes) > MAX_PASSWORD_BYTES:
            logger.warning(f"비밀번호가 {MAX_PASSWORD_BYTES}바이트를 초과하여 자릅니다.")
            password_bytes = password_bytes[:MAX_PASSWORD_BYTES]

        return bcrypt.checkpw(password_bytes, hashed_password.encode('utf-8'))
    except Exception as e:
        logger.error(f"비밀번호 검증 중 오류 발생: {str(e)}", exc_info=True)
        return False


def get_password_hash(password: str) -> str:
    """
    비밀번호 해싱

    Args:
        password: 평문 비밀번호

    Returns:
        str: 해시된 비밀번호

    Raises:
        ValueError: 비밀번호가 너무 긴 경우
    """
    try:
        # bcrypt 제한 체크 (72바이트)
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > MAX_PASSWORD_BYTES:
            logger.warning(f"비밀번호가 {MAX_PASSWORD_BYTES}바이트를 초과하여 자동으로 자릅니다. (현재: {len(password_bytes)}바이트)")
            password_bytes = password_bytes[:MAX_PASSWORD_BYTES]

        # bcrypt로 해싱
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        logger.debug("비밀번호 해싱 완료")
        return hashed.decode('utf-8')
    except Exception as e:
        logger.error(f"비밀번호 해싱 중 오류 발생: {str(e)}", exc_info=True)
        raise ValueError(f"비밀번호 해싱 실패: {str(e)}")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    JWT 액세스 토큰 생성

    Args:
        data: 토큰에 포함할 데이터
        expires_delta: 만료 시간

    Returns:
        str: JWT 토큰
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """
    JWT 토큰 디코딩

    Args:
        token: JWT 토큰

    Returns:
        dict: 디코딩된 데이터 또는 None
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
