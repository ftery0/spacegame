"""아이템/파워업 시스템"""
import pygame
import random
from enum import Enum
from core.config import SCREEN_WIDTH, SCREEN_HEIGHT


class PowerUpType(Enum):
    """파워업 타입"""
    SHIELD = "shield"  # 무적 (3초)
    SPEED_BOOST = "speed_boost"  # 이동속도 증가 (5초)
    MULTI_SHOT = "multi_shot"  # 3연발 (5초)
    HEALTH = "health"  # 체력 회복 +1
    SCORE_MULTIPLIER = "score_multiplier"  # 점수 2배 (5초)


class PowerUp:
    """
    파워업 아이템

    화면 상단에서 생성되어 천천히 하강하며,
    플레이어가 획득하면 다양한 효과를 제공합니다.
    """

    # 파워업 타입별 색상 (임시, 나중에 이미지로 대체)
    COLORS = {
        PowerUpType.SHIELD: (100, 200, 255),  # 연한 파랑
        PowerUpType.SPEED_BOOST: (255, 200, 0),  # 노랑
        PowerUpType.MULTI_SHOT: (255, 100, 100),  # 빨강
        PowerUpType.HEALTH: (100, 255, 100),  # 초록
        PowerUpType.SCORE_MULTIPLIER: (255, 215, 0),  # 골드
    }

    # 파워업 타입별 표시 텍스트
    LABELS = {
        PowerUpType.SHIELD: "🛡️",
        PowerUpType.SPEED_BOOST: "⚡",
        PowerUpType.MULTI_SHOT: "🔫",
        PowerUpType.HEALTH: "❤️",
        PowerUpType.SCORE_MULTIPLIER: "⭐",
    }

    # 파워업 타입별 지속시간 (프레임 수, 60 FPS 기준)
    DURATIONS = {
        PowerUpType.SHIELD: 180,  # 3초
        PowerUpType.SPEED_BOOST: 300,  # 5초
        PowerUpType.MULTI_SHOT: 300,  # 5초
        PowerUpType.HEALTH: 0,  # 즉시 효과
        PowerUpType.SCORE_MULTIPLIER: 300,  # 5초
    }

    def __init__(self, powerup_type: PowerUpType, x: float = None, y: float = -50):
        """
        PowerUp 초기화

        Args:
            powerup_type: 파워업 타입
            x: 시작 x 좌표 (None이면 랜덤)
            y: 시작 y 좌표
        """
        self.type = powerup_type
        self.speed = 1.5  # 하강 속도
        self.size = 30

        # 위치 설정
        if x is None:
            x = random.randint(self.size, SCREEN_WIDTH - self.size)

        self.rect = pygame.Rect(x, y, self.size, self.size)

    def update(self):
        """파워업 업데이트 (하강)"""
        self.rect.y += self.speed

    def draw(self, screen: pygame.Surface, font: pygame.font.Font = None):
        """
        파워업 그리기

        Args:
            screen: pygame 화면
            font: 텍스트 렌더링용 폰트 (선택사항)
        """
        # 파워업 원 그리기
        color = self.COLORS.get(self.type, (255, 255, 255))
        pygame.draw.circle(screen, color, self.rect.center, self.size // 2)

        # 테두리
        pygame.draw.circle(screen, (255, 255, 255), self.rect.center, self.size // 2, 2)

        # 아이콘/텍스트 (폰트가 있으면)
        if font:
            label = self.LABELS.get(self.type, "?")
            text_surface = font.render(label, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)

    def is_off_screen(self) -> bool:
        """
        화면 밖으로 나갔는지 확인

        Returns:
            bool: 화면 밖이면 True
        """
        return self.rect.y > SCREEN_HEIGHT

    def get_duration(self) -> int:
        """
        파워업 지속시간 반환

        Returns:
            int: 지속시간 (프레임 수)
        """
        return self.DURATIONS.get(self.type, 0)


class PowerUpManager:
    """
    파워업 관리자

    파워업 생성, 활성 효과 관리, 타이머 추적 등을 담당합니다.
    """

    def __init__(self):
        """PowerUpManager 초기화"""
        self.active_powerups = []  # 화면의 파워업 아이템 리스트
        self.active_effects = {}  # 활성 효과 {PowerUpType: 남은_프레임}

        # 생성 확률 (각 타입의 상대적 확률)
        self.spawn_weights = {
            PowerUpType.SHIELD: 15,
            PowerUpType.SPEED_BOOST: 20,
            PowerUpType.MULTI_SHOT: 20,
            PowerUpType.HEALTH: 10,
            PowerUpType.SCORE_MULTIPLIER: 15,
        }

    def spawn_random_powerup(self) -> PowerUp:
        """
        랜덤 파워업 생성

        Returns:
            PowerUp: 생성된 파워업
        """
        types = list(self.spawn_weights.keys())
        weights = list(self.spawn_weights.values())
        powerup_type = random.choices(types, weights=weights)[0]

        powerup = PowerUp(powerup_type)
        self.active_powerups.append(powerup)
        return powerup

    def update_powerups(self):
        """모든 파워업 업데이트"""
        for powerup in self.active_powerups:
            powerup.update()

        # 화면 밖 파워업 제거
        self.active_powerups = [p for p in self.active_powerups if not p.is_off_screen()]

    def update_effects(self):
        """활성 효과 타이머 업데이트"""
        expired_effects = []

        for effect_type, remaining_frames in self.active_effects.items():
            remaining_frames -= 1
            if remaining_frames <= 0:
                expired_effects.append(effect_type)
            else:
                self.active_effects[effect_type] = remaining_frames

        # 만료된 효과 제거
        for effect_type in expired_effects:
            del self.active_effects[effect_type]

    def activate_powerup(self, powerup_type: PowerUpType):
        """
        파워업 효과 활성화

        Args:
            powerup_type: 활성화할 파워업 타입
        """
        duration = PowerUp.DURATIONS.get(powerup_type, 0)

        if duration > 0:
            # 지속 효과는 타이머 갱신
            self.active_effects[powerup_type] = duration
        # 즉시 효과 (HEALTH)는 별도 처리 필요

    def is_effect_active(self, powerup_type: PowerUpType) -> bool:
        """
        특정 효과가 활성화되어 있는지 확인

        Args:
            powerup_type: 확인할 파워업 타입

        Returns:
            bool: 활성화 상태
        """
        return powerup_type in self.active_effects

    def get_remaining_time(self, powerup_type: PowerUpType) -> int:
        """
        특정 효과의 남은 시간 반환

        Args:
            powerup_type: 파워업 타입

        Returns:
            int: 남은 프레임 수
        """
        return self.active_effects.get(powerup_type, 0)

    def clear_powerups(self):
        """모든 파워업 및 효과 초기화"""
        self.active_powerups.clear()
        self.active_effects.clear()

    def draw_powerups(self, screen: pygame.Surface, font: pygame.font.Font = None):
        """
        모든 파워업 그리기

        Args:
            screen: pygame 화면
            font: 텍스트 렌더링용 폰트
        """
        for powerup in self.active_powerups:
            powerup.draw(screen, font)

    def draw_active_effects_ui(self, screen: pygame.Surface, font: pygame.font.Font, x: int = 10, y: int = 100):
        """
        활성 효과 UI 표시

        Args:
            screen: pygame 화면
            font: 폰트
            x: 시작 x 좌표
            y: 시작 y 좌표
        """
        offset_y = 0

        for effect_type, remaining_frames in self.active_effects.items():
            # 아이콘
            label = PowerUp.LABELS.get(effect_type, "?")
            color = PowerUp.COLORS.get(effect_type, (255, 255, 255))

            # 배경 원
            pygame.draw.circle(screen, color, (x + 15, y + offset_y + 15), 15)
            pygame.draw.circle(screen, (255, 255, 255), (x + 15, y + offset_y + 15), 15, 2)

            # 아이콘 텍스트
            icon_text = font.render(label, True, (255, 255, 255))
            icon_rect = icon_text.get_rect(center=(x + 15, y + offset_y + 15))
            screen.blit(icon_text, icon_rect)

            # 남은 시간 (초)
            remaining_seconds = remaining_frames // 60
            time_text = font.render(f"{remaining_seconds}s", True, (255, 255, 255))
            screen.blit(time_text, (x + 35, y + offset_y + 5))

            offset_y += 35

    def get_active_powerups(self) -> list:
        """
        활성 파워업 아이템 리스트 반환

        Returns:
            list: 파워업 리스트
        """
        return self.active_powerups
