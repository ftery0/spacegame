"""업적 알림 UI 시스템"""
import pygame
from typing import Optional, List
from game.achievements import AchievementChecker


class AchievementNotification:
    """
    업적 달성 알림

    화면 상단 중앙에 슬라이드 인/아웃 애니메이션과 함께 표시됩니다.
    """

    def __init__(self, achievement_code: str, checker: AchievementChecker):
        """
        알림 초기화

        Args:
            achievement_code: 업적 코드
            checker: 업적 체커 (이름/설명 가져오기용)
        """
        self.achievement_code = achievement_code
        self.name = checker.get_achievement_display_name(achievement_code)
        self.description = checker.get_achievement_description(achievement_code)

        # 알림 상태
        self.timer = 0
        self.max_duration = 240  # 4초 (60 FPS 기준)
        self.slide_in_duration = 30  # 0.5초
        self.slide_out_duration = 30  # 0.5초

        # 알림 박스 크기 및 위치
        self.width = 400
        self.height = 100
        self.target_x = (500 - self.width) // 2  # 화면 중앙 (SCREEN_WIDTH = 500)
        self.target_y = 20  # 화면 상단

        # 현재 위치 (애니메이션용)
        self.current_x = self.target_x
        self.current_y = -self.height  # 화면 밖에서 시작

    def update(self):
        """알림 업데이트 (애니메이션)"""
        self.timer += 1

        # 슬라이드 인 애니메이션
        if self.timer < self.slide_in_duration:
            progress = self.timer / self.slide_in_duration
            # easeOutCubic
            progress = 1 - pow(1 - progress, 3)
            self.current_y = -self.height + (self.target_y + self.height) * progress

        # 표시 상태
        elif self.timer < self.max_duration - self.slide_out_duration:
            self.current_y = self.target_y

        # 슬라이드 아웃 애니메이션
        elif self.timer < self.max_duration:
            remaining_time = self.max_duration - self.timer
            progress = remaining_time / self.slide_out_duration
            # easeInCubic
            progress = pow(progress, 3)
            self.current_y = self.target_y + (self.target_y + self.height) * (1 - progress)

    def is_finished(self) -> bool:
        """
        알림이 끝났는지 확인

        Returns:
            bool: 알림이 끝났으면 True
        """
        return self.timer >= self.max_duration

    def draw(self, screen: pygame.Surface, font_name: str = None):
        """
        알림 그리기

        Args:
            screen: pygame 화면
            font_name: 폰트 파일 경로 (선택사항)
        """
        # 알림 박스 배경
        box_rect = pygame.Rect(
            int(self.current_x),
            int(self.current_y),
            self.width,
            self.height
        )

        # 테두리가 있는 반투명 박스
        # 배경
        box_surface = pygame.Surface((self.width, self.height))
        box_surface.set_alpha(230)
        box_surface.fill((30, 30, 50))
        screen.blit(box_surface, (box_rect.x, box_rect.y))

        # 테두리 (골드)
        pygame.draw.rect(screen, (255, 215, 0), box_rect, 3)

        # 상단 장식 라인
        pygame.draw.rect(
            screen,
            (255, 215, 0),
            (box_rect.x, box_rect.y, self.width, 8)
        )

        # 업적 아이콘 (트로피)
        icon_x = box_rect.x + 20
        icon_y = box_rect.y + self.height // 2

        # 트로피 모양 (간단한 원과 사각형)
        pygame.draw.circle(screen, (255, 215, 0), (icon_x, icon_y - 10), 15)
        pygame.draw.rect(
            screen,
            (255, 215, 0),
            (icon_x - 8, icon_y + 5, 16, 12)
        )

        # 텍스트
        try:
            from utils import load_font
            title_font = load_font(font_name, 26) if font_name else pygame.font.Font(None, 26)
            desc_font = load_font(font_name, 18) if font_name else pygame.font.Font(None, 18)
        except:
            title_font = pygame.font.Font(None, 26)
            desc_font = pygame.font.Font(None, 18)

        # "업적 달성!" 텍스트
        header_text = title_font.render("🏆 업적 달성!", True, (255, 215, 0))
        screen.blit(header_text, (icon_x + 35, box_rect.y + 15))

        # 업적 이름
        name_text = title_font.render(self.name, True, (255, 255, 255))
        screen.blit(name_text, (icon_x + 35, box_rect.y + 45))

        # 업적 설명 (작은 글씨)
        desc_text = desc_font.render(self.description, True, (200, 200, 200))
        screen.blit(desc_text, (icon_x + 35, box_rect.y + 72))


class AchievementNotificationManager:
    """
    업적 알림 관리자

    여러 업적이 연속으로 달성될 때 큐로 관리합니다.
    """

    def __init__(self, checker: AchievementChecker):
        """
        관리자 초기화

        Args:
            checker: 업적 체커
        """
        self.checker = checker
        self.notification_queue: List[AchievementNotification] = []
        self.current_notification: Optional[AchievementNotification] = None

    def add_achievement(self, achievement_code: str):
        """
        업적 알림 추가

        Args:
            achievement_code: 업적 코드
        """
        notification = AchievementNotification(achievement_code, self.checker)
        self.notification_queue.append(notification)

    def update(self):
        """알림 업데이트"""
        # 현재 알림이 없고 큐에 대기 중인 알림이 있으면
        if not self.current_notification and self.notification_queue:
            self.current_notification = self.notification_queue.pop(0)

        # 현재 알림 업데이트
        if self.current_notification:
            self.current_notification.update()

            # 알림이 끝났으면 제거
            if self.current_notification.is_finished():
                self.current_notification = None

    def draw(self, screen: pygame.Surface, font_name: str = None):
        """
        알림 그리기

        Args:
            screen: pygame 화면
            font_name: 폰트 파일 경로
        """
        if self.current_notification:
            self.current_notification.draw(screen, font_name)

    def has_active_notification(self) -> bool:
        """
        활성 알림이 있는지 확인

        Returns:
            bool: 활성 알림이 있으면 True
        """
        return self.current_notification is not None

    def has_pending_notifications(self) -> bool:
        """
        대기 중인 알림이 있는지 확인

        Returns:
            bool: 대기 중인 알림이 있으면 True
        """
        return len(self.notification_queue) > 0

    def clear(self):
        """모든 알림 제거"""
        self.current_notification = None
        self.notification_queue.clear()
