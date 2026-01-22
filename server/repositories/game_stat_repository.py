"""게임 통계 레포지토리"""
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from models.game_stat import GameStat
from typing import List, Optional


class GameStatRepository:
    """게임 통계 데이터 액세스"""

    @staticmethod
    def create(db: Session, user_id: int, stat_data: dict) -> GameStat:
        """게임 통계 생성"""
        stat = GameStat(user_id=user_id, **stat_data)
        stat.calculate_accuracy()
        db.add(stat)
        db.commit()
        db.refresh(stat)
        return stat

    @staticmethod
    def get_by_user(db: Session, user_id: int, limit: int = 10) -> List[GameStat]:
        """사용자의 게임 통계 조회"""
        return db.query(GameStat).filter(
            GameStat.user_id == user_id
        ).order_by(desc(GameStat.game_date)).limit(limit).all()

    @staticmethod
    def get_user_summary(db: Session, user_id: int) -> dict:
        """사용자 통계 요약"""
        stats = db.query(
            func.count(GameStat.id).label('total_games'),
            func.sum(GameStat.play_time).label('total_play_time'),
            func.max(GameStat.final_score).label('highest_score'),
            func.sum(GameStat.stones_destroyed).label('total_stones'),
            func.sum(GameStat.enemies_destroyed).label('total_enemies'),
            func.avg(GameStat.accuracy).label('avg_accuracy'),
            func.max(GameStat.max_combo).label('best_combo'),
            func.sum(GameStat.skills_used).label('total_skills'),
            func.sum(GameStat.items_collected).label('total_items'),
            func.max(GameStat.max_stage_reached).label('max_stage'),
            func.sum(func.cast(GameStat.boss_defeated, db.bind.dialect.NUMERIC)).label('bosses_defeated')
        ).filter(GameStat.user_id == user_id).first()

        return {
            'total_games': stats.total_games or 0,
            'total_play_time': stats.total_play_time or 0,
            'highest_score': stats.highest_score or 0,
            'total_stones_destroyed': stats.total_stones or 0,
            'total_enemies_destroyed': stats.total_enemies or 0,
            'average_accuracy': round(stats.avg_accuracy or 0.0, 2),
            'best_combo': stats.best_combo or 0,
            'total_skills_used': stats.total_skills or 0,
            'total_items_collected': stats.total_items or 0,
            'max_stage_ever': stats.max_stage or 1,
            'bosses_defeated_count': stats.bosses_defeated or 0
        }
