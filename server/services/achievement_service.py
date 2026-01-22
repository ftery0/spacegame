"""업적 서비스"""
from sqlalchemy.orm import Session
from repositories.achievement_repository import AchievementRepository
from schemas.achievement import AchievementResponse, UserAchievementResponse
from typing import List


class AchievementService:
    """업적 비즈니스 로직"""

    @staticmethod
    def get_all_achievements(db: Session) -> List[AchievementResponse]:
        """모든 업적 조회"""
        achievements = AchievementRepository.get_all(db)
        return [AchievementResponse.model_validate(ach) for ach in achievements]

    @staticmethod
    def get_user_achievements(db: Session, user_id: int) -> List[UserAchievementResponse]:
        """사용자의 업적 조회"""
        user_achievements = AchievementRepository.get_user_achievements(db, user_id)
        return [UserAchievementResponse.model_validate(ua) for ua in user_achievements]

    @staticmethod
    def unlock_achievement(db: Session, user_id: int, achievement_code: str, progress: int = 100) -> UserAchievementResponse:
        """업적 언락"""
        achievement = AchievementRepository.get_by_code(db, achievement_code)
        if not achievement:
            raise ValueError(f"업적을 찾을 수 없습니다: {achievement_code}")

        user_achievement = AchievementRepository.unlock_achievement(
            db, user_id, achievement.id, progress
        )
        return UserAchievementResponse.model_validate(user_achievement)

    @staticmethod
    def check_and_unlock_achievements(db: Session, user_id: int, game_stats: dict) -> List[str]:
        """
        게임 통계를 기반으로 업적 체크 및 언락

        Returns:
            List[str]: 새로 언락된 업적 코드 목록
        """
        unlocked = []

        # 첫 게임
        if not AchievementRepository.check_achievement_unlocked(db, user_id, "first_game"):
            AchievementRepository.unlock_achievement(
                db, user_id,
                AchievementRepository.get_by_code(db, "first_game").id
            )
            unlocked.append("first_game")

        # 백발백중 (명중률 90% 이상)
        if game_stats.get('accuracy', 0) >= 90 and game_stats.get('missiles_fired', 0) >= 20:
            if not AchievementRepository.check_achievement_unlocked(db, user_id, "perfect_aim"):
                AchievementRepository.unlock_achievement(
                    db, user_id,
                    AchievementRepository.get_by_code(db, "perfect_aim").id
                )
                unlocked.append("perfect_aim")

        # 콤보 마스터 (100 콤보)
        if game_stats.get('max_combo', 0) >= 100:
            if not AchievementRepository.check_achievement_unlocked(db, user_id, "combo_master"):
                AchievementRepository.unlock_achievement(
                    db, user_id,
                    AchievementRepository.get_by_code(db, "combo_master").id
                )
                unlocked.append("combo_master")

        # TODO: 더 많은 업적 체크 로직 추가

        return unlocked
