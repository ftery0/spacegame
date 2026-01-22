"""Game entity tests"""
import pytest
import pygame
from game.entities import Player, Stone, Missile
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, PLAYER_START_X, PLAYER_START_Y,
    PLAYER_SPEED, STONE_SPEED, MISSILE_SPEED
)


@pytest.fixture(scope="session")
def pygame_init():
    """pygame 초기화"""
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture
def mock_image(pygame_init):
    """모의 이미지 생성"""
    return pygame.Surface((50, 50))


class TestPlayer:
    """플레이어 엔티티 테스트"""

    def test_player_initialization(self, mock_image):
        """플레이어 초기화"""
        player = Player(mock_image)

        assert player.rect.x == PLAYER_START_X
        assert player.rect.y == PLAYER_START_Y
        assert player.speed == PLAYER_SPEED

    def test_player_move_left(self, mock_image):
        """플레이어 왼쪽 이동"""
        player = Player(mock_image)
        initial_x = player.rect.x
        player.move_left()

        assert player.rect.x == initial_x - PLAYER_SPEED

    def test_player_move_left_boundary(self, mock_image):
        """플레이어 왼쪽 경계 테스트"""
        player = Player(mock_image)
        player.rect.x = 0
        player.move_left()

        assert player.rect.x == 0  # 이동하지 않음

    def test_player_move_right(self, mock_image):
        """플레이어 오른쪽 이동"""
        player = Player(mock_image)
        initial_x = player.rect.x
        player.move_right()

        assert player.rect.x == initial_x + PLAYER_SPEED

    def test_player_move_up(self, mock_image):
        """플레이어 위쪽 이동"""
        player = Player(mock_image)
        initial_y = player.rect.y
        player.move_up()

        assert player.rect.y == initial_y - PLAYER_SPEED

    def test_player_move_down(self, mock_image):
        """플레이어 아래쪽 이동"""
        player = Player(mock_image)
        initial_y = player.rect.y
        player.move_down()

        assert player.rect.y == initial_y + PLAYER_SPEED

    def test_player_get_rect(self, mock_image):
        """플레이어 사각형 반환"""
        player = Player(mock_image)
        rect = player.get_rect()

        assert rect == player.rect


class TestStone:
    """운석 엔티티 테스트"""

    def test_stone_initialization(self, mock_image):
        """운석 초기화"""
        stone = Stone(mock_image, x=100, y=0)

        assert stone.rect.x == 100
        assert stone.rect.y == 0
        assert stone.speed == STONE_SPEED

    def test_stone_update(self, mock_image):
        """운석 업데이트"""
        stone = Stone(mock_image, x=100, y=0)
        initial_y = stone.rect.y
        stone.update()

        assert stone.rect.y == initial_y + STONE_SPEED

    def test_stone_is_off_screen(self, mock_image):
        """운석 화면 범위 벗어남 확인"""
        stone = Stone(mock_image, y=SCREEN_HEIGHT + 1)

        assert stone.is_off_screen() is True

    def test_stone_is_on_screen(self, mock_image):
        """운석 화면 범위 내 확인"""
        stone = Stone(mock_image, y=100)

        assert stone.is_off_screen() is False

    def test_stone_get_rect(self, mock_image):
        """운석 사각형 반환"""
        stone = Stone(mock_image)
        rect = stone.get_rect()

        assert rect == stone.rect


class TestMissile:
    """미사일 엔티티 테스트"""

    def test_missile_initialization(self, mock_image):
        """미사일 초기화"""
        missile = Missile(mock_image, x=100, y=500)

        assert missile.rect.x == 100
        assert missile.rect.y == 500
        assert missile.speed == MISSILE_SPEED

    def test_missile_update(self, mock_image):
        """미사일 업데이트"""
        missile = Missile(mock_image, x=100, y=500)
        initial_y = missile.rect.y
        missile.update()

        assert missile.rect.y == initial_y - MISSILE_SPEED

    def test_missile_is_off_screen(self, mock_image):
        """미사일 화면 범위 벗어남 확인"""
        missile = Missile(mock_image, x=100, y=-1)

        assert missile.is_off_screen() is True

    def test_missile_is_on_screen(self, mock_image):
        """미사일 화면 범위 내 확인"""
        missile = Missile(mock_image, x=100, y=100)

        assert missile.is_off_screen() is False

    def test_missile_get_rect(self, mock_image):
        """미사일 사각형 반환"""
        missile = Missile(mock_image, x=100, y=500)
        rect = missile.get_rect()

        assert rect == missile.rect
