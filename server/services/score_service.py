"""점수 비즈니스 로직"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from repositories.score_repository import ScoreRepository
from models.user import User
from models.score import Score


class ScoreService:
    """점수 서비스"""

    def __init__(self, db: Session):
        """
        ScoreService 초기화

        Args:
            db: SQLAlchemy 세션
        """
        self.db = db
        self.score_repo = ScoreRepository(db)

    def create_score(self, user_id: int, score: int) -> Dict[str, Any]:
        """
        새로운 점수 생성

        Args:
            user_id: 사용자 ID
            score: 점수

        Returns:
            Dict: 생성된 점수 정보
        """
        score_obj = self.score_repo.create_score(user_id, score)
        user = self.db.query(User).filter(User.id == user_id).first()

        return {
            "id": score_obj.id,
            "user_id": score_obj.user_id,
            "score": score_obj.score,
            "created_at": score_obj.created_at,
            "username": user.username if user else "Unknown"
        }

    def get_user_scores(self, user_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """
        사용자의 점수 목록 조회

        Args:
            user_id: 사용자 ID
            limit: 조회할 개수

        Returns:
            List[Dict]: 사용자의 점수 목록
        """
        scores = self.score_repo.get_user_scores(user_id, limit)
        user = self.db.query(User).filter(User.id == user_id).first()

        result = []
        for score in scores:
            result.append({
                "id": score.id,
                "user_id": score.user_id,
                "score": score.score,
                "created_at": score.created_at,
                "username": user.username if user else "Unknown"
            })

        return result

    def get_top_scores(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        상위 점수 조회

        Args:
            limit: 조회할 개수

        Returns:
            List[Dict]: 상위 점수 목록
        """
        return self.score_repo.get_top_scores(limit)

    def get_recent_scores(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        최근 점수 조회

        Args:
            limit: 조회할 개수

        Returns:
            List[Dict]: 최근 점수 목록
        """
        scores = (
            self.db.query(Score, User.username)
            .join(User, Score.user_id == User.id)
            .order_by(desc(Score.created_at))
            .limit(limit)
            .all()
        )

        result = []
        for score, username in scores:
            result.append({
                "id": score.id,
                "user_id": score.user_id,
                "score": score.score,
                "created_at": score.created_at,
                "username": username
            })

        return result

    def get_user_statistics(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        사용자의 통계 조회

        Args:
            user_id: 사용자 ID

        Returns:
            Optional[Dict]: 사용자의 통계 정보
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        # 사용자의 모든 점수 조회
        user_scores = self.score_repo.get_user_scores(user_id, limit=1000)

        if not user_scores:
            return None

        # 통계 계산
        scores_values = [s.score for s in user_scores]
        total_games = len(scores_values)
        best_score = max(scores_values)
        average_score = sum(scores_values) / total_games

        # 랭킹 계산
        rank = self.score_repo.get_user_rank(user_id, best_score)

        return {
            "user_id": user.id,
            "username": user.username,
            "total_games": total_games,
            "best_score": best_score,
            "average_score": round(average_score, 2),
            "rank": rank
        }

    def delete_score(self, user_id: int, score_id: int) -> bool:
        """
        점수 삭제 (본인의 점수만 가능)

        Args:
            user_id: 사용자 ID
            score_id: 삭제할 점수 ID

        Returns:
            bool: 삭제 성공 여부
        """
        score = self.score_repo.get_by_id(score_id)
        if not score or score.user_id != user_id:
            return False

        return self.score_repo.delete(score_id)
