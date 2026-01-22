"""AI 적 엔티티 및 행동 로직"""
import pygame
import random
from core.config import SCREEN_WIDTH, SCREEN_HEIGHT


class Enemy:
    """
    AI 적 엔티티

    플레이어를 향해 발사체를 쏘고, 미사일을 회피하는 지능적인 행동을 합니다.
    """

    def __init__(self, image: pygame.Surface, enemy_speed: float = 2.0, evasion_skill: float = 0.8):
        """
        Enemy 초기화

        Args:
            image: 적 이미지
            enemy_speed: 이동 속도
            evasion_skill: 회피 능력 (0.0 ~ 1.0, 높을수록 잘 피함)
        """
        self.image = image
        self.speed = enemy_speed
        self.evasion_skill = evasion_skill

        # 랜덤 시작 위치 (화면 상단)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = -self.rect.height

        # 이동 방향
        self.horizontal_direction = random.choice([-1, 1])  # -1: 왼쪽, 1: 오른쪽
        self.horizontal_speed = random.uniform(0.5, 1.5)

        # 공격 관련
        self.attack_timer = 0
        self.can_attack = False

    def update(self, missiles: list = None):
        """
        적 업데이트 (이동 및 회피)

        Args:
            missiles: 현재 화면의 미사일 리스트 (회피 판단용)
        """
        # 기본 하강 이동
        self.rect.y += self.speed

        # 좌우 이동
        self.rect.x += self.horizontal_direction * self.horizontal_speed

        # 화면 경계 처리 (좌우)
        if self.rect.x <= 0:
            self.rect.x = 0
            self.horizontal_direction = 1
        elif self.rect.x >= SCREEN_WIDTH - self.rect.width:
            self.rect.x = SCREEN_WIDTH - self.rect.width
            self.horizontal_direction = -1

        # 미사일 회피 로직
        if missiles:
            self._evade_missiles(missiles)

        # 공격 타이머 증가
        self.attack_timer += 1

    def _evade_missiles(self, missiles: list):
        """
        미사일 회피 로직

        Args:
            missiles: 미사일 리스트
        """
        # 가장 가까운 위협적인 미사일 찾기
        closest_missile = None
        min_distance = float('inf')

        for missile in missiles:
            # 미사일이 적보다 아래에 있고, 수평 거리가 가까우면 위협
            if missile.rect.y < self.rect.y:
                horizontal_dist = abs(missile.rect.centerx - self.rect.centerx)
                vertical_dist = self.rect.y - missile.rect.y

                # 수평 거리가 가까우면 위협도가 높음
                if horizontal_dist < 100 and vertical_dist < 200:
                    distance = (horizontal_dist ** 2 + vertical_dist ** 2) ** 0.5
                    if distance < min_distance:
                        min_distance = distance
                        closest_missile = missile

        # 위협적인 미사일이 있으면 회피 시도
        if closest_missile:
            # 회피 스킬에 따라 확률적으로 회피
            if random.random() < self.evasion_skill:
                # 미사일의 반대 방향으로 이동
                if closest_missile.rect.centerx < self.rect.centerx:
                    # 미사일이 왼쪽에 있으면 오른쪽으로
                    self.horizontal_direction = 1
                    self.horizontal_speed = min(self.horizontal_speed * 1.5, 3.0)
                else:
                    # 미사일이 오른쪽에 있으면 왼쪽으로
                    self.horizontal_direction = -1
                    self.horizontal_speed = min(self.horizontal_speed * 1.5, 3.0)

                # 속도 증가로 회피 (일시적으로 더 빠르게 하강)
                self.rect.y += self.speed * 0.5

    def can_shoot(self, attack_rate: int) -> bool:
        """
        발사 가능 여부 확인

        Args:
            attack_rate: 공격 주기 (프레임 수)

        Returns:
            bool: 발사 가능하면 True
        """
        if self.attack_timer >= attack_rate:
            self.attack_timer = 0
            return True
        return False

    def get_shoot_position(self) -> tuple:
        """
        발사체 생성 위치 반환

        Returns:
            tuple: (x, y) 좌표
        """
        x = self.rect.centerx
        y = self.rect.bottom
        return (x, y)

    def draw(self, screen: pygame.Surface):
        """
        적 그리기

        Args:
            screen: pygame 화면
        """
        screen.blit(self.image, self.rect)

    def is_off_screen(self) -> bool:
        """
        화면 밖으로 나갔는지 확인

        Returns:
            bool: 화면 밖이면 True
        """
        return self.rect.y > SCREEN_HEIGHT


class EnemyProjectile:
    """
    적 발사체

    적이 플레이어를 향해 발사하는 투사체입니다.
    """

    def __init__(self, image: pygame.Surface, x: float, y: float, speed: float = 3.0):
        """
        EnemyProjectile 초기화

        Args:
            image: 발사체 이미지
            x: 시작 x 좌표
            y: 시작 y 좌표
            speed: 발사체 속도
        """
        self.image = image
        self.speed = speed
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.y = y

    def update(self):
        """발사체 업데이트 (하강)"""
        self.rect.y += self.speed

    def draw(self, screen: pygame.Surface):
        """
        발사체 그리기

        Args:
            screen: pygame 화면
        """
        screen.blit(self.image, self.rect)

    def is_off_screen(self) -> bool:
        """
        화면 밖으로 나갔는지 확인

        Returns:
            bool: 화면 밖이면 True
        """
        return self.rect.y > SCREEN_HEIGHT
