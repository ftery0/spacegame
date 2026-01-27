"""게임 설정 및 상수 관리"""
import os
import sys

# 프로젝트 루트 디렉토리 경로 자동 감지
if getattr(sys, 'frozen', False):
    # PyInstaller로 빌드된 경우
    PROJECT_ROOT = os.path.dirname(sys.executable)
else:
    # 일반 Python 스크립트 실행
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 리소스 경로
TEXTURE_DIR = os.path.join(PROJECT_ROOT, "texture")
FONT_DIR = os.path.join(PROJECT_ROOT, "font")

# 화면 설정
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 800
FPS = 60

# 색상 상수
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# 플레이어 설정
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 50
PLAYER_SPEED = 5
PLAYER_START_X = 250
PLAYER_START_Y = 400

# 돌(적) 설정
STONE_MIN_SIZE = 30
STONE_MAX_SIZE = 50
STONE_SPEED = 3
STONE_SPAWN_INTERVAL_START = 90
STONE_SPAWN_INTERVAL_MIN = 40

# 미사일 설정
MISSILE_WIDTH = 10
MISSILE_HEIGHT = 30
MISSILE_SPEED = 5

# 적 설정 (기본값, 난이도에 따라 조정됨)
ENEMY_WIDTH = 50
ENEMY_HEIGHT = 50
ENEMY_SPEED = 2.5
ENEMY_SPAWN_CHANCE = 0.2  # 기본 생성 확률
ENEMY_EVASION_SKILL = 0.8  # 기본 회피 능력
ENEMY_ATTACK_RATE = 90  # 기본 공격 주기 (프레임)
ENEMY_PROJECTILE_SPEED = 3.0

# 적 레이저 설정
ENEMY_LASER_CHARGE_TIME = 300  # 5초 충전 (60 FPS 기준)
ENEMY_LASER_FIRE_TIME = 60  # 1초 발사
ENEMY_LASER_COOLDOWN_TIME = 60  # 1초 쿨다운
ENEMY_LASER_WIDTH = 8  # 레이저 빔 두께
ENEMY_LASER_COLOR = (255, 50, 50)  # 빨간색 레이저
ENEMY_LASER_CHARGE_COLOR = (255, 200, 50)  # 노란색 충전 이펙트

# 게임 플레이 설정
INITIAL_HEALTH = 3
SKILL_THRESHOLD = 10

# 리소스 파일 경로
class Resources:
    """리소스 파일 경로 관리"""

    # 이미지
    BACKGROUND = os.path.join(TEXTURE_DIR, "back_ground_Ui.gif")
    PLAYER = os.path.join(TEXTURE_DIR, "player.png")
    STONE = os.path.join(TEXTURE_DIR, "rock1.png")
    MISSILE = os.path.join(TEXTURE_DIR, "mix.png")
    COLLISION = os.path.join(TEXTURE_DIR, "bob.png")
    HEART_FULL = os.path.join(TEXTURE_DIR, "heart.png")
    HEART_EMPTY = os.path.join(TEXTURE_DIR, "heart2.png")
    SKILL_ICON = os.path.join(TEXTURE_DIR, "skill.png")
    ENEMY = os.path.join(TEXTURE_DIR, "rock1.png")  # TODO: 전용 적 이미지 추가
    ENEMY_PROJECTILE = os.path.join(TEXTURE_DIR, "mix.png")  # TODO: 전용 발사체 이미지 추가

    # 사운드
    BACKGROUND_MUSIC = os.path.join(TEXTURE_DIR, "backsound.mp3")
    MISSILE_SOUND = os.path.join(TEXTURE_DIR, "laser2.mp3")

    # 적 레이저 사운드 (나중에 사용자가 제공)
    ENEMY_LASER_CHARGE_SOUND = os.path.join(PROJECT_ROOT, "sounds", "enemy_laser_charge.mp3")  # TODO: 충전 사운드 추가 필요
    ENEMY_LASER_FIRE_SOUND = os.path.join(PROJECT_ROOT, "sounds", "enemy_laser_fire.mp3")  # TODO: 발사 사운드 추가 필요

    # 폰트
    MAIN_FONT = os.path.join(FONT_DIR, "BMDOHYEON_ttf.ttf")

    @staticmethod
    def validate():
        """모든 리소스 파일이 존재하는지 확인"""
        missing_files = []

        for attr_name in dir(Resources):
            if attr_name.startswith('_'):
                continue

            attr_value = getattr(Resources, attr_name)
            if isinstance(attr_value, str) and not os.path.exists(attr_value):
                missing_files.append(attr_value)

        if missing_files:
            error_msg = "다음 리소스 파일을 찾을 수 없습니다:\n"
            for file in missing_files:
                error_msg += f"  - {file}\n"
            raise FileNotFoundError(error_msg)

        return True

# UI 설정
class UI:
    """UI 요소 위치 및 크기"""

    # 시작 화면 버튼
    START_BUTTON = {"x": 100, "y": 120, "width": 300, "height": 70}
    RANKING_BUTTON = {"x": 100, "y": 210, "width": 140, "height": 60}
    PROFILE_BUTTON = {"x": 260, "y": 210, "width": 140, "height": 60}
    STATS_BUTTON = {"x": 100, "y": 290, "width": 140, "height": 60}
    ACHIEVEMENT_BUTTON = {"x": 260, "y": 290, "width": 140, "height": 60}
    INFO_BUTTON = {"x": 100, "y": 370, "width": 300, "height": 60}
    QUIT_BUTTON = {"x": 100, "y": 450, "width": 300, "height": 60}

    # 게임 화면 버튼
    BACK_BUTTON = {"x": 10, "y": 750, "width": 150, "height": 50}

    # 정보 화면 버튼
    INFO_BACK_BUTTON = {"x": 20, "y": 50, "width": 40, "height": 50}

    # 하트 표시
    HEART_SIZE = 30
    HEART_START_X = 10
    HEART_START_Y = 10
    HEART_SPACING = 40

    # 스킬 아이콘
    SKILL_ICON_X = 400
    SKILL_ICON_Y = 650
    SKILL_ICON_SIZE = 100

    # 폰트 크기
    FONT_SIZE_LARGE = 50
    FONT_SIZE_MEDIUM = 30
