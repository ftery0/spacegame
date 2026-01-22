"""업적 레포지토리"""
from sqlalchemy.orm import Session, joinedload
from models.achievement import Achievement
from models.user_achievement import UserAchievement
from typing import List, Optional


class AchievementRepository:
    """업적 데이터 액세스"""

    @staticmethod
    def get_all(db: Session) -> List[Achievement]:
        """모든 업적 조회"""
        return db.query(Achievement).all()

    @staticmethod
    def get_by_code(db: Session, code: str) -> Optional[Achievement]:
        """코드로 업적 조회"""
        return db.query(Achievement).filter(Achievement.code == code).first()

    @staticmethod
    def get_user_achievements(db: Session, user_id: int) -> List[UserAchievement]:
        """사용자의 업적 조회"""
        return db.query(UserAchievement).options(
            joinedload(UserAchievement.achievement)
        ).filter(UserAchievement.user_id == user_id).all()

    @staticmethod
    def unlock_achievement(db: Session, user_id: int, achievement_id: int, progress: int = 100) -> UserAchievement:
        """업적 언락"""
        # 이미 언락되어 있는지 확인
        existing = db.query(UserAchievement).filter(
            UserAchievement.user_id == user_id,
            UserAchievement.achievement_id == achievement_id
        ).first()

        if existing:
            # 진행도 업데이트
            existing.progress = progress
            existing.completed = (progress >= 100)
            db.commit()
            db.refresh(existing)
            return existing

        # 새로 생성
        user_achievement = UserAchievement(
            user_id=user_id,
            achievement_id=achievement_id,
            progress=progress,
            completed=(progress >= 100)
        )
        db.add(user_achievement)
        db.commit()
        db.refresh(user_achievement)
        return user_achievement

    @staticmethod
    def check_achievement_unlocked(db: Session, user_id: int, achievement_code: str) -> bool:
        """업적이 언락되어 있는지 확인"""
        achievement = AchievementRepository.get_by_code(db, achievement_code)
        if not achievement:
            return False

        user_achievement = db.query(UserAchievement).filter(
            UserAchievement.user_id == user_id,
            UserAchievement.achievement_id == achievement.id,
            UserAchievement.completed == True
        ).first()

        return user_achievement is not None
