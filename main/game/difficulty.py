"""난이도 관리 시스템"""
import json
from typing import Dict, Optional
from pathlib import Path


class DifficultyLevel:
    """난이도 레벨 상수"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class DifficultyManager:
    """
    난이도 관리자

    게임 난이도 설정을 관리하고 서버에서 받아온 설정을 캐시합니다.
    """

    def __init__(self):
        self.current_difficulty = DifficultyLevel.MEDIUM
        self.settings = {}
        self._cache_file = Path("difficulty_cache.json")
        self._load_cache()

    def _load_cache(self):
        """캐시된 난이도 설정 로드"""
        if self._cache_file.exists():
            try:
                with open(self._cache_file, "r", encoding="utf-8") as f:
                    self.settings = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._init_default_settings()
        else:
            self._init_default_settings()

    def _init_default_settings(self):
        """기본 난이도 설정 초기화 (서버 연결 실패 시 사용)"""
        self.settings = {
            DifficultyLevel.EASY: {
                "name": "easy",
                "display_name": "초급",
                "stone_speed": 1.5,
                "stone_spawn_interval": 120,
                "enemy_spawn_chance": 0.15,
                "enemy_speed": 2.0,
                "enemy_evasion_skill": 0.70,
                "enemy_attack_rate": 120,
                "score_multiplier": 1.0,
                "player_health": 5
            },
            DifficultyLevel.MEDIUM: {
                "name": "medium",
                "display_name": "중급",
                "stone_speed": 2.5,
                "stone_spawn_interval": 80,
                "enemy_spawn_chance": 0.25,
                "enemy_speed": 3.0,
                "enemy_evasion_skill": 0.85,
                "enemy_attack_rate": 90,
                "score_multiplier": 1.5,
                "player_health": 3
            },
            DifficultyLevel.HARD: {
                "name": "hard",
                "display_name": "고급",
                "stone_speed": 3.5,
                "stone_spawn_interval": 50,
                "enemy_spawn_chance": 0.40,
                "enemy_speed": 4.5,
                "enemy_evasion_skill": 0.95,
                "enemy_attack_rate": 60,
                "score_multiplier": 2.0,
                "player_health": 3
            }
        }

    def save_cache(self):
        """현재 설정을 캐시 파일에 저장"""
        try:
            with open(self._cache_file, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except IOError:
            pass

    def update_from_api(self, difficulties: list):
        """
        API에서 받아온 난이도 설정으로 업데이트

        Args:
            difficulties: API에서 받아온 난이도 목록
        """
        self.settings = {}
        for diff in difficulties:
            self.settings[diff['name']] = diff
        self.save_cache()

    def set_difficulty(self, level: str):
        """
        난이도 설정

        Args:
            level: 'easy', 'medium', 'hard'
        """
        if level in self.settings:
            self.current_difficulty = level
        else:
            self.current_difficulty = DifficultyLevel.MEDIUM

    def get_current_settings(self) -> Dict:
        """
        현재 난이도 설정 반환

        Returns:
            Dict: 현재 난이도 설정 딕셔너리
        """
        return self.settings.get(
            self.current_difficulty,
            self.settings[DifficultyLevel.MEDIUM]
        )

    def get_difficulty_info(self, level: str) -> Optional[Dict]:
        """
        특정 난이도 정보 반환

        Args:
            level: 'easy', 'medium', 'hard'

        Returns:
            Optional[Dict]: 난이도 정보 또는 None
        """
        return self.settings.get(level)

    def get_all_difficulties(self) -> Dict[str, Dict]:
        """
        모든 난이도 설정 반환

        Returns:
            Dict[str, Dict]: 모든 난이도 설정
        """
        return self.settings

    def get_current_difficulty(self) -> str:
        """
        현재 난이도 레벨 반환

        Returns:
            str: 현재 난이도 ('easy', 'medium', 'hard')
        """
        return self.current_difficulty

    def get_display_name(self, level: str = None) -> str:
        """
        난이도 표시 이름 반환

        Args:
            level: 난이도 레벨 (None이면 현재 난이도)

        Returns:
            str: 난이도 표시 이름 (예: '초급', '중급', '고급')
        """
        level = level or self.current_difficulty
        settings = self.settings.get(level)
        if settings:
            return settings.get("display_name", level)
        return level
