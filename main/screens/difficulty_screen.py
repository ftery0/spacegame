"""난이도 선택 화면"""
import pygame
from core.config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, RED, Resources, UI
from utils import load_font
from screens.base_screen import BaseScreen
from game.difficulty import DifficultyManager, DifficultyLevel


class DifficultyScreen(BaseScreen):
    """난이도 선택 화면 클래스"""

    def __init__(self, screen: pygame.Surface, background_img: pygame.Surface, difficulty_manager: DifficultyManager):
        """
        DifficultyScreen 초기화

        Args:
            screen: pygame 화면
            background_img: 배경 이미지
            difficulty_manager: 난이도 관리자
        """
        super().__init__(screen, background_img)
        self.difficulty_manager = difficulty_manager

        # 폰트 로드
        self.font_large = load_font(Resources.MAIN_FONT, UI.FONT_SIZE_LARGE)
        self.font_medium = load_font(Resources.MAIN_FONT, UI.FONT_SIZE_MEDIUM)
        self.font_small = load_font(Resources.MAIN_FONT, 20)

        # 선택된 난이도
        self.selected_difficulty = difficulty_manager.get_current_difficulty()

        # 버튼 생성
        button_width = 250
        button_height = 120
        button_spacing = 30
        start_x = (SCREEN_WIDTH - (button_width * 3 + button_spacing * 2)) // 2
        y_pos = 250

        self.easy_button = pygame.Rect(start_x, y_pos, button_width, button_height)
        self.medium_button = pygame.Rect(start_x + button_width + button_spacing, y_pos, button_width, button_height)
        self.hard_button = pygame.Rect(start_x + (button_width + button_spacing) * 2, y_pos, button_width, button_height)

        self.confirm_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, 500, 200, 60)
        self.back_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, 580, 200, 60)

        # 난이도 정보
        self.difficulties = {
            DifficultyLevel.EASY: {
                "button": self.easy_button,
                "color": (0, 200, 100),  # 초록
                "hover_color": (0, 255, 120),
                "emoji": "🟢"
            },
            DifficultyLevel.MEDIUM: {
                "button": self.medium_button,
                "color": (200, 200, 0),  # 노랑
                "hover_color": (255, 255, 0),
                "emoji": "🟡"
            },
            DifficultyLevel.HARD: {
                "button": self.hard_button,
                "color": (200, 0, 0),  # 빨강
                "hover_color": (255, 0, 0),
                "emoji": "🔴"
            }
        }

    def handle_events(self) -> bool:
        """이벤트 처리"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos

                # 난이도 선택
                if self.easy_button.collidepoint(mouse_pos):
                    self.selected_difficulty = DifficultyLevel.EASY
                elif self.medium_button.collidepoint(mouse_pos):
                    self.selected_difficulty = DifficultyLevel.MEDIUM
                elif self.hard_button.collidepoint(mouse_pos):
                    self.selected_difficulty = DifficultyLevel.HARD

                # 확인 버튼
                elif self.confirm_button.collidepoint(mouse_pos):
                    self.difficulty_manager.set_difficulty(self.selected_difficulty)
                    self.running = False
                    self.difficulty_manager.set_difficulty(self.selected_difficulty)
                    self.running = False
                    return self.running

                # 뒤로 가기
                elif self.back_button.collidepoint(mouse_pos):
                    self.running = False
                elif self.back_button.collidepoint(mouse_pos):
                    self.running = False
                    return self.running

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    return self.running

        return self.running

    def update(self):
        """상태 업데이트 (현재 필요 없음)"""
        pass

    def render(self):
        """화면 렌더링"""
        self.draw_background()

        # 반투명 오버레이
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        mouse_pos = pygame.mouse.get_pos()

        # 제목
        title_text = self.font_large.render("난이도 선택", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title_text, title_rect)

        # 난이도 버튼들
        for level, info in self.difficulties.items():
            self._draw_difficulty_button(level, info, mouse_pos)

        # 선택된 난이도 정보 표시
        self._draw_difficulty_info()

        # 확인/뒤로 버튼
        self._draw_action_buttons(mouse_pos)

    def _draw_difficulty_button(self, level: str, info: dict, mouse_pos: tuple):
        """난이도 버튼 그리기"""
        button = info["button"]
        is_selected = (level == self.selected_difficulty)
        is_hover = button.collidepoint(mouse_pos)

        # 버튼 색상
        if is_selected:
            color = info["hover_color"]
            border_width = 5
        elif is_hover:
            color = info["color"]
            border_width = 3
        else:
            color = tuple(color_val // 2 for color_val in info["color"])
            border_width = 2

        # 버튼 배경
        pygame.draw.rect(self.screen, color, button)
        pygame.draw.rect(self.screen, WHITE, button, border_width)

        # 난이도 이름
        display_name = self.difficulty_manager.get_display_name(level)
        name_text = self.font_medium.render(display_name, True, WHITE)
        name_rect = name_text.get_rect(center=(button.centerx, button.centery - 20))
        self.screen.blit(name_text, name_rect)

        # 배율 표시
        settings = self.difficulty_manager.get_difficulty_info(level)
        if settings:
            multiplier = settings.get("score_multiplier", 1.0)
            mult_text = self.font_small.render(f"x{multiplier:.1f}", True, WHITE)
            mult_rect = mult_text.get_rect(center=(button.centerx, button.centery + 20))
            self.screen.blit(mult_text, mult_rect)

    def _draw_difficulty_info(self):
        """선택된 난이도 정보 표시"""
        settings = self.difficulty_manager.get_difficulty_info(self.selected_difficulty)
        if not settings:
            return

        info_y = 420
        info_texts = [
            f"운석 속도: {settings['stone_speed']:.1f}",
            f"적 등장 확률: {int(settings['enemy_spawn_chance'] * 100)}%",
            f"체력: {settings['player_health']}",
            f"점수 배율: x{settings['score_multiplier']:.1f}"
        ]

        for i, text in enumerate(info_texts):
            info_text = self.font_small.render(text, True, WHITE)
            info_rect = info_text.get_rect(center=(SCREEN_WIDTH // 2, info_y + i * 25))
            self.screen.blit(info_text, info_rect)

    def _draw_action_buttons(self, mouse_pos: tuple):
        """확인/뒤로 버튼 그리기"""
        # 확인 버튼
        confirm_color = (0, 150, 0) if self.confirm_button.collidepoint(mouse_pos) else (0, 100, 0)
        pygame.draw.rect(self.screen, confirm_color, self.confirm_button)
        pygame.draw.rect(self.screen, WHITE, self.confirm_button, 2)
        confirm_text = self.font_medium.render("확인", True, WHITE)
        confirm_rect = confirm_text.get_rect(center=self.confirm_button.center)
        self.screen.blit(confirm_text, confirm_rect)

        # 뒤로 버튼
        back_color = (100, 100, 100) if self.back_button.collidepoint(mouse_pos) else (70, 70, 70)
        pygame.draw.rect(self.screen, back_color, self.back_button)
        pygame.draw.rect(self.screen, WHITE, self.back_button, 2)
        back_text = self.font_medium.render("뒤로", True, WHITE)
        back_rect = back_text.get_rect(center=self.back_button.center)
        self.screen.blit(back_text, back_rect)


def show_difficulty_screen(screen: pygame.Surface, background_img: pygame.Surface,
                          difficulty_manager: DifficultyManager) -> bool:
    """
    난이도 선택 화면 표시 (하위호환성 래퍼 함수)

    Args:
        screen: pygame 화면
        background_img: 배경 이미지
        difficulty_manager: 난이도 관리자

    Returns:
        bool: 성공 여부
    """
    difficulty_screen = DifficultyScreen(screen, background_img, difficulty_manager)
    difficulty_screen.run()
    return True
