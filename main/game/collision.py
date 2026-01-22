"""Collision detection module"""
from typing import List, Tuple
from game.entities import Player, Stone, Missile


class CollisionDetector:
    """충돌 감지 모듈"""

    @staticmethod
    def check_missile_stone_collision(
        missiles: List[Missile],
        stones: List[Stone]
    ) -> List[Tuple[int, int]]:
        """
        미사일과 운석의 충돌 확인

        Args:
            missiles: 미사일 리스트
            stones: 운석 리스트

        Returns:
            List[Tuple[int, int]]: [(미사일 인덱스, 운석 인덱스), ...]
        """
        collisions = []

        for missile_idx, missile in enumerate(missiles):
            for stone_idx, stone in enumerate(stones):
                if missile.get_rect().colliderect(stone.get_rect()):
                    collisions.append((missile_idx, stone_idx))

        return collisions

    @staticmethod
    def check_player_stone_collision(
        player: Player,
        stones: List[Stone]
    ) -> List[int]:
        """
        플레이어와 운석의 충돌 확인

        Args:
            player: 플레이어
            stones: 운석 리스트

        Returns:
            List[int]: 충돌한 운석의 인덱스 리스트
        """
        collisions = []
        player_rect = player.get_rect()

        for stone_idx, stone in enumerate(stones):
            if player_rect.colliderect(stone.get_rect()):
                collisions.append(stone_idx)

        return collisions

    @staticmethod
    def check_missile_out_of_bounds(missiles: List[Missile]) -> List[int]:
        """
        화면 범위를 벗어난 미사일 확인

        Args:
            missiles: 미사일 리스트

        Returns:
            List[int]: 화면 범위를 벗어난 미사일의 인덱스 리스트
        """
        out_of_bounds = []

        for idx, missile in enumerate(missiles):
            if missile.is_off_screen():
                out_of_bounds.append(idx)

        return out_of_bounds

    @staticmethod
    def check_stone_out_of_bounds(stones: List[Stone]) -> List[int]:
        """
        화면 범위를 벗어난 운석 확인

        Args:
            stones: 운석 리스트

        Returns:
            List[int]: 화면 범위를 벗어난 운석의 인덱스 리스트
        """
        out_of_bounds = []

        for idx, stone in enumerate(stones):
            if stone.is_off_screen():
                out_of_bounds.append(idx)

        return out_of_bounds

    @staticmethod
    def check_all_collisions(
        player: Player,
        missiles: List[Missile],
        stones: List[Stone]
    ) -> dict:
        """
        모든 충돌 확인

        Args:
            player: 플레이어
            missiles: 미사일 리스트
            stones: 운석 리스트

        Returns:
            dict: 충돌 정보 딕셔너리
                {
                    'missile_stone': [(미사일_idx, 운석_idx), ...],
                    'player_stone': [운석_idx, ...],
                    'missile_out': [미사일_idx, ...],
                    'stone_out': [운석_idx, ...]
                }
        """
        return {
            'missile_stone': CollisionDetector.check_missile_stone_collision(missiles, stones),
            'player_stone': CollisionDetector.check_player_stone_collision(player, stones),
            'missile_out': CollisionDetector.check_missile_out_of_bounds(missiles),
            'stone_out': CollisionDetector.check_stone_out_of_bounds(stones)
        }
