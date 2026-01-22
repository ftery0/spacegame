"""API service wrapper for backend communication"""
import logging
import requests
import threading
from typing import Optional, Dict, Any, List, Callable
from concurrent.futures import ThreadPoolExecutor, Future
from core.session_manager import SessionManager

logger = logging.getLogger(__name__)


class GameAPIClient:
    """API 통신을 위한 게임 API 클라이언트"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        GameAPIClient 초기화

        Args:
            base_url: API 서버의 기본 URL
        """
        self.base_url = base_url
        self.session_manager = SessionManager()
        self._executor = ThreadPoolExecutor(max_workers=3, thread_name_prefix="api-worker")

    def _get_headers(self) -> Dict[str, str]:
        """
        API 요청 헤더 반환

        Returns:
            Dict[str, str]: 요청 헤더
        """
        headers = {"Content-Type": "application/json"}
        auth_header = self.session_manager.get_auth_header()
        if auth_header:
            headers.update(auth_header)
        return headers

    def register(self, username: str, password: str) -> tuple[bool, Optional[Dict], Optional[str]]:
        """
        회원가입

        Args:
            username: 사용자명
            password: 비밀번호

        Returns:
            tuple: (성공 여부, 응답 데이터, 에러 메시지)
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/register",
                json={"username": username, "password": password},
                timeout=5
            )

            if response.status_code == 201:
                data = response.json()
                logger.info(f"회원가입 성공: {username}")
                return True, data, None
            else:
                error_msg = response.json().get("detail", "회원가입 실패")
                logger.warning(f"회원가입 실패: {username} - {error_msg}")
                return False, None, error_msg

        except requests.exceptions.RequestException as e:
            logger.error(f"회원가입 네트워크 오류: {str(e)}")
            return False, None, f"네트워크 오류: {str(e)}"

    def login(self, username: str, password: str) -> tuple[bool, Optional[Dict], Optional[str]]:
        """
        로그인

        Args:
            username: 사용자명
            password: 비밀번호

        Returns:
            tuple: (성공 여부, 응답 데이터, 에러 메시지)
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json={"username": username, "password": password},
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                # 토큰 저장
                self.session_manager.login(
                    data["user"]["username"],
                    data["user"]["id"],
                    data["access_token"],
                    data["token_type"]
                )
                logger.info(f"로그인 성공: {username}")
                return True, data, None
            else:
                error_msg = response.json().get("detail", "로그인 실패")
                logger.warning(f"로그인 실패: {username} - {error_msg}")
                return False, None, error_msg

        except requests.exceptions.RequestException as e:
            logger.error(f"로그인 네트워크 오류: {str(e)}")
            return False, None, f"네트워크 오류: {str(e)}"

    def save_score(self, score: int) -> tuple[bool, Optional[Dict], Optional[str]]:
        """
        점수 저장

        Args:
            score: 점수

        Returns:
            tuple: (성공 여부, 응답 데이터, 에러 메시지)
        """
        if not self.session_manager.is_logged_in():
            return False, None, "로그인이 필요합니다"

        try:
            response = requests.post(
                f"{self.base_url}/api/scores",
                json={"score": score},
                headers=self._get_headers(),
                timeout=5
            )

            if response.status_code == 201:
                return True, response.json(), None
            else:
                error_msg = response.json().get("detail", "점수 저장 실패")
                return False, None, error_msg

        except requests.exceptions.RequestException as e:
            return False, None, f"네트워크 오류: {str(e)}"

    def get_top_scores(self, limit: int = 10) -> tuple[bool, Optional[List], Optional[str]]:
        """
        상위 점수 조회

        Args:
            limit: 조회할 개수

        Returns:
            tuple: (성공 여부, 점수 리스트, 에러 메시지)
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/scores/top?limit={limit}",
                headers=self._get_headers(),
                timeout=5
            )

            if response.status_code == 200:
                return True, response.json(), None
            else:
                error_msg = response.json().get("detail", "점수 조회 실패")
                return False, None, error_msg

        except requests.exceptions.RequestException as e:
            return False, None, f"네트워크 오류: {str(e)}"

    def get_my_scores(self) -> tuple[bool, Optional[List], Optional[str]]:
        """
        내 점수 조회

        Returns:
            tuple: (성공 여부, 점수 리스트, 에러 메시지)
        """
        if not self.session_manager.is_logged_in():
            return False, None, "로그인이 필요합니다"

        try:
            response = requests.get(
                f"{self.base_url}/api/scores/my",
                headers=self._get_headers(),
                timeout=5
            )

            if response.status_code == 200:
                return True, response.json(), None
            else:
                error_msg = response.json().get("detail", "점수 조회 실패")
                return False, None, error_msg

        except requests.exceptions.RequestException as e:
            return False, None, f"네트워크 오류: {str(e)}"

    def get_my_stats(self) -> tuple[bool, Optional[Dict], Optional[str]]:
        """
        내 통계 조회

        Returns:
            tuple: (성공 여부, 통계 데이터, 에러 메시지)
        """
        if not self.session_manager.is_logged_in():
            return False, None, "로그인이 필요합니다"

        try:
            response = requests.get(
                f"{self.base_url}/api/scores/stats",
                headers=self._get_headers(),
                timeout=5
            )

            if response.status_code == 200:
                return True, response.json(), None
            else:
                error_msg = response.json().get("detail", "통계 조회 실패")
                return False, None, error_msg

        except requests.exceptions.RequestException as e:
            return False, None, f"네트워크 오류: {str(e)}"

    def check_connection(self) -> bool:
        """
        서버 연결 확인

        Returns:
            bool: 연결 여부
        """
        try:
            response = requests.get(f"{self.base_url}/health", timeout=3)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def logout(self):
        """로그아웃 처리"""
        self.session_manager.logout()

    def is_logged_in(self) -> bool:
        """
        로그인 여부 확인

        Returns:
            bool: 로그인 상태
        """
        return self.session_manager.is_logged_in()

    # 비동기 메서드들 (Future 반환)

    def register_async(self, username: str, password: str) -> Future:
        """
        비동기 회원가입

        Args:
            username: 사용자명
            password: 비밀번호

        Returns:
            Future: (성공 여부, 응답 데이터, 에러 메시지) 튜플을 반환하는 Future
        """
        return self._executor.submit(self.register, username, password)

    def login_async(self, username: str, password: str) -> Future:
        """
        비동기 로그인

        Args:
            username: 사용자명
            password: 비밀번호

        Returns:
            Future: (성공 여부, 응답 데이터, 에러 메시지) 튜플을 반환하는 Future
        """
        return self._executor.submit(self.login, username, password)

    def save_score_async(self, score: int) -> Future:
        """
        비동기 점수 저장

        Args:
            score: 점수

        Returns:
            Future: (성공 여부, 응답 데이터, 에러 메시지) 튜플을 반환하는 Future
        """
        return self._executor.submit(self.save_score, score)

    def get_top_scores_async(self, limit: int = 10) -> Future:
        """
        비동기 상위 점수 조회

        Args:
            limit: 조회할 개수

        Returns:
            Future: (성공 여부, 점수 리스트, 에러 메시지) 튜플을 반환하는 Future
        """
        return self._executor.submit(self.get_top_scores, limit)

    def get_my_scores_async(self) -> Future:
        """
        비동기 내 점수 조회

        Returns:
            Future: (성공 여부, 점수 리스트, 에러 메시지) 튜플을 반환하는 Future
        """
        return self._executor.submit(self.get_my_scores)

    def get_my_stats_async(self) -> Future:
        """
        비동기 내 통계 조회

        Returns:
            Future: (성공 여부, 통계 데이터, 에러 메시지) 튜플을 반환하는 Future
        """
        return self._executor.submit(self.get_my_stats)

    def check_connection_async(self) -> Future:
        """
        비동기 서버 연결 확인

        Returns:
            Future: 연결 여부를 반환하는 Future
        """
        return self._executor.submit(self.check_connection)

    def shutdown(self):
        """
        ThreadPoolExecutor 종료

        게임 종료 시 호출하여 모든 스레드를 정리합니다.
        """
        self._executor.shutdown(wait=True)
        logger.info("API 클라이언트 스레드 풀 종료")
