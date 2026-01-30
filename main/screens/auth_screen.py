"""로그인 및 회원가입 화면 - 글래스모피즘 UI"""
import pygame
import math
from core.config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, RED, Resources, UI
from utils import load_font
from services.api_service import GameAPIClient
from screens.base_screen import BaseScreen


class AuthScreen(BaseScreen):
    """로그인/회원가입 화면 - 부드럽고 현대적인 디자인"""

    def __init__(self, screen: pygame.Surface, background_img: pygame.Surface, api_client: GameAPIClient):
        super().__init__(screen, background_img)
        self.api_client = api_client

        # 폰트 로드
        self.font_title = load_font(Resources.MAIN_FONT, 56)
        self.font_subtitle = load_font(Resources.MAIN_FONT, 24)
        self.font_large = load_font(Resources.MAIN_FONT, 28)
        self.font_medium = load_font(Resources.MAIN_FONT, 22)
        self.font_small = load_font(Resources.MAIN_FONT, 16)

        # 글로우/네온 색상 팔레트
        self.COLOR_NEON_BLUE = (0, 229, 255)  # 시안
        self.COLOR_NEON_PURPLE = (191, 64, 191)  # 네온 퍼플
        self.COLOR_NEON_PINK = (255, 20, 147)  # 핫핑크
        self.COLOR_SUCCESS = (0, 255, 127)  # 스프링 그린
        self.COLOR_ERROR = (255, 69, 58)  # 밝은 레드

        # 배경/글래스 색상
        self.COLOR_GLASS = (255, 255, 255, 25)  # 반투명 흰색
        self.COLOR_GLASS_BORDER = (255, 255, 255, 80)
        self.COLOR_TEXT = (255, 255, 255)
        self.COLOR_TEXT_DIM = (200, 200, 220)
        self.COLOR_INPUT_BG = (30, 30, 50, 100)

        # 상태
        self.mode = "login"
        self.username = ""
        self.password = ""
        self.active_field = "username"
        self.message = ""
        self.message_color = WHITE
        self.login_success = False

        # 애니메이션
        self.time = 0
        self.tab_slide_progress = 0
        self.message_alpha = 0
        self.input_focus_glow = {"username": 0, "password": 0}

        self._calculate_positions()

    def _calculate_positions(self):
        """UI 위치 계산 - 더 넓고 여유로운 레이아웃"""
        # 메인 컨테이너
        container_width = 460
        container_height = 580
        self.container_x = (SCREEN_WIDTH - container_width) // 2
        self.container_y = (SCREEN_HEIGHT - container_height) // 2

        # 제목 영역
        self.title_y = self.container_y + 40

        # 탭 (언더라인 스타일)
        self.tab_y = self.container_y + 120
        tab_width = 120
        tab_spacing = 40
        total_tabs_width = tab_width * 2 + tab_spacing
        start_x = (SCREEN_WIDTH - total_tabs_width) // 2

        self.login_tab = pygame.Rect(start_x, self.tab_y, tab_width, 40)
        self.register_tab = pygame.Rect(start_x + tab_width + tab_spacing, self.tab_y, tab_width, 40)

        # 입력 필드 (더 크고 여유롭게)
        input_width = 380
        input_x = (SCREEN_WIDTH - input_width) // 2
        self.username_box = pygame.Rect(input_x, self.container_y + 210, input_width, 65)
        self.password_box = pygame.Rect(input_x, self.container_y + 300, input_width, 65)

        # 버튼
        button_width = 380
        button_x = (SCREEN_WIDTH - button_width) // 2
        self.submit_button = pygame.Rect(button_x, self.container_y + 400, button_width, 60)
        self.skip_button = pygame.Rect(button_x, self.container_y + 480, button_width, 48)

    def handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos

                if self.login_tab.collidepoint(mouse_pos):
                    if self.mode != "login":
                        self.mode = "login"
                        self.message = ""
                        self.message_alpha = 0
                elif self.register_tab.collidepoint(mouse_pos):
                    if self.mode != "register":
                        self.mode = "register"
                        self.message = ""
                        self.message_alpha = 0

                if self.username_box.collidepoint(mouse_pos):
                    self.active_field = "username"
                elif self.password_box.collidepoint(mouse_pos):
                    self.active_field = "password"

                if self.submit_button.collidepoint(mouse_pos):
                    self._handle_submit()

                if self.skip_button.collidepoint(mouse_pos):
                    return False

            if event.type == pygame.KEYDOWN:
                self._handle_keydown(event)

        return True

    def _handle_submit(self):
        if not self.username.strip() or not self.password.strip():
            self.message = "아이디와 비밀번호를 입력하세요"
            self.message_color = self.COLOR_ERROR
            self.message_alpha = 255
        else:
            if not self.api_client.check_connection():
                self.message = "서버 연결 실패 (오프라인 모드)"
                self.message_color = self.COLOR_ERROR
                self.message_alpha = 255
            else:
                if self.mode == "login":
                    success, data, error = self.api_client.login(self.username.strip(), self.password)
                    if success:
                        self.message = f"환영합니다!"
                        self.message_color = self.COLOR_SUCCESS
                        self.message_alpha = 255
                        pygame.time.wait(800)
                        self.login_success = True
                        self.running = False
                    else:
                        self.message = error if error else "로그인 실패"
                        self.message_color = self.COLOR_ERROR
                        self.message_alpha = 255
                else:
                    if len(self.username.strip()) < 3:
                        self.message = "아이디는 3자 이상"
                        self.message_color = self.COLOR_ERROR
                        self.message_alpha = 255
                    elif len(self.password) < 4:
                        self.message = "비밀번호는 4자 이상"
                        self.message_color = self.COLOR_ERROR
                        self.message_alpha = 255
                    else:
                        success, data, error = self.api_client.register(self.username.strip(), self.password)
                        if success:
                            self.message = "회원가입 완료!"
                            self.message_color = self.COLOR_SUCCESS
                            self.message_alpha = 255
                            pygame.time.wait(800)
                            self.login_success = True
                            self.running = False
                        else:
                            self.message = error if error else "회원가입 실패"
                            self.message_color = self.COLOR_ERROR
                            self.message_alpha = 255

    def _handle_keydown(self, event):
        if event.key == pygame.K_TAB:
            self.active_field = "password" if self.active_field == "username" else "username"
        elif event.key == pygame.K_RETURN:
            if self.active_field == "password" and self.username.strip() and self.password.strip():
                self._handle_submit()
            elif self.active_field == "username":
                self.active_field = "password"
        elif event.key == pygame.K_BACKSPACE:
            if self.active_field == "username":
                self.username = self.username[:-1]
            else:
                self.password = self.password[:-1]
        elif event.key == pygame.K_ESCAPE:
            self.running = False
        else:
            if event.unicode.isprintable():
                if self.active_field == "username" and len(self.username) < 20:
                    self.username += event.unicode
                elif self.active_field == "password" and len(self.password) < 50:
                    self.password += event.unicode

    def update(self):
        self.time += 1

        # 입력 필드 글로우 애니메이션
        for field in ["username", "password"]:
            target = 1.0 if self.active_field == field else 0.0
            self.input_focus_glow[field] += (target - self.input_focus_glow[field]) * 0.15

        # 메시지 페이드
        if self.message_alpha > 0:
            self.message_alpha = max(0, self.message_alpha - 2)

    def render(self):
        self.draw_background()

        # 어두운 오버레이 (부드러운 그라데이션)
        self._draw_dark_overlay()

        # 배경 애니메이션 파티클
        self._draw_particles()

        # 타이틀
        self._draw_title()

        # 탭
        self._draw_tabs()

        mouse_pos = pygame.mouse.get_pos()

        # 입력 필드
        self._draw_input_field(
            self.username_box,
            "username",
            "아이디",
            self.username,
            False,
            mouse_pos
        )
        self._draw_input_field(
            self.password_box,
            "password",
            "비밀번호",
            self.password,
            True,
            mouse_pos
        )

        # 버튼
        self._draw_button(
            self.submit_button,
            "로그인" if self.mode == "login" else "회원가입",
            True,
            mouse_pos
        )
        self._draw_button(
            self.skip_button,
            "건너뛰기",
            False,
            mouse_pos
        )

        # 메시지
        if self.message and self.message_alpha > 0:
            self._draw_message()

        # 하단 도움말
        self._draw_help_text()

    def _draw_dark_overlay(self):
        """부드러운 어두운 오버레이"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)

        # 중앙이 밝은 방사형 그라데이션
        for r in range(max(SCREEN_WIDTH, SCREEN_HEIGHT) // 2, 0, -5):
            alpha = int(200 * (r / (max(SCREEN_WIDTH, SCREEN_HEIGHT) // 2)))
            color = (10, 10, 25)
            pygame.draw.circle(overlay, color, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), r)

        self.screen.blit(overlay, (0, 0))

    def _draw_particles(self):
        """배경 떠다니는 파티클"""
        for i in range(8):
            angle = (self.time * 0.01 + i * 45) % 360
            radius = 180 + math.sin(self.time * 0.02 + i) * 40
            x = SCREEN_WIDTH // 2 + math.cos(math.radians(angle)) * radius
            y = SCREEN_HEIGHT // 2 + math.sin(math.radians(angle)) * radius

            size = 3 + math.sin(self.time * 0.05 + i * 0.7) * 2

            # 네온 글로우
            glow_surf = pygame.Surface((size * 8, size * 8), pygame.SRCALPHA)
            color = self.COLOR_NEON_BLUE if i % 2 == 0 else self.COLOR_NEON_PURPLE

            for r in range(int(size * 4), 0, -1):
                alpha = int(30 * (1 - r / (size * 4)))
                pygame.draw.circle(glow_surf, (*color, alpha), (size * 4, size * 4), r)

            self.screen.blit(glow_surf, (x - size * 4, y - size * 4))

    def _draw_title(self):
        """타이틀 - 네온 효과"""
        title = "SPACE DEFENDER"

        # 네온 글로우
        title_surface = self.font_title.render(title, True, self.COLOR_NEON_BLUE)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, self.title_y))

        # 글로우 효과
        glow_surf = pygame.Surface((title_rect.width + 40, title_rect.height + 40), pygame.SRCALPHA)
        for i in range(10, 0, -1):
            alpha = int(20 * (1 - i / 10))
            glow_text = self.font_title.render(title, True, (*self.COLOR_NEON_BLUE, alpha))
            glow_rect = glow_text.get_rect(center=(glow_surf.get_width() // 2, glow_surf.get_height() // 2))
            glow_surf.blit(glow_text, (glow_rect.x + i - 5, glow_rect.y + i - 5))

        self.screen.blit(glow_surf, (title_rect.x - 20, title_rect.y - 20))
        self.screen.blit(title_surface, title_rect)

        # 서브타이틀
        subtitle = "로그인하여 게임을 시작하세요"
        sub_surface = self.font_small.render(subtitle, True, self.COLOR_TEXT_DIM)
        sub_rect = sub_surface.get_rect(center=(SCREEN_WIDTH // 2, self.title_y + 50))
        self.screen.blit(sub_surface, sub_rect)

    def _draw_tabs(self):
        """언더라인 스타일 탭"""
        for tab_rect, mode, text in [
            (self.login_tab, "login", "로그인"),
            (self.register_tab, "register", "회원가입")
        ]:
            is_active = self.mode == mode

            # 텍스트
            color = self.COLOR_NEON_BLUE if is_active else self.COLOR_TEXT_DIM
            tab_text = self.font_large.render(text, True, color)
            text_rect = tab_text.get_rect(center=tab_rect.center)
            self.screen.blit(tab_text, text_rect)

            # 활성 탭 언더라인 (네온)
            if is_active:
                line_y = tab_rect.bottom + 5
                # 글로우
                for i in range(5, 0, -1):
                    alpha = int(50 * (1 - i / 5))
                    pygame.draw.line(
                        self.screen,
                        (*self.COLOR_NEON_BLUE, alpha),
                        (tab_rect.left, line_y + i),
                        (tab_rect.right, line_y + i),
                        i
                    )
                # 메인 라인
                pygame.draw.line(
                    self.screen,
                    self.COLOR_NEON_BLUE,
                    (tab_rect.left, line_y),
                    (tab_rect.right, line_y),
                    3
                )

    def _draw_input_field(self, rect, field_name, label, value, is_password, mouse_pos):
        """글래스모피즘 입력 필드"""
        is_active = self.active_field == field_name
        is_hovered = rect.collidepoint(mouse_pos)
        glow_intensity = self.input_focus_glow[field_name]

        # 글로우 효과
        if glow_intensity > 0:
            glow_surf = pygame.Surface((rect.width + 20, rect.height + 20), pygame.SRCALPHA)
            glow_color = (*self.COLOR_NEON_BLUE, int(80 * glow_intensity))
            pygame.draw.rect(glow_surf, glow_color, glow_surf.get_rect(), border_radius=35)
            self.screen.blit(glow_surf, (rect.x - 10, rect.y - 10))

        # 글래스 배경
        glass_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        glass_surf.fill((40, 40, 60, 120))
        self.screen.blit(glass_surf, rect.topleft)

        # 테두리
        border_color = self.COLOR_NEON_BLUE if is_active else (
            (120, 120, 150) if is_hovered else (80, 80, 100)
        )
        border_width = 2 if is_active else 1
        pygame.draw.rect(self.screen, border_color, rect, border_width, border_radius=32)

        # 라벨 (필드 내부 상단)
        label_color = self.COLOR_NEON_BLUE if is_active else self.COLOR_TEXT_DIM
        label_surf = self.font_small.render(label, True, label_color)
        self.screen.blit(label_surf, (rect.x + 20, rect.y + 8))

        # 입력 텍스트
        display_text = value if not is_password else "•" * len(value)

        if display_text:
            text_surf = self.font_medium.render(display_text, True, self.COLOR_TEXT)
        else:
            placeholder = "입력하세요..."
            text_surf = self.font_medium.render(placeholder, True, (120, 120, 140))

        self.screen.blit(text_surf, (rect.x + 20, rect.y + 32))

        # 커서
        if is_active and pygame.time.get_ticks() % 1000 < 500:
            cursor_x = rect.x + 20 + text_surf.get_width() + 3
            pygame.draw.line(
                self.screen,
                self.COLOR_NEON_BLUE,
                (cursor_x, rect.y + 35),
                (cursor_x, rect.y + 55),
                2
            )

    def _draw_button(self, rect, text, is_primary, mouse_pos):
        """네온 버튼"""
        is_hovered = rect.collidepoint(mouse_pos)

        if is_primary:
            # 메인 버튼 - 네온 그라데이션
            if is_hovered:
                # 글로우
                glow_surf = pygame.Surface((rect.width + 30, rect.height + 30), pygame.SRCALPHA)
                for i in range(15, 0, -1):
                    alpha = int(40 * (1 - i / 15))
                    pygame.draw.rect(
                        glow_surf,
                        (*self.COLOR_NEON_BLUE, alpha),
                        glow_surf.get_rect(),
                        border_radius=35
                    )
                self.screen.blit(glow_surf, (rect.x - 15, rect.y - 15))

            # 버튼 배경 (그라데이션 효과)
            button_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            for y in range(rect.height):
                progress = y / rect.height
                r = int(self.COLOR_NEON_PURPLE[0] * (1 - progress) + self.COLOR_NEON_BLUE[0] * progress)
                g = int(self.COLOR_NEON_PURPLE[1] * (1 - progress) + self.COLOR_NEON_BLUE[1] * progress)
                b = int(self.COLOR_NEON_PURPLE[2] * (1 - progress) + self.COLOR_NEON_BLUE[2] * progress)
                pygame.draw.line(button_surf, (r, g, b, 200), (0, y), (rect.width, y))

            self.screen.blit(button_surf, rect.topleft)
            pygame.draw.rect(self.screen, self.COLOR_GLASS_BORDER, rect, 2, border_radius=30)
        else:
            # 보조 버튼 - 투명
            glass_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            glass_surf.fill((60, 60, 80, 80 if is_hovered else 50))
            self.screen.blit(glass_surf, rect.topleft)
            pygame.draw.rect(self.screen, (120, 120, 140), rect, 1, border_radius=24)

        # 텍스트
        text_surf = self.font_large.render(text, True, self.COLOR_TEXT)
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)

    def _draw_message(self):
        """메시지 팝업"""
        msg_surf = self.font_medium.render(self.message, True, self.message_color)
        msg_rect = msg_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80))

        # 배경
        bg_rect = msg_rect.inflate(40, 24)
        bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surf.fill((20, 20, 30, int(self.message_alpha * 0.9)))
        self.screen.blit(bg_surf, bg_rect.topleft)

        # 테두리
        pygame.draw.rect(self.screen, (*self.message_color, self.message_alpha), bg_rect, 2, border_radius=20)

        # 텍스트
        msg_surf.set_alpha(self.message_alpha)
        self.screen.blit(msg_surf, msg_rect)

    def _draw_help_text(self):
        """하단 도움말"""
        help_text = "Tab: 전환  •  Enter: 확인  •  ESC: 나가기"
        help_surf = self.font_small.render(help_text, True, (120, 120, 140))
        help_rect = help_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        self.screen.blit(help_surf, help_rect)

    def on_exit(self) -> bool:
        return self.login_success


def show_auth_screen(screen, background_img, api_client: GameAPIClient):
    auth_screen = AuthScreen(screen, background_img, api_client)
    auth_screen.run()
    return auth_screen.on_exit()
