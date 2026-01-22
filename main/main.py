"""우주선 게임 - 메인 시작 화면"""
import pygame
import sys
from config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, RED, Resources, UI
from utils import load_image, load_music, load_font, create_button_rect, show_error_dialog
import gameview


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

        # 화면 설정
        startScr = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
        pygame.display.set_caption('원석 부수기')

        # 버튼 생성
        startBtnObj = create_button_rect(UI.START_BUTTON)
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
                        pygame.mixer.music.stop()
                        gameview.gameStart()
                        # 게임에서 돌아왔을 때 음악 재시작
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

            # 정보 버튼
            startinfomtext = font.render("정보", True, RED if startinfom.collidepoint(mouse_pos) else WHITE)
            startScr.blit(startinfomtext, [startinfom.x, startinfom.y])

            # 나가기 버튼
            stopbttext = font.render("나가기", True, RED if stopbt.collidepoint(mouse_pos) else WHITE)
            startScr.blit(stopbttext, [stopbt.x, stopbt.y])

            pygame.display.flip()

    except Exception as e:
        show_error_dialog("예기치 않은 오류", f"게임 실행 중 오류 발생:\n{str(e)}")

    finally:
        # 안전하게 종료
        pygame.mixer.music.stop()
        pygame.quit()


if __name__ == "__main__":
    startView()
