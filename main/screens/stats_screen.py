"""통계 화면"""
import pygame
from core.config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, RED, Resources, UI
from utils import load_image, load_font, create_button_rect, show_error_dialog


def show_stats_screen(api_client):
    """
    통계 화면 표시

    Args:
        api_client: API 클라이언트
    """
    try:
        gameScr = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
        pygame.display.set_caption('원석 부수기 - 통계')

        back_button = create_button_rect(UI.INFO_BACK_BUTTON)

        try:
            background_img = load_image(Resources.BACKGROUND, (SCREEN_WIDTH, SCREEN_HEIGHT))
            title_font = load_font(Resources.MAIN_FONT, 48)
            font = load_font(Resources.MAIN_FONT, 28)
            small_font = load_font(Resources.MAIN_FONT, 22)
        except (FileNotFoundError, pygame.error) as e:
            show_error_dialog("통계 화면 로드 오류", str(e))
            return

        # 통계 데이터 가져오기
        stats_data = None
        error_message = None

        if api_client and api_client.is_logged_in():
            try:
                # 서버에서 통계 데이터 가져오기
                success, data, error = api_client.get_my_stats_summary()
                if success and data:
                    stats_data = data
                else:
                    error_message = error or "통계 로드 실패"
            except Exception as e:
                error_message = f"통계 로드 실패: {str(e)}"
        else:
            error_message = "로그인이 필요합니다"

        running = True
        scroll_offset = 0

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if back_button.collidepoint(event.pos):
                        running = False

                    # 마우스 휠 스크롤
                    if event.button == 4:  # 위로 스크롤
                        scroll_offset = min(scroll_offset + 20, 0)
                    elif event.button == 5:  # 아래로 스크롤
                        scroll_offset = max(scroll_offset - 20, -200)

            # 배경 그리기
            gameScr.blit(background_img, [0, 0])

            # 반투명 오버레이
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            gameScr.blit(overlay, (0, 0))

            # BACK 버튼
            mouse_pos = pygame.mouse.get_pos()
            back_text = font.render("BACK", True, RED if back_button.collidepoint(mouse_pos) else WHITE)
            gameScr.blit(back_text, [back_button.x, back_button.y])

            # 제목
            title_text = title_font.render("게임 통계", True, WHITE)
            title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 80))
            gameScr.blit(title_text, title_rect)

            y_pos = 150 + scroll_offset

            if error_message:
                # 에러 메시지
                error_text = font.render(error_message, True, (255, 200, 0))
                error_rect = error_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                gameScr.blit(error_text, error_rect)
            elif stats_data:
                # 통계 표시
                stats_items = [
                    ("총 플레이 횟수", f"{stats_data.get('total_games', 0)}회", WHITE),
                    ("최고 점수", f"{stats_data.get('highest_score', 0):,}점", (255, 215, 0)),
                    ("", "", None),  # 구분선
                    ("파괴한 운석", f"{stats_data.get('total_stones_destroyed', 0):,}개", (100, 200, 255)),
                    ("처치한 적", f"{stats_data.get('total_enemies_destroyed', 0):,}명", (255, 100, 100)),
                    ("평균 명중률", f"{stats_data.get('average_accuracy', 0):.1f}%", (0, 255, 100)),
                    ("", "", None),  # 구분선
                    ("최대 콤보", f"{stats_data.get('best_combo', 0)}", (255, 165, 0)),
                    ("최고 스테이지", f"{stats_data.get('max_stage_ever', 1)}", (200, 100, 255)),
                    ("총 스킬 사용", f"{stats_data.get('total_skills_used', 0)}회", (255, 255, 100)),
                    ("총 아이템 수집", f"{stats_data.get('total_items_collected', 0)}개", (200, 255, 200)),
                    ("총 플레이 시간", f"{stats_data.get('total_play_time', 0) // 60}분", WHITE),
                ]

                for label, value, color in stats_items:
                    if y_pos > 100 and y_pos < SCREEN_HEIGHT - 50:  # 화면 범위 내에만 표시
                        if not label:  # 구분선
                            pygame.draw.line(gameScr, (100, 100, 100),
                                           (SCREEN_WIDTH // 2 - 200, y_pos + 10),
                                           (SCREEN_WIDTH // 2 + 200, y_pos + 10), 2)
                            y_pos += 30
                        else:
                            label_text = font.render(label, True, (200, 200, 200))
                            value_text = font.render(value, True, color)

                            label_rect = label_text.get_rect(midright=(SCREEN_WIDTH // 2 - 20, y_pos))
                            value_rect = value_text.get_rect(midleft=(SCREEN_WIDTH // 2 + 20, y_pos))

                            gameScr.blit(label_text, label_rect)
                            gameScr.blit(value_text, value_rect)
                            y_pos += 45
                    else:
                        y_pos += 45 if label else 30

            # 스크롤 힌트
            if stats_data and y_pos > SCREEN_HEIGHT:
                hint_text = small_font.render("마우스 휠로 스크롤", True, (150, 150, 150))
                hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
                gameScr.blit(hint_text, hint_rect)

            pygame.display.update()

    except Exception as e:
        show_error_dialog("통계 화면 오류", f"통계 화면 실행 중 오류 발생:\n{str(e)}")
