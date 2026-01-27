"""게임 플레이 및 정보 화면"""
import pygame
import random
import logging
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
from game.enemy import Enemy, EnemyProjectile, EnemyState
from game.powerup import PowerUp, PowerUpType, PowerUpManager
from game.stage import StageManager
from game.statistics import GameStatistics
from game.achievements import AchievementChecker
from game.achievement_notification import AchievementNotificationManager

logger = logging.getLogger(__name__)


def show_game_over_screen(screen, font, score, background_img, api_client, max_combo=0,
                          statistics=None, achievements_unlocked=None):
    """
    게임 오버 화면 및 점수 저장

    Args:
        screen: pygame 화면
        font: 폰트 객체
        score: 최종 점수
        background_img: 배경 이미지
        api_client: API 클라이언트
        max_combo: 최대 콤보 수
        statistics: 게임 통계 (GameStatistics 객체)
        achievements_unlocked: 이번 게임에서 달성한 업적 리스트

    Returns:
        bool: True면 재시작, False면 메뉴로
    """
    score_saved = False
    stats_saved = False
    save_message = ""

    # 로그인되어 있으면 자동으로 점수 및 통계 저장 시도
    if api_client.is_logged_in():
        result = api_client.save_score(score)
        if result:
            save_message = f"점수가 저장되었습니다! (#{score})"
            score_saved = True

            # 통계 조회
            user_stats = api_client.get_my_stats()
            if user_stats:
                save_message += f" | 랭킹: {user_stats['rank']}위"
        else:
            save_message = "점수 저장 실패 (서버 오류)"

        # 상세 통계 저장
        if statistics:
            try:
                stats_data = statistics.to_dict()
                stats_data['final_score'] = score
                success, data, error = api_client.save_game_stat(stats_data)
                if success:
                    stats_saved = True
                    logger.info("게임 통계 저장 성공")
                else:
                    logger.warning(f"게임 통계 저장 실패: {error}")
            except Exception as e:
                logger.error(f"통계 저장 실패: {e}")
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

        # 통계 표시
        y_offset = 320
        stats_font = load_font(Resources.MAIN_FONT, 24)

        if statistics:
            # 최대 콤보
            combo_display = stats_font.render(f"Max Combo: {max_combo}", True, (255, 215, 0))
            combo_rect = combo_display.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            screen.blit(combo_display, combo_rect)
            y_offset += 35

            # 스테이지
            stage_text = stats_font.render(f"Stage: {statistics.max_stage}", True, (100, 200, 255))
            stage_rect = stage_text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            screen.blit(stage_text, stage_rect)
            y_offset += 35

            # 명중률
            accuracy_color = (0, 255, 0) if statistics.get_accuracy() >= 70 else (255, 255, 100)
            accuracy_text = stats_font.render(f"Accuracy: {statistics.get_accuracy():.1f}%", True, accuracy_color)
            accuracy_rect = accuracy_text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            screen.blit(accuracy_text, accuracy_rect)
            y_offset += 35
        elif max_combo > 1:
            combo_display = stats_font.render(f"Max Combo: {max_combo}", True, (255, 215, 0))
            combo_rect = combo_display.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            screen.blit(combo_display, combo_rect)
            y_offset += 35

        # 업적 표시 (강화된 버전)
        if achievements_unlocked and len(achievements_unlocked) > 0:
            y_offset += 10
            achievement_font = load_font(Resources.MAIN_FONT, 24)
            small_ach_font = load_font(Resources.MAIN_FONT, 18)

            # 업적 박스 배경
            box_width = 420
            box_height = 60 + len(achievements_unlocked[:4]) * 45
            box_x = (SCREEN_WIDTH - box_width) // 2
            box_y = y_offset - 10

            # 반투명 박스
            achievement_box = pygame.Surface((box_width, box_height))
            achievement_box.set_alpha(200)
            achievement_box.fill((30, 30, 50))
            screen.blit(achievement_box, (box_x, box_y))

            # 테두리 (골드)
            pygame.draw.rect(screen, (255, 215, 0), (box_x, box_y, box_width, box_height), 3)

            # 제목
            achievement_title = achievement_font.render("🏆 업적 달성!", True, (255, 215, 0))
            achievement_title_rect = achievement_title.get_rect(center=(SCREEN_WIDTH // 2, y_offset + 15))
            screen.blit(achievement_title, achievement_title_rect)
            y_offset += 45

            from game.achievements import AchievementChecker
            checker = AchievementChecker()

            for achievement_code in achievements_unlocked[:4]:  # 최대 4개 표시
                # 업적 아이콘 (골드 원)
                icon_x = box_x + 30
                icon_y = y_offset
                pygame.draw.circle(screen, (255, 215, 0), (icon_x, icon_y), 12)

                # 체크 마크
                check_font = load_font(Resources.MAIN_FONT, 16)
                check_text = check_font.render("✓", True, (0, 0, 0))
                check_rect = check_text.get_rect(center=(icon_x, icon_y))
                screen.blit(check_text, check_rect)

                # 업적 이름 및 설명
                ach_name = checker.get_achievement_display_name(achievement_code)
                ach_desc = checker.get_achievement_description(achievement_code)

                name_text = achievement_font.render(ach_name, True, (255, 215, 0))
                screen.blit(name_text, (icon_x + 25, y_offset - 15))

                desc_text = small_ach_font.render(ach_desc[:45] + "..." if len(ach_desc) > 45 else ach_desc, True, (180, 180, 180))
                screen.blit(desc_text, (icon_x + 25, y_offset + 8))

                y_offset += 45

            # 더 많은 업적이 있으면 표시
            if len(achievements_unlocked) > 4:
                more_text = small_ach_font.render(f"... 외 {len(achievements_unlocked) - 4}개", True, (150, 150, 150))
                more_rect = more_text.get_rect(center=(SCREEN_WIDTH // 2, y_offset - 10))
                screen.blit(more_text, more_rect)

            y_offset += 15

        # 사용자 이름 표시 (로그인된 경우)
        y_offset += 10
        if api_client.is_logged_in():
            user_text = stats_font.render(f"플레이어: {api_client.session_manager.username}", True, WHITE)
            user_rect = user_text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            screen.blit(user_text, user_rect)
            y_offset += 40

        # 저장 메시지
        message_color = (0, 255, 0) if score_saved else (255, 200, 0)
        small_font = load_font(Resources.MAIN_FONT, 20)
        save_text = small_font.render(save_message, True, message_color)
        save_rect = save_text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
        screen.blit(save_text, save_rect)

        # 종료 안내
        hint_font = load_font(Resources.MAIN_FONT, 18)
        hint_text = hint_font.render("아무 키나 눌러 메뉴로...", True, (150, 150, 150))
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        screen.blit(hint_text, hint_rect)

        pygame.display.flip()
        clock.tick(30)


class GameState:
    """게임 상태 관리"""

    def __init__(self, difficulty_manager=None, api_client=None):
        self.score = 0
        self.health = INITIAL_HEALTH
        self.game_over = False
        self.skill_count = 0
        self.skill_available = False
        self.stones = []
        self.missiles = []
        self.enemies = []
        self.enemy_projectiles = []
        self.stone_spawn_timer = 0
        self.stone_spawn_interval = STONE_SPAWN_INTERVAL_START
        self.current_frame = 0
        self.combo_system = ComboSystem(timeout_frames=180)
        self.difficulty_manager = difficulty_manager
        self.powerup_manager = PowerUpManager()

        # 새로운 시스템들
        self.stage_manager = StageManager()
        difficulty_name = difficulty_manager.current_difficulty if difficulty_manager else "medium"

        # 레이저 피해 쿨다운 (연속 피해 방지)
        self.laser_damage_cooldown = 0  # 프레임 단위
        self.statistics = GameStatistics(difficulty=difficulty_name)
        self.achievement_checker = AchievementChecker(api_client)
        self.achievement_notification_manager = AchievementNotificationManager(self.achievement_checker)

        # 적 관련 통계 (하위 호환성 유지)
        self.enemies_destroyed = 0
        self.missiles_fired = 0
        self.missiles_hit = 0

        # 플레이어 상태 (파워업 효과)
        self.player_speed_multiplier = 1.0
        self.is_invincible = False

    def reset(self):
        """게임 상태 초기화"""
        self.score = 0
        self.health = INITIAL_HEALTH
        self.game_over = False
        self.skill_count = 0
        self.laser_damage_cooldown = 0
        self.skill_available = False
        self.stones.clear()
        self.missiles.clear()
        self.enemies.clear()
        self.enemy_projectiles.clear()
        self.stone_spawn_timer = 0
        self.stone_spawn_interval = STONE_SPAWN_INTERVAL_START
        self.current_frame = 0
        self.combo_system.reset()
        self.powerup_manager.clear_powerups()
        self.stage_manager.reset()
        self.statistics.reset()
        self.achievement_checker.reset()
        self.enemies_destroyed = 0
        self.missiles_fired = 0
        self.missiles_hit = 0
        self.player_speed_multiplier = 1.0
        self.is_invincible = False

    def take_damage(self):
        """플레이어 피해 입음 (무적 상태면 무시)"""
        if self.is_invincible:
            return  # 무적 상태에서는 피해 무시

        self.health -= 1
        self.statistics.on_damage_taken()  # 통계 기록
        if self.health <= 0:
            self.game_over = True

    def add_missile_hit(self, is_enemy=False):
        """
        미사일 히트 카운트

        Args:
            is_enemy: 적을 파괴한 경우 True
        """
        self.skill_count += 1
        self.missiles_hit += 1

        # 통계 업데이트
        self.statistics.on_missile_hit()
        if is_enemy:
            self.statistics.on_enemy_destroyed()
        else:
            self.statistics.on_stone_destroyed()

        # 콤보 추가
        self.combo_system.add_hit(self.current_frame)
        self.statistics.on_combo_update(self.combo_system.get_combo_count())

        # 콤보 배율 적용하여 점수 추가 (적은 2배 점수)
        base_score = 2 if is_enemy else 1
        multiplier = self.combo_system.get_multiplier()

        # 점수 배율 파워업 적용
        if self.powerup_manager.is_effect_active(PowerUpType.SCORE_MULTIPLIER):
            multiplier *= 2.0

        self.score += int(base_score * multiplier)

        if is_enemy:
            self.enemies_destroyed += 1

        if self.skill_count >= SKILL_THRESHOLD:
            self.skill_available = True

    def use_skill(self):
        """스킬 사용 (모든 돌과 적 제거)"""
        if self.skill_available or self.skill_count >= SKILL_THRESHOLD:
            # 스킬 사용 통계
            self.statistics.on_skill_used()

            # 모든 돌 제거 (콤보 유지하면서)
            for stone in self.stones:
                self.combo_system.add_hit(self.current_frame)
                self.statistics.on_combo_update(self.combo_system.get_count())
                self.statistics.on_stone_destroyed()
                multiplier = self.combo_system.get_multiplier()
                self.score += int(1 * multiplier)

            # 모든 적 제거 (적은 2배 점수)
            for enemy in self.enemies:
                self.combo_system.add_hit(self.current_frame)
                self.statistics.on_combo_update(self.combo_system.get_count())
                self.statistics.on_enemy_destroyed()
                multiplier = self.combo_system.get_multiplier()
                self.score += int(2 * multiplier)
                self.enemies_destroyed += 1

            self.stones.clear()
            self.enemies.clear()
            self.enemy_projectiles.clear()  # 적 발사체도 제거
            self.skill_available = False
            self.skill_count = 0

    def apply_powerup(self, powerup_type: PowerUpType):
        """
        파워업 효과 적용

        Args:
            powerup_type: 파워업 타입
        """
        # 아이템 수집 통계
        self.statistics.on_item_collected()

        if powerup_type == PowerUpType.HEALTH:
            # 체력 회복 (최대치까지)
            self.health = min(self.health + 1, INITIAL_HEALTH)
        elif powerup_type == PowerUpType.SHIELD:
            # 무적 효과
            self.powerup_manager.activate_powerup(powerup_type)
            self.is_invincible = True
        elif powerup_type == PowerUpType.SPEED_BOOST:
            # 속도 증가
            self.powerup_manager.activate_powerup(powerup_type)
            self.player_speed_multiplier = 1.5
        elif powerup_type == PowerUpType.MULTI_SHOT:
            # 3연발
            self.powerup_manager.activate_powerup(powerup_type)
        elif powerup_type == PowerUpType.SCORE_MULTIPLIER:
            # 점수 2배
            self.powerup_manager.activate_powerup(powerup_type)

    def update_powerup_effects(self):
        """파워업 효과 상태 업데이트"""
        # 무적 효과 확인
        if not self.powerup_manager.is_effect_active(PowerUpType.SHIELD):
            self.is_invincible = False

        # 속도 증가 효과 확인
        if not self.powerup_manager.is_effect_active(PowerUpType.SPEED_BOOST):
            self.player_speed_multiplier = 1.0


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

        # 난이도 설정 가져오기
        if difficulty_manager:
            difficulty_settings = difficulty_manager.get_current_settings()
            enemy_speed = difficulty_settings.get('enemy_speed', 2.5)
            enemy_spawn_chance = difficulty_settings.get('enemy_spawn_chance', 0.2)
            enemy_evasion_skill = difficulty_settings.get('enemy_evasion_skill', 0.8)
            enemy_attack_rate = difficulty_settings.get('enemy_attack_rate', 90)
        else:
            # 기본값 사용
            from core.config import ENEMY_SPEED, ENEMY_SPAWN_CHANCE, ENEMY_EVASION_SKILL, ENEMY_ATTACK_RATE
            enemy_speed = ENEMY_SPEED
            enemy_spawn_chance = ENEMY_SPAWN_CHANCE
            enemy_evasion_skill = ENEMY_EVASION_SKILL
            enemy_attack_rate = ENEMY_ATTACK_RATE

        # 리소스 로드
        try:
            from core.config import ENEMY_WIDTH, ENEMY_HEIGHT, ENEMY_PROJECTILE_SPEED

            background_img = load_image(Resources.BACKGROUND, (SCREEN_WIDTH, SCREEN_HEIGHT))
            player_img = load_image(Resources.PLAYER, (PLAYER_WIDTH, PLAYER_HEIGHT))
            stone_img = load_image(Resources.STONE, (STONE_MAX_SIZE, STONE_MAX_SIZE))
            missile_img = load_image(Resources.MISSILE, (MISSILE_WIDTH, MISSILE_HEIGHT))
            collision_img = load_image(Resources.COLLISION, (STONE_MAX_SIZE, STONE_MAX_SIZE))
            heart_full_img = load_image(Resources.HEART_FULL, (UI.HEART_SIZE, UI.HEART_SIZE))
            heart_empty_img = load_image(Resources.HEART_EMPTY, (UI.HEART_SIZE, UI.HEART_SIZE))
            skill_icon = load_image(Resources.SKILL_ICON, (UI.SKILL_ICON_SIZE, UI.SKILL_ICON_SIZE))
            enemy_img = load_image(Resources.ENEMY, (ENEMY_WIDTH, ENEMY_HEIGHT))
            enemy_proj_img = load_image(Resources.ENEMY_PROJECTILE, (MISSILE_WIDTH, MISSILE_HEIGHT))

            missile_sound = load_sound(Resources.MISSILE_SOUND)
            load_music(Resources.BACKGROUND_MUSIC)
            pygame.mixer.music.play(-1)

            # 적 레이저 사운드 (선택적 로드 - 파일이 없어도 계속 진행)
            enemy_laser_charge_sound = None
            enemy_laser_fire_sound = None
            try:
                import os
                if os.path.exists(Resources.ENEMY_LASER_CHARGE_SOUND):
                    enemy_laser_charge_sound = load_sound(Resources.ENEMY_LASER_CHARGE_SOUND)
                if os.path.exists(Resources.ENEMY_LASER_FIRE_SOUND):
                    enemy_laser_fire_sound = load_sound(Resources.ENEMY_LASER_FIRE_SOUND)
            except Exception as e:
                logger.warning(f"적 레이저 사운드 로드 실패 (선택사항): {e}")

            font = load_font(Resources.MAIN_FONT, UI.FONT_SIZE_MEDIUM)
        except (FileNotFoundError, pygame.error) as e:
            show_error_dialog("게임 리소스 로드 오류", str(e))
            return

        # 게임 상태 초기화
        game_state = GameState(difficulty_manager, api_client)
        player = Player(player_img)

        # 적 상태 추적 (사운드 재생용)
        enemy_states = {}  # {enemy_id: previous_state}

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
                            # 멀티샷 파워업 확인
                            if game_state.powerup_manager.is_effect_active(PowerUpType.MULTI_SHOT):
                                # 3연발
                                missile_x = player.rect.x + PLAYER_WIDTH / 2 - MISSILE_WIDTH / 2
                                missile_y = player.rect.y

                                # 중앙
                                missile_center = Missile(missile_img, missile_x, missile_y)
                                game_state.missiles.append(missile_center)

                                # 왼쪽
                                missile_left = Missile(missile_img, missile_x - 15, missile_y)
                                game_state.missiles.append(missile_left)

                                # 오른쪽
                                missile_right = Missile(missile_img, missile_x + 15, missile_y)
                                game_state.missiles.append(missile_right)

                                game_state.missiles_fired += 3
                                game_state.statistics.on_missile_fired(3)
                            else:
                                # 일반 발사
                                missile_x = player.rect.x + PLAYER_WIDTH / 2 - MISSILE_WIDTH / 2
                                missile_y = player.rect.y
                                missile = Missile(missile_img, missile_x, missile_y)
                                game_state.missiles.append(missile)
                                game_state.missiles_fired += 1
                                game_state.statistics.on_missile_fired(1)

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
                game_state.powerup_manager.update_effects()
                game_state.update_powerup_effects()
                game_state.stage_manager.update_notification()

                # 스테이지 진행 체크
                if game_state.stage_manager.check_advance(game_state.score):
                    # 스테이지 진행 시 통계 업데이트
                    game_state.statistics.on_stage_advanced(game_state.stage_manager.current_stage_number)

            # 플레이어 움직임 (속도 파워업 적용)
            if not game_state.game_over:
                keys = pygame.key.get_pressed()
                # 원래 속도에 multiplier 적용
                if keys[pygame.K_UP]:
                    player.rect.y -= PLAYER_SPEED * game_state.player_speed_multiplier
                    if player.rect.y < 0:
                        player.rect.y = 0
                if keys[pygame.K_DOWN]:
                    player.rect.y += PLAYER_SPEED * game_state.player_speed_multiplier
                    if player.rect.y > SCREEN_HEIGHT - PLAYER_HEIGHT:
                        player.rect.y = SCREEN_HEIGHT - PLAYER_HEIGHT
                if keys[pygame.K_LEFT]:
                    player.rect.x -= PLAYER_SPEED * game_state.player_speed_multiplier
                    if player.rect.x < 0:
                        player.rect.x = 0
                if keys[pygame.K_RIGHT]:
                    player.rect.x += PLAYER_SPEED * game_state.player_speed_multiplier
                    if player.rect.x > SCREEN_WIDTH - PLAYER_WIDTH:
                        player.rect.x = SCREEN_WIDTH - PLAYER_WIDTH

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
                # 스테이지 배율 적용한 스폰 간격
                adjusted_interval = int(game_state.stone_spawn_interval *
                                       game_state.stage_manager.get_stone_spawn_multiplier())
                if game_state.stone_spawn_timer >= adjusted_interval:
                    # 스테이지 배율 적용한 운석 속도
                    speed_multiplier = game_state.stage_manager.get_stone_speed_multiplier()
                    stone = Stone(stone_img, speed_multiplier=speed_multiplier)
                    game_state.stones.append(stone)
                    game_state.stone_spawn_timer = 0
                    game_state.stone_spawn_interval = max(
                        game_state.stone_spawn_interval - 1,
                        STONE_SPAWN_INTERVAL_MIN
                    )

            # 적 생성 (확률적, 스테이지 배율 적용)
            if not game_state.game_over:
                # 스테이지 배율 적용
                adjusted_spawn_chance = enemy_spawn_chance * game_state.stage_manager.get_enemy_spawn_multiplier()
                if random.random() < adjusted_spawn_chance / 60:  # 프레임당 확률 조정
                    enemy = Enemy(enemy_img, enemy_speed, enemy_evasion_skill)
                    game_state.enemies.append(enemy)

            # 파워업 생성 (확률적, 약 5초마다 1개)
            if not game_state.game_over:
                if random.random() < 0.003:  # 약 0.3% 확률 (60 FPS 기준 약 5초마다 1개)
                    game_state.powerup_manager.spawn_random_powerup()

            # 돌 업데이트 및 그리기
            for stone in game_state.stones:
                stone.update()
                stone.draw(gameScr)

            # 적 업데이트 및 그리기 (레이저 시스템)
            for enemy in game_state.enemies:
                enemy_id = id(enemy)  # 적의 고유 ID
                prev_state = enemy_states.get(enemy_id, None)

                # 적 업데이트 (플레이어, 미사일, 운석 전달하여 AI 로직 실행)
                enemy.update(player, game_state.missiles, game_state.stones)

                # 상태 변경 감지 및 사운드 재생
                current_state = enemy.state
                if prev_state != current_state:
                    # 충전 시작 시 충전 사운드 재생
                    if current_state == EnemyState.CHARGING and enemy_laser_charge_sound:
                        enemy_laser_charge_sound.play()

                    # 발사 시작 시 발사 사운드 재생
                    elif current_state == EnemyState.FIRING and enemy_laser_fire_sound:
                        enemy_laser_fire_sound.play()

                    # 상태 업데이트
                    enemy_states[enemy_id] = current_state

                # 적 그리기 (레이저 포함)
                enemy.draw(gameScr)

            # 화면 밖으로 나간 적의 상태 추적 정리
            current_enemy_ids = {id(enemy) for enemy in game_state.enemies}
            enemy_states = {eid: state for eid, state in enemy_states.items() if eid in current_enemy_ids}

            # 적 발사체 업데이트 및 그리기
            for projectile in game_state.enemy_projectiles:
                projectile.update()
                projectile.draw(gameScr)

            # 파워업 업데이트 및 그리기
            game_state.powerup_manager.update_powerups()
            game_state.powerup_manager.draw_powerups(gameScr, load_font(Resources.MAIN_FONT, 20))

            # 충돌 감지
            collisions = CollisionDetector.check_all_collisions(
                player,
                game_state.missiles,
                game_state.stones,
                game_state.enemies,
                game_state.enemy_projectiles,
                game_state.powerup_manager.get_active_powerups()
            )

            # 플레이어-운석 충돌 처리
            unique_player_stones = sorted(set(collisions['player_stone']), reverse=True)
            for stone_idx in unique_player_stones:
                game_state.take_damage()
                gameScr.blit(collision_img, (game_state.stones[stone_idx].rect.x, game_state.stones[stone_idx].rect.y))
                del game_state.stones[stone_idx]

            # 플레이어-적 충돌 처리
            unique_player_enemies = sorted(set(collisions['player_enemy']), reverse=True)
            for enemy_idx in unique_player_enemies:
                game_state.take_damage()
                gameScr.blit(collision_img, (game_state.enemies[enemy_idx].rect.x, game_state.enemies[enemy_idx].rect.y))
                del game_state.enemies[enemy_idx]

            # 플레이어-적 발사체 충돌 처리
            unique_player_projectiles = sorted(set(collisions['player_enemy_projectile']), reverse=True)
            for proj_idx in unique_player_projectiles:
                game_state.take_damage()
                del game_state.enemy_projectiles[proj_idx]

            # 플레이어-적 레이저 충돌 처리 (쿨다운 적용)
            unique_player_lasers = set(collisions['player_enemy_laser'])
            if unique_player_lasers and not game_state.powerup_manager.has_active_powerup(PowerUpType.SHIELD):
                # 레이저에 맞으면 피해 (무적 상태가 아닌 경우)
                # 쿨다운이 끝났을 때만 피해 적용 (30 프레임 = 0.5초)
                if game_state.laser_damage_cooldown <= 0:
                    game_state.take_damage()
                    game_state.laser_damage_cooldown = 30  # 0.5초 쿨다운

            # 레이저 피해 쿨다운 감소
            if game_state.laser_damage_cooldown > 0:
                game_state.laser_damage_cooldown -= 1

            # 플레이어-파워업 충돌 처리
            unique_player_powerups = sorted(set(collisions['player_powerup']), reverse=True)
            for powerup_idx in unique_player_powerups:
                powerup = game_state.powerup_manager.get_active_powerups()[powerup_idx]
                game_state.apply_powerup(powerup.type)  # 내부에서 통계 업데이트
                del game_state.powerup_manager.active_powerups[powerup_idx]

            # 미사일-운석 충돌 처리
            stones_to_remove = set()
            missiles_to_remove = set()
            for missile_idx, stone_idx in collisions['missile_stone']:
                if stone_idx not in stones_to_remove:
                    game_state.add_missile_hit(is_enemy=False)
                    gameScr.blit(collision_img, (game_state.stones[stone_idx].rect.x, game_state.stones[stone_idx].rect.y))
                stones_to_remove.add(stone_idx)
                missiles_to_remove.add(missile_idx)

            # 미사일-적 충돌 처리
            enemies_to_remove = set()
            for missile_idx, enemy_idx in collisions['missile_enemy']:
                if enemy_idx not in enemies_to_remove:
                    game_state.add_missile_hit(is_enemy=True)
                    gameScr.blit(collision_img, (game_state.enemies[enemy_idx].rect.x, game_state.enemies[enemy_idx].rect.y))
                enemies_to_remove.add(enemy_idx)
                missiles_to_remove.add(missile_idx)

            # 큰 인덱스부터 삭제
            for stone_idx in sorted(stones_to_remove, reverse=True):
                del game_state.stones[stone_idx]
            for enemy_idx in sorted(enemies_to_remove, reverse=True):
                del game_state.enemies[enemy_idx]
            for missile_idx in sorted(missiles_to_remove, reverse=True):
                del game_state.missiles[missile_idx]

            # 범위 벗어난 객체 제거
            for missile_idx in sorted(collisions['missile_out'], reverse=True):
                del game_state.missiles[missile_idx]

            for stone_idx in sorted(collisions['stone_out'], reverse=True):
                del game_state.stones[stone_idx]

            for enemy_idx in sorted(collisions['enemy_out'], reverse=True):
                del game_state.enemies[enemy_idx]

            for proj_idx in sorted(collisions['enemy_projectile_out'], reverse=True):
                del game_state.enemy_projectiles[proj_idx]

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

            # UI 그리기 - 스테이지
            stage_text = font.render(f"Stage: {game_state.stage_manager.current_stage_number}", True, (100, 200, 255))
            stage_rect = stage_text.get_rect(center=(SCREEN_WIDTH - 70, 60))
            gameScr.blit(stage_text, stage_rect)

            # 스테이지 진행 알림
            if game_state.stage_manager.show_stage_notification:
                stage_noti_font = load_font(Resources.MAIN_FONT, 56)
                stage_noti_text = stage_noti_font.render(
                    game_state.stage_manager.get_stage_info(),
                    True,
                    (255, 215, 0) if game_state.stage_manager.is_boss_stage() else (100, 200, 255)
                )
                stage_noti_rect = stage_noti_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                # 반투명 배경
                overlay = pygame.Surface((SCREEN_WIDTH, 100))
                overlay.set_alpha(150)
                overlay.fill((0, 0, 0))
                gameScr.blit(overlay, (0, SCREEN_HEIGHT // 2 - 50))
                gameScr.blit(stage_noti_text, stage_noti_rect)

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

            # UI 그리기 - 활성 파워업 효과
            effect_font = load_font(Resources.MAIN_FONT, 18)
            game_state.powerup_manager.draw_active_effects_ui(gameScr, effect_font, 10, 100)

            # 무적 상태 표시 (화면 테두리)
            if game_state.is_invincible:
                pygame.draw.rect(gameScr, (100, 200, 255), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), 5)

            # 실시간 업적 체크 (게임 중)
            if not game_state.game_over:
                game_state.achievement_checker.check_realtime_achievements(
                    game_state.statistics,
                    game_state.score
                )

            # 업적 알림 업데이트 및 그리기
            game_state.achievement_notification_manager.update()
            game_state.achievement_notification_manager.draw(gameScr, Resources.MAIN_FONT)

            # 업적 체커에서 대기 중인 알림 확인 및 추가
            while game_state.achievement_checker.has_notifications():
                achievement_code = game_state.achievement_checker.pop_notification()
                if achievement_code:
                    game_state.achievement_notification_manager.add_achievement(achievement_code)

            # UI 그리기 - BACK 버튼
            mouse_pos = pygame.mouse.get_pos()
            back_text = font.render("BACK", True, RED if back_button.collidepoint(mouse_pos) else WHITE)
            gameScr.blit(back_text, [back_button.x, back_button.y])

            # 게임 오버 처리
            if game_state.game_over:
                # 게임 오버 화면 표시 및 점수 저장
                pygame.display.flip()
                pygame.time.wait(1000)  # 1초 대기

                # 통계 및 업적 체크
                max_combo = game_state.combo_system.get_max_combo()
                achievements_unlocked = game_state.achievement_checker.check_achievements(
                    game_state.statistics,
                    game_state.score
                )

                show_game_over_screen(
                    gameScr, font, game_state.score, background_img, api_client,
                    max_combo, game_state.statistics, achievements_unlocked
                )
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

