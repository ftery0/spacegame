"""Collision detection module"""
from typing import List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from game.entities import Player, Stone, Missile
    from game.enemy import Enemy, EnemyProjectile


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
    def check_missile_enemy_collision(missiles: List, enemies: List) -> List[Tuple[int, int]]:
        """
        미사일과 적의 충돌 확인

        Args:
            missiles: 미사일 리스트
            enemies: 적 리스트

        Returns:
            List[Tuple[int, int]]: [(미사일 인덱스, 적 인덱스), ...]
        """
        collisions = []

        for missile_idx, missile in enumerate(missiles):
            for enemy_idx, enemy in enumerate(enemies):
                if missile.rect.colliderect(enemy.rect):
                    collisions.append((missile_idx, enemy_idx))

        return collisions

    @staticmethod
    def check_player_enemy_collision(player, enemies: List) -> List[int]:
        """
        플레이어와 적의 충돌 확인

        Args:
            player: 플레이어
            enemies: 적 리스트

        Returns:
            List[int]: 충돌한 적의 인덱스 리스트
        """
        collisions = []
        player_rect = player.get_rect()

        for enemy_idx, enemy in enumerate(enemies):
            if player_rect.colliderect(enemy.rect):
                collisions.append(enemy_idx)

        return collisions

    @staticmethod
    def check_player_enemy_projectile_collision(player, enemy_projectiles: List) -> List[int]:
        """
        플레이어와 적 발사체의 충돌 확인

        Args:
            player: 플레이어
            enemy_projectiles: 적 발사체 리스트

        Returns:
            List[int]: 충돌한 발사체의 인덱스 리스트
        """
        collisions = []
        player_rect = player.get_rect()

        for proj_idx, projectile in enumerate(enemy_projectiles):
            if player_rect.colliderect(projectile.rect):
                collisions.append(proj_idx)

        return collisions

    @staticmethod
    def check_enemy_out_of_bounds(enemies: List) -> List[int]:
        """
        화면 범위를 벗어난 적 확인

        Args:
            enemies: 적 리스트

        Returns:
            List[int]: 화면 범위를 벗어난 적의 인덱스 리스트
        """
        out_of_bounds = []

        for idx, enemy in enumerate(enemies):
            if enemy.is_off_screen():
                out_of_bounds.append(idx)

        return out_of_bounds

    @staticmethod
    def check_enemy_projectile_out_of_bounds(enemy_projectiles: List) -> List[int]:
        """
        화면 범위를 벗어난 적 발사체 확인

        Args:
            enemy_projectiles: 적 발사체 리스트

        Returns:
            List[int]: 화면 범위를 벗어난 발사체의 인덱스 리스트
        """
        out_of_bounds = []

        for idx, projectile in enumerate(enemy_projectiles):
            if projectile.is_off_screen():
                out_of_bounds.append(idx)

        return out_of_bounds

    @staticmethod
    def check_all_collisions(
        player,
        missiles: List,
        stones: List,
        enemies: List = None,
        enemy_projectiles: List = None
    ) -> dict:
        """
        모든 충돌 확인

        Args:
            player: 플레이어
            missiles: 미사일 리스트
            stones: 운석 리스트
            enemies: 적 리스트 (선택사항)
            enemy_projectiles: 적 발사체 리스트 (선택사항)

        Returns:
            dict: 충돌 정보 딕셔너리
                {
                    'missile_stone': [(미사일_idx, 운석_idx), ...],
                    'player_stone': [운석_idx, ...],
                    'missile_out': [미사일_idx, ...],
                    'stone_out': [운석_idx, ...],
                    'missile_enemy': [(미사일_idx, 적_idx), ...],
                    'player_enemy': [적_idx, ...],
                    'player_enemy_projectile': [발사체_idx, ...],
                    'enemy_out': [적_idx, ...],
                    'enemy_projectile_out': [발사체_idx, ...]
                }
        """
        enemies = enemies or []
        enemy_projectiles = enemy_projectiles or []

        return {
            'missile_stone': CollisionDetector.check_missile_stone_collision(missiles, stones),
            'player_stone': CollisionDetector.check_player_stone_collision(player, stones),
            'missile_out': CollisionDetector.check_missile_out_of_bounds(missiles),
            'stone_out': CollisionDetector.check_stone_out_of_bounds(stones),
            'missile_enemy': CollisionDetector.check_missile_enemy_collision(missiles, enemies),
            'player_enemy': CollisionDetector.check_player_enemy_collision(player, enemies),
            'player_enemy_projectile': CollisionDetector.check_player_enemy_projectile_collision(player, enemy_projectiles),
            'enemy_out': CollisionDetector.check_enemy_out_of_bounds(enemies),
            'enemy_projectile_out': CollisionDetector.check_enemy_projectile_out_of_bounds(enemy_projectiles)
        }
