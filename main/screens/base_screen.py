"""Abstract base screen class"""
from abc import ABC, abstractmethod
import pygame


class BaseScreen(ABC):
    """모든 화면의 기본 추상 클래스"""

    def __init__(self, screen: pygame.Surface, background_img: pygame.Surface):
        """
        기본 화면 초기화

        Args:
            screen: pygame 화면
            background_img: 배경 이미지
        """
        self.screen = screen
        self.background_img = background_img
        self.running = True
        self.clock = pygame.time.Clock()

    @abstractmethod
    def handle_events(self) -> bool:
        """
        이벤트 처리

        Returns:
            bool: 계속 실행할지 여부 (True: 계속, False: 종료)
        """
        pass

    @abstractmethod
    def update(self):
        """상태 업데이트"""
        pass

    @abstractmethod
    def render(self):
        """화면 렌더링"""
        pass

    def run(self) -> bool:
        """
        화면 메인 루프 실행

        Returns:
            bool: 다음 화면으로 진행할지 여부
        """
        self.running = True
        while self.running:
            self.running = self.handle_events()
            self.update()
            self.render()
            pygame.display.flip()
            self.clock.tick(30)

        return self.on_exit()

    def on_exit(self) -> bool:
        """
        화면 종료 시 처리

        Returns:
            bool: 다음 화면으로 진행할지 여부 (기본값: True)
        """
        return True

    def draw_background(self):
        """배경 이미지 그리기"""
        self.screen.blit(self.background_img, [0, 0])

    def quit(self):
        """화면 종료"""
        self.running = False
