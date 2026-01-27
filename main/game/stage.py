"""스테이지/레벨 시스템"""
import time


class Stage:
    """스테이지 정보"""

    def __init__(self, number: int):
        """
        스테이지 초기화

        Args:
            number: 스테이지 번호 (1부터 시작)
        """
        self.number = number
        self.score_threshold = number * 500  # 스테이지당 500점
        self.stone_speed_multiplier = 1.0 + (number - 1) * 0.15  # 스테이지마다 15% 증가
        self.stone_spawn_multiplier = max(1.0 - (number - 1) * 0.1, 0.5)  # 스폰 간격 감소 (최소 50%)
        self.enemy_count_multiplier = 1.0 + (number - 1) * 0.2  # 적 출현율 20% 증가
        self.is_boss_stage = (number % 5 == 0)  # 5스테이지마다 보스

    def get_display_name(self) -> str:
        """스테이지 표시 이름"""
        if self.is_boss_stage:
            return f"STAGE {self.number} - BOSS!"
        return f"STAGE {self.number}"

    def get_background_index(self) -> int:
        """배경 인덱스 (향후 다른 배경 사용 시)"""
        # 5스테이지마다 배경 변경 (0, 1, 2, 3...)
        return min((self.number - 1) // 5, 3)


class StageManager:
    """스테이지 관리"""

    def __init__(self):
        """스테이지 매니저 초기화"""
        self.current_stage_number = 1
        self.stage = Stage(1)
        self.stage_start_time = time.time()
        self.stage_advanced_count = 0
        self.show_stage_notification = False
        self.notification_timer = 0
        self.notification_duration = 180  # 3초 (60 FPS 기준)

    def check_advance(self, score: int) -> bool:
        """
        스테이지 진행 체크

        Args:
            score: 현재 점수

        Returns:
            bool: 스테이지가 진행되었으면 True
        """
        if score >= self.stage.score_threshold:
            self.advance()
            return True
        return False

    def advance(self):
        """다음 스테이지로 진행"""
        self.current_stage_number += 1
        self.stage = Stage(self.current_stage_number)
        self.stage_start_time = time.time()
        self.stage_advanced_count += 1
        self.show_stage_notification = True
        self.notification_timer = self.notification_duration

    def update_notification(self):
        """알림 타이머 업데이트"""
        if self.show_stage_notification:
            self.notification_timer -= 1
            if self.notification_timer <= 0:
                self.show_stage_notification = False

    def get_stage_info(self) -> str:
        """현재 스테이지 정보 텍스트"""
        return self.stage.get_display_name()

    def get_stone_speed_multiplier(self) -> float:
        """현재 스테이지의 운석 속도 배율"""
        return self.stage.stone_speed_multiplier

    def get_stone_spawn_multiplier(self) -> float:
        """현재 스테이지의 운석 스폰 배율"""
        return self.stage.stone_spawn_multiplier

    def get_enemy_spawn_multiplier(self) -> float:
        """현재 스테이지의 적 스폰 배율"""
        return self.stage.enemy_count_multiplier

    def is_boss_stage(self) -> bool:
        """현재 스테이지가 보스 스테이지인지"""
        return self.stage.is_boss_stage

    def get_max_stage_reached(self) -> int:
        """도달한 최대 스테이지"""
        return self.current_stage_number

    def reset(self):
        """스테이지 매니저 리셋"""
        self.current_stage_number = 1
        self.stage = Stage(1)
        self.stage_start_time = time.time()
        self.stage_advanced_count = 0
        self.show_stage_notification = False
        self.notification_timer = 0
