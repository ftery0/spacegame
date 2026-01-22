"""랭킹 화면"""
import pygame
from core.config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, RED, Resources, UI
from utils import load_font
from services.api_service import GameAPIClient
from screens.base_screen import BaseScreen


class RankingScreen(BaseScreen):
    """랭킹 표시 화면"""

    def __init__(self, screen: pygame.Surface, background_img: pygame.Surface, api_client: GameAPIClient):
        """
        RankingScreen 초기화

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

        # 랭킹 데이터
        self.rankings = []
        self.error_message = ""
        self.loading = True

        # 초기 데이터 로드
        self._load_rankings()

    def _load_rankings(self):
        """랭킹 데이터 로드"""
        if not self.api_client.check_connection():
            self.error_message = "서버에 연결할 수 없습니다"
            self.loading = False
        else:
            self.rankings = self.api_client.get_top_scores(limit=10)
            if not self.rankings:
                self.error_message = "랭킹 데이터를 불러올 수 없습니다"
            self.loading = False

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

        # 제목
        title_text = self.font_large.render("🏆 TOP 10 랭킹", True, (255, 215, 0))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 120))
        self.screen.blit(title_text, title_rect)

        if self.loading:
            # 로딩 중
            loading_text = self.font_medium.render("로딩 중...", True, WHITE)
            loading_rect = loading_text.get_rect(center=(SCREEN_WIDTH // 2, 400))
            self.screen.blit(loading_text, loading_rect)

        elif self.error_message:
            # 에러 메시지
            error_text = self.font_medium.render(self.error_message, True, RED)
            error_rect = error_text.get_rect(center=(SCREEN_WIDTH // 2, 400))
            self.screen.blit(error_text, error_rect)

        else:
            # 헤더
            header_y = 180
            rank_header = self.font_small.render("순위", True, (200, 200, 200))
            self.screen.blit(rank_header, (50, header_y))

            name_header = self.font_small.render("플레이어", True, (200, 200, 200))
            self.screen.blit(name_header, (150, header_y))

            score_header = self.font_small.render("점수", True, (200, 200, 200))
            self.screen.blit(score_header, (350, header_y))

            # 구분선
            pygame.draw.line(self.screen, WHITE, (30, header_y + 35), (SCREEN_WIDTH - 30, header_y + 35), 2)

            # 랭킹 표시
            start_y = 230
            for i, ranking in enumerate(self.rankings):
                y_pos = start_y + i * 50

                # 순위에 따른 색상
                if ranking['rank'] == 1:
                    rank_color = (255, 215, 0)
                    rank_text = "🥇"
                elif ranking['rank'] == 2:
                    rank_color = (192, 192, 192)
                    rank_text = "🥈"
                elif ranking['rank'] == 3:
                    rank_color = (205, 127, 50)
                    rank_text = "🥉"
                else:
                    rank_color = WHITE
                    rank_text = f"{ranking['rank']}위"

                # 내 랭킹 강조
                is_my_rank = (self.api_client.is_logged_in() and
                             ranking['username'] == self.api_client.session_manager.username)
                if is_my_rank:
                    highlight = pygame.Rect(30, y_pos - 5, SCREEN_WIDTH - 60, 45)
                    pygame.draw.rect(self.screen, (50, 100, 50), highlight)
                    pygame.draw.rect(self.screen, (0, 255, 0), highlight, 2)

                # 순위
                rank_display = self.font_small.render(rank_text, True, rank_color)
                self.screen.blit(rank_display, (50, y_pos))

                # 이름
                username = ranking['username']
                if is_my_rank:
                    username += " (나)"
                name_color = (0, 255, 0) if is_my_rank else WHITE
                name_display = self.font_small.render(username, True, name_color)
                self.screen.blit(name_display, (150, y_pos))

                # 점수
                score_display = self.font_small.render(str(ranking['score']), True, rank_color)
                self.screen.blit(score_display, (350, y_pos))

            # 안내 문구
            hint_text = self.font_small.render("ESC: 뒤로가기", True, (150, 150, 150))
            self.screen.blit(hint_text, (SCREEN_WIDTH // 2 - 80, 750))


# 하위호환성을 위한 함수
def show_ranking_screen(screen, background_img, api_client: GameAPIClient):
    """
    랭킹 화면 표시 (하위호환성 래퍼 함수)

    Args:
        screen: pygame 화면
        background_img: 배경 이미지
        api_client: API 클라이언트
    """
    ranking_screen = RankingScreen(screen, background_img, api_client)
    ranking_screen.run()
