"""업적 화면"""
import pygame
from core.config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, RED, Resources, UI
from utils import load_image, load_font, create_button_rect, show_error_dialog
from game.achievements import AchievementChecker


def show_achievement_screen(api_client):
    """
    업적 화면 표시

    Args:
        api_client: API 클라이언트
    """
    try:
        gameScr = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
        pygame.display.set_caption('원석 부수기 - 업적')

        back_button = create_button_rect(UI.INFO_BACK_BUTTON)

        try:
            background_img = load_image(Resources.BACKGROUND, (SCREEN_WIDTH, SCREEN_HEIGHT))
            title_font = load_font(Resources.MAIN_FONT, 48)
            font = load_font(Resources.MAIN_FONT, 24)
            small_font = load_font(Resources.MAIN_FONT, 18)
        except (FileNotFoundError, pygame.error) as e:
            show_error_dialog("업적 화면 로드 오류", str(e))
            return

        # 업적 목록 가져오기
        checker = AchievementChecker(api_client)

        # 모든 업적 코드
        all_achievements = [
            'first_game',
            'perfect_aim',
            'immortal',
            'speedrunner',
            'combo_master',
            'stone_breaker_single',
            'enemy_hunter_single',
            'boss_slayer',
            'stage_master',
            'expert_player',
            'item_collector',
        ]

        # 서버에서 잠금 해제된 업적 가져오기
        unlocked_achievements = set()
        if api_client and api_client.is_logged_in():
            try:
                success, achievements, error = api_client.get_my_achievements()
                if success and achievements:
                    # 서버 응답에서 업적 코드 추출
                    unlocked_achievements = {ach.get('achievement', {}).get('code')
                                            for ach in achievements
                                            if ach.get('completed')}
            except Exception as e:
                print(f"업적 로드 실패: {e}")

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
                        scroll_offset = max(scroll_offset - 20, -400)

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
            title_text = title_font.render("업적", True, WHITE)
            title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 80))
            gameScr.blit(title_text, title_rect)

            # 진행도 표시
            total_achievements = len(all_achievements)
            unlocked_count = len(unlocked_achievements)
            progress_text = small_font.render(
                f"달성: {unlocked_count} / {total_achievements} ({unlocked_count * 100 // total_achievements}%)",
                True,
                (255, 215, 0)
            )
            progress_rect = progress_text.get_rect(center=(SCREEN_WIDTH // 2, 130))
            gameScr.blit(progress_text, progress_rect)

            y_pos = 170 + scroll_offset

            # 업적 목록
            for achievement_code in all_achievements:
                if y_pos > 100 and y_pos < SCREEN_HEIGHT - 50:  # 화면 범위 내에만 표시
                    is_unlocked = achievement_code in unlocked_achievements

                    # 업적 이름
                    name = checker.get_achievement_display_name(achievement_code)
                    description = checker.get_achievement_description(achievement_code)

                    # 색상 (잠금 해제 여부)
                    name_color = (255, 215, 0) if is_unlocked else (150, 150, 150)
                    desc_color = WHITE if is_unlocked else (100, 100, 100)

                    # 아이콘 (간단한 원)
                    icon_x = SCREEN_WIDTH // 2 - 250
                    icon_y = y_pos + 15
                    icon_color = (255, 215, 0) if is_unlocked else (80, 80, 80)
                    pygame.draw.circle(gameScr, icon_color, (icon_x, icon_y), 20)

                    # 체크 표시 또는 자물쇠
                    icon_font = load_font(Resources.MAIN_FONT, 24)
                    icon_symbol = "✓" if is_unlocked else "🔒"
                    icon_text = icon_font.render(icon_symbol, True, (0, 0, 0) if is_unlocked else WHITE)
                    icon_text_rect = icon_text.get_rect(center=(icon_x, icon_y))
                    gameScr.blit(icon_text, icon_text_rect)

                    # 업적 이름
                    name_text = font.render(name, True, name_color)
                    gameScr.blit(name_text, (icon_x + 40, y_pos))

                    # 업적 설명
                    desc_text = small_font.render(description, True, desc_color)
                    gameScr.blit(desc_text, (icon_x + 40, y_pos + 30))

                    # 구분선
                    pygame.draw.line(gameScr, (60, 60, 60),
                                   (icon_x - 30, y_pos + 65),
                                   (SCREEN_WIDTH // 2 + 250, y_pos + 65), 1)

                    y_pos += 75
                else:
                    y_pos += 75

            # 스크롤 힌트
            if y_pos > SCREEN_HEIGHT:
                hint_text = small_font.render("마우스 휠로 스크롤", True, (150, 150, 150))
                hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
                gameScr.blit(hint_text, hint_rect)

            pygame.display.update()

    except Exception as e:
        show_error_dialog("업적 화면 오류", f"업적 화면 실행 중 오류 발생:\n{str(e)}")
