"""게임 통계 수집 시스템"""
import time
from typing import Dict, Optional


class GameStatistics:
    """게임 통계 수집"""

    def __init__(self, difficulty: str = "medium"):
        """
        통계 수집 초기화

        Args:
            difficulty: 난이도 ('easy', 'medium', 'hard')
        """
        self.difficulty = difficulty
        self.start_time = time.time()

        # 기본 통계
        self.stones_destroyed = 0
        self.enemies_destroyed = 0

        # 전투 통계
        self.missiles_fired = 0
        self.missiles_hit = 0

        # 콤보/스킬 통계
        self.max_combo = 0
        self.skills_used = 0
        self.items_collected = 0

        # 스테이지 정보
        self.max_stage = 1
        self.boss_defeated = 0

        # 피해 통계
        self.damage_taken = 0

    def on_stone_destroyed(self):
        """운석 파괴 시 호출"""
        self.stones_destroyed += 1

    def on_enemy_destroyed(self):
        """적 파괴 시 호출"""
        self.enemies_destroyed += 1

    def on_missile_fired(self, count: int = 1):
        """
        미사일 발사 시 호출

        Args:
            count: 발사한 미사일 수 (기본값: 1)
        """
        self.missiles_fired += count

    def on_missile_hit(self):
        """미사일 명중 시 호출"""
        self.missiles_hit += 1

    def on_combo_update(self, combo: int):
        """
        콤보 업데이트 시 호출

        Args:
            combo: 현재 콤보 수
        """
        self.max_combo = max(self.max_combo, combo)

    def on_skill_used(self):
        """스킬 사용 시 호출"""
        self.skills_used += 1

    def on_item_collected(self):
        """아이템 획득 시 호출"""
        self.items_collected += 1

    def on_stage_advanced(self, stage: int):
        """
        스테이지 진행 시 호출

        Args:
            stage: 진행한 스테이지 번호
        """
        self.max_stage = max(self.max_stage, stage)

    def on_boss_defeated(self):
        """보스 처치 시 호출"""
        self.boss_defeated += 1

    def on_damage_taken(self):
        """피해 입을 시 호출"""
        self.damage_taken += 1

    def get_play_time(self) -> int:
        """
        플레이 시간 (초)

        Returns:
            int: 플레이 시간 (초 단위)
        """
        return int(time.time() - self.start_time)

    def get_accuracy(self) -> float:
        """
        명중률 계산

        Returns:
            float: 명중률 (0-100)
        """
        if self.missiles_fired == 0:
            return 0.0
        return round((self.missiles_hit / self.missiles_fired) * 100, 2)

    def is_perfect_game(self) -> bool:
        """
        완벽한 게임인지 확인 (피해 없음)

        Returns:
            bool: 피해를 받지 않았으면 True
        """
        return self.damage_taken == 0

    def to_dict(self) -> Dict:
        """
        딕셔너리 변환 (서버 전송용)

        Returns:
            Dict: 통계 데이터
        """
        return {
            'difficulty': self.difficulty,
            'play_time': self.get_play_time(),
            'stones_destroyed': self.stones_destroyed,
            'enemies_destroyed': self.enemies_destroyed,
            'missiles_fired': self.missiles_fired,
            'missiles_hit': self.missiles_hit,
            'accuracy': self.get_accuracy(),
            'max_combo': self.max_combo,
            'skills_used': self.skills_used,
            'items_collected': self.items_collected,
            'max_stage_reached': self.max_stage,
            'boss_defeated': self.boss_defeated > 0,
        }

    def get_summary_text(self) -> str:
        """
        통계 요약 텍스트

        Returns:
            str: 요약 텍스트
        """
        return (
            f"플레이 시간: {self.get_play_time()}초\n"
            f"운석 파괴: {self.stones_destroyed}개\n"
            f"적 처치: {self.enemies_destroyed}명\n"
            f"명중률: {self.get_accuracy():.1f}%\n"
            f"최대 콤보: {self.max_combo}\n"
            f"최대 스테이지: {self.max_stage}"
        )

    def reset(self):
        """통계 초기화"""
        self.start_time = time.time()
        self.stones_destroyed = 0
        self.enemies_destroyed = 0
        self.missiles_fired = 0
        self.missiles_hit = 0
        self.max_combo = 0
        self.skills_used = 0
        self.items_collected = 0
        self.max_stage = 1
        self.boss_defeated = 0
        self.damage_taken = 0
