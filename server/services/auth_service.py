"""인증 비즈니스 로직"""
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from core.security import get_password_hash, verify_password, create_access_token
from core.config import settings
from repositories.user_repository import UserRepository
from models.user import User


class AuthService:
    """인증 서비스"""

    def __init__(self, db: Session):
        """
        AuthService 초기화

        Args:
            db: SQLAlchemy 세션
        """
        self.db = db
        self.user_repo = UserRepository(db)

    def register_user(self, username: str, password: str) -> Tuple[bool, Optional[User], Optional[str]]:
        """
        새로운 사용자 등록

        Args:
            username: 사용자명
            password: 비밀번호

        Returns:
            Tuple[bool, Optional[User], Optional[str]]: (성공 여부, 사용자, 에러 메시지)
        """
        # 사용자명 중복 확인
        if self.user_repo.user_exists(username):
            return False, None, "이미 사용 중인 사용자 이름입니다"

        # 비밀번호 해싱
        hashed_password = get_password_hash(password)

        # 사용자 생성
        try:
            user = self.user_repo.create_user(username, hashed_password)
            return True, user, None
        except Exception as e:
            return False, None, f"사용자 등록 중 오류 발생: {str(e)}"

    def login_user(self, username: str, password: str) -> Tuple[bool, Optional[User], Optional[str]]:
        """
        사용자 로그인

        Args:
            username: 사용자명
            password: 비밀번호

        Returns:
            Tuple[bool, Optional[User], Optional[str]]: (성공 여부, 사용자, 에러 메시지)
        """
        # 사용자 조회
        user = self.user_repo.get_by_username(username)
        if not user:
            return False, None, "사용자 이름 또는 비밀번호가 올바르지 않습니다"

        # 비밀번호 검증
        if not verify_password(password, user.hashed_password):
            return False, None, "사용자 이름 또는 비밀번호가 올바르지 않습니다"

        return True, user, None

    def create_access_token_for_user(self, user: User) -> str:
        """
        사용자를 위한 액세스 토큰 생성

        Args:
            user: 사용자

        Returns:
            str: JWT 액세스 토큰
        """
        return create_access_token(data={"sub": user.username})

    def verify_access_token(self, token: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        액세스 토큰 검증

        Args:
            token: JWT 토큰

        Returns:
            Tuple[bool, Optional[str], Optional[str]]: (성공 여부, 사용자명, 에러 메시지)
        """
        from core.security import decode_token

        payload = decode_token(token)
        if payload is None:
            return False, None, "토큰이 유효하지 않습니다"

        username = payload.get("sub")
        if username is None:
            return False, None, "토큰에 사용자 정보가 없습니다"

        return True, username, None

    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        사용자명으로 사용자 조회

        Args:
            username: 사용자명

        Returns:
            Optional[User]: 조회된 사용자 또는 None
        """
        return self.user_repo.get_by_username(username)
