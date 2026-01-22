"""Reusable Button component"""
import pygame
from typing import Callable, Optional


class Button:
    """재사용 가능한 버튼 컴포넌트"""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        font: pygame.font.Font,
        color_normal: tuple = (50, 50, 50),
        color_hover: tuple = (100, 100, 100),
        text_color: tuple = (255, 255, 255),
        text_color_hover: tuple = (255, 0, 0),
        on_click: Optional[Callable] = None
    ):
        """
        버튼 초기화

        Args:
            x: X 위치
            y: Y 위치
            width: 버튼 너비
            height: 버튼 높이
            text: 버튼 텍스트
            font: 폰트
            color_normal: 일반 상태 배경색
            color_hover: 호버 상태 배경색
            text_color: 일반 상태 텍스트색
            text_color_hover: 호버 상태 텍스트색
            on_click: 클릭 시 콜백 함수
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color_normal = color_normal
        self.color_hover = color_hover
        self.text_color = text_color
        self.text_color_hover = text_color_hover
        self.on_click = on_click
        self.is_hovered = False

    def check_hover(self, mouse_pos: tuple) -> bool:
        """
        마우스가 버튼 위에 있는지 확인

        Args:
            mouse_pos: 마우스 위치 (x, y)

        Returns:
            bool: 호버 상태 여부
        """
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered

    def check_click(self, mouse_pos: tuple) -> bool:
        """
        버튼 클릭 확인

        Args:
            mouse_pos: 마우스 위치 (x, y)

        Returns:
            bool: 클릭되었는지 여부
        """
        if self.rect.collidepoint(mouse_pos):
            if self.on_click:
                self.on_click()
            return True
        return False

    def draw(self, screen: pygame.Surface):
        """
        버튼 그리기

        Args:
            screen: pygame 화면
        """
        # 배경 그리기
        bg_color = self.color_hover if self.is_hovered else self.color_normal
        pygame.draw.rect(screen, bg_color, self.rect)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 2)

        # 텍스트 그리기
        text_color = self.text_color_hover if self.is_hovered else self.text_color
        text_surface = self.font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def update_text(self, new_text: str):
        """
        버튼 텍스트 업데이트

        Args:
            new_text: 새로운 텍스트
        """
        self.text = new_text

    def set_position(self, x: int, y: int):
        """
        버튼 위치 변경

        Args:
            x: 새로운 X 위치
            y: 새로운 Y 위치
        """
        self.rect.x = x
        self.rect.y = y

    def is_clicked(self, event: pygame.event.Event) -> bool:
        """
        이벤트가 버튼 클릭인지 확인

        Args:
            event: pygame 이벤트

        Returns:
            bool: 클릭 여부
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            return self.check_click(event.pos)
        return False
