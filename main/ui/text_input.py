"""Reusable TextInput component"""
import pygame


class TextInput:
    """재사용 가능한 텍스트 입력 컴포넌트"""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        placeholder: str = "",
        font: pygame.font.Font = None,
        text_color: tuple = (0, 0, 0),
        bg_color: tuple = (255, 255, 255),
        border_color: tuple = (0, 0, 0),
        is_password: bool = False
    ):
        """
        텍스트 입력 필드 초기화

        Args:
            x: X 위치
            y: Y 위치
            width: 너비
            height: 높이
            placeholder: 플레이스홀더 텍스트
            font: 폰트
            text_color: 텍스트 색상
            bg_color: 배경색
            border_color: 테두리 색상
            is_password: 비밀번호 필드 여부
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.placeholder = placeholder
        self.font = font or pygame.font.Font(None, 24)
        self.text = ""
        self.display_text = ""
        self.text_color = text_color
        self.bg_color = bg_color
        self.border_color = border_color
        self.is_password = is_password
        self.is_focused = False
        self.cursor_visible = True
        self.cursor_timer = 0

    def handle_event(self, event: pygame.event.Event):
        """
        이벤트 처리

        Args:
            event: pygame 이벤트
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.is_focused = self.rect.collidepoint(event.pos)

        elif event.type == pygame.KEYDOWN and self.is_focused:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_TAB:
                self.is_focused = False
            elif len(self.text) < 50:  # 최대 길이 50
                if event.unicode.isprintable():
                    self.text += event.unicode

        self._update_display_text()

    def _update_display_text(self):
        """디스플레이 텍스트 업데이트 (비밀번호 마스킹)"""
        if self.is_password:
            self.display_text = "*" * len(self.text)
        else:
            self.display_text = self.text

    def draw(self, screen: pygame.Surface):
        """
        텍스트 입력 필드 그리기

        Args:
            screen: pygame 화면
        """
        # 배경 그리기
        pygame.draw.rect(screen, self.bg_color, self.rect)

        # 테두리 그리기
        border_width = 3 if self.is_focused else 1
        pygame.draw.rect(screen, self.border_color, self.rect, border_width)

        # 텍스트 렌더링
        text_to_display = self.display_text if self.text else self.placeholder
        text_color = self.text_color if self.text else (150, 150, 150)
        text_surface = self.font.render(text_to_display, True, text_color)

        # 커서 렌더링
        text_width = text_surface.get_width()
        cursor_x = self.rect.x + 10 + text_width

        if self.is_focused and self.cursor_visible:
            pygame.draw.line(
                screen,
                self.text_color,
                (cursor_x, self.rect.y + 5),
                (cursor_x, self.rect.y + self.rect.height - 5),
                2
            )

        # 텍스트 위치 조정 (입력 필드 너비 초과 시 스크롤)
        text_x = max(10, self.rect.x + 10 - (text_width - (self.rect.width - 20)))
        screen.blit(text_surface, (text_x, self.rect.y + 5))

        # 커서 깜빡임 처리
        self.cursor_timer += 1
        if self.cursor_timer > 30:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

    def get_text(self) -> str:
        """
        입력된 텍스트 반환

        Returns:
            str: 입력된 텍스트
        """
        return self.text

    def set_text(self, text: str):
        """
        텍스트 설정

        Args:
            text: 설정할 텍스트
        """
        self.text = text
        self._update_display_text()

    def clear(self):
        """입력 필드 초기화"""
        self.text = ""
        self.display_text = ""

    def is_empty(self) -> bool:
        """
        입력 필드가 비어있는지 확인

        Returns:
            bool: 비어있으면 True
        """
        return len(self.text) == 0

    def focus(self):
        """입력 필드에 포커스 설정"""
        self.is_focused = True

    def unfocus(self):
        """입력 필드 포커스 제거"""
        self.is_focused = False
