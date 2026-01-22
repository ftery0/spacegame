"""Score repository for data access"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from models.user import User
from models.score import Score
from .base import BaseRepository


class ScoreRepository(BaseRepository[Score]):
    """점수 데이터 접근 계층"""

    def __init__(self, db: Session):
        """
        ScoreRepository 초기화

        Args:
            db: SQLAlchemy 세션
        """
        super().__init__(db, Score)

    def get_user_scores(self, user_id: int, limit: int = 100) -> List[Score]:
        """
        특정 사용자의 점수 조회

        Args:
            user_id: 사용자 ID
            limit: 조회할 개수

        Returns:
            List[Score]: 사용자의 점수 목록
        """
        return (
            self.db.query(Score)
            .filter(Score.user_id == user_id)
            .order_by(desc(Score.created_at))
            .limit(limit)
            .all()
        )

    def get_top_scores(self, limit: int = 10) -> List[dict]:
        """
        상위 점수 조회 (각 사용자의 최고 점수 기준)

        Args:
            limit: 조회할 개수

        Returns:
            List[dict]: 상위 점수 및 사용자 정보
        """
        subquery = (
            self.db.query(
                Score.user_id,
                func.max(Score.score).label('best_score'),
                func.max(Score.created_at).label('latest_date')
            )
            .group_by(Score.user_id)
            .subquery()
        )

        scores = (
            self.db.query(Score, User.username)
            .join(User, Score.user_id == User.id)
            .join(
                subquery,
                (Score.user_id == subquery.c.user_id) &
                (Score.score == subquery.c.best_score)
            )
            .order_by(desc(Score.score), Score.created_at)
            .limit(limit)
            .all()
        )

        ranking = []
        for rank, (score, username) in enumerate(scores, start=1):
            ranking.append({
                "rank": rank,
                "user_id": score.user_id,
                "username": username,
                "score": score.score,
                "created_at": score.created_at
            })

        return ranking

    def get_user_best_score(self, user_id: int) -> Optional[int]:
        """
        사용자의 최고 점수 조회

        Args:
            user_id: 사용자 ID

        Returns:
            Optional[int]: 최고 점수 또는 None
        """
        result = (
            self.db.query(func.max(Score.score))
            .filter(Score.user_id == user_id)
            .scalar()
        )
        return result

    def get_user_rank(self, user_id: int, best_score: int) -> int:
        """
        사용자의 랭킹 조회

        Args:
            user_id: 사용자 ID
            best_score: 사용자의 최고 점수

        Returns:
            int: 사용자의 랭킹
        """
        subquery = (
            self.db.query(
                Score.user_id,
                func.max(Score.score).label('best_score')
            )
            .group_by(Score.user_id)
            .subquery()
        )

        higher_count = (
            self.db.query(func.count(subquery.c.user_id))
            .filter(subquery.c.best_score > best_score)
            .scalar()
        )

        return higher_count + 1

    def create_score(self, user_id: int, score: int) -> Score:
        """
        새로운 점수 생성

        Args:
            user_id: 사용자 ID
            score: 점수

        Returns:
            Score: 생성된 점수
        """
        new_score = Score(user_id=user_id, score=score)
        return self.create(new_score)
