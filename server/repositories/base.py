"""기본 repository 클래스"""
from typing import Generic, TypeVar, Optional, List, Type
from sqlalchemy.orm import Session
from sqlalchemy import select

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """기본 repository 추상 클래스"""

    def __init__(self, db: Session, model: Type[T]):
        """
        Repository 초기화

        Args:
            db: SQLAlchemy 세션
            model: ORM 모델 클래스
        """
        self.db = db
        self.model = model

    def get_by_id(self, id: int) -> Optional[T]:
        """
        ID로 항목 조회

        Args:
            id: 조회할 항목의 ID

        Returns:
            Optional[T]: 조회된 항목 또는 None
        """
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        """
        모든 항목 조회

        Args:
            limit: 조회할 개수
            offset: 시작 위치

        Returns:
            List[T]: 조회된 항목 목록
        """
        return self.db.query(self.model).limit(limit).offset(offset).all()

    def create(self, obj: T) -> T:
        """
        새로운 항목 생성

        Args:
            obj: 생성할 객체

        Returns:
            T: 생성된 객체
        """
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, id: int, obj_data: dict) -> Optional[T]:
        """
        항목 업데이트

        Args:
            id: 업데이트할 항목의 ID
            obj_data: 업데이트할 데이터

        Returns:
            Optional[T]: 업데이트된 항목 또는 None
        """
        obj = self.get_by_id(id)
        if not obj:
            return None

        for key, value in obj_data.items():
            setattr(obj, key, value)

        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, id: int) -> bool:
        """
        항목 삭제

        Args:
            id: 삭제할 항목의 ID

        Returns:
            bool: 삭제 성공 여부
        """
        obj = self.get_by_id(id)
        if not obj:
            return False

        self.db.delete(obj)
        self.db.commit()
        return True
