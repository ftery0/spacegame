"""콤보 시스템"""


class ComboSystem:
    """
    콤보 시스템

    연속으로 적/운석을 파괴할 때 콤보 카운트를 증가시키고,
    일정 시간 내에 다시 파괴하지 않으면 콤보가 초기화됩니다.
    """

    def __init__(self, timeout_frames: int = 180):
        """
        콤보 시스템 초기화

        Args:
            timeout_frames: 콤보 타임아웃 (프레임 수, 기본 180 = 3초 @ 60 FPS)
        """
        self.combo_count = 0
        self.combo_timeout = timeout_frames
        self.last_hit_frame = 0
        self.combo_timer = 0
        self.max_combo = 0  # 최고 콤보 기록

    def add_hit(self, current_frame: int):
        """
        적/운석 파괴 시 콤보 추가

        Args:
            current_frame: 현재 프레임 번호
        """
        time_since_last = current_frame - self.last_hit_frame

        # 타임아웃 내에 다시 파괴했으면 콤보 계속
        if time_since_last <= self.combo_timeout and self.combo_count > 0:
            self.combo_count += 1
        else:
            # 처음이거나 타임아웃 후면 새로 시작
            self.combo_count = 1

        self.last_hit_frame = current_frame
        self.combo_timer = self.combo_timeout

        # 최고 콤보 갱신
        if self.combo_count > self.max_combo:
            self.max_combo = self.combo_count

    def update(self, current_frame: int):
        """
        콤보 타이머 업데이트

        Args:
            current_frame: 현재 프레임 번호
        """
        if self.combo_count == 0:
            return

        time_elapsed = current_frame - self.last_hit_frame

        # 타임아웃 경과 시 콤보 초기화
        if time_elapsed > self.combo_timeout:
            self.combo_count = 0
            self.combo_timer = 0
        else:
            self.combo_timer = self.combo_timeout - time_elapsed

    def get_multiplier(self) -> float:
        """
        현재 콤보에 따른 점수 배율 계산

        Returns:
            float: 점수 배율 (1.0 ~ 10.0)
        """
        if self.combo_count < 5:
            return 1.0
        elif self.combo_count < 10:
            return 2.0
        elif self.combo_count < 20:
            return 3.0
        elif self.combo_count < 50:
            return 5.0
        else:
            return 10.0

    def get_display_text(self) -> str:
        """
        UI 표시용 텍스트 반환

        Returns:
            str: 콤보 표시 텍스트 (예: "25 COMBO!")
        """
        if self.combo_count <= 1:
            return ""

        multiplier = self.get_multiplier()
        return f"{self.combo_count} COMBO!"

    def get_multiplier_text(self) -> str:
        """
        배율 표시 텍스트 반환

        Returns:
            str: 배율 텍스트 (예: "x3.0 ⚡")
        """
        if self.combo_count <= 1:
            return ""

        multiplier = self.get_multiplier()
        return f"x{multiplier:.0f} ⚡"

    def get_timer_percent(self) -> float:
        """
        타이머 진행도 (백분율)

        Returns:
            float: 0.0 ~ 1.0
        """
        if self.combo_timeout == 0:
            return 0.0
        return self.combo_timer / self.combo_timeout

    def reset(self):
        """콤보 초기화"""
        self.combo_count = 0
        self.combo_timer = 0
        self.last_hit_frame = 0

    def get_combo_count(self) -> int:
        """
        현재 콤보 카운트 반환

        Returns:
            int: 콤보 카운트
        """
        return self.combo_count

    def get_max_combo(self) -> int:
        """
        최고 콤보 기록 반환

        Returns:
            int: 최고 콤보
        """
        return self.max_combo
