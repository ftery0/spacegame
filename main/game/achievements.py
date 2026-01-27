"""업적 시스템"""
from typing import List, Dict, Optional
from game.statistics import GameStatistics


class AchievementChecker:
    """업적 달성 체크"""

    def __init__(self, api_client=None):
        """
        업적 체커 초기화

        Args:
            api_client: API 클라이언트 (선택사항)
        """
        self.api_client = api_client
        self.unlocked_this_game = []
        self.notification_queue = []
        self.checked_achievements = set()  # 이미 체크한 업적 (중복 방지)

    def check_achievements(self, stats: GameStatistics, final_score: int) -> List[str]:
        """
        게임 종료 시 업적 체크

        Args:
            stats: 게임 통계
            final_score: 최종 점수

        Returns:
            List[str]: 이번 게임에서 달성한 업적 코드 리스트
        """
        achievements = []

        # 첫 게임 (서버에서 체크)
        # 'first_game' - 첫 게임 플레이

        # 백발백중 (명중률 90% 이상, 최소 20발 이상 발사)
        if stats.get_accuracy() >= 90 and stats.missiles_fired >= 20:
            achievements.append('perfect_aim')

        # 불사신 (피해 없이 500점 이상)
        if stats.is_perfect_game() and final_score >= 500:
            achievements.append('immortal')

        # 스피드러너 (3분 안에 1000점)
        if final_score >= 1000 and stats.get_play_time() <= 180:
            achievements.append('speedrunner')

        # 콤보 마스터 (100 콤보 달성)
        if stats.max_combo >= 100:
            achievements.append('combo_master')

        # 운석 파괴자 (게임당 100개 운석 파괴)
        if stats.stones_destroyed >= 100:
            achievements.append('stone_breaker_single')

        # 적 사냥꾼 (게임당 50명 적 처치)
        if stats.enemies_destroyed >= 50:
            achievements.append('enemy_hunter_single')

        # 보스 학살자 (보스 처치)
        if stats.boss_defeated > 0:
            achievements.append('boss_slayer')

        # 스테이지 마스터 (스테이지 10 도달)
        if stats.max_stage >= 10:
            achievements.append('stage_master')

        # 고수 (하드 난이도에서 2000점)
        if stats.difficulty == 'hard' and final_score >= 2000:
            achievements.append('expert_player')

        # 아이템 수집가 (게임당 20개 아이템 수집)
        if stats.items_collected >= 20:
            achievements.append('item_collector')

        # 서버에 업적 달성 전송
        for achievement_code in achievements:
            if achievement_code not in self.unlocked_this_game:
                self._unlock_achievement(achievement_code)
                self.unlocked_this_game.append(achievement_code)
                self.notification_queue.append(achievement_code)

        return achievements

    def _unlock_achievement(self, code: str):
        """
        업적 언락 (서버에 전송)

        Args:
            code: 업적 코드
        """
        if self.api_client and self.api_client.is_logged_in():
            try:
                success, data, error = self.api_client.unlock_achievement(code)
                if not success:
                    print(f"업적 언락 실패: {error}")
            except Exception as e:
                print(f"업적 언락 중 오류: {e}")

    def get_achievement_display_name(self, code: str) -> str:
        """
        업적 표시 이름

        Args:
            code: 업적 코드

        Returns:
            str: 표시 이름
        """
        achievement_names = {
            'first_game': '첫 걸음',
            'perfect_aim': '백발백중',
            'immortal': '불사신',
            'speedrunner': '스피드러너',
            'combo_master': '콤보 마스터',
            'stone_breaker': '운석 파괴자',
            'stone_breaker_single': '운석 헌터',
            'enemy_hunter': '적 사냥꾼',
            'enemy_hunter_single': '적 킬러',
            'boss_slayer': '보스 학살자',
            'stage_master': '스테이지 마스터',
            'expert_player': '고수',
            'item_collector': '아이템 수집가',
        }
        return achievement_names.get(code, code)

    def get_achievement_description(self, code: str) -> str:
        """
        업적 설명

        Args:
            code: 업적 코드

        Returns:
            str: 업적 설명
        """
        descriptions = {
            'first_game': '첫 게임을 플레이하세요',
            'perfect_aim': '미사일 명중률 90% 이상 달성',
            'immortal': '체력을 잃지 않고 500점 달성',
            'speedrunner': '3분 안에 1000점 달성',
            'combo_master': '100 콤보 달성',
            'stone_breaker': '누적 1000개 운석 파괴',
            'stone_breaker_single': '한 게임에서 100개 운석 파괴',
            'enemy_hunter': '누적 100명 적 처치',
            'enemy_hunter_single': '한 게임에서 50명 적 처치',
            'boss_slayer': '보스를 처치하세요',
            'stage_master': '스테이지 10에 도달',
            'expert_player': '하드 난이도에서 2000점 달성',
            'item_collector': '한 게임에서 20개 아이템 수집',
        }
        return descriptions.get(code, '???')

    def has_notifications(self) -> bool:
        """
        알림이 있는지 확인

        Returns:
            bool: 알림이 있으면 True
        """
        return len(self.notification_queue) > 0

    def pop_notification(self) -> Optional[str]:
        """
        알림 하나 가져오기

        Returns:
            Optional[str]: 업적 코드 (없으면 None)
        """
        if self.notification_queue:
            return self.notification_queue.pop(0)
        return None

    def check_realtime_achievements(self, stats: GameStatistics, current_score: int):
        """
        게임 중 실시간 업적 체크

        Args:
            stats: 게임 통계
            current_score: 현재 점수
        """
        achievements = []

        # 콤보 마스터 (100 콤보 달성)
        if stats.max_combo >= 100 and 'combo_master' not in self.checked_achievements:
            achievements.append('combo_master')
            self.checked_achievements.add('combo_master')

        # 스테이지 마스터 (스테이지 10 도달)
        if stats.max_stage >= 10 and 'stage_master' not in self.checked_achievements:
            achievements.append('stage_master')
            self.checked_achievements.add('stage_master')

        # 업적 달성 시 서버에 전송 및 알림 큐에 추가
        for achievement_code in achievements:
            if achievement_code not in self.unlocked_this_game:
                self._unlock_achievement(achievement_code)
                self.unlocked_this_game.append(achievement_code)
                self.notification_queue.append(achievement_code)

    def reset(self):
        """체커 리셋"""
        self.unlocked_this_game.clear()
        self.notification_queue.clear()
        self.checked_achievements.clear()
