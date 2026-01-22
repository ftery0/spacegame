"""게임 플레이 및 정보 화면"""
import pygame
import random
from core.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, RED,
    PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_SPEED, PLAYER_START_X, PLAYER_START_Y,
    STONE_MIN_SIZE, STONE_MAX_SIZE, STONE_SPEED, STONE_SPAWN_INTERVAL_START, STONE_SPAWN_INTERVAL_MIN,
    MISSILE_WIDTH, MISSILE_HEIGHT, MISSILE_SPEED,
    INITIAL_HEALTH, SKILL_THRESHOLD, FPS, Resources, UI
)
from utils import (
    load_image, load_sound, load_music, load_font, create_button_rect,
    is_off_screen, safe_remove_from_list, show_error_dialog, render_text_centered
)
from services.api_service import GameAPIClient
from game.entities import Player, Stone, Missile
from game.collision import CollisionDetector
from game.combo import ComboSystem
from game.difficulty import DifficultyManager


def show_game_over_screen(screen, font, score, background_img, api_client, max_combo=0):
    """
    게임 오버 화면 및 점수 저장

    Args:
        screen: pygame 화면
        font: 폰트 객체
        score: 최종 점수
        background_img: 배경 이미지
        api_client: API 클라이언트
        max_combo: 최대 콤보 수

    Returns:
        bool: True면 재시작, False면 메뉴로
    """
    score_saved = False
    save_message = ""

    # 로그인되어 있으면 자동으로 점수 저장 시도
    if api_client.is_logged_in():
        result = api_client.save_score(score)
        if result:
            save_message = f"점수가 저장되었습니다! (#{score})"
            score_saved = True

            # 통계 조회
            stats = api_client.get_my_stats()
            if stats:
                save_message += f" | 랭킹: {stats['rank']}위"
        else:
            save_message = "점수 저장 실패 (서버 오류)"
    else:
        save_message = "오프라인 모드 (점수 저장 안됨)"

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                # 아무 키나 누르면 메뉴로
                return False

            if event.type == pygame.MOUSEBUTTONDOWN:
                # 아무 곳이나 클릭해도 메뉴로
                return False

        # 화면 그리기
        screen.blit(background_img, [0, 0])

        # 반투명 오버레이
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # 게임 오버 텍스트
        game_over_text = font.render("GAME OVER", True, RED)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        screen.blit(game_over_text, game_over_rect)

        # 점수 표시
        score_text = font.render(f"Score: {score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 280))
        screen.blit(score_text, score_rect)

        # 최대 콤보 표시
        if max_combo > 1:
            combo_font = load_font(Resources.MAIN_FONT, 28)
            combo_display = combo_font.render(f"Max Combo: {max_combo}", True, (255, 215, 0))
            combo_rect = combo_display.get_rect(center=(SCREEN_WIDTH // 2, 320))
            screen.blit(combo_display, combo_rect)

        # 사용자 이름 표시 (로그인된 경우)
        user_y = 360 if max_combo > 1 else 340
        if api_client.is_logged_in():
            user_text = font.render(f"플레이어: {api_client.session_manager.username}", True, WHITE)
            user_rect = user_text.get_rect(center=(SCREEN_WIDTH // 2, user_y))
            screen.blit(user_text, user_rect)

        # 저장 메시지
        message_y = 420 if max_combo > 1 else 400
        message_color = (0, 255, 0) if score_saved else (255, 200, 0)
        small_font = load_font(Resources.MAIN_FONT, 22)
        save_text = small_font.render(save_message, True, message_color)
        save_rect = save_text.get_rect(center=(SCREEN_WIDTH // 2, message_y))
        screen.blit(save_text, save_rect)

        # 종료 안내
        hint_y = 500 if max_combo > 1 else 480
        hint_font = load_font(Resources.MAIN_FONT, 20)
        hint_text = hint_font.render("아무 키나 눌러 메뉴로...", True, (150, 150, 150))
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, hint_y))
        screen.blit(hint_text, hint_rect)

        pygame.display.flip()
        clock.tick(30)


class GameState:
    """게임 상태 관리"""

    def __init__(self, difficulty_manager=None):
        self.score = 0
        self.health = INITIAL_HEALTH
        self.game_over = False
        self.skill_count = 0
        self.skill_available = False
        self.stones = []
        self.missiles = []
        self.stone_spawn_timer = 0
        self.stone_spawn_interval = STONE_SPAWN_INTERVAL_START
        self.current_frame = 0
        self.combo_system = ComboSystem(timeout_frames=180)
        self.difficulty_manager = difficulty_manager

    def reset(self):
        """게임 상태 초기화"""
        self.score = 0
        self.health = INITIAL_HEALTH
        self.game_over = False
        self.skill_count = 0
        self.skill_available = False
        self.stones.clear()
        self.missiles.clear()
        self.stone_spawn_timer = 0
        self.stone_spawn_interval = STONE_SPAWN_INTERVAL_START
        self.current_frame = 0
        self.combo_system.reset()

    def take_damage(self):
        """플레이어 피해 입음"""
        self.health -= 1
        if self.health <= 0:
            self.game_over = True

    def add_missile_hit(self):
        """미사일 히트 카운트"""
        self.skill_count += 1

        # 콤보 추가
        self.combo_system.add_hit(self.current_frame)

        # 콤보 배율 적용하여 점수 추가
        base_score = 1
        multiplier = self.combo_system.get_multiplier()
        self.score += int(base_score * multiplier)

        if self.skill_count >= SKILL_THRESHOLD:
            self.skill_available = True

    def use_skill(self):
        """스킬 사용"""
        if self.skill_available or self.skill_count >= SKILL_THRESHOLD:
            # 모든 돌 제거 (콤보 유지하면서)
            num_stones = len(self.stones)
            for stone in self.stones:
                self.combo_system.add_hit(self.current_frame)
                multiplier = self.combo_system.get_multiplier()
                self.score += int(1 * multiplier)

            self.stones.clear()
            self.skill_available = False
            self.skill_count = 0


def gameStart(api_client=None, difficulty_manager=None):
    """
    게임 플레이 화면

    Args:
        api_client: API 클라이언트 (선택사항, 없으면 오프라인 모드)
        difficulty_manager: 난이도 관리자 (선택사항)
    """
    try:
        # API 클라이언트가 없으면 생성 (오프라인 모드)
        if api_client is None:
            api_client = GameAPIClient()

        # 게임 초기화
        gameScr = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
        pygame.display.set_caption('원석 부수기')
        fps = pygame.time.Clock()

        # 버튼 생성
        back_button = create_button_rect(UI.BACK_BUTTON)

        # 리소스 로드
        try:
            background_img = load_image(Resources.BACKGROUND, (SCREEN_WIDTH, SCREEN_HEIGHT))
            player_img = load_image(Resources.PLAYER, (PLAYER_WIDTH, PLAYER_HEIGHT))
            stone_img = load_image(Resources.STONE, (STONE_MAX_SIZE, STONE_MAX_SIZE))
            missile_img = load_image(Resources.MISSILE, (MISSILE_WIDTH, MISSILE_HEIGHT))
            collision_img = load_image(Resources.COLLISION, (STONE_MAX_SIZE, STONE_MAX_SIZE))
            heart_full_img = load_image(Resources.HEART_FULL, (UI.HEART_SIZE, UI.HEART_SIZE))
            heart_empty_img = load_image(Resources.HEART_EMPTY, (UI.HEART_SIZE, UI.HEART_SIZE))
            skill_icon = load_image(Resources.SKILL_ICON, (UI.SKILL_ICON_SIZE, UI.SKILL_ICON_SIZE))

            missile_sound = load_sound(Resources.MISSILE_SOUND)
            load_music(Resources.BACKGROUND_MUSIC)
            pygame.mixer.music.play(-1)

            font = load_font(Resources.MAIN_FONT, UI.FONT_SIZE_MEDIUM)
        except (FileNotFoundError, pygame.error) as e:
            show_error_dialog("게임 리소스 로드 오류", str(e))
            return

        # 게임 상태 초기화
        game_state = GameState(difficulty_manager)
        player = Player(player_img)

        # 메인 게임 루프
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if back_button.collidepoint(event.pos):
                        running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # 미사일 발사
                        if not game_state.game_over:
                            missile_x = player.rect.x + PLAYER_WIDTH / 2 - MISSILE_WIDTH / 2
                            missile_y = player.rect.y
                            missile = Missile(missile_img, missile_x, missile_y)
                            game_state.missiles.append(missile)
                            try:
                                missile_sound.play()
                            except pygame.error:
                                pass

                    elif event.key == pygame.K_f or event.unicode == "ㄹ":
                        # 스킬 사용
                        game_state.use_skill()

            # 프레임 카운터 및 콤보 시스템 업데이트
            if not game_state.game_over:
                game_state.current_frame += 1
                game_state.combo_system.update(game_state.current_frame)

            # 플레이어 움직임
            if not game_state.game_over:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_UP]:
                    player.move_up()
                if keys[pygame.K_DOWN]:
                    player.move_down()
                if keys[pygame.K_LEFT]:
                    player.move_left()
                if keys[pygame.K_RIGHT]:
                    player.move_right()

            # 배경 그리기
            gameScr.blit(background_img, [0, 0])

            # 플레이어 그리기
            player.draw(gameScr)

            # 미사일 업데이트 및 그리기
            for missile in game_state.missiles:
                missile.update()
                missile.draw(gameScr)

            # 돌 생성
            if not game_state.game_over:
                game_state.stone_spawn_timer += 1
                if game_state.stone_spawn_timer >= game_state.stone_spawn_interval:
                    stone = Stone(stone_img)
                    game_state.stones.append(stone)
                    game_state.stone_spawn_timer = 0
                    game_state.stone_spawn_interval = max(
                        game_state.stone_spawn_interval - 1,
                        STONE_SPAWN_INTERVAL_MIN
                    )

            # 돌 업데이트 및 충돌 처리
            for stone in game_state.stones:
                stone.update()
                stone.draw(gameScr)

            # 충돌 감지
            collisions = CollisionDetector.check_all_collisions(player, game_state.missiles, game_state.stones)

            # 플레이어-운석 충돌 처리
            unique_player_stones = sorted(set(collisions['player_stone']), reverse=True)
            for stone_idx in unique_player_stones:
                game_state.take_damage()
                gameScr.blit(collision_img, (game_state.stones[stone_idx].rect.x, game_state.stones[stone_idx].rect.y))
                del game_state.stones[stone_idx]

            # 미사일-운석 충돌 처리
            # 중복 제거를 위해 각 인덱스를 개별적으로 수집
            stones_to_remove = set()
            missiles_to_remove = set()
            for missile_idx, stone_idx in collisions['missile_stone']:
                if stone_idx not in stones_to_remove:
                    game_state.add_missile_hit()
                    gameScr.blit(collision_img, (game_state.stones[stone_idx].rect.x, game_state.stones[stone_idx].rect.y))
                stones_to_remove.add(stone_idx)
                missiles_to_remove.add(missile_idx)

            # 큰 인덱스부터 삭제
            for stone_idx in sorted(stones_to_remove, reverse=True):
                del game_state.stones[stone_idx]
            for missile_idx in sorted(missiles_to_remove, reverse=True):
                del game_state.missiles[missile_idx]

            # 범위 벗어난 객체 제거
            for missile_idx in sorted(collisions['missile_out'], reverse=True):
                del game_state.missiles[missile_idx]

            for stone_idx in sorted(collisions['stone_out'], reverse=True):
                del game_state.stones[stone_idx]

            # UI 그리기 - 체력
            if not game_state.game_over:
                for i in range(game_state.health):
                    gameScr.blit(heart_full_img, [UI.HEART_START_X + i * UI.HEART_SPACING, UI.HEART_START_Y])
                for i in range(game_state.health, INITIAL_HEALTH):
                    gameScr.blit(heart_empty_img, [UI.HEART_START_X + i * UI.HEART_SPACING, UI.HEART_START_Y])

            # UI 그리기 - 점수
            score_text = font.render(f"Score: {game_state.score}", True, WHITE)
            score_rect = score_text.get_rect(center=(70, 60))
            gameScr.blit(score_text, score_rect)

            # UI 그리기 - 스킬
            if game_state.skill_available:
                gameScr.blit(skill_icon, [UI.SKILL_ICON_X, UI.SKILL_ICON_Y])
                skill_text = font.render("스킬: F 키 사용 가능", True, WHITE)
                gameScr.blit(skill_text, [10, 650])
            else:
                skill_text = font.render(
                    f"스킬: {game_state.skill_count} / {SKILL_THRESHOLD}",
                    True,
                    WHITE
                )
                gameScr.blit(skill_text, [10, 650])

            # UI 그리기 - 콤보 시스템
            combo_text = game_state.combo_system.get_display_text()
            if combo_text:
                # 콤보 텍스트 (화면 중앙 상단)
                combo_font = load_font(Resources.MAIN_FONT, 48)
                combo_surface = combo_font.render(combo_text, True, (255, 215, 0))  # 골드 색상
                combo_rect = combo_surface.get_rect(center=(SCREEN_WIDTH // 2, 100))
                gameScr.blit(combo_surface, combo_rect)

                # 배율 텍스트
                multiplier_text = game_state.combo_system.get_multiplier_text()
                mult_font = load_font(Resources.MAIN_FONT, 32)
                mult_surface = mult_font.render(multiplier_text, True, (255, 165, 0))  # 오렌지 색상
                mult_rect = mult_surface.get_rect(center=(SCREEN_WIDTH // 2, 145))
                gameScr.blit(mult_surface, mult_rect)

                # 타이머 바 (콤보 아래)
                timer_percent = game_state.combo_system.get_timer_percent()
                bar_width = 200
                bar_height = 8
                bar_x = SCREEN_WIDTH // 2 - bar_width // 2
                bar_y = 170

                # 배경 바
                pygame.draw.rect(gameScr, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))

                # 진행 바 (시간이 줄어들면 색상도 변경)
                if timer_percent > 0.5:
                    bar_color = (0, 255, 0)  # 초록
                elif timer_percent > 0.25:
                    bar_color = (255, 255, 0)  # 노랑
                else:
                    bar_color = (255, 0, 0)  # 빨강

                current_bar_width = int(bar_width * timer_percent)
                pygame.draw.rect(gameScr, bar_color, (bar_x, bar_y, current_bar_width, bar_height))

            # UI 그리기 - BACK 버튼
            mouse_pos = pygame.mouse.get_pos()
            back_text = font.render("BACK", True, RED if back_button.collidepoint(mouse_pos) else WHITE)
            gameScr.blit(back_text, [back_button.x, back_button.y])

            # 게임 오버 처리
            if game_state.game_over:
                # 게임 오버 화면 표시 및 점수 저장
                pygame.display.flip()
                pygame.time.wait(1000)  # 1초 대기
                max_combo = game_state.combo_system.get_max_combo()
                show_game_over_screen(gameScr, font, game_state.score, background_img, api_client, max_combo)
                running = False  # 메인 메뉴로 돌아가기

            pygame.display.flip()
            fps.tick(FPS)

    except Exception as e:
        show_error_dialog("게임 실행 오류", f"게임 플레이 중 오류 발생:\n{str(e)}")

    finally:
        pygame.mixer.music.stop()


def gameinform():
    """게임 정보 화면"""
    try:
        gameScr = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
        pygame.display.set_caption('원석 부수기 - 게임 정보')

        back_button = create_button_rect(UI.INFO_BACK_BUTTON)

        try:
            background_img = load_image(Resources.BACKGROUND, (SCREEN_WIDTH, SCREEN_HEIGHT))
            font = load_font(Resources.MAIN_FONT, UI.FONT_SIZE_MEDIUM)
        except (FileNotFoundError, pygame.error) as e:
            show_error_dialog("정보 화면 로드 오류", str(e))
            return

        info_texts = [
            "화살표 키로 움직이기",
            "(위, 아래, 좌, 우)",
            "",
            "스페이스바로 미사일 발사!",
            "",
            "돌을 맞춰서 경험치 모으기",
            "",
            "F 키로 스킬 사용",
            "(경험치 10개마다 사용 가능)",
            "",
            "돌은 점점 빨라진다!",
            "체력은 3개만 가능",
            "잘 버텨서 점수를 높여보자!"
        ]

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if back_button.collidepoint(event.pos):
                        running = False

            # 배경 그리기
            gameScr.blit(background_img, [0, 0])

            # BACK 버튼
            mouse_pos = pygame.mouse.get_pos()
            back_text = font.render("BACK", True, RED if back_button.collidepoint(mouse_pos) else WHITE)
            gameScr.blit(back_text, [back_button.x, back_button.y])

            # 정보 텍스트
            y_pos = 200
            for text in info_texts:
                if text:
                    info_text = font.render(text, True, WHITE)
                    gameScr.blit(info_text, [20, y_pos])
                y_pos += 40

            pygame.display.update()

    except Exception as e:
        show_error_dialog("정보 화면 오류", f"정보 화면 실행 중 오류 발생:\n{str(e)}")

