"""데이터베이스 설정"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 데이터베이스 URL (SQLite 사용)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./spacegame.db")

# SQLAlchemy 엔진 생성
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# 세션 로컬 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스 생성
Base = declarative_base()


def get_db():
    """데이터베이스 세션 의존성"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """데이터베이스 초기화"""
    # 모든 모델 import (테이블 생성을 위해)
    from models.user import User
    from models.score import Score
    from models.game_stat import GameStat
    from models.achievement import Achievement
    from models.user_achievement import UserAchievement
    from models.difficulty_setting import DifficultySetting

    # 테이블 생성
    Base.metadata.create_all(bind=engine)

    # 초기 데이터 삽입 (난이도 설정, 업적)
    _insert_initial_data()


def _insert_initial_data():
    """초기 데이터 삽입"""
    from models.difficulty_setting import DifficultySetting
    from models.achievement import Achievement

    db = SessionLocal()
    try:
        # 난이도 설정이 없으면 추가
        if db.query(DifficultySetting).count() == 0:
            difficulties = [
                DifficultySetting(
                    name="easy",
                    display_name="초급",
                    stone_speed=1.5,
                    stone_spawn_interval=120,
                    enemy_spawn_chance=0.15,
                    enemy_speed=2.0,
                    enemy_evasion_skill=0.70,
                    enemy_attack_rate=120,
                    score_multiplier=1.0,
                    player_health=5
                ),
                DifficultySetting(
                    name="medium",
                    display_name="중급",
                    stone_speed=2.5,
                    stone_spawn_interval=80,
                    enemy_spawn_chance=0.25,
                    enemy_speed=3.0,
                    enemy_evasion_skill=0.85,
                    enemy_attack_rate=90,
                    score_multiplier=1.5,
                    player_health=3
                ),
                DifficultySetting(
                    name="hard",
                    display_name="고급",
                    stone_speed=3.5,
                    stone_spawn_interval=50,
                    enemy_spawn_chance=0.40,
                    enemy_speed=4.5,
                    enemy_evasion_skill=0.95,
                    enemy_attack_rate=60,
                    score_multiplier=2.0,
                    player_health=3
                )
            ]
            db.add_all(difficulties)
            db.commit()

        # 업적이 없으면 추가
        if db.query(Achievement).count() == 0:
            achievements = [
                Achievement(
                    code="first_game",
                    name="첫 걸음",
                    description="첫 게임을 플레이하세요",
                    category="basic",
                    condition_type="games_played",
                    condition_value=1,
                    rarity="common"
                ),
                Achievement(
                    code="perfect_aim",
                    name="백발백중",
                    description="미사일 명중률 90% 이상 달성",
                    category="combat",
                    condition_type="accuracy",
                    condition_value=90,
                    rarity="rare"
                ),
                Achievement(
                    code="immortal",
                    name="불사신",
                    description="체력을 잃지 않고 게임 클리어",
                    category="survival",
                    condition_type="no_damage",
                    condition_value=1,
                    rarity="epic"
                ),
                Achievement(
                    code="speedrunner",
                    name="스피드러너",
                    description="3분 안에 1000점 달성",
                    category="time",
                    condition_type="score_time",
                    condition_value=180,
                    rarity="rare"
                ),
                Achievement(
                    code="combo_master",
                    name="콤보 마스터",
                    description="100 콤보 달성",
                    category="combo",
                    condition_type="max_combo",
                    condition_value=100,
                    rarity="epic"
                ),
                Achievement(
                    code="stone_breaker",
                    name="운석 파괴자",
                    description="누적 1000개 운석 파괴",
                    category="combat",
                    condition_type="total_stones",
                    condition_value=1000,
                    rarity="common"
                ),
                Achievement(
                    code="enemy_hunter",
                    name="적 사냥꾼",
                    description="누적 100명 적 처치",
                    category="combat",
                    condition_type="total_enemies",
                    condition_value=100,
                    rarity="common"
                ),
                Achievement(
                    code="boss_slayer",
                    name="보스 학살자",
                    description="보스를 10번 처치",
                    category="boss",
                    condition_type="bosses_defeated",
                    condition_value=10,
                    rarity="rare"
                )
            ]
            db.add_all(achievements)
            db.commit()

    finally:
        db.close()
