"""Game entity classes"""
import pygame
import random
from core.config import (
    PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_SPEED, PLAYER_START_X, PLAYER_START_Y,
    STONE_MIN_SIZE, STONE_MAX_SIZE, STONE_SPEED,
    MISSILE_WIDTH, MISSILE_HEIGHT, MISSILE_SPEED,
    SCREEN_WIDTH, SCREEN_HEIGHT
)


class Player:
    """플레이어 엔티티"""

    def __init__(self, image: pygame.Surface):
        """
        플레이어 초기화

        Args:
            image: 플레이어 이미지
        """
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = PLAYER_START_X
        self.rect.y = PLAYER_START_Y
        self.speed = PLAYER_SPEED

    def move_left(self):
        """왼쪽 이동"""
        if self.rect.x > 0:
            self.rect.x -= self.speed

    def move_right(self):
        """오른쪽 이동"""
        if self.rect.x + self.rect.width < SCREEN_WIDTH:
            self.rect.x += self.speed

    def move_up(self):
        """위쪽 이동"""
        if self.rect.y > 0:
            self.rect.y -= self.speed

    def move_down(self):
        """아래쪽 이동"""
        if self.rect.y + self.rect.height < SCREEN_HEIGHT:
            self.rect.y += self.speed

    def draw(self, screen: pygame.Surface):
        """
        플레이어 그리기

        Args:
            screen: pygame 화면
        """
        screen.blit(self.image, self.rect)

    def get_rect(self) -> pygame.Rect:
        """
        플레이어 사각형 반환

        Returns:
            pygame.Rect: 플레이어 사각형
        """
        return self.rect


class Stone:
    """운석 엔티티"""

    def __init__(self, image: pygame.Surface, x: int = None, y: int = 0, speed_multiplier: float = 1.0):
        """
        운석 초기화

        Args:
            image: 운석 이미지
            x: X 위치 (기본값: 무작위)
            y: Y 위치 (기본값: 0)
            speed_multiplier: 속도 배율 (스테이지별 난이도)
        """
        self.size = random.randint(STONE_MIN_SIZE, STONE_MAX_SIZE)
        self.image = pygame.transform.scale(image, (self.size, self.size))
        self.rect = self.image.get_rect()
        self.rect.x = x if x is not None else random.randint(0, SCREEN_WIDTH - self.size)
        self.rect.y = y
        self.speed = STONE_SPEED * speed_multiplier

    def update(self):
        """운석 업데이트"""
        self.rect.y += self.speed

    def draw(self, screen: pygame.Surface):
        """
        운석 그리기

        Args:
            screen: pygame 화면
        """
        screen.blit(self.image, self.rect)

    def is_off_screen(self) -> bool:
        """
        운석이 화면 범위를 벗어났는지 확인

        Returns:
            bool: 벗어났으면 True
        """
        return self.rect.y > SCREEN_HEIGHT

    def get_rect(self) -> pygame.Rect:
        """
        운석 사각형 반환

        Returns:
            pygame.Rect: 운석 사각형
        """
        return self.rect


class Missile:
    """미사일 엔티티"""

    def __init__(self, image: pygame.Surface, x: int, y: int):
        """
        미사일 초기화

        Args:
            image: 미사일 이미지
            x: 시작 X 위치
            y: 시작 Y 위치
        """
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = MISSILE_SPEED

    def update(self):
        """미사일 업데이트"""
        self.rect.y -= self.speed

    def draw(self, screen: pygame.Surface):
        """
        미사일 그리기

        Args:
            screen: pygame 화면
        """
        screen.blit(self.image, self.rect)

    def is_off_screen(self) -> bool:
        """
        미사일이 화면 범위를 벗어났는지 확인

        Returns:
            bool: 벗어났으면 True
        """
        return self.rect.y < 0

    def get_rect(self) -> pygame.Rect:
        """
        미사일 사각형 반환

        Returns:
            pygame.Rect: 미사일 사각형
        """
        return self.rect
