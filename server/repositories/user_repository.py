"""User repository for data access"""
from typing import Optional
from sqlalchemy.orm import Session
from models.user import User
from .base import BaseRepository


class UserRepository(BaseRepository[User]):
    """사용자 데이터 접근 계층"""

    def __init__(self, db: Session):
        """
        UserRepository 초기화

        Args:
            db: SQLAlchemy 세션
        """
        super().__init__(db, User)

    def get_by_username(self, username: str) -> Optional[User]:
        """
        사용자명으로 사용자 조회

        Args:
            username: 조회할 사용자명

        Returns:
            Optional[User]: 조회된 사용자 또는 None
        """
        return self.db.query(User).filter(User.username == username).first()

    def create_user(self, username: str, hashed_password: str) -> User:
        """
        새로운 사용자 생성

        Args:
            username: 사용자명
            hashed_password: 해시된 비밀번호

        Returns:
            User: 생성된 사용자
        """
        user = User(username=username, hashed_password=hashed_password)
        return self.create(user)

    def user_exists(self, username: str) -> bool:
        """
        사용자 존재 여부 확인

        Args:
            username: 확인할 사용자명

        Returns:
            bool: 사용자 존재 여부
        """
        return self.db.query(User).filter(User.username == username).first() is not None
