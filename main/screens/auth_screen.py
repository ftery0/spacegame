"""로그인 및 회원가입 화면"""
import pygame
from core.config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, RED, Resources, UI
from utils import load_font
from services.api_service import GameAPIClient
from screens.base_screen import BaseScreen


class AuthScreen(BaseScreen):
    """로그인/회원가입 화면 클래스"""

    def __init__(self, screen: pygame.Surface, background_img: pygame.Surface, api_client: GameAPIClient):
        """
        AuthScreen 초기화

        Args:
            screen: pygame 화면
            background_img: 배경 이미지
            api_client: API 클라이언트
        """
        super().__init__(screen, background_img)
        self.api_client = api_client

        # 폰트 로드
        self.font_large = load_font(Resources.MAIN_FONT, UI.FONT_SIZE_LARGE)
        self.font_medium = load_font(Resources.MAIN_FONT, UI.FONT_SIZE_MEDIUM)
        self.font_small = load_font(Resources.MAIN_FONT, 20)

        # 상태 변수
        self.mode = "login"
        self.username = ""
        self.password = ""
        self.active_field = "username"
        self.message = ""
        self.message_color = WHITE
        self.login_success = False

        # 버튼 생성
        self.login_tab = pygame.Rect(50, 100, 200, 60)
        self.register_tab = pygame.Rect(250, 100, 200, 60)
        self.username_box = pygame.Rect(SCREEN_WIDTH // 2 - 150, 250, 300, 50)
        self.password_box = pygame.Rect(SCREEN_WIDTH // 2 - 150, 330, 300, 50)
        self.submit_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, 430, 200, 50)
        self.skip_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, 510, 200, 50)

    def handle_events(self) -> bool:
        """이벤트 처리"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos

                # 탭 전환
                if self.login_tab.collidepoint(mouse_pos):
                    self.mode = "login"
                    self.message = ""
                elif self.register_tab.collidepoint(mouse_pos):
                    self.mode = "register"
                    self.message = ""

                # 입력 필드 선택
                if self.username_box.collidepoint(mouse_pos):
                    self.active_field = "username"
                elif self.password_box.collidepoint(mouse_pos):
                    self.active_field = "password"

                # 제출 버튼
                if self.submit_button.collidepoint(mouse_pos):
                    self._handle_submit()

                # 건너뛰기 버튼
                if self.skip_button.collidepoint(mouse_pos):
                    return False

            if event.type == pygame.KEYDOWN:
                self._handle_keydown(event)

        return True

    def _handle_submit(self):
        """제출 버튼 처리"""
        if not self.username.strip() or not self.password.strip():
            self.message = "아이디와 비밀번호를 입력하세요"
            self.message_color = RED
        else:
            if not self.api_client.check_connection():
                self.message = "서버에 연결할 수 없습니다 (오프라인 모드)"
                self.message_color = RED
            else:
                if self.mode == "login":
                    success, data, error = self.api_client.login(self.username.strip(), self.password)
                    if success:
                        self.message = f"환영합니다, {self.username}님!"
                        self.message_color = (0, 255, 0)
                        pygame.time.wait(1000)
                        self.login_success = True
                        self.running = False
                    else:
                        self.message = error if error else "로그인 실패"
                        self.message_color = RED
                else:  # register
                    if len(self.username.strip()) < 3:
                        self.message = "아이디는 3자 이상이어야 합니다"
                        self.message_color = RED
                    elif len(self.password) < 4:
                        self.message = "비밀번호는 4자 이상이어야 합니다"
                        self.message_color = RED
                    else:
                        success, data, error = self.api_client.register(self.username.strip(), self.password)
                        if success:
                            self.message = "회원가입 완료! 환영합니다!"
                            self.message_color = (0, 255, 0)
                            pygame.time.wait(1000)
                            self.login_success = True
                            self.running = False
                        else:
                            self.message = error if error else "회원가입 실패"
                            self.message_color = RED

    def _handle_keydown(self, event: pygame.event.Event):
        """키 입력 처리"""
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

        # 탭 그리기
        self._draw_tabs(mouse_pos)

        # 제목
        title = "로그인" if self.mode == "login" else "회원가입"
        title_text = self.font_large.render(title, True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(title_text, title_rect)

        # 입력 필드 그리기
        self._draw_input_fields(mouse_pos)

        # 버튼 그리기
        self._draw_buttons(mouse_pos)

        # 메시지
        if self.message:
            msg_text = self.font_small.render(self.message, True, self.message_color)
            msg_rect = msg_text.get_rect(center=(SCREEN_WIDTH // 2, 600))
            self.screen.blit(msg_text, msg_rect)

        # 안내 문구
        if self.mode == "register":
            hint = "아이디 3자 이상, 비밀번호 4자 이상"
        else:
            hint = "Tab: 필드 전환 | Enter: 로그인"
        hint_text = self.font_small.render(hint, True, (150, 150, 150))
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, 650))
        self.screen.blit(hint_text, hint_rect)

    def _draw_tabs(self, mouse_pos):
        """탭 그리기"""
        # 로그인 탭
        tab_color = (70, 70, 150) if self.mode == "login" else (50, 50, 50)
        pygame.draw.rect(self.screen, tab_color, self.login_tab)
        pygame.draw.rect(self.screen, WHITE if self.login_tab.collidepoint(mouse_pos) else (150, 150, 150), self.login_tab, 2)
        login_text = self.font_medium.render("로그인", True, WHITE)
        login_rect = login_text.get_rect(center=self.login_tab.center)
        self.screen.blit(login_text, login_rect)

        # 회원가입 탭
        tab_color = (70, 70, 150) if self.mode == "register" else (50, 50, 50)
        pygame.draw.rect(self.screen, tab_color, self.register_tab)
        pygame.draw.rect(self.screen, WHITE if self.register_tab.collidepoint(mouse_pos) else (150, 150, 150), self.register_tab, 2)
        register_text = self.font_medium.render("회원가입", True, WHITE)
        register_rect = register_text.get_rect(center=self.register_tab.center)
        self.screen.blit(register_text, register_rect)

    def _draw_input_fields(self, mouse_pos):
        """입력 필드 그리기"""
        # 아이디 입력
        username_label = self.font_small.render("아이디:", True, WHITE)
        self.screen.blit(username_label, (self.username_box.x, self.username_box.y - 25))
        box_color = (100, 100, 255) if self.active_field == "username" else WHITE
        pygame.draw.rect(self.screen, box_color, self.username_box, 2)
        username_text = self.font_medium.render(self.username, True, WHITE)
        self.screen.blit(username_text, (self.username_box.x + 10, self.username_box.y + 10))

        # 커서 (아이디)
        if self.active_field == "username" and pygame.time.get_ticks() % 1000 < 500:
            cursor_x = self.username_box.x + 10 + username_text.get_width() + 2
            pygame.draw.line(self.screen, WHITE, (cursor_x, self.username_box.y + 10), (cursor_x, self.username_box.y + 40), 2)

        # 비밀번호 입력
        password_label = self.font_small.render("비밀번호:", True, WHITE)
        self.screen.blit(password_label, (self.password_box.x, self.password_box.y - 25))
        box_color = (100, 100, 255) if self.active_field == "password" else WHITE
        pygame.draw.rect(self.screen, box_color, self.password_box, 2)
        password_display = "*" * len(self.password)
        password_text = self.font_medium.render(password_display, True, WHITE)
        self.screen.blit(password_text, (self.password_box.x + 10, self.password_box.y + 10))

        # 커서 (비밀번호)
        if self.active_field == "password" and pygame.time.get_ticks() % 1000 < 500:
            cursor_x = self.password_box.x + 10 + password_text.get_width() + 2
            pygame.draw.line(self.screen, WHITE, (cursor_x, self.password_box.y + 10), (cursor_x, self.password_box.y + 40), 2)

    def _draw_buttons(self, mouse_pos):
        """버튼 그리기"""
        title = "로그인" if self.mode == "login" else "회원가입"

        # 제출 버튼
        button_color = (0, 150, 0) if self.submit_button.collidepoint(mouse_pos) else (0, 100, 0)
        pygame.draw.rect(self.screen, button_color, self.submit_button)
        pygame.draw.rect(self.screen, WHITE, self.submit_button, 2)
        submit_text = self.font_medium.render(title, True, WHITE)
        submit_rect = submit_text.get_rect(center=self.submit_button.center)
        self.screen.blit(submit_text, submit_rect)

        # 건너뛰기 버튼
        button_color = (100, 100, 100) if self.skip_button.collidepoint(mouse_pos) else (70, 70, 70)
        pygame.draw.rect(self.screen, button_color, self.skip_button)
        pygame.draw.rect(self.screen, WHITE, self.skip_button, 2)
        skip_text = self.font_small.render("오프라인으로 플레이", True, WHITE)
        skip_rect = skip_text.get_rect(center=self.skip_button.center)
        self.screen.blit(skip_text, skip_rect)

    def on_exit(self) -> bool:
        """
        화면 종료 시 처리

        Returns:
            bool: 로그인 성공 여부
        """
        return self.login_success


# 하위호환성을 위한 함수
def show_auth_screen(screen, background_img, api_client: GameAPIClient):
    """
    로그인/회원가입 화면 (하위호환성 래퍼 함수)

    Args:
        screen: pygame 화면
        background_img: 배경 이미지
        api_client: API 클라이언트

    Returns:
        bool: 로그인 성공 여부
    """
    auth_screen = AuthScreen(screen, background_img, api_client)
    auth_screen.run()
    return auth_screen.on_exit()
