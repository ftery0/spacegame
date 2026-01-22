"""프로필 및 통계 화면"""
import pygame
from core.config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, RED, Resources, UI
from utils import load_font
from services.api_service import GameAPIClient
from screens.base_screen import BaseScreen


class ProfileScreen(BaseScreen):
    """프로필 및 통계 화면 클래스"""

    def __init__(self, screen: pygame.Surface, background_img: pygame.Surface, api_client: GameAPIClient):
        """
        ProfileScreen 초기화

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
        self.font_small = load_font(Resources.MAIN_FONT, 22)

        # BACK 버튼
        self.back_button = pygame.Rect(20, 50, 100, 50)

        # 데이터
        self.error_message = ""
        self.stats = None
        self.my_scores = []

        # 초기 데이터 로드
        self._load_data()

    def _load_data(self):
        """프로필 데이터 로드"""
        # 로그인 확인
        if not self.api_client.is_logged_in():
            self.error_message = "로그인이 필요합니다"
        else:
            # 통계 데이터 가져오기
            if not self.api_client.check_connection():
                self.error_message = "서버에 연결할 수 없습니다"
            else:
                self.stats = self.api_client.get_my_stats()
                self.my_scores = self.api_client.get_my_scores()

                if not self.stats:
                    self.error_message = "통계 데이터를 불러올 수 없습니다"

                # 최근 5개만 표시
                self.my_scores = self.my_scores[:5] if self.my_scores else []

    def handle_events(self) -> bool:
        """이벤트 처리"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.back_button.collidepoint(event.pos):
                    return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

        return True

    def update(self):
        """상태 업데이트"""
        pass

    def render(self):
        """화면 렌더링"""
        self.draw_background()

        # 반투명 오버레이
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(220)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        mouse_pos = pygame.mouse.get_pos()

        # BACK 버튼
        button_color = (100, 100, 100) if self.back_button.collidepoint(mouse_pos) else (50, 50, 50)
        pygame.draw.rect(self.screen, button_color, self.back_button)
        pygame.draw.rect(self.screen, WHITE, self.back_button, 2)
        back_text = self.font_small.render("BACK", True, WHITE)
        back_rect = back_text.get_rect(center=self.back_button.center)
        self.screen.blit(back_text, back_rect)

        if self.error_message:
            # 에러 메시지
            error_text = self.font_medium.render(self.error_message, True, RED)
            error_rect = error_text.get_rect(center=(SCREEN_WIDTH // 2, 400))
            self.screen.blit(error_text, error_rect)

        elif self.stats:
            # 제목 (사용자 이름)
            title_text = self.font_large.render(f"👤 {self.stats['username']}", True, (100, 200, 255))
            title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 120))
            self.screen.blit(title_text, title_rect)

            # 통계 박스
            stats_box = pygame.Rect(50, 180, SCREEN_WIDTH - 100, 280)
            pygame.draw.rect(self.screen, (30, 30, 50), stats_box)
            pygame.draw.rect(self.screen, (100, 100, 255), stats_box, 3)

            # 통계 제목
            stats_title = self.font_medium.render("📊 나의 통계", True, WHITE)
            self.screen.blit(stats_title, (70, 200))

            # 구분선
            pygame.draw.line(self.screen, WHITE, (70, 235), (SCREEN_WIDTH - 70, 235), 2)

            # 통계 정보
            y_offset = 260

            # 순위
            rank_text = self.font_small.render(f"🏆 전체 순위: {self.stats['rank']}위", True, (255, 215, 0))
            self.screen.blit(rank_text, (80, y_offset))
            y_offset += 45

            # 총 게임 수
            games_text = self.font_small.render(f"🎮 총 게임 수: {self.stats['total_games']}회", True, WHITE)
            self.screen.blit(games_text, (80, y_offset))
            y_offset += 45

            # 최고 점수
            best_text = self.font_small.render(f"⭐ 최고 점수: {self.stats['best_score']}", True, (0, 255, 0))
            self.screen.blit(best_text, (80, y_offset))
            y_offset += 45

            # 평균 점수
            avg_text = self.font_small.render(f"📈 평균 점수: {self.stats['average_score']:.1f}", True, (255, 255, 100))
            self.screen.blit(avg_text, (80, y_offset))

            # 최근 기록
            if self.my_scores:
                recent_title = self.font_medium.render("📜 최근 기록 (최대 5개)", True, WHITE)
                self.screen.blit(recent_title, (70, 490))

                pygame.draw.line(self.screen, WHITE, (70, 525), (SCREEN_WIDTH - 70, 525), 2)

                # 최근 점수 표시
                for i, score_data in enumerate(self.my_scores):
                    y_pos = 545 + i * 35

                    # 점수
                    score_text = self.font_small.render(f"{i+1}. {score_data['score']}점", True, WHITE)
                    self.screen.blit(score_text, (80, y_pos))

        # 안내 문구
        hint_text = self.font_small.render("ESC: 뒤로가기", True, (150, 150, 150))
        self.screen.blit(hint_text, (SCREEN_WIDTH // 2 - 80, 750))


# 하위호환성을 위한 함수
def show_profile_screen(screen, background_img, api_client: GameAPIClient):
    """
    프로필 및 통계 화면 표시 (하위호환성 래퍼 함수)

    Args:
        screen: pygame 화면
        background_img: 배경 이미지
        api_client: API 클라이언트
    """
    profile_screen = ProfileScreen(screen, background_img, api_client)
    profile_screen.run()
