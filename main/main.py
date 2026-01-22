"""우주선 게임 - 메인 시작 화면"""
import logging
import pygame
import sys
from core.config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, RED, Resources, UI
from core.logging_config import setup_logging
from utils import load_image, load_music, load_font, create_button_rect, show_error_dialog
from services.api_service import GameAPIClient
from screens.auth_screen import show_auth_screen
from screens.ranking_screen import show_ranking_screen
from screens.profile_screen import show_profile_screen
from screens.difficulty_screen import show_difficulty_screen
from screens import game_screen as gameview
from game.difficulty import DifficultyManager

# 로깅 설정
setup_logging(log_level="INFO")
logger = logging.getLogger(__name__)


def startView():
    """게임 시작 화면 표시"""
    try:
        # Pygame 초기화
        pygame.init()

        # 리소스 유효성 검사
        try:
            Resources.validate()
        except FileNotFoundError as e:
            show_error_dialog("리소스 파일 오류", str(e))
            return

        # API 클라이언트 초기화
        api_client = GameAPIClient()

        # 난이도 관리자 초기화
        difficulty_manager = DifficultyManager()

        # 서버에서 난이도 설정 가져오기
        try:
            success, difficulties, error = api_client.get_difficulties()
            if success and difficulties:
                difficulty_manager.update_from_api(difficulties)
                logger.info(f"난이도 설정 {len(difficulties)}개 로드 완료")
            else:
                logger.warning(f"난이도 설정 로드 실패, 기본값 사용: {error}")
        except Exception as e:
            logger.error(f"난이도 설정 로드 중 오류: {str(e)}")

        # 화면 설정
        startScr = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
        pygame.display.set_caption('원석 부수기')

        # 버튼 생성
        startBtnObj = create_button_rect(UI.START_BUTTON)
        rankingBtn = create_button_rect(UI.RANKING_BUTTON)
        profileBtn = create_button_rect(UI.PROFILE_BUTTON)
        startinfom = create_button_rect(UI.INFO_BUTTON)
        stopbt = create_button_rect(UI.QUIT_BUTTON)

        # 리소스 로드
        try:
            backGImg = load_image(Resources.BACKGROUND, (SCREEN_WIDTH, SCREEN_HEIGHT))
            load_music(Resources.BACKGROUND_MUSIC)
            pygame.mixer.music.play(-1)
            font = load_font(Resources.MAIN_FONT, UI.FONT_SIZE_LARGE)
        except (FileNotFoundError, pygame.error) as e:
            show_error_dialog("리소스 로드 오류", str(e))
            return

        # 메인 루프
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if startBtnObj.collidepoint(event.pos):
                        # 로그인 확인
                        if not api_client.is_logged_in():
                            # 로그인/회원가입 화면 표시
                            pygame.mixer.music.stop()
                            logged_in = show_auth_screen(startScr, backGImg, api_client)
                            if logged_in:
                                # 로그인 성공 후 난이도 선택 -> 게임 시작
                                show_difficulty_screen(startScr, backGImg, difficulty_manager)
                                gameview.gameStart(api_client, difficulty_manager)
                            # 음악 재시작
                            try:
                                load_music(Resources.BACKGROUND_MUSIC)
                                pygame.mixer.music.play(-1)
                            except pygame.error:
                                pass
                        else:
                            # 이미 로그인된 경우 난이도 선택 -> 게임 시작
                            pygame.mixer.music.stop()
                            show_difficulty_screen(startScr, backGImg, difficulty_manager)
                            gameview.gameStart(api_client, difficulty_manager)
                            try:
                                load_music(Resources.BACKGROUND_MUSIC)
                                pygame.mixer.music.play(-1)
                            except pygame.error:
                                pass

                    elif rankingBtn.collidepoint(event.pos):
                        # 랭킹 화면
                        pygame.mixer.music.stop()
                        show_ranking_screen(startScr, backGImg, api_client)
                        try:
                            load_music(Resources.BACKGROUND_MUSIC)
                            pygame.mixer.music.play(-1)
                        except pygame.error:
                            pass

                    elif profileBtn.collidepoint(event.pos):
                        # 프로필 화면
                        pygame.mixer.music.stop()
                        show_profile_screen(startScr, backGImg, api_client)
                        try:
                            load_music(Resources.BACKGROUND_MUSIC)
                            pygame.mixer.music.play(-1)
                        except pygame.error:
                            pass

                    elif startinfom.collidepoint(event.pos):
                        pygame.mixer.music.stop()
                        gameview.gameinform()
                        # 정보 화면에서 돌아왔을 때 음악 재시작
                        try:
                            load_music(Resources.BACKGROUND_MUSIC)
                            pygame.mixer.music.play(-1)
                        except pygame.error:
                            pass

                    elif stopbt.collidepoint(event.pos):
                        running = False

            # 배경 그리기
            startScr.blit(backGImg, [0, 0])

            # 마우스 위치
            mouse_pos = pygame.mouse.get_pos()

            # 게임 시작 버튼
            startText = font.render("게임 시작하기", True, RED if startBtnObj.collidepoint(mouse_pos) else WHITE)
            startScr.blit(startText, [startBtnObj.x, startBtnObj.y])

            # 랭킹 버튼
            font_small = load_font(Resources.MAIN_FONT, 28)
            rankingText = font_small.render("🏆 랭킹", True, RED if rankingBtn.collidepoint(mouse_pos) else WHITE)
            rankingTextRect = rankingText.get_rect(center=(rankingBtn.x + rankingBtn.width // 2, rankingBtn.y + rankingBtn.height // 2))
            startScr.blit(rankingText, rankingTextRect)

            # 프로필 버튼
            profileText = font_small.render("👤 프로필", True, RED if profileBtn.collidepoint(mouse_pos) else WHITE)
            profileTextRect = profileText.get_rect(center=(profileBtn.x + profileBtn.width // 2, profileBtn.y + profileBtn.height // 2))
            startScr.blit(profileText, profileTextRect)

            # 정보 버튼
            startinfomtext = font.render("정보", True, RED if startinfom.collidepoint(mouse_pos) else WHITE)
            startinfomtextRect = startinfomtext.get_rect(center=(startinfom.x + startinfom.width // 2, startinfom.y + startinfom.height // 2))
            startScr.blit(startinfomtext, startinfomtextRect)

            # 나가기 버튼
            stopbttext = font.render("나가기", True, RED if stopbt.collidepoint(mouse_pos) else WHITE)
            stopbttextRect = stopbttext.get_rect(center=(stopbt.x + stopbt.width // 2, stopbt.y + stopbt.height // 2))
            startScr.blit(stopbttext, stopbttextRect)

            pygame.display.flip()

    except Exception as e:
        show_error_dialog("예기치 않은 오류", f"게임 실행 중 오류 발생:\n{str(e)}")

    finally:
        # 안전하게 종료
        pygame.mixer.music.stop()
        pygame.quit()


if __name__ == "__main__":
    startView()
