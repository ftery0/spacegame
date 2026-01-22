"""게임 플레이 및 정보 화면"""
import pygame
import random
from config import (
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


class GameState:
    """게임 상태 관리"""

    def __init__(self):
        self.score = 0
        self.health = INITIAL_HEALTH
        self.game_over = False
        self.skill_count = 0
        self.skill_available = False
        self.stones = []
        self.missiles = []
        self.stone_spawn_timer = 0
        self.stone_spawn_interval = STONE_SPAWN_INTERVAL_START

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

    def take_damage(self):
        """플레이어 피해 입음"""
        self.health -= 1
        if self.health <= 0:
            self.game_over = True

    def add_missile_hit(self):
        """미사일 히트 카운트"""
        self.skill_count += 1
        self.score += 1
        if self.skill_count >= SKILL_THRESHOLD:
            self.skill_available = True

    def use_skill(self):
        """스킬 사용"""
        if self.skill_available or self.skill_count >= SKILL_THRESHOLD:
            # 모든 돌 제거
            for stone in self.stones:
                self.score += 1
            self.stones.clear()
            self.skill_available = False
            self.skill_count = 0


def gameStart():
    """게임 플레이 화면"""
    try:
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
        game_state = GameState()
        player_rect = pygame.Rect(PLAYER_START_X, PLAYER_START_Y, PLAYER_WIDTH, PLAYER_HEIGHT)

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
                            missile_x = player_rect.x + PLAYER_WIDTH / 2 - MISSILE_WIDTH / 2
                            missile_y = player_rect.y
                            missile_rect = pygame.Rect(missile_x, missile_y, MISSILE_WIDTH, MISSILE_HEIGHT)
                            game_state.missiles.append({
                                "rect": missile_rect,
                                "image": missile_img
                            })
                            try:
                                missile_sound.play()
                            except pygame.error:
                                pass

                    elif event.key == pygame.K_f or event.unicode == "ㄹ":
                        # 스킬 사용
                        game_state.use_skill()

            # 플레이어 움직임
            if not game_state.game_over:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_UP] and player_rect.y > 0:
                    player_rect.y -= PLAYER_SPEED
                if keys[pygame.K_DOWN] and player_rect.y < SCREEN_HEIGHT - PLAYER_HEIGHT:
                    player_rect.y += PLAYER_SPEED
                if keys[pygame.K_LEFT] and player_rect.x > 0:
                    player_rect.x -= PLAYER_SPEED
                if keys[pygame.K_RIGHT] and player_rect.x < SCREEN_WIDTH - PLAYER_WIDTH:
                    player_rect.x += PLAYER_SPEED

            # 배경 그리기
            gameScr.blit(background_img, [0, 0])

            # 플레이어 그리기
            gameScr.blit(player_img, player_rect)

            # 미사일 업데이트 및 그리기
            missiles_to_remove = []
            for missile in game_state.missiles:
                missile["rect"].y -= MISSILE_SPEED
                if is_off_screen(missile["rect"], SCREEN_WIDTH, SCREEN_HEIGHT):
                    missiles_to_remove.append(missile)
                else:
                    gameScr.blit(missile["image"], (missile["rect"].x, missile["rect"].y))

            safe_remove_from_list(game_state.missiles, missiles_to_remove)

            # 돌 생성
            if not game_state.game_over:
                game_state.stone_spawn_timer += 1
                if game_state.stone_spawn_timer >= game_state.stone_spawn_interval:
                    stone_size = random.randint(STONE_MIN_SIZE, STONE_MAX_SIZE)
                    stone_x = random.randint(0, SCREEN_WIDTH - stone_size)
                    stone_y = -stone_size
                    stone_rect = pygame.Rect(stone_x, stone_y, stone_size, stone_size)
                    game_state.stones.append({
                        "rect": stone_rect,
                        "image": pygame.transform.scale(stone_img, (stone_size, stone_size))
                    })
                    game_state.stone_spawn_timer = 0
                    game_state.stone_spawn_interval = max(
                        game_state.stone_spawn_interval - 1,
                        STONE_SPAWN_INTERVAL_MIN
                    )

            # 돌 업데이트 및 충돌 처리
            stones_to_remove = []
            for stone in game_state.stones:
                stone["rect"].y += STONE_SPEED

                # 플레이어와 충돌
                if stone["rect"].colliderect(player_rect):
                    game_state.take_damage()
                    stones_to_remove.append(stone)
                    gameScr.blit(collision_img, (stone["rect"].x, stone["rect"].y))

                # 미사일과 충돌
                for missile in game_state.missiles[:]:
                    if stone["rect"].colliderect(missile["rect"]):
                        game_state.add_missile_hit()
                        stones_to_remove.append(stone)
                        if missile in game_state.missiles:
                            game_state.missiles.remove(missile)
                        gameScr.blit(collision_img, (stone["rect"].x, stone["rect"].y))
                        break

                # 화면 밖
                if is_off_screen(stone["rect"], SCREEN_WIDTH, SCREEN_HEIGHT):
                    stones_to_remove.append(stone)
                else:
                    gameScr.blit(stone["image"], (stone["rect"].x, stone["rect"].y))

            safe_remove_from_list(game_state.stones, stones_to_remove)

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

            # UI 그리기 - BACK 버튼
            mouse_pos = pygame.mouse.get_pos()
            back_text = font.render("BACK", True, RED if back_button.collidepoint(mouse_pos) else WHITE)
            gameScr.blit(back_text, [back_button.x, back_button.y])

            # 게임 오버 화면
            if game_state.game_over:
                game_over_text = font.render("GAME OVER", True, RED)
                gameScr.blit(game_over_text, [150, 350])
                final_score_text = font.render(f"Score: {game_state.score}", True, RED)
                gameScr.blit(final_score_text, [170, 400])

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

