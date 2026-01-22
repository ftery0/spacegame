"""Collision detection tests"""
import pytest
import pygame
from game.entities import Player, Stone, Missile
from game.collision import CollisionDetector
from config import PLAYER_START_X, PLAYER_START_Y


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


@pytest.fixture
def player(mock_image):
    """플레이어 픽스처"""
    return Player(mock_image)


class TestCollisionDetector:
    """충돌 감지 테스트"""

    def test_missile_stone_collision_hit(self, mock_image):
        """미사일과 운석 충돌"""
        missile = Missile(mock_image, x=100, y=100)
        stone = Stone(mock_image, x=100, y=100)

        collisions = CollisionDetector.check_missile_stone_collision([missile], [stone])

        assert len(collisions) > 0
        assert (0, 0) in collisions

    def test_missile_stone_no_collision(self, mock_image):
        """미사일과 운석 충돌 없음"""
        missile = Missile(mock_image, x=0, y=0)
        stone = Stone(mock_image, x=400, y=400)

        collisions = CollisionDetector.check_missile_stone_collision([missile], [stone])

        assert len(collisions) == 0

    def test_multiple_missile_stone_collisions(self, mock_image):
        """여러 미사일과 운석 충돌"""
        missile1 = Missile(mock_image, x=100, y=100)
        missile2 = Missile(mock_image, x=200, y=200)
        stone1 = Stone(mock_image, x=100, y=100)
        stone2 = Stone(mock_image, x=200, y=200)

        collisions = CollisionDetector.check_missile_stone_collision(
            [missile1, missile2],
            [stone1, stone2]
        )

        assert len(collisions) >= 2

    def test_player_stone_collision(self, mock_image, player):
        """플레이어와 운석 충돌"""
        # 플레이어 위치로 운석 생성
        stone = Stone(mock_image, x=PLAYER_START_X, y=PLAYER_START_Y)

        collisions = CollisionDetector.check_player_stone_collision(player, [stone])

        assert len(collisions) > 0
        assert 0 in collisions

    def test_player_stone_no_collision(self, mock_image, player):
        """플레이어와 운석 충돌 없음"""
        stone = Stone(mock_image, x=400, y=400)

        collisions = CollisionDetector.check_player_stone_collision(player, [stone])

        assert len(collisions) == 0

    def test_missile_out_of_bounds(self, mock_image):
        """미사일 화면 범위 벗어남"""
        missile1 = Missile(mock_image, x=100, y=-1)
        missile2 = Missile(mock_image, x=100, y=100)

        out_of_bounds = CollisionDetector.check_missile_out_of_bounds([missile1, missile2])

        assert len(out_of_bounds) == 1
        assert 0 in out_of_bounds

    def test_stone_out_of_bounds(self, mock_image):
        """운석 화면 범위 벗어남"""
        stone1 = Stone(mock_image, y=801)  # SCREEN_HEIGHT = 800
        stone2 = Stone(mock_image, y=400)

        out_of_bounds = CollisionDetector.check_stone_out_of_bounds([stone1, stone2])

        assert len(out_of_bounds) == 1
        assert 0 in out_of_bounds

    def test_check_all_collisions(self, mock_image, player):
        """모든 충돌 확인"""
        missile = Missile(mock_image, x=100, y=100)
        stone = Stone(mock_image, x=100, y=100)
        out_of_bounds_missile = Missile(mock_image, x=200, y=-1)
        out_of_bounds_stone = Stone(mock_image, y=801)

        collisions = CollisionDetector.check_all_collisions(
            player,
            [missile, out_of_bounds_missile],
            [stone, out_of_bounds_stone]
        )

        assert 'missile_stone' in collisions
        assert 'player_stone' in collisions
        assert 'missile_out' in collisions
        assert 'stone_out' in collisions
        assert len(collisions['missile_out']) > 0
        assert len(collisions['stone_out']) > 0
