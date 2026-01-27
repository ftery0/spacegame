"""AI 적 엔티티 및 레이저 공격 시스템"""
import pygame
import random
import math
from enum import Enum
from core.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    ENEMY_LASER_CHARGE_TIME, ENEMY_LASER_FIRE_TIME, ENEMY_LASER_COOLDOWN_TIME,
    ENEMY_LASER_WIDTH, ENEMY_LASER_COLOR, ENEMY_LASER_CHARGE_COLOR
)


class EnemyState(Enum):
    """적 AI 상태"""
    PATROL = "patrol"  # 순찰 (기본 이동)
    CHASE = "chase"  # 플레이어 추적
    EVADE = "evade"  # 회피 (운석/미사일)
    CHARGING = "charging"  # 레이저 충전
    FIRING = "firing"  # 레이저 발사
    COOLDOWN = "cooldown"  # 쿨다운


class Enemy:
    """
    AI 적 엔티티

    플레이어를 추적하고, 레이저를 충전하여 발사합니다.
    운석과 미사일을 회피하는 지능적인 행동을 합니다.
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

        # AI 상태
        self.state = EnemyState.PATROL
        self.state_timer = 0

        # 레이저 시스템
        self.laser = None
        self.laser_charge_progress = 0  # 0.0 ~ 1.0

        # 타겟 (플레이어 추적용)
        self.target_player = None

    def update(self, player, missiles: list = None, stones: list = None):
        """
        적 업데이트 (AI 행동 및 레이저 시스템)

        Args:
            player: 플레이어 객체
            missiles: 현재 화면의 미사일 리스트 (회피 판단용)
            stones: 현재 화면의 운석 리스트 (회피 판단용)
        """
        self.target_player = player
        self.state_timer += 1

        # 위험 감지 (운석 및 미사일)
        danger = self._detect_danger(missiles, stones)

        # 상태 머신
        if danger and self.state not in [EnemyState.CHARGING, EnemyState.FIRING]:
            # 위험이 있으면 회피
            self.state = EnemyState.EVADE
            self._evade(danger)
        elif self.state == EnemyState.PATROL:
            # 순찰 상태: 기본 이동
            self._patrol()
            # 일정 거리 내에 플레이어가 있으면 충전 시작
            if self._is_player_in_range(250):
                self._start_charging()
        elif self.state == EnemyState.CHASE:
            # 추적 상태: 플레이어를 향해 이동
            self._chase_player()
            if self._is_player_in_range(200):
                self._start_charging()
        elif self.state == EnemyState.CHARGING:
            # 충전 상태: 레이저 충전
            self._charge_laser()
        elif self.state == EnemyState.FIRING:
            # 발사 상태: 레이저 발사
            self._fire_laser()
        elif self.state == EnemyState.COOLDOWN:
            # 쿨다운 상태
            self._cooldown()
        elif self.state == EnemyState.EVADE:
            # 회피 후 다시 추적 모드로
            if self.state_timer > 30:  # 0.5초 후
                self.state = EnemyState.CHASE
                self.state_timer = 0

        # 레이저 업데이트
        if self.laser:
            self.laser.update()

    def _detect_danger(self, missiles: list, stones: list):
        """
        주변 위험 감지 (운석 및 미사일)

        Args:
            missiles: 미사일 리스트
            stones: 운석 리스트

        Returns:
            위협 객체 (운석 또는 미사일) 또는 None
        """
        danger_radius = 80  # 80px 이내 위험 감지

        # 운석 감지
        if stones:
            for stone in stones:
                distance = math.sqrt(
                    (self.rect.centerx - stone.rect.centerx) ** 2 +
                    (self.rect.centery - stone.rect.centery) ** 2
                )
                # 운석이 내 위에 있고 가까우면 위험
                if distance < danger_radius and stone.rect.y < self.rect.y:
                    return stone

        # 미사일 감지 (플레이어의 미사일)
        if missiles:
            for missile in missiles:
                distance = math.sqrt(
                    (self.rect.centerx - missile.rect.centerx) ** 2 +
                    (self.rect.centery - missile.rect.centery) ** 2
                )
                # 미사일이 내 아래에 있고 가까우면 위험
                if distance < 100 and missile.rect.y < self.rect.y:
                    horizontal_dist = abs(missile.rect.centerx - self.rect.centerx)
                    if horizontal_dist < 50:  # 수평 거리가 가까우면 위험
                        return missile

        return None

    def _evade(self, danger):
        """
        위험 회피

        Args:
            danger: 위협 객체 (운석 또는 미사일)
        """
        # 회피 스킬 체크
        if random.random() > self.evasion_skill:
            return  # 회피 실패

        # 안전한 방향 계산 (위협 반대 방향)
        dx = self.rect.centerx - danger.rect.centerx
        dy = self.rect.centery - danger.rect.centery

        # 정규화
        length = math.sqrt(dx**2 + dy**2)
        if length > 0:
            dx /= length
            dy /= length

        # 회피 이동 (1.5배 빠름)
        self.rect.x += dx * self.speed * 1.5
        self.rect.y += dy * self.speed * 0.5  # 수평 회피 위주

        # 화면 범위 체크
        self._clamp_to_screen()

    def _patrol(self):
        """순찰 (기본 이동)"""
        # 기본 하강 이동
        self.rect.y += self.speed

        # 좌우 이동
        self.rect.x += self.horizontal_direction * self.horizontal_speed

        # 화면 경계 처리
        if self.rect.x <= 0:
            self.rect.x = 0
            self.horizontal_direction = 1
        elif self.rect.x >= SCREEN_WIDTH - self.rect.width:
            self.rect.x = SCREEN_WIDTH - self.rect.width
            self.horizontal_direction = -1

    def _chase_player(self):
        """플레이어 추적"""
        if not self.target_player:
            return

        # 플레이어 방향 계산
        dx = self.target_player.rect.centerx - self.rect.centerx
        dy = self.target_player.rect.centery - self.rect.centery

        # 정규화
        length = math.sqrt(dx**2 + dy**2)
        if length > 0:
            dx /= length
            dy /= length

        # 이동 (추적 시 약간 느림)
        self.rect.x += dx * self.speed * 0.8
        self.rect.y += dy * self.speed * 0.8

        self._clamp_to_screen()

    def _is_player_in_range(self, range_distance: float) -> bool:
        """
        플레이어가 사정거리 내에 있는지 확인

        Args:
            range_distance: 사정거리

        Returns:
            bool: 사정거리 내에 있으면 True
        """
        if not self.target_player:
            return False

        distance = math.sqrt(
            (self.rect.centerx - self.target_player.rect.centerx) ** 2 +
            (self.rect.centery - self.target_player.rect.centery) ** 2
        )
        return distance < range_distance

    def _start_charging(self):
        """레이저 충전 시작"""
        self.state = EnemyState.CHARGING
        self.state_timer = 0
        self.laser_charge_progress = 0

    def _charge_laser(self):
        """레이저 충전"""
        self.laser_charge_progress = self.state_timer / ENEMY_LASER_CHARGE_TIME

        # 충전 완료
        if self.state_timer >= ENEMY_LASER_CHARGE_TIME:
            self._start_firing()

    def _start_firing(self):
        """레이저 발사 시작"""
        self.state = EnemyState.FIRING
        self.state_timer = 0

        # 레이저 생성 (플레이어 방향)
        if self.target_player:
            angle = math.atan2(
                self.target_player.rect.centery - self.rect.centery,
                self.target_player.rect.centerx - self.rect.centerx
            )
            self.laser = EnemyLaser(
                self.rect.centerx,
                self.rect.centery,
                angle,
                ENEMY_LASER_FIRE_TIME
            )

    def _fire_laser(self):
        """레이저 발사 중"""
        # 발사 시간 종료
        if self.state_timer >= ENEMY_LASER_FIRE_TIME:
            self.laser = None
            self.state = EnemyState.COOLDOWN
            self.state_timer = 0

    def _cooldown(self):
        """쿨다운"""
        # 쿨다운 종료
        if self.state_timer >= ENEMY_LASER_COOLDOWN_TIME:
            self.state = EnemyState.CHASE
            self.state_timer = 0

    def _clamp_to_screen(self):
        """화면 범위 제한"""
        self.rect.x = max(0, min(self.rect.x, SCREEN_WIDTH - self.rect.width))
        self.rect.y = max(50, min(self.rect.y, SCREEN_HEIGHT - self.rect.height))

    def get_laser(self):
        """
        현재 활성화된 레이저 반환

        Returns:
            EnemyLaser 또는 None
        """
        return self.laser

    def is_charging(self) -> bool:
        """충전 중인지 확인"""
        return self.state == EnemyState.CHARGING

    def is_firing(self) -> bool:
        """발사 중인지 확인"""
        return self.state == EnemyState.FIRING

    def draw(self, screen: pygame.Surface):
        """
        적 그리기

        Args:
            screen: pygame 화면
        """
        # 적 이미지 그리기
        screen.blit(self.image, self.rect)

        # 충전 이펙트 그리기
        if self.state == EnemyState.CHARGING:
            self._draw_charge_effect(screen)

        # 레이저 그리기
        if self.laser:
            self.laser.draw(screen)

    def _draw_charge_effect(self, screen: pygame.Surface):
        """
        충전 이펙트 그리기

        Args:
            screen: pygame 화면
        """
        # 충전 진행도 바
        bar_width = self.rect.width
        bar_height = 5
        bar_x = self.rect.x
        bar_y = self.rect.y - 15

        # 배경 (회색)
        pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))

        # 충전 진행도 (노란색 -> 빨간색)
        progress_width = int(bar_width * self.laser_charge_progress)
        color = ENEMY_LASER_CHARGE_COLOR
        pygame.draw.rect(screen, color, (bar_x, bar_y, progress_width, bar_height))

        # 충전 완료 임박 시 깜빡임
        if self.laser_charge_progress > 0.8:
            if (self.state_timer // 5) % 2 == 0:  # 깜빡임 효과
                # 적 주변에 경고 원 그리기
                pygame.draw.circle(
                    screen,
                    ENEMY_LASER_CHARGE_COLOR,
                    self.rect.center,
                    self.rect.width // 2 + 5,
                    2
                )

    def is_off_screen(self) -> bool:
        """
        화면 밖으로 나갔는지 확인

        Returns:
            bool: 화면 밖이면 True
        """
        return self.rect.y > SCREEN_HEIGHT


class EnemyLaser:
    """
    적 레이저 빔

    직선으로 발사되며 일정 시간 동안 지속됩니다.
    """

    def __init__(self, start_x: float, start_y: float, angle: float, duration: int):
        """
        EnemyLaser 초기화

        Args:
            start_x: 시작 x 좌표
            start_y: 시작 y 좌표
            angle: 발사 각도 (라디안)
            duration: 지속 시간 (프레임)
        """
        self.start_x = start_x
        self.start_y = start_y
        self.angle = angle
        self.duration = duration
        self.timer = 0

        # 레이저 끝 위치 계산 (화면 끝까지)
        self.length = 1000  # 충분히 긴 레이저
        self.end_x = start_x + math.cos(angle) * self.length
        self.end_y = start_y + math.sin(angle) * self.length

    def update(self):
        """레이저 업데이트"""
        self.timer += 1

    def is_active(self) -> bool:
        """
        레이저가 활성화되어 있는지 확인

        Returns:
            bool: 활성화되어 있으면 True
        """
        return self.timer < self.duration

    def get_collision_rect(self) -> pygame.Rect:
        """
        충돌 감지를 위한 사각형 반환

        Returns:
            pygame.Rect: 레이저 충돌 영역
        """
        # 레이저를 사각형으로 근사
        min_x = min(self.start_x, self.end_x)
        max_x = max(self.start_x, self.end_x)
        min_y = min(self.start_y, self.end_y)
        max_y = max(self.start_y, self.end_y)

        return pygame.Rect(
            min_x,
            min_y,
            max_x - min_x + ENEMY_LASER_WIDTH,
            max_y - min_y + ENEMY_LASER_WIDTH
        )

    def collides_with(self, rect: pygame.Rect) -> bool:
        """
        레이저가 사각형과 충돌하는지 확인 (선분-사각형 충돌)

        Args:
            rect: 충돌을 확인할 사각형

        Returns:
            bool: 충돌하면 True
        """
        # 간단한 충돌 감지: 레이저의 바운딩 박스와 rect 충돌 확인
        laser_rect = self.get_collision_rect()
        return laser_rect.colliderect(rect)

    def draw(self, screen: pygame.Surface):
        """
        레이저 그리기

        Args:
            screen: pygame 화면
        """
        # 레이저 빔 그리기 (굵은 선)
        pygame.draw.line(
            screen,
            ENEMY_LASER_COLOR,
            (self.start_x, self.start_y),
            (self.end_x, self.end_y),
            ENEMY_LASER_WIDTH
        )

        # 레이저 중심부 (더 밝은 색)
        pygame.draw.line(
            screen,
            (255, 150, 150),
            (self.start_x, self.start_y),
            (self.end_x, self.end_y),
            max(1, ENEMY_LASER_WIDTH // 2)
        )


# 하위 호환성을 위해 EnemyProjectile 클래스 유지 (사용하지 않음)
class EnemyProjectile:
    """
    적 발사체 (사용 중단 - 레이저로 대체됨)

    하위 호환성을 위해 유지되지만, 실제로는 사용되지 않습니다.
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
